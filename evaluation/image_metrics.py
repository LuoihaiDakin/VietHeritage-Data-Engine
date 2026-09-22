import cv2
import numpy as np


def calculate_sharpness(image):
    """
    Calculate image sharpness using
    Laplacian variance.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    variance = cv2.Laplacian(
        gray,
        cv2.CV_64F
    ).var()

    return float(variance)


def calculate_brightness(image):
    """
    Calculate average image brightness.
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
    Calculate image contrast using
    grayscale standard deviation.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return float(
        np.std(gray)
    )


def compare_images(original, processed):
    """
    Compare basic quality metrics between
    original and processed images.
    """

    results = {
        "original_sharpness":
            calculate_sharpness(original),

        "processed_sharpness":
            calculate_sharpness(processed),

        "original_brightness":
            calculate_brightness(original),

        "processed_brightness":
            calculate_brightness(processed),

        "original_contrast":
            calculate_contrast(original),

        "processed_contrast":
            calculate_contrast(processed)
    }

    return results