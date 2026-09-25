import cv2
import numpy as np


# ============================================================
# SHARPNESS
# ============================================================

def calculate_sharpness(image):
    """
    Sharpness using Laplacian variance.

    Higher values generally indicate more
    high-frequency detail, but the value also
    depends strongly on image content and size.
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


# ============================================================
# BRIGHTNESS
# ============================================================

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


# ============================================================
# CONTRAST
# ============================================================

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


# ============================================================
# NOISE ESTIMATION
# ============================================================

def calculate_noise(image):
    """
    Estimate image noise using a high-pass residual.

    The image is compared with a lightly blurred version.
    The median absolute deviation (MAD) of the residual
    provides a robust noise estimate.

    This is an estimate, not a ground-truth noise measurement.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    gray = gray.astype(
        np.float32
    )

    blurred = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    residual = gray - blurred

    mad = np.median(
        np.abs(
            residual -
            np.median(residual)
        )
    )

    noise = 1.4826 * mad

    return float(
        noise
    )


# ============================================================
# EDGE DENSITY
# ============================================================

def calculate_edge_density(image):
    """
    Calculate the percentage of pixels classified
    as edges by Canny edge detection.

    Result:
        0.0 - 1.0
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    edges = cv2.Canny(
        blurred,
        50,
        150
    )

    edge_pixels = np.count_nonzero(
        edges
    )

    total_pixels = edges.shape[0] * edges.shape[1]

    if total_pixels == 0:
        return 0.0

    return float(
        edge_pixels / total_pixels
    )


# ============================================================
# EVALUATION
# ============================================================

def evaluate_image(image):
    """
    Calculate technical image-quality metrics.

    Metrics:
        - width
        - height
        - brightness
        - contrast
        - sharpness
        - noise
        - edge_density
    """

    if image is None:
        raise ValueError(
            "evaluate_image received an empty image."
        )

    if len(image.shape) != 3:
        raise ValueError(
            "evaluate_image expects a color image."
        )

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
        ),

        "noise": round(
            calculate_noise(image),
            2
        ),

        "edge_density": round(
            calculate_edge_density(image),
            4
        )
    }