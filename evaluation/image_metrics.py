import cv2
import numpy as np


# ==========================================================
# INTERNAL HELPER
# ==========================================================

def _to_grayscale(image):
    """
    Convert an image to grayscale.

    Supports:
    - BGR color images
    - grayscale images
    """

    if image is None:
        raise ValueError(
            "Image is None."
        )

    if len(image.shape) == 2:
        return image

    return cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


# ==========================================================
# SHARPNESS
# ==========================================================

def calculate_sharpness(image):
    """
    Calculate image sharpness using
    Laplacian variance.

    Higher values generally indicate
    stronger edges and image details.
    """

    gray = _to_grayscale(image)

    variance = cv2.Laplacian(
        gray,
        cv2.CV_64F
    ).var()

    return float(variance)


# ==========================================================
# BRIGHTNESS
# ==========================================================

def calculate_brightness(image):
    """
    Calculate average image brightness.

    Returns a value between 0 and 255.
    """

    gray = _to_grayscale(image)

    brightness = np.mean(
        gray
    )

    return float(brightness)


# ==========================================================
# CONTRAST
# ==========================================================

def calculate_contrast(image):
    """
    Calculate image contrast using
    grayscale standard deviation.

    Higher values generally indicate
    stronger intensity variation.
    """

    gray = _to_grayscale(image)

    contrast = np.std(
        gray
    )

    return float(contrast)


# ==========================================================
# NOISE
# ==========================================================

def calculate_noise(image):
    """
    Estimate image noise using the
    difference between the original
    image and a Gaussian-blurred image.

    Higher values indicate stronger
    high-frequency variation.

    This is only a simple noise estimate,
    not a professional noise measurement.
    """

    gray = _to_grayscale(image)

    blurred = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    difference = cv2.absdiff(
        gray,
        blurred
    )

    noise = np.mean(
        difference
    )

    return float(noise)


# ==========================================================
# ALL IMAGE METRICS
# ==========================================================

def calculate_image_metrics(image):
    """
    Calculate all available image-quality
    metrics for one image.

    Returns:
        dictionary containing:

        - sharpness
        - brightness
        - contrast
        - noise
    """

    return {
        "sharpness": round(
            calculate_sharpness(image),
            4
        ),

        "brightness": round(
            calculate_brightness(image),
            4
        ),

        "contrast": round(
            calculate_contrast(image),
            4
        ),

        "noise": round(
            calculate_noise(image),
            4
        )
    }


# ==========================================================
# COMPARE TWO IMAGES
# ==========================================================

def compare_images(original, processed):
    """
    Compare image-quality metrics between
    an original image and a processed image.

    Metrics:

    - Sharpness
    - Brightness
    - Contrast
    - Noise
    """

    original_metrics = (
        calculate_image_metrics(
            original
        )
    )

    processed_metrics = (
        calculate_image_metrics(
            processed
        )
    )

    results = {

        "original_sharpness":
            original_metrics["sharpness"],

        "processed_sharpness":
            processed_metrics["sharpness"],

        "original_brightness":
            original_metrics["brightness"],

        "processed_brightness":
            processed_metrics["brightness"],

        "original_contrast":
            original_metrics["contrast"],

        "processed_contrast":
            processed_metrics["contrast"],

        "original_noise":
            original_metrics["noise"],

        "processed_noise":
            processed_metrics["noise"]
    }

    return results


# ==========================================================
# OPTIONAL COMPARISON WITH CHANGES
# ==========================================================

def compare_images_with_changes(
    original,
    processed
):
    """
    Compare two images and also calculate
    the change in each metric.

    Useful for evaluating whether a
    preprocessing/restoration step changed
    the image characteristics.
    """

    original_metrics = (
        calculate_image_metrics(
            original
        )
    )

    processed_metrics = (
        calculate_image_metrics(
            processed
        )
    )

    return {

        "original": original_metrics,

        "processed": processed_metrics,

        "change": {

            "sharpness": round(
                processed_metrics["sharpness"]
                - original_metrics["sharpness"],
                4
            ),

            "brightness": round(
                processed_metrics["brightness"]
                - original_metrics["brightness"],
                4
            ),

            "contrast": round(
                processed_metrics["contrast"]
                - original_metrics["contrast"],
                4
            ),

            "noise": round(
                processed_metrics["noise"]
                - original_metrics["noise"],
                4
            )
        }
    }


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print(
        "VietHeritage image metrics module"
    )

    print(
        "Available functions:"
    )

    print(
        "- calculate_sharpness(image)"
    )

    print(
        "- calculate_brightness(image)"
    )

    print(
        "- calculate_contrast(image)"
    )

    print(
        "- calculate_noise(image)"
    )

    print(
        "- calculate_image_metrics(image)"
    )

    print(
        "- compare_images(original, processed)"
    )

    print(
        "- compare_images_with_changes("
        "original, processed)"
    )