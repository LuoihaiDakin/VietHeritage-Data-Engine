import cv2


def denoise_image(image):
    """
    Remove noise from an image.
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
    Adjust brightness and contrast.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    brightness = gray.mean()
    contrast = gray.std()

    # Adjust brightness
    if brightness < 100:
        image = cv2.convertScaleAbs(image, alpha=1.0, beta=30)

    elif brightness > 180:
        image = cv2.convertScaleAbs(image, alpha=1.0, beta=-30)

    # Adjust contrast
    if contrast < 30:
        image = cv2.convertScaleAbs(image, alpha=1.3, beta=0)

    return image