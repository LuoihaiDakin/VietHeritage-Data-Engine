import cv2


def restore_edges(image):
    """
    Restore and enhance important visual edges
    in a cultural heritage image.

    Returns:
        restored_image
        restored_edges
    """

    # --------------------------------
    # Convert to grayscale
    # --------------------------------

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # --------------------------------
    # Detect edges
    # --------------------------------

    edges = cv2.Canny(
        gray,
        100,
        200
    )

    # --------------------------------
    # Reconnect small broken edges
    # --------------------------------

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (2, 2)
    )

    restored_edges = cv2.dilate(
        edges,
        kernel,
        iterations=1
    )

    # --------------------------------
    # Convert edges to BGR
    # --------------------------------

    restored_edges_bgr = cv2.cvtColor(
        restored_edges,
        cv2.COLOR_GRAY2BGR
    )

    # --------------------------------
    # Sharpen original image
    # --------------------------------

    gaussian_kernel = cv2.getGaussianKernel(
        5,
        0
    )

    gaussian = gaussian_kernel @ gaussian_kernel.T

    blurred = cv2.filter2D(
        image,
        -1,
        gaussian
    )

    sharpened = cv2.addWeighted(
        image,
        1.5,
        blurred,
        -0.5,
        0
    )

    # --------------------------------
    # Blend edges with sharpened image
    # --------------------------------

    restored = cv2.addWeighted(
        sharpened,
        0.85,
        restored_edges_bgr,
        0.15,
        0
    )

    return restored, restored_edges_bgr