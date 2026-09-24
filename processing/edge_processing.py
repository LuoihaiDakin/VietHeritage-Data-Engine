import cv2
import numpy as np


def process_edges(image):
    """
    Extract and clean important edges.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Slight blur to reduce noise
    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    # Edge detection
    edges = cv2.Canny(
        blurred,
        50,
        150
    )

    # Morphological closing
    kernel = np.ones(
        (3, 3),
        np.uint8
    )

    edges = cv2.morphologyEx(
        edges,
        cv2.MORPH_CLOSE,
        kernel
    )

    return edges