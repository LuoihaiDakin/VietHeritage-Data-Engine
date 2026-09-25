import cv2
import numpy as np


def segment_image(image):
    """
    VietHeritage foreground segmentation.

    Pipeline:
        Input image
            ↓
        GrabCut
            ↓
        Foreground mask
            ↓
        Morphological cleanup
            ↓
        Hole filling
            ↓
        Final mask
            ↓
        Transparent PNG

    Returns:
        bgra:
            Image with transparent background.

        foreground:
            Binary foreground mask.
    """

    if image is None:
        raise ValueError(
            "segment_image received an empty image."
        )

    if len(image.shape) != 3:
        raise ValueError(
            "segment_image expects a color image."
        )

    height, width = image.shape[:2]

    if height < 20 or width < 20:
        raise ValueError(
            "Image is too small for segmentation."
        )

    # ========================================================
    # 1. Initial GrabCut mask
    # ========================================================

    mask = np.zeros(
        (height, width),
        np.uint8
    )

    # Keep a small border as probable background.
    margin_x = max(
        5,
        int(width * 0.03)
    )

    margin_y = max(
        5,
        int(height * 0.03)
    )

    rect_width = width - 2 * margin_x
    rect_height = height - 2 * margin_y

    if rect_width <= 0 or rect_height <= 0:
        raise ValueError(
            "Invalid GrabCut rectangle."
        )

    rect = (
        margin_x,
        margin_y,
        rect_width,
        rect_height
    )

    # ========================================================
    # 2. GrabCut
    # ========================================================

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

    # ========================================================
    # 3. Convert GrabCut result to binary foreground mask
    # ========================================================

    foreground = np.where(
        (mask == cv2.GC_FGD) |
        (mask == cv2.GC_PR_FGD),
        255,
        0
    ).astype(
        np.uint8
    )

    # ========================================================
    # 4. Remove tiny isolated regions
    # ========================================================

    open_kernel = np.ones(
        (3, 3),
        np.uint8
    )

    foreground = cv2.morphologyEx(
        foreground,
        cv2.MORPH_OPEN,
        open_kernel,
        iterations=1
    )

    # ========================================================
    # 5. Connect broken regions
    # ========================================================

    close_kernel = np.ones(
        (5, 5),
        np.uint8
    )

    foreground = cv2.morphologyEx(
        foreground,
        cv2.MORPH_CLOSE,
        close_kernel,
        iterations=1
    )

    # ========================================================
    # 6. Fill small holes inside the foreground
    # ========================================================

    contours, _ = cv2.findContours(
        foreground,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if contours:
        largest_contour = max(
            contours,
            key=cv2.contourArea
        )

        filled = np.zeros_like(
            foreground
        )

        cv2.drawContours(
            filled,
            [largest_contour],
            -1,
            255,
            thickness=cv2.FILLED
        )

        # Keep the GrabCut result while using
        # the largest connected foreground region.
        foreground = cv2.bitwise_and(
            foreground,
            filled
        )

    # ========================================================
    # 7. Final mask cleanup
    # ========================================================

    foreground = cv2.GaussianBlur(
        foreground,
        (3, 3),
        0
    )

    _, foreground = cv2.threshold(
        foreground,
        127,
        255,
        cv2.THRESH_BINARY
    )

    # ========================================================
    # 8. Create transparent PNG
    # ========================================================

    bgra = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2BGRA
    )

    bgra[:, :, 3] = foreground

    return bgra, foreground