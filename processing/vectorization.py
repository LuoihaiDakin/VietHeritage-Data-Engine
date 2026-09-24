import cv2


def vectorize_mask(mask, svg_path):
    """
    Convert a binary segmentation mask
    into a simple SVG using contours.
    """

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    height, width = mask.shape[:2]

    paths = []

    for contour in contours:

        # Ignore tiny noise
        area = cv2.contourArea(contour)

        if area < 20:
            continue

        epsilon = 0.002 * cv2.arcLength(
            contour,
            True
        )

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

    with open(
        svg_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
        )

        file.write(
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width}" '
            f'height="{height}" '
            f'viewBox="0 0 {width} {height}">\n'
        )

        for path in paths:

            file.write(
                f'  <path d="{path}" '
                f'fill="black" '
                f'stroke="none"/>\n'
            )

        file.write("</svg>\n")

    return svg_path