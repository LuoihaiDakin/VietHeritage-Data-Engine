import os
import cv2
import numpy as np


# ==========================================
# CONFIGURATION
# ==========================================

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff"
}

# Number of GrabCut iterations
GRABCUT_ITERATIONS = 5

# Minimum foreground area ratio.
# If the detected foreground is too small,
# the system will fall back to a simpler mask.
MIN_FOREGROUND_RATIO = 0.02


# ==========================================
# LOAD IMAGE
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
        print(
            f"ERROR: Cannot read image: {image_path}"
        )
        return None

    return image


# ==========================================
# CREATE INITIAL MASK
# ==========================================

def create_initial_mask(image):
    """
    Create an initial foreground/background
    mask for GrabCut.

    The border is considered background.
    The central region is considered probable
    foreground.
    """

    height, width = image.shape[:2]

    mask = np.full(
        (height, width),
        cv2.GC_BGD,
        dtype=np.uint8
    )

    # Keep a border around the image as background.
    border_x = max(
        int(width * 0.05),
        5
    )

    border_y = max(
        int(height * 0.05),
        5
    )

    # Central region = probable foreground
    x1 = border_x
    y1 = border_y
    x2 = width - border_x
    y2 = height - border_y

    mask[
        y1:y2,
        x1:x2
    ] = cv2.GC_PR_FGD

    return mask


# ==========================================
# GRABCUT SEGMENTATION
# ==========================================

def grabcut_segmentation(image):
    """
    Perform foreground segmentation using GrabCut.
    """

    mask = create_initial_mask(
        image
    )

    background_model = np.zeros(
        (1, 65),
        np.float64
    )

    foreground_model = np.zeros(
        (1, 65),
        np.float64
    )

    cv2.grabCut(
        image,
        mask,
        None,
        background_model,
        foreground_model,
        GRABCUT_ITERATIONS,
        cv2.GC_INIT_WITH_MASK
    )

    # Pixels marked as definite/probable foreground
    # become white.
    foreground_mask = np.where(
        (
            (mask == cv2.GC_FGD) |
            (mask == cv2.GC_PR_FGD)
        ),
        255,
        0
    ).astype(
        np.uint8
    )

    return foreground_mask


# ==========================================
# CLEAN MASK
# ==========================================

def clean_mask(mask):
    """
    Remove small noise and fill small holes.
    """

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (5, 5)
    )

    # Remove small noise
    cleaned = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel,
        iterations=1
    )

    # Close small holes
    cleaned = cv2.morphologyEx(
        cleaned,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )

    return cleaned


# ==========================================
# CHECK MASK QUALITY
# ==========================================

def check_mask(mask):
    """
    Check whether the segmentation result
    contains a reasonable foreground area.
    """

    total_pixels = mask.shape[0] * mask.shape[1]

    foreground_pixels = np.count_nonzero(
        mask
    )

    if total_pixels == 0:
        return False

    foreground_ratio = (
        foreground_pixels /
        total_pixels
    )

    return (
        foreground_ratio >=
        MIN_FOREGROUND_RATIO
    )


# ==========================================
# FALLBACK MASK
# ==========================================

def create_fallback_mask(image):
    """
    Create a simple central mask if GrabCut
    produces an unusable result.

    This is only a fallback and is not intended
    to replace proper segmentation.
    """

    height, width = image.shape[:2]

    mask = np.zeros(
        (height, width),
        dtype=np.uint8
    )

    x1 = int(width * 0.05)
    y1 = int(height * 0.05)

    x2 = int(width * 0.95)
    y2 = int(height * 0.95)

    mask[
        y1:y2,
        x1:x2
    ] = 255

    return mask


# ==========================================
# APPLY MASK
# ==========================================

def apply_mask(image, mask):
    """
    Extract the segmented foreground.
    Background becomes black.
    """

    result = cv2.bitwise_and(
        image,
        image,
        mask=mask
    )

    return result


# ==========================================
# CREATE TRANSPARENT RESULT
# ==========================================

def create_transparent_result(
    image,
    mask
):
    """
    Create a BGRA image where the segmented
    foreground remains visible and the
    background becomes transparent.
    """

    alpha = mask.copy()

    result = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2BGRA
    )

    result[:, :, 3] = alpha

    return result


