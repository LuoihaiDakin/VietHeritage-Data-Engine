import cv2
import numpy as np


def process_edges(image):
    """
    VietHeritage Edge Restoration / Processing.

    Pipeline:
        Grayscale
            ↓
        Noise reduction
            ↓
        Contrast enhancement
            ↓
        Canny edge detection
            ↓
        Morphological closing
            ↓
        Morphological opening
            ↓
        Final edge cleanup

    Input:
        OpenCV BGR image

    Output:
        Clean binary edge map
    """

    if image is None:
        raise ValueError(
            "process_edges received an empty image."
        )

    if len(image.shape) != 3:
        raise ValueError(
            "process_edges expects a color image."
        )

    # ========================================================
    # 1. Convert to grayscale
    # ========================================================

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # ========================================================
    # 2. Noise reduction
    # ========================================================

    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    # ========================================================
    # 3. Local contrast enhancement
    # ========================================================

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(
        blurred
    )

    # ========================================================
    # 4. Canny edge detection
    # ========================================================

    edges = cv2.Canny(
        enhanced,
        50,
        150
    )

    # ========================================================
    # 5. Close small gaps in heritage patterns
    # ========================================================

    close_kernel = np.ones(
        (3, 3),
        np.uint8
    )

    edges = cv2.morphologyEx(
        edges,
        cv2.MORPH_CLOSE,
        close_kernel,
        iterations=1
    )

    # ========================================================
    # 6. Remove isolated noise
    # ========================================================

    open_kernel = np.ones(
        (2, 2),
        np.uint8
    )

    edges = cv2.morphologyEx(
        edges,
        cv2.MORPH_OPEN,
        open_kernel,
        iterations=1
    )

    # ========================================================
    # 7. Final binary cleanup
    # ========================================================

    _, edges = cv2.threshold(
        edges,
        127,
        255,
        cv2.THRESH_BINARY
    )

    return edges