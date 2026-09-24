import cv2


def clean_image(image):
    """
    Basic image cleaning.

    Steps:
    1. Denoising
    2. Brightness/contrast normalization
    3. Color conversion back to BGR
    """

    # Denoising
    denoised = cv2.fastNlMeansDenoisingColored(
        image,
        None,
        5,
        5,
        7,
        21
    )

    # Convert to LAB
    lab = cv2.cvtColor(
        denoised,
        cv2.COLOR_BGR2LAB
    )

    l_channel, a_channel, b_channel = cv2.split(lab)

    # CLAHE for local contrast enhancement
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    l_channel = clahe.apply(l_channel)

    # Merge channels
    enhanced_lab = cv2.merge(
        [l_channel, a_channel, b_channel]
    )

    # Convert back to BGR
    cleaned = cv2.cvtColor(
        enhanced_lab,
        cv2.COLOR_LAB2BGR
    )

    return cleaned