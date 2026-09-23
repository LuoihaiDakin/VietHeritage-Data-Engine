import os
import json
import cv2
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

TARGET_SIZE = 1024

DENOISE_STRENGTH = 7

CLAHE_CLIP_LIMIT = 2.0
CLAHE_GRID_SIZE = (8, 8)


# ============================================================
# LOAD IMAGE
# ============================================================

def load_image(image_path):
    """
    Load image using OpenCV.
    """

    image = cv2.imread(
        image_path,
        cv2.IMREAD_COLOR
    )

    if image is None:
        print(
            f"WARNING: Cannot read image: {image_path}"
        )

        return None

    return image


# ============================================================
# DENOISING
# ============================================================

def denoise_image(image):
    """
    Reduce noise while preserving edges.
    """

    denoised = cv2.fastNlMeansDenoisingColored(
        image,
        None,
        DENOISE_STRENGTH,
        DENOISE_STRENGTH,
        7,
        21
    )

    return denoised


# ============================================================
# CONTRAST ENHANCEMENT
# ============================================================

def enhance_contrast(image):
    """
    Improve local contrast using CLAHE.
    """

    lab = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB
    )

    l_channel, a_channel, b_channel = cv2.split(
        lab
    )

    clahe = cv2.createCLAHE(
        clipLimit=CLAHE_CLIP_LIMIT,
        tileGridSize=CLAHE_GRID_SIZE
    )

    l_channel = clahe.apply(
        l_channel
    )

    enhanced_lab = cv2.merge(
        (
            l_channel,
            a_channel,
            b_channel
        )
    )

    enhanced = cv2.cvtColor(
        enhanced_lab,
        cv2.COLOR_LAB2BGR
    )

    return enhanced


# ============================================================
# BRIGHTNESS CORRECTION
# ============================================================

def correct_brightness(image):
    """
    Apply mild gamma correction based on
    average image brightness.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    brightness = gray.mean()

    if brightness < 70:

        gamma = 0.75

    elif brightness > 190:

        gamma = 1.20

    else:

        return image

    lookup_table = np.array(
        [
            (
                ((i / 255.0) ** gamma)
                * 255
            )
            for i in range(256)
        ],
        dtype=np.uint8
    )

    corrected = cv2.LUT(
        image,
        lookup_table
    )

    return corrected


# ============================================================
# UPSCALING
# ============================================================

def upscale_image(image):
    """
    Upscale small images using Lanczos interpolation.

    This does NOT create missing historical detail.
    It only increases image resolution.
    """

    height, width = image.shape[:2]

    if width >= TARGET_SIZE and height >= TARGET_SIZE:

        return image

    scale = TARGET_SIZE / min(
        width,
        height
    )

    new_width = int(
        width * scale
    )

    new_height = int(
        height * scale
    )

    upscaled = cv2.resize(
        image,
        (
            new_width,
            new_height
        ),
        interpolation=cv2.INTER_LANCZOS4
    )

    return upscaled


# ============================================================
# FULL PREPROCESSING PIPELINE
# ============================================================

def preprocess_image(image):
    """
    Apply preprocessing operations in sequence.
    """

    result = image.copy()

    # Step 1
    result = denoise_image(
        result
    )

    # Step 2
    result = correct_brightness(
        result
    )

    # Step 3
    result = enhance_contrast(
        result
    )

    # Step 4
    result = upscale_image(
        result
    )

    return result


# ============================================================
# PATH HELPERS
# ============================================================

def get_project_root():
    """
    Get project root directory.
    """

    return os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )


# ============================================================
# PROCESS ONE IMAGE
# ============================================================

def process_one_image(
    metadata,
    dataset_path,
    output_path
):
    """
    Process one image and save it.
    """

    relative_path = metadata.get(
        "path"
    )

    if not relative_path:

        print(
            "WARNING: Image path missing."
        )

        return False

    # Convert relative dataset path
    # into absolute path
    image_path = os.path.join(
        dataset_path,
        relative_path.replace(
            "/",
            os.sep
        )
    )

    image = load_image(
        image_path
    )

    if image is None:
        return False

    processed = preprocess_image(
        image
    )

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    success = cv2.imwrite(
        output_path,
        processed
    )

    if not success:

        print(
            f"WARNING: Failed to save: {output_path}"
        )

        return False

    return True


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "========================================"
    )

    print(
        "   VietHeritage Image Preprocessing"
    )

    print(
        "========================================"
    )

    print()

    project_root = get_project_root()

    dataset_path = os.path.join(
        project_root,
        "dataset"
    )

    metadata_path = os.path.join(
        dataset_path,
        "metadata",
        "quality_report.json"
    )

    output_root = os.path.join(
        project_root,
        "outputs",
        "preprocessing"
    )

    # --------------------------------------------------------
    # Check metadata
    # --------------------------------------------------------

    if not os.path.exists(
        metadata_path
    ):

        print(
            "ERROR: quality_report.json not found."
        )

        print(
            metadata_path
        )

        print()

        print(
            "Run quality_scorer.py first."
        )

        return

    # --------------------------------------------------------
    # Load quality report
    # --------------------------------------------------------

    with open(
        metadata_path,
        "r",
        encoding="utf-8"
    ) as file:

        report = json.load(
            file
        )

    results = report.get(
        "results",
        []
    )

    if not results:

        print(
            "No image results found."
        )

        return

    print(
        f"Images in quality report: "
        f"{len(results)}"
    )

    print()

    # --------------------------------------------------------
    # Process images
    # --------------------------------------------------------

    processed_count = 0
    skipped_count = 0

    for item in results:

        quality = item.get(
            "quality"
        )

        relative_path = item.get(
            "path"
        )

        if not relative_path:
            skipped_count += 1
            continue

        # ----------------------------------------------------
        # Only process POOR and ACCEPTABLE images
        # ----------------------------------------------------

        if quality == "GOOD":

            print(
                f"SKIP GOOD: "
                f"{item.get('filename')}"
            )

            skipped_count += 1

            continue

        input_path = os.path.join(
            dataset_path,
            relative_path.replace(
                "/",
                os.sep
            )
        )

        # Preserve category folders
        category = item.get(
            "category",
            "unknown"
        )

        filename = item.get(
            "filename"
        )

        output_path = os.path.join(
            output_root,
            category,
            filename
        )

        print(
            f"PROCESSING: "
            f"{filename}"
        )

        success = process_one_image(
            item,
            dataset_path,
            output_path
        )

        if success:

            processed_count += 1

        else:

            skipped_count += 1

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()

    print(
        "========================================"
    )

    print(
        "        PREPROCESSING SUMMARY"
    )

    print(
        "========================================"
    )

    print(
        f"Processed : {processed_count}"
    )

    print(
        f"Skipped   : {skipped_count}"
    )

    print()

    print(
        f"Output directory:"
    )

    print(
        output_root
    )

    print()

    print(
        "Preprocessing completed."
    )


if __name__ == "__main__":
    main()