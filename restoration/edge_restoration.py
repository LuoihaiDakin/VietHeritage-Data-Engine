import cv2


def restore_edges(image):
    """
    Enhance edges and restore image details.
    """

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect edges
    edges = cv2.Canny(gray, 100, 200)

    # Dilate edges slightly to reconnect broken lines
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (2, 2)
    )

    restored_edges = cv2.dilate(
        edges,
        kernel,
        iterations=1
    )

    # Convert edges back to 3 channels
    restored_edges = cv2.cvtColor(
        restored_edges,
        cv2.COLOR_GRAY2BGR
    )

    # Sharpen original image
    sharpen_kernel = (
        0, -1, 0,
        -1, 5, -1,
        0, -1, 0
    )

    sharpened = cv2.filter2D(
        image,
        -1,
        sharpen_kernel
    )

    return sharpened, restored_edges