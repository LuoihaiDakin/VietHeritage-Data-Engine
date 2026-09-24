import cv2
import numpy as np


def segment_image(image):
    """
    Baseline foreground segmentation.

    Uses GrabCut to separate the main
    object from the background.
    """

    height, width = image.shape[:2]

    mask = np.zeros(
        (height, width),
        np.uint8
    )

    # Initial rectangle.
    # Leave a small border around the image.
    margin_x = max(5, int(width * 0.05))
    margin_y = max(5, int(height * 0.05))

    rect = (
        margin_x,
        margin_y,
        width - 2 * margin_x,
        height - 2 * margin_y
    )

    bgd_model = np.zeros(
        (1, 65),
        np.float64
    )

    fgd_model = np.zeros(
        (1, 65),
        np.float64
    )

    cv2.grabCut(
        image,
        mask,
        rect,
        bgd_model,
        fgd_model,
        5,
        cv2.GC_INIT_WITH_RECT
    )

    # Foreground = 1 or 3
    foreground = np.where(
        (mask == cv2.GC_FGD) |
        (mask == cv2.GC_PR_FGD),
        255,
        0
    ).astype("uint8")

    # Clean mask
    kernel = np.ones(
        (3, 3),
        np.uint8
    )

    foreground = cv2.morphologyEx(
        foreground,
        cv2.MORPH_OPEN,
        kernel
    )

    foreground = cv2.morphologyEx(
        foreground,
        cv2.MORPH_CLOSE,
        kernel
    )

    # Create transparent PNG
    bgra = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2BGRA
    )

    bgra[:, :, 3] = foreground

    return bgra, foreground