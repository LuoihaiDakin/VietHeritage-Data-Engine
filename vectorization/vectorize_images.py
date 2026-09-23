import os
import json
import cv2
import numpy as np


# ==========================================
# CONFIGURATION
# ==========================================

SUPPORTED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff"
}

# Remove very small contours
MIN_CONTOUR_AREA = 20

# Higher value = more simplification
# Lower value = more detailed contour
APPROXIMATION_FACTOR = 0.002


# ==========================================
# LOAD MASK
# ==========================================

def load_mask(mask_path):
    """
    Load a binary segmentation mask.
    """

    mask = cv2.imread(
        mask_path,
        cv2.IMREAD_GRAYSCALE
    )

    if mask is None:
        print(
            f"ERROR: Cannot read mask: {mask_path}"
        )
        return None

    return mask


# ==========================================
# CLEAN MASK
# ==========================================

def clean_mask(mask):
    """
    Ensure the mask is binary.
    """

    _, binary = cv2.threshold(
        mask,
        127,
        255,
        cv2.THRESH_BINARY
    )

    return binary


# ==========================================
# FIND CONTOURS
# ==========================================

def find_contours(mask):
    """
    Extract external contours from the mask.
    """

    contours, hierarchy = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    return contours


# ==========================================
# FILTER CONTOURS
# ==========================================

def filter_contours(contours):
    """
    Remove contours that are too small.
    """

    filtered = []

    for contour in contours:

        area = cv2.contourArea(
            contour
        )

        if area < MIN_CONTOUR_AREA:
            continue

        filtered.append(
            contour
        )

    return filtered


# ==========================================
# SIMPLIFY CONTOUR
# ==========================================

def simplify_contour(contour):
    """
    Simplify contour using
    Douglas-Peucker approximation.
    """

    perimeter = cv2.arcLength(
        contour,
        True
    )

    epsilon = (
        APPROXIMATION_FACTOR *
        perimeter
    )

    simplified = cv2.approxPolyDP(
        contour,
        epsilon,
        True
    )

    return simplified


# ==========================================
# CONTOUR TO SVG PATH
# ==========================================

def contour_to_svg_path(contour):
    """
    Convert OpenCV contour points
    into an SVG path.
    """

    points = contour.reshape(
        -1,
        2
    )

    if len(points) == 0:
        return ""

    first_x = int(points[0][0])
    first_y = int(points[0][1])

    path = (
        f"M {first_x} {first_y}"
    )

    for point in points[1:]:

        x = int(point[0])
        y = int(point[1])

        path += (
            f" L {x} {y}"
        )

    path += " Z"

    return path


# ==========================================
# CREATE SVG
# ==========================================

def create_svg(
    contours,
    width,
    height
):
    """
    Create SVG document from contours.
    """

    svg_lines = []

    svg_lines.append(
        '<?xml version="1.0" encoding="UTF-8"?>'
    )

    svg_lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" '
        f'height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )

    svg_lines.append(
        '<g fill="black" '
        'stroke="none">'
    )

    for contour in contours:

        path = contour_to_svg_path(
            contour
        )

        if path:

            svg_lines.append(
                f'<path d="{path}"/>'
            )

    svg_lines.append(
        '</g>'
    )

    svg_lines.append(
        '</svg>'
    )

    return "\n".join(
        svg_lines
    )


# ==========================================
# CONTOUR INFORMATION
# ==========================================

def calculate_contour_info(
    contour,
    simplified
):
    """
    Generate numerical information
    about a vector contour.
    """

    area = cv2.contourArea(
        contour
    )

    perimeter = cv2.arcLength(
        contour,
        True
    )

    x, y, width, height = (
        cv2.boundingRect(
            contour
        )
    )

    moments = cv2.moments(
        contour
    )

    if moments["m00"] != 0:

        center_x = (
            moments["m10"] /
            moments["m00"]
        )

        center_y = (
            moments["m01"] /
            moments["m00"]
        )

    else:

        center_x = 0
        center_y = 0

    return {
        "area": round(
            float(area),
            2
        ),
        "perimeter": round(
            float(perimeter),
            2
        ),
        "bounding_box": {
            "x": int(x),
            "y": int(y),
            "width": int(width),
            "height": int(height)
        },
        "center": {
            "x": round(
                float(center_x),
                2
            ),
            "y": round(
                float(center_y),
                2
            )
        },
        "original_points": int(
            len(contour)
        ),
        "simplified_points": int(
            len(simplified)
        )
    }


# ==========================================
# CREATE JSON
# ==========================================

def create_vector_metadata(
    image_name,
    width,
    height,
    contours
):
    """
    Create JSON metadata describing
    extracted vector contours.
    """

    vector_data = []

    for index, contour in enumerate(
        contours
    ):

        simplified = simplify_contour(
            contour
        )

        info = calculate_contour_info(
            contour,
            simplified
        )

        info["id"] = (
            f"contour_{index + 1}"
        )

        vector_data.append(
            info
        )

    return {
        "source_image": image_name,
        "width": int(width),
        "height": int(height),
        "vector_count": len(
            vector_data
        ),
        "vectors": vector_data
    }


