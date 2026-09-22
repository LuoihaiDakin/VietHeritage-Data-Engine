import cv2


def enhance_image(image):
    """
    Improve local contrast and reduce noise
    while preserving the original image structure.
    """

    # --------------------------------
    # Convert BGR to LAB
    # --------------------------------

    lab = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB
    )

    # --------------------------------
    # Split LAB channels
    # --------------------------------

    l_channel, a_channel, b_channel = cv2.split(
        lab
    )

    # --------------------------------
    # Improve local contrast
    # --------------------------------

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced_l = clahe.apply(
        l_channel
    )

    # --------------------------------
    # Merge channels
    # --------------------------------

    enhanced_lab = cv2.merge(
        (
            enhanced_l,
            a_channel,
            b_channel
        )
    )

    # --------------------------------
    # Convert back to BGR
    # --------------------------------

    enhanced = cv2.cvtColor(
        enhanced_lab,
        cv2.COLOR_LAB2BGR
    )

    # --------------------------------
    # Slight denoising
    # --------------------------------

    enhanced = cv2.fastNlMeansDenoisingColored(
        enhanced,
        None,
        3,
        3,
        7,
        21
    )

    return enhanced