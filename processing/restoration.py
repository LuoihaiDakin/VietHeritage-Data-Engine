import os
import subprocess
import tempfile

import cv2


# ============================================================
# REAL-ESRGAN CONFIGURATION
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# Folder containing the Real-ESRGAN executable
REALESRGAN_DIR = os.path.join(
    PROJECT_ROOT,
    "ai_models",
    "realesrgan"
)

# Real-ESRGAN executable
REALESRGAN_EXE = os.path.join(
    REALESRGAN_DIR,
    "realesrgan-ncnn-vulkan.exe"
)

# Folder containing .bin and .param model files
REALESRGAN_MODEL_DIR = os.path.join(
    REALESRGAN_DIR,
    "models"
)

# Model used for VietHeritage
REALESRGAN_MODEL = "realesrgan-x4plus"

# 4x super resolution
REALESRGAN_SCALE = 4


# ============================================================
# CHECK REAL-ESRGAN
# ============================================================

def check_realesrgan():
    """
    Check whether the Real-ESRGAN executable
    and required model files exist.
    """

    if not os.path.isfile(REALESRGAN_EXE):
        raise FileNotFoundError(
            "Real-ESRGAN executable not found:\n"
            f"{REALESRGAN_EXE}"
        )

    model_bin = os.path.join(
        REALESRGAN_MODEL_DIR,
        f"{REALESRGAN_MODEL}.bin"
    )

    model_param = os.path.join(
        REALESRGAN_MODEL_DIR,
        f"{REALESRGAN_MODEL}.param"
    )

    if not os.path.isfile(model_bin):
        raise FileNotFoundError(
            "Real-ESRGAN model .bin not found:\n"
            f"{model_bin}"
        )

    if not os.path.isfile(model_param):
        raise FileNotFoundError(
            "Real-ESRGAN model .param not found:\n"
            f"{model_param}"
        )


# ============================================================
# AI SUPER RESOLUTION
# ============================================================

def super_resolution_ai(image):
    """
    Upscale an OpenCV image using Real-ESRGAN x4plus.

    Input:
        OpenCV BGR image

    Output:
        OpenCV BGR image
    """

    check_realesrgan()

    # Temporary folder is used so the main project
    # does not accumulate unnecessary intermediate files.
    with tempfile.TemporaryDirectory(
        prefix="vietheritage_sr_"
    ) as temp_dir:

        input_path = os.path.join(
            temp_dir,
            "input.png"
        )

        output_path = os.path.join(
            temp_dir,
            "output.png"
        )

        # ----------------------------------------------------
        # Save input image
        # ----------------------------------------------------

        success = cv2.imwrite(
            input_path,
            image
        )

        if not success:
            raise RuntimeError(
                "Failed to save temporary input image."
            )

        # ----------------------------------------------------
        # Build Real-ESRGAN command
        # ----------------------------------------------------

        command = [
            REALESRGAN_EXE,

            "-i",
            input_path,

            "-o",
            output_path,

            "-m",
            REALESRGAN_MODEL_DIR,

            "-n",
            REALESRGAN_MODEL,

            "-s",
            str(REALESRGAN_SCALE),

            "-f",
            "png"
        ]

        # ----------------------------------------------------
        # Run Real-ESRGAN
        # ----------------------------------------------------

        try:
            result = subprocess.run(
                command,
                cwd=REALESRGAN_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False
            )

        except OSError as error:
            raise RuntimeError(
                "Failed to start Real-ESRGAN.\n\n"
                f"Executable:\n"
                f"{REALESRGAN_EXE}\n\n"
                f"Error:\n"
                f"{error}"
            ) from error

        # ----------------------------------------------------
        # Check process result
        # ----------------------------------------------------

        if result.returncode != 0:
            raise RuntimeError(
                "Real-ESRGAN failed.\n\n"
                f"Command:\n"
                f"{' '.join(command)}\n\n"
                f"Real-ESRGAN output:\n"
                f"{result.stdout}"
            )

        # ----------------------------------------------------
        # Check output file
        # ----------------------------------------------------

        if not os.path.isfile(output_path):
            raise RuntimeError(
                "Real-ESRGAN finished but did not create "
                "the output image.\n\n"
                f"Real-ESRGAN output:\n"
                f"{result.stdout}"
            )

        # ----------------------------------------------------
        # Read restored image
        # ----------------------------------------------------

        restored = cv2.imread(
            output_path,
            cv2.IMREAD_COLOR
        )

        if restored is None:
            raise RuntimeError(
                "Failed to read the Real-ESRGAN output image."
            )

        return restored


# ============================================================
# RESTORATION PIPELINE
# ============================================================

def restore_image(image):
    """
    VietHeritage AI restoration.

    Current pipeline:

        Input
          ↓
        Real-ESRGAN x4plus
          ↓
        AI restored image

    Additional enhancement will be added
    after the Real-ESRGAN integration is verified.
    """

    if image is None:
        raise ValueError(
            "restore_image received an empty image."
        )

    if len(image.shape) != 3:
        raise ValueError(
            "restore_image expects a color image."
        )

    restored = super_resolution_ai(
        image
    )

    return restored