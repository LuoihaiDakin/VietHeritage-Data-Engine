import os
import cv2
import numpy as np


# ==========================================
# CONFIGURATION
# ==========================================

TARGET_SIZE = 1024

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
        print(f"ERROR: Cannot read image: {image_path}")
        return None

    return image


# ==========================================
# RESIZE IMAGE
# ==========================================

def resize_image(image):
    """
    Resize image while preserving aspect ratio.

    The longest side will be TARGET_SIZE.
    """

    height, width = image.shape[:2]

    if height <= 0 or width <= 0:
        return None

    longest_side = max(
        height,
        width
    )

    # Already at or below target size
    if longest_side == TARGET_SIZE:
        return image

    scale = TARGET_SIZE / longest_side

    new_width = max(
        1,
        int(width * scale)
    )

    new_height = max(
        1,
        int(height * scale)
    )

    resized = cv2.resize(
        image,
        (new_width, new_height),
        interpolation=cv2.INTER_AREA
        if scale < 1
        else cv2.INTER_LANCZOS4
    )

    return resized


# ==========================================
# COLOR NORMALIZATION
# ==========================================

def normalize_color(image):
    """
    Normalize color distribution using LAB color space.

    This does not force the image to grayscale.
    """

    lab = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB
    )

    l_channel, a_channel, b_channel = cv2.split(lab)

    # Normalize luminance gently
    l_normalized = cv2.normalize(
        l_channel,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

    normalized_lab = cv2.merge(
        (
            l_normalized,
            a_channel,
            b_channel
        )
    )

    normalized = cv2.cvtColor(
        normalized_lab,
        cv2.COLOR_LAB2BGR
    )

    return normalized


# ==========================================
# WHITE BALANCE
# ==========================================

def white_balance(image):
    """
    Simple gray-world white balance.

    This reduces strong color casts while
    keeping the original color information.
    """

    image_float = image.astype(
        np.float32
    )

    mean_b = np.mean(
        image_float[:, :, 0]
    )

    mean_g = np.mean(
        image_float[:, :, 1]
    )

    mean_r = np.mean(
        image_float[:, :, 2]
    )

    mean_gray = (
        mean_b +
        mean_g +
        mean_r
    ) / 3.0

    if mean_b > 0:
        image_float[:, :, 0] *= (
            mean_gray / mean_b
        )

    if mean_g > 0:
        image_float[:, :, 1] *= (
            mean_gray / mean_g
        )

    if mean_r > 0:
        image_float[:, :, 2] *= (
            mean_gray / mean_r
        )

    image_float = np.clip(
        image_float,
        0,
        255
    )

    return image_float.astype(
        np.uint8
    )


# ==========================================
# NORMALIZE BRIGHTNESS
# ==========================================

def normalize_brightness(image):
    """
    Apply gentle brightness normalization.
    """

    lab = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB
    )

    l_channel, a_channel, b_channel = cv2.split(
        lab
    )

    mean_brightness = float(
        np.mean(l_channel)
    )

    # Only make strong corrections.
    if mean_brightness < 50:

        difference = 50 - mean_brightness

        l_channel = cv2.add(
            l_channel,
            int(min(difference, 30))
        )

    elif mean_brightness > 210:

        difference = mean_brightness - 210

        l_channel = cv2.subtract(
            l_channel,
            int(min(difference, 30))
        )

    normalized_lab = cv2.merge(
        (
            l_channel,
            a_channel,
            b_channel
        )
    )

    normalized = cv2.cvtColor(
        normalized_lab,
        cv2.COLOR_LAB2BGR
    )

    return normalized


# ==========================================
# STANDARDIZE IMAGE FORMAT
# ==========================================

def standardize_format(image):
    """
    Ensure the image is a standard 8-bit
    3-channel BGR image.
    """

    if image.dtype != np.uint8:

        image = np.clip(
            image,
            0,
            255
        ).astype(
            np.uint8
        )

    if len(image.shape) == 2:

        image = cv2.cvtColor(
            image,
            cv2.COLOR_GRAY2BGR
        )

    elif image.shape[2] == 4:

        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGRA2BGR
        )

    return image


# ==========================================
# NORMALIZATION PIPELINE
# ==========================================

def normalize_image(image):
    """
    Complete normalization pipeline.

    1. Standardize image format
    2. White balance
    3. Brightness normalization
    4. Color normalization
    5. Resize
    """

    image = standardize_format(
        image
    )

    image = white_balance(
        image
    )

    image = normalize_brightness(
        image
    )

    image = normalize_color(
        image
    )

    image = resize_image(
        image
    )

    return image


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
# PROCESS IMAGE
# ==========================================

def process_image(
    input_path,
    output_path
):
    """
    Normalize one image and save it.
    """

    image = load_image(
        input_path
    )

    if image is None:
        return False

    normalized = normalize_image(
        image
    )

    if normalized is None:
        print(
            f"ERROR: Normalization failed: {input_path}"
        )
        return False

    output_directory = os.path.dirname(
        output_path
    )

    os.makedirs(
        output_directory,
        exist_ok=True
    )

    success = cv2.imwrite(
        output_path,
        normalized
    )

    if not success:

        print(
            f"ERROR: Failed to save: {output_path}"
        )

        return False

    return True


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
        "restoration"
    )

    output_directory = os.path.join(
        project_root,
        "outputs",
        "normalization"
    )

    print(
        "========================================"
    )

    print(
        "      VietHeritage Normalization"
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

    if not os.path.exists(
        input_directory
    ):

        print(
            "ERROR: Restoration output directory "
            "does not exist."
        )

        print(
            "Run restoration first."
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
            f"Normalizing: {relative_path}"
        )

        success = process_image(
            input_path,
            output_path
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

    print()

    print(
        "========================================"
    )

    print(
        "NORMALIZATION COMPLETED"
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
        "========================================"
    )


if __name__ == "__main__":
    main()