import cv2


def vectorize_mask(mask, svg_path):
    """
    VietHeritage raster-to-vector conversion.

    Converts a binary segmentation mask into SVG paths.

    Pipeline:
        Binary mask
            ↓
        Contour extraction
            ↓
        Noise filtering
            ↓
        Contour simplification
            ↓
        SVG path generation
    """

    if mask is None:
        raise ValueError(
            "vectorize_mask received an empty mask."
        )

    if len(mask.shape) != 2:
        raise ValueError(
            "vectorize_mask expects a binary grayscale mask."
        )

    height, width = mask.shape[:2]

    # ========================================================
    # 1. Ensure binary mask
    # ========================================================

    _, binary = cv2.threshold(
        mask,
        127,
        255,
        cv2.THRESH_BINARY
    )

    # ========================================================
    # 2. Find contours
    #
    # RETR_TREE keeps internal contours as well.
    # This is important for detailed heritage patterns.
    # ========================================================

    contours, hierarchy = cv2.findContours(
        binary,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    paths = []

    # ========================================================
    # 3. Convert contours into SVG paths
    # ========================================================

    for contour in contours:

        area = cv2.contourArea(
            contour
        )

        # Ignore tiny noise
        if area < 20:
            continue

        perimeter = cv2.arcLength(
            contour,
            True
        )

        if perimeter <= 0:
            continue

        # Slight simplification.
        # Keep enough points for cultural patterns.
        epsilon = 0.002 * perimeter

        simplified = cv2.approxPolyDP(
            contour,
            epsilon,
            True
        )

        if len(simplified) < 3:
            continue

        points = simplified.reshape(
            -1,
            2
        )

        path_data = []

        for index, point in enumerate(points):

            x = int(point[0])
            y = int(point[1])

            if index == 0:
                path_data.append(
                    f"M {x} {y}"
                )
            else:
                path_data.append(
                    f"L {x} {y}"
                )

        path_data.append("Z")

        paths.append(
            " ".join(path_data)
        )

    # ========================================================
    # 4. Write SVG
    # ========================================================

    with open(
        svg_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
        )

        file.write(
            f'<svg '
            f'xmlns="http://www.w3.org/2000/svg" '
            f'width="{width}" '
            f'height="{height}" '
            f'viewBox="0 0 {width} {height}">\n'
        )

        file.write(
            '  <g fill="black" '
            'stroke="none">\n'
        )

        for path in paths:

            file.write(
                f'    <path d="{path}"/>\n'
            )

        file.write(
            '  </g>\n'
        )

        file.write(
            '</svg>\n'
        )

    return svg_path