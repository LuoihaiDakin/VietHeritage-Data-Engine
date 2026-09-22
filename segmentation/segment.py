import cv2
import numpy as np
import os


def segment_image(input_path, output_path):
    """
    Segment the main cultural pattern from the background.
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"File does not exist: {input_path}"
        )

    image = cv2.imread(input_path)

    if image is None:
        raise ValueError(
            f"Cannot read image: {input_path}"
        )

    # Convert to grayscale
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Improve local contrast
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    # Adaptive threshold
    mask = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        21,
        5
    )

    # Remove small noise
    kernel_small = np.ones(
        (3, 3),
        np.uint8
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel_small
    )

    # Connect nearby parts
    kernel_large = np.ones(
        (5, 5),
        np.uint8
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel_large
    )

    # Find contours
    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    clean_mask = np.zeros_like(mask)

    image_area = mask.shape[0] * mask.shape[1]

    for contour in contours:

        area = cv2.contourArea(contour)

        # Keep meaningful objects
        if area > image_area * 0.002:

            cv2.drawContours(
                clean_mask,
                [contour],
                -1,
                255,
                thickness=cv2.FILLED
            )

    # Save mask
    output_dir = os.path.dirname(output_path)

    if output_dir:
        os.makedirs(
            output_dir,
            exist_ok=True
        )

    success = cv2.imwrite(
        output_path,
        clean_mask
    )

    if not success:
        raise IOError(
            f"Failed to save: {output_path}"
        )

    return clean_mask


def apply_mask(
    image_path,
    mask_path,
    output_path
):
    """
    Apply segmentation mask to the original image.
    """

    image = cv2.imread(image_path)

    mask = cv2.imread(
        mask_path,
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        raise ValueError(
            f"Cannot read image: {image_path}"
        )

    if mask is None:
        raise ValueError(
            f"Cannot read mask: {mask_path}"
        )

    # Match dimensions
    if image.shape[:2] != mask.shape[:2]:

        mask = cv2.resize(
            mask,
            (image.shape[1], image.shape[0]),
            interpolation=cv2.INTER_NEAREST
        )

    # Apply mask
    result = cv2.bitwise_and(
        image,
        image,
        mask=mask
    )

    output_dir = os.path.dirname(output_path)

    if output_dir:
        os.makedirs(
            output_dir,
            exist_ok=True
        )

    success = cv2.imwrite(
        output_path,
        result
    )

    if not success:
        raise IOError(
            f"Failed to save: {output_path}"
        )

    return result


if __name__ == "__main__":

    input_image = "outputs/restored_test.jpg"

    mask_image = "outputs/segmentation_mask.jpg"

    segmented_image = "outputs/segmented_test.jpg"

    print("Starting segmentation...")

    segment_image(
        input_image,
        mask_image
    )

    print(
        f"Segmentation mask saved to: "
        f"{mask_image}"
    )

    apply_mask(
        input_image,
        mask_image,
        segmented_image
    )

    print(
        f"Segmented image saved to: "
        f"{segmented_image}"
    )

    print("Segmentation completed.")