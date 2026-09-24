import cv2


def super_resolution_baseline(
    image,
    scale=4
):
    """
    Baseline super-resolution using
    bicubic interpolation.

    This is NOT an AI super-resolution model.
    It is used as the initial baseline.
    """

    height, width = image.shape[:2]

    new_width = width * scale
    new_height = height * scale

    upscaled = cv2.resize(
        image,
        (new_width, new_height),
        interpolation=cv2.INTER_CUBIC
    )

    return upscaled


def restore_image(image):
    """
    Baseline restoration pipeline.

    1. Upscale
    2. Denoise
    3. Sharpen
    """

    # Super resolution baseline
    upscaled = super_resolution_baseline(
        image,
        scale=4
    )

    # Mild denoising
    denoised = cv2.fastNlMeansDenoisingColored(
        upscaled,
        None,
        3,
        3,
        7,
        21
    )

    # Sharpening
    gaussian = cv2.GaussianBlur(
        denoised,
        (0, 0),
        1.2
    )

    sharpened = cv2.addWeighted(
        denoised,
        1.5,
        gaussian,
        -0.5,
        0
    )

    return sharpened