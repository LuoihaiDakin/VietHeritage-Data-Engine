import cv2
import numpy as np


def calculate_sharpness(image):
    """
    Sharpness using Laplacian variance.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return float(
        cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()
    )


def calculate_brightness(image):
    """
    Mean grayscale brightness.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return float(
        np.mean(gray)
    )


def calculate_contrast(image):
    """
    Standard deviation of grayscale values.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return float(
        np.std(gray)
    )


def evaluate_image(image):
    """
    Calculate baseline technical metrics.
    """

    height, width = image.shape[:2]

    return {
        "width": width,
        "height": height,
        "brightness": round(
            calculate_brightness(image),
            2
        ),
        "contrast": round(
            calculate_contrast(image),
            2
        ),
        "sharpness": round(
            calculate_sharpness(image),
            2
        )
    }