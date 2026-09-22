import cv2


def upscale_image(image, scale=2):
    """
    Upscale an image using Lanczos interpolation.

    This is the baseline before introducing
    an AI super-resolution model.
    """

    height, width = image.shape[:2]

    new_width = width * scale
    new_height = height * scale

    upscaled = cv2.resize(
        image,
        (new_width, new_height),
        interpolation=cv2.INTER_LANCZOS4
    )

    return upscaled