# ==========================================
# PROCESS ONE MASK
# ==========================================

def process_mask(
    input_path,
    svg_output_path,
    json_output_path
):
    """
    Convert one segmentation mask
    into SVG and JSON.
    """

    mask = load_mask(
        input_path
    )

    if mask is None:
        return False

    mask = clean_mask(
        mask
    )

    height, width = mask.shape[:2]

    contours = find_contours(
        mask
    )

    contours = filter_contours(
        contours
    )

    if len(contours) == 0:

        print(
            "  WARNING: No valid contours found."
        )

        return False

    # --------------------------------------
    # Simplify contours
    # --------------------------------------

    simplified_contours = []

    for contour in contours:

        simplified = simplify_contour(
            contour
        )

        if len(simplified) >= 3:

            simplified_contours.append(
                simplified
            )

    if len(simplified_contours) == 0:

        print(
            "  WARNING: No usable vector contours."
        )

        return False

    # --------------------------------------
    # SVG
    # --------------------------------------

    svg_content = create_svg(
        simplified_contours,
        width,
        height
    )

    # --------------------------------------
    # JSON
    # --------------------------------------

    metadata = create_vector_metadata(
        os.path.basename(
            input_path
        ),
        width,
        height,
        contours
    )

    # --------------------------------------
    # Create directories
    # --------------------------------------

    os.makedirs(
        os.path.dirname(
            svg_output_path
        ),
        exist_ok=True
    )

    os.makedirs(
        os.path.dirname(
            json_output_path
        ),
        exist_ok=True
    )

    # --------------------------------------
    # Save SVG
    # --------------------------------------

    with open(
        svg_output_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            svg_content
        )

    # --------------------------------------
    # Save JSON
    # --------------------------------------

    with open(
        json_output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4,
            ensure_ascii=False
        )

    return True


# ==========================================
# FIND MASKS
# ==========================================

def find_masks(input_directory):
    """
    Find all segmentation masks.
    """

    mask_files = []

    for root, directories, files in os.walk(
        input_directory
    ):

        for filename in files:

            if not filename.endswith(
                "_mask.png"
            ):
                continue

            full_path = os.path.join(
                root,
                filename
            )

            mask_files.append(
                full_path
            )

    return mask_files


# ==========================================
# MAIN
# ==========================================

def main():

    project_root = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    input_directory = os.path.join(
        project_root,
        "outputs",
        "segmentation_masks"
    )

    svg_directory = os.path.join(
        project_root,
        "outputs",
        "vectorization"
    )

    json_directory = os.path.join(
        project_root,
        "outputs",
        "vector_metadata"
    )

    print(
        "========================================"
    )

    print(
        "       VietHeritage Vectorization"
    )

    print(
        "========================================"
    )

    print()

    print(
        f"Input masks : {input_directory}"
    )

    print(
        f"SVG output  : {svg_directory}"
    )

    print(
        f"JSON output : {json_directory}"
    )

    print()

    # --------------------------------------
    # Check input
    # --------------------------------------

    if not os.path.exists(
        input_directory
    ):

        print(
            "ERROR: Segmentation masks "
            "directory does not exist."
        )

        print(
            "Run segmentation first."
        )

        return

    # --------------------------------------
    # Find masks
    # --------------------------------------

    mask_files = find_masks(
        input_directory
    )

    print(
        f"Masks found: {len(mask_files)}"
    )

    print()

    success_count = 0
    failed_count = 0

    # --------------------------------------
    # Process
    # --------------------------------------

    for input_path in mask_files:

        relative_path = os.path.relpath(
            input_path,
            input_directory
        )

        base_name = os.path.splitext(
            relative_path
        )[0]

        # Remove "_mask"
        if base_name.endswith(
            "_mask"
        ):

            base_name = base_name[
                :-5
            ]

        svg_output_path = os.path.join(
            svg_directory,
            base_name + ".svg"
        )

        json_output_path = os.path.join(
            json_directory,
            base_name + ".json"
        )

        print(
            f"Vectorizing: {relative_path}"
        )

        success = process_mask(
            input_path,
            svg_output_path,
            json_output_path
        )

        if success:

            success_count += 1

            print(
                "  -> OK"
            )

        else:

            failed_count += 1

            print(
                "  -> FAILED"
            )

    # --------------------------------------
    # Summary
    # --------------------------------------

    print()

    print(
        "========================================"
    )

    print(
        "VECTORIZATION COMPLETED"
    )

    print(
        f"Successful: {success_count}"
    )

    print(
        f"Failed:     {failed_count}"
    )

    print(
        f"SVG:        {svg_directory}"
    )

    print(
        f"Metadata:   {json_directory}"
    )

    print(
        "========================================"
    )


if __name__ == "__main__":
    main()