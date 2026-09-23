import os
import cv2
import numpy as np


# ==========================================
# CONFIGURATION
# ==========================================

SHARPEN_AMOUNT = 1.2
DENOISE_STRENGTH = 3

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff"
}


# ==========================================
# IMAGE LOADING
# ==========================================

def load_image(image_path):
    """
    Load image from disk.
    """

    image = cv2.imread(
        image_path,
        cv2.IMREAD_COLOR
    )

    if image is None:
        print(f"ERROR: Cannot read image: {image_path}")
        return None

    return image


# ==========================================
# LIGHT DENOISING
# ==========================================

def denoise_image(image):
    """
    Apply light denoising.

    This is intentionally mild because
    heritage patterns may contain fine details.
    """

    result = cv2.fastNlMeansDenoisingColored(
        image,
        None,
        DENOISE_STRENGTH,
        DENOISE_STRENGTH,
        7,
        21
    )

    return result


# ==========================================
# LOCAL CONTRAST ENHANCEMENT
# ==========================================

def enhance_local_contrast(image):
    """
    Improve local contrast using CLAHE.
    """

    lab = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB
    )

    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=1.5,
        tileGridSize=(8, 8)
    )

    enhanced_l = clahe.apply(l_channel)

    enhanced_lab = cv2.merge(
        (
            enhanced_l,
            a_channel,
            b_channel
        )
    )

    result = cv2.cvtColor(
        enhanced_lab,
        cv2.COLOR_LAB2BGR
    )

    return result


# ==========================================
# SHARPENING
# ==========================================

def sharpen_image(image):
    """
    Apply controlled unsharp masking.

    This enhances existing edges but does not
    create real missing historical details.
    """

    blurred = cv2.GaussianBlur(
        image,
        (0, 0),
        2
    )

    sharpened = cv2.addWeighted(
        image,
        1.0 + SHARPEN_AMOUNT,
        blurred,
        -SHARPEN_AMOUNT,
        0
    )

    return sharpened


# ==========================================
# EDGE PRESERVING SMOOTHING
# ==========================================

def preserve_edges(image):
    """
    Use bilateral filtering to reduce small noise
    while preserving important pattern edges.
    """

    result = cv2.bilateralFilter(
        image,
        5,
        40,
        40
    )

    return result


# ==========================================
# RESTORATION PIPELINE
# ==========================================

def restore_image(image):
    """
    Complete restoration pipeline.

    Order:

    1. Light denoising
    2. Edge-preserving smoothing
    3. Local contrast enhancement
    4. Controlled sharpening
    """

    result = denoise_image(image)

    result = preserve_edges(result)

    result = enhance_local_contrast(result)

    result = sharpen_image(result)

    return result


# ==========================================
# PROCESS SINGLE IMAGE
# ==========================================

def process_image(input_path, output_path):
    """
    Restore one image and save the result.
    """

    image = load_image(input_path)

    if image is None:
        return False

    restored = restore_image(image)

    output_directory = os.path.dirname(
        output_path
    )

    os.makedirs(
        output_directory,
        exist_ok=True
    )

    success = cv2.imwrite(
        output_path,
        restored
    )

    if not success:
        print(
            f"ERROR: Failed to save: {output_path}"
        )

        return False

    return True


# ==========================================
# FIND IMAGES
# ==========================================

def find_images(input_directory):
    """
    Recursively find supported images.
    """

    image_files = []

    for root, directories, files in os.walk(
        input_directory
    ):

        for filename in files:

            extension = os.path.splitext(
                filename
            )[1].lower()

            if extension not in SUPPORTED_EXTENSIONS:
                continue

            full_path = os.path.join(
                root,
                filename
            )

            image_files.append(full_path)

    return image_files


# ==========================================
# MAIN
# ==========================================

def main():

    project_root = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    input_directory = os.path.join(
        project_root,
        "outputs",
        "preprocessing"
    )

    output_directory = os.path.join(
        project_root,
        "outputs",
        "restoration"
    )

    print(
        "========================================"
    )

    print(
        "      VietHeritage Restoration Engine"
    )

    print(
        "========================================"
    )

    print()

    print(
        f"Input : {input_directory}"
    )

    print(
        f"Output: {output_directory}"
    )

    print()

    if not os.path.exists(input_directory):

        print(
            "ERROR: Preprocessing output directory "
            "does not exist."
        )

        print(
            "Run preprocessing first."
        )

        return

    image_files = find_images(
        input_directory
    )

    print(
        f"Images found: {len(image_files)}"
    )

    print()

    success_count = 0
    failed_count = 0

    for input_path in image_files:

        relative_path = os.path.relpath(
            input_path,
            input_directory
        )

        output_path = os.path.join(
            output_directory,
            relative_path
        )

        print(
            f"Restoring: {relative_path}"
        )

        success = process_image(
            input_path,
            output_path
        )

        if success:
            success_count += 1
            print("  -> OK")

        else:
            failed_count += 1
            print("  -> FAILED")

    print()

    print(
        "========================================"
    )

    print("RESTORATION COMPLETED")

    print(
        f"Successful: {success_count}"
    )

    print(
        f"Failed:     {failed_count}"
    )

    print(
        f"Output:     {output_directory}"
    )

    print(
        "========================================"
    )


if __name__ == "__main__":
    main()