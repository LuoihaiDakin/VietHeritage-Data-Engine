import os
import re
import xml.etree.ElementTree as ET


def normalize_svg(input_path, output_path):
    """
    Normalize an SVG cultural asset.

    The normalization process:
    - validates the SVG
    - normalizes width and height
    - normalizes the viewBox
    - removes unnecessary whitespace
    - keeps vector paths
    """

    # --------------------------------------------------
    # 1. Check input
    # --------------------------------------------------

    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"SVG file does not exist: {input_path}"
        )

    # --------------------------------------------------
    # 2. Read SVG
    # --------------------------------------------------

    try:
        tree = ET.parse(input_path)
        root = tree.getroot()
    except ET.ParseError as error:
        raise ValueError(
            f"Invalid SVG file: {error}"
        )

    # --------------------------------------------------
    # 3. SVG namespace
    # --------------------------------------------------

    namespace = {
        "svg": "http://www.w3.org/2000/svg"
    }

    # --------------------------------------------------
    # 4. Get SVG dimensions
    # --------------------------------------------------

    width = root.get("width")
    height = root.get("height")

    viewbox = root.get("viewBox")

    # --------------------------------------------------
    # 5. Extract numeric dimensions
    # --------------------------------------------------

    def extract_number(value):

        if value is None:
            return None

        match = re.search(
            r"[-+]?\d*\.?\d+",
            value
        )

        if match:
            return float(match.group())

        return None

    width_value = extract_number(width)
    height_value = extract_number(height)

    # --------------------------------------------------
    # 6. Validate dimensions
    # --------------------------------------------------

    if width_value is None:
        width_value = 1000

    if height_value is None:
        height_value = 1000

    # --------------------------------------------------
    # 7. Normalize viewBox
    # --------------------------------------------------

    if not viewbox:

        root.set(
            "viewBox",
            f"0 0 {width_value} {height_value}"
        )

    else:

        values = viewbox.split()

        if len(values) == 4:

            try:

                x = float(values[0])
                y = float(values[1])
                w = float(values[2])
                h = float(values[3])

                root.set(
                    "viewBox",
                    f"0 0 {w:g} {h:g}"
                )

            except ValueError:

                root.set(
                    "viewBox",
                    f"0 0 {width_value:g} {height_value:g}"
                )

        else:

            root.set(
                "viewBox",
                f"0 0 {width_value:g} {height_value:g}"
            )

    # --------------------------------------------------
    # 8. Normalize SVG size
    # --------------------------------------------------

    root.set(
        "width",
        str(int(width_value))
    )

    root.set(
        "height",
        str(int(height_value))
    )

    # --------------------------------------------------
    # 9. Count vector paths
    # --------------------------------------------------

    path_count = 0
    polyline_count = 0

    for element in root.iter():

        tag = element.tag.split("}")[-1]

        if tag == "path":
            path_count += 1

        elif tag == "polyline":
            polyline_count += 1

    total_vectors = (
        path_count +
        polyline_count
    )

    if total_vectors == 0:

        raise ValueError(
            "No vector paths found in SVG."
        )

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
    # 11. Save normalized SVG
    # --------------------------------------------------

    tree.write(
        output_path,
        encoding="utf-8",
        xml_declaration=True
    )

    # --------------------------------------------------
    # 12. Report
    # --------------------------------------------------

    print(
        "SVG normalization completed."
    )

    print(
        f"Vector paths: {total_vectors}"
    )

    print(
        f"Output: {output_path}"
    )


if __name__ == "__main__":

    input_svg = (
        "outputs/vectorized_test.svg"
    )

    output_svg = (
        "outputs/normalized_test.svg"
    )

    print(
        "Starting SVG normalization..."
    )

    normalize_svg(
        input_svg,
        output_svg
    )