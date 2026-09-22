import cv2
import os


def remove_small_edges(edge_image, min_area=12):
    """
    Remove very small connected edge components.
    """

    binary = cv2.threshold(
        edge_image,
        100,
        255,
        cv2.THRESH_BINARY
    )[1]

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        binary,
        connectivity=8
    )

    cleaned = binary.copy()
    cleaned[:] = 0

    for label in range(1, num_labels):

        area = stats[label, cv2.CC_STAT_AREA]

        if area >= min_area:
            cleaned[labels == label] = 255

    return cleaned


def vectorize_image(
    mask_path,
    edge_path,
    output_path
):
    """
    Convert cultural-pattern edges into SVG paths.
    """

    # --------------------------------------------------
    # 1. Check input files
    # --------------------------------------------------

    if not os.path.exists(mask_path):
        raise FileNotFoundError(
            f"Mask file does not exist: {mask_path}"
        )

    if not os.path.exists(edge_path):
        raise FileNotFoundError(
            f"Edge file does not exist: {edge_path}"
        )

    # --------------------------------------------------
    # 2. Read images
    # --------------------------------------------------

    mask = cv2.imread(
        mask_path,
        cv2.IMREAD_GRAYSCALE
    )

    edges = cv2.imread(
        edge_path,
        cv2.IMREAD_GRAYSCALE
    )

    if mask is None:
        raise ValueError(
            f"Cannot read mask: {mask_path}"
        )

    if edges is None:
        raise ValueError(
            f"Cannot read edges: {edge_path}"
        )

    # --------------------------------------------------
    # 3. Match image sizes
    # --------------------------------------------------

    if mask.shape != edges.shape:

        edges = cv2.resize(
            edges,
            (mask.shape[1], mask.shape[0]),
            interpolation=cv2.INTER_NEAREST
        )

    # --------------------------------------------------
    # 4. Convert segmentation mask to binary
    # --------------------------------------------------

    binary_mask = cv2.threshold(
        mask,
        127,
        255,
        cv2.THRESH_BINARY
    )[1]

    # --------------------------------------------------
    # 5. Convert edges to binary
    # --------------------------------------------------

    binary_edges = cv2.threshold(
        edges,
        100,
        255,
        cv2.THRESH_BINARY
    )[1]

    # --------------------------------------------------
    # 6. Keep only edges inside the segmented object
    # --------------------------------------------------

    object_edges = cv2.bitwise_and(
        binary_edges,
        binary_edges,
        mask=binary_mask
    )

    # --------------------------------------------------
    # 7. Remove small noise
    # --------------------------------------------------

    object_edges = remove_small_edges(
        object_edges,
        min_area=12
    )

    # --------------------------------------------------
    # 8. Connect small broken lines
    # --------------------------------------------------

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (2, 2)
    )

    object_edges = cv2.morphologyEx(
        object_edges,
        cv2.MORPH_CLOSE,
        kernel
    )

    # --------------------------------------------------
    # 9. Find edge contours
    # --------------------------------------------------

    contours, _ = cv2.findContours(
        object_edges,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_NONE
    )

    height, width = object_edges.shape

    # --------------------------------------------------
    # 10. Create output directory
    # --------------------------------------------------

    output_dir = os.path.dirname(output_path)

    if output_dir:
        os.makedirs(
            output_dir,
            exist_ok=True
        )

    # --------------------------------------------------
    # 11. Start SVG
    # --------------------------------------------------

    svg_parts = []

    svg_parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" '
        f'height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )

    svg_parts.append(
        '<g fill="none" '
        'stroke="black" '
        'stroke-width="1.2" '
        'stroke-linecap="round" '
        'stroke-linejoin="round">'
    )

    path_count = 0

    # --------------------------------------------------
    # 12. Convert contours into SVG polylines
    # --------------------------------------------------

    for contour in contours:

        # Ignore extremely short contours
        if len(contour) < 5:
            continue

        # Calculate contour length
        perimeter = cv2.arcLength(
            contour,
            False
        )

        # Remove very short lines
        if perimeter < 20:
            continue

        # Simplify contour
        epsilon = 0.003 * perimeter

        simplified = cv2.approxPolyDP(
            contour,
            epsilon,
            False
        )

        # Ignore contours with too few points
        if len(simplified) < 3:
            continue

        points = []

        for point in simplified:

            x, y = point[0]

            points.append(
                f"{x},{y}"
            )

        points_string = " ".join(points)

        svg_parts.append(
            f'<polyline points="{points_string}" />'
        )

        path_count += 1

    # --------------------------------------------------
    # 13. Close SVG
    # --------------------------------------------------

    svg_parts.append(
        '</g>'
    )

    svg_parts.append(
        '</svg>'
    )

    svg_content = "\n".join(
        svg_parts
    )

    # --------------------------------------------------
    # 14. Save SVG
    # --------------------------------------------------

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(svg_content)

    # --------------------------------------------------
    # 15. Show result
    # --------------------------------------------------

    print(
        f"SVG saved to: {output_path}"
    )

    print(
        f"Vector paths created: {path_count}"
    )


if __name__ == "__main__":

    # Input segmentation mask
    mask_path = (
        "outputs/segmentation_mask.jpg"
    )

    # Input edge image
    edge_path = (
        "outputs/edges_test.jpg"
    )

    # Output SVG
    output_path = (
        "outputs/vectorized_test.svg"
    )

    print(
        "Starting improved vectorization..."
    )

    vectorize_image(
        mask_path,
        edge_path,
        output_path
    )

    print(
        "Vectorization completed."
    )