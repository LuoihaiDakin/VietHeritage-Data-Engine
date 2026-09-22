import cv2


def denoise_image(image):
    """
    Reduce noise while preserving important image details.
    """

    cleaned_image = cv2.fastNlMeansDenoisingColored(
        image,
        None,
        10,
        10,
        7,
        21
    )

    return cleaned_image


def adjust_brightness_contrast(image):
    """
    Adjust brightness and contrast based on the image itself.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    brightness = gray.mean()
    contrast = gray.std()

    alpha = 1.0
    beta = 0

    # Adjust brightness
    if brightness < 100:
        beta = 30

    elif brightness > 180:
        beta = -30

    # Adjust contrast
    if contrast < 30:
        alpha = 1.3

    adjusted = cv2.convertScaleAbs(
        image,
        alpha=alpha,
        beta=beta
    )

    return adjusted


def clean_image(image):
    """
    Complete cleaning pipeline.
    """

    # Step 1: denoise
    cleaned = denoise_image(image)

    # Step 2: adjust brightness and contrast
    cleaned = adjust_brightness_contrast(cleaned)

    return cleaned