# ==========================================
# PROCESS ONE IMAGE
# ==========================================

def process_image(
    input_path,
    output_image_path,
    output_mask_path,
    output_transparent_path
):
    """
    Segment one image and save:

    1. Segmented image
    2. Binary mask
    3. Transparent PNG
    """

    image = load_image(
        input_path
    )

    if image is None:
        return False

    # --------------------------------------
    # GrabCut
    # --------------------------------------

    mask = grabcut_segmentation(
        image
    )

    # --------------------------------------
    # Clean mask
    # --------------------------------------

    mask = clean_mask(
        mask
    )

    # --------------------------------------
    # Check result
    # --------------------------------------

    if not check_mask(mask):

        print(
            "  WARNING: Segmentation mask "
            "is too small."
        )

        print(
            "  Using fallback mask."
        )

        mask = create_fallback_mask(
            image
        )

    # --------------------------------------
    # Create outputs
    # --------------------------------------

    segmented = apply_mask(
        image,
        mask
    )

    transparent = create_transparent_result(
        image,
        mask
    )

    # --------------------------------------
    # Create directories
    # --------------------------------------

    os.makedirs(
        os.path.dirname(
            output_image_path
        ),
        exist_ok=True
    )

    os.makedirs(
        os.path.dirname(
            output_mask_path
        ),
        exist_ok=True
    )

    os.makedirs(
        os.path.dirname(
            output_transparent_path
        ),
        exist_ok=True
    )

    # --------------------------------------
    # Save
    # --------------------------------------

    image_success = cv2.imwrite(
        output_image_path,
        segmented
    )

    mask_success = cv2.imwrite(
        output_mask_path,
        mask
    )

    transparent_success = cv2.imwrite(
        output_transparent_path,
        transparent
    )

    if not image_success:
        return False

    if not mask_success:
        return False

    if not transparent_success:
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

            image_files.append(
                full_path
            )

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
        "normalization"
    )

    output_directory = os.path.join(
        project_root,
        "outputs",
        "segmentation"
    )

    mask_directory = os.path.join(
        project_root,
        "outputs",
        "segmentation_masks"
    )

    transparent_directory = os.path.join(
        project_root,
        "outputs",
        "segmentation_transparent"
    )

    print(
        "========================================"
    )

    print(
        "       VietHeritage Segmentation"
    )

    print(
        "========================================"
    )

    print()

    print(
        f"Input: {input_directory}"
    )

    print(
        f"Segmented output: {output_directory}"
    )

    print(
        f"Masks: {mask_directory}"
    )

    print(
        f"Transparent: {transparent_directory}"
    )

    print()

    # --------------------------------------
    # Check input
    # --------------------------------------

    if not os.path.exists(
        input_directory
    ):

        print(
            "ERROR: Normalization output "
            "directory does not exist."
        )

        print(
            "Run normalization first."
        )

        return

    # --------------------------------------
    # Find images
    # --------------------------------------

    image_files = find_images(
        input_directory
    )

    print(
        f"Images found: {len(image_files)}"
    )

    print()

    success_count = 0
    failed_count = 0

    # --------------------------------------
    # Process
    # --------------------------------------

    for input_path in image_files:

        relative_path = os.path.relpath(
            input_path,
            input_directory
        )

        output_image_path = os.path.join(
            output_directory,
            relative_path
        )

        base_name = os.path.splitext(
            relative_path
        )[0]

        output_mask_path = os.path.join(
            mask_directory,
            base_name + "_mask.png"
        )

        output_transparent_path = os.path.join(
            transparent_directory,
            base_name + "_transparent.png"
        )

        print(
            f"Segmenting: {relative_path}"
        )

        success = process_image(
            input_path,
            output_image_path,
            output_mask_path,
            output_transparent_path
        )

        if success:

            success_count += 1

            print(
                "  -> OK"
            )

        else:

            failed_count += 1

            print(
                "  -> FAILED"
            )

    # --------------------------------------
    # Summary
    # --------------------------------------

    print()

    print(
        "========================================"
    )

    print(
        "SEGMENTATION COMPLETED"
    )

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
        f"Masks:      {mask_directory}"
    )

    print(
        f"Transparent:{transparent_directory}"
    )

    print(
        "========================================"
    )


if __name__ == "__main__":
    main()