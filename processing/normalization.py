import cv2


def normalize_image(image, max_size=1200):
    """
    Normalize image size and channel format.

    - Convert image to standard BGR format
    - Remove alpha channel if present
    - Resize image while preserving aspect ratio
    - Keep original image if it is already within max_size
    """

    if image is None:
        raise ValueError("Input image is None.")

    # ----------------------------------------
    # 1. Normalize channels
    # ----------------------------------------

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

    # ----------------------------------------
    # 2. Normalize image size
    # ----------------------------------------

    height, width = image.shape[:2]

    largest_dimension = max(
        width,
        height
    )

    if largest_dimension > max_size:

        scale = max_size / largest_dimension

        new_width = int(width * scale)
        new_height = int(height * scale)

        image = cv2.resize(
            image,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA
        )

    return image