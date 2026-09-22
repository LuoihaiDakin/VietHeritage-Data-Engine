import os
import json
import cv2
import xml.etree.ElementTree as ET

from image_metrics import (
    calculate_image_metrics
)


# ==========================================================
# PROJECT PATHS
# ==========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

OUTPUTS_DIR = os.path.join(
    PROJECT_ROOT,
    "outputs"
)

EVALUATION_DIR = os.path.join(
    PROJECT_ROOT,
    "evaluation"
)

REPORT_PATH = os.path.join(
    EVALUATION_DIR,
    "evaluation_report.json"
)


# ==========================================================
# PIPELINE FILES
# ==========================================================

FILES = {

    "cleaning": os.path.join(
        OUTPUTS_DIR,
        "cleaned_test.jpg"
    ),

    "restoration": os.path.join(
        OUTPUTS_DIR,
        "restored_test.jpg"
    ),

    "edges": os.path.join(
        OUTPUTS_DIR,
        "edges_test.jpg"
    ),

    "segmentation_mask": os.path.join(
        OUTPUTS_DIR,
        "segmentation_mask.jpg"
    ),

    "segmented": os.path.join(
        OUTPUTS_DIR,
        "segmented_test.jpg"
    ),

    "vectorization": os.path.join(
        OUTPUTS_DIR,
        "vectorized_test.svg"
    ),

    "normalization": os.path.join(
        OUTPUTS_DIR,
        "normalized_test.svg"
    )
}


# ==========================================================
# BASIC FILE FUNCTIONS
# ==========================================================

def file_exists(path):
    """
    Check whether a file exists.
    """

    return os.path.isfile(path)


def get_file_size(path):
    """
    Return file size in bytes.
    """

    if not file_exists(path):
        return 0

    return os.path.getsize(path)


# ==========================================================
# IMAGE INFORMATION
# ==========================================================

def evaluate_image(path):
    """
    Evaluate basic image properties.
    """

    result = {
        "exists": False,
        "readable": False,
        "width": 0,
        "height": 0,
        "channels": 0,
        "file_size_bytes": 0
    }

    if not file_exists(path):
        return result

    result["exists"] = True

    result["file_size_bytes"] = (
        get_file_size(path)
    )

    image = cv2.imread(
        path,
        cv2.IMREAD_UNCHANGED
    )

    if image is None:
        return result

    result["readable"] = True

    result["height"] = image.shape[0]
    result["width"] = image.shape[1]

    if len(image.shape) == 2:

        result["channels"] = 1

    else:

        result["channels"] = image.shape[2]

    return result


# ==========================================================
# IMAGE QUALITY
# ==========================================================

def evaluate_image_quality(path):
    """
    Calculate image-quality metrics using
    functions from image_metrics.py.

    Metrics:

    - Sharpness
    - Brightness
    - Contrast
    - Noise
    """

    result = {
        "exists": False,
        "readable": False,
        "sharpness": None,
        "brightness": None,
        "contrast": None,
        "noise": None
    }

    if not file_exists(path):
        return result

    result["exists"] = True

    image = cv2.imread(
        path,
        cv2.IMREAD_COLOR
    )

    if image is None:
        return result

    result["readable"] = True

    metrics = calculate_image_metrics(
        image
    )

    result["sharpness"] = (
        metrics["sharpness"]
    )

    result["brightness"] = (
        metrics["brightness"]
    )

    result["contrast"] = (
        metrics["contrast"]
    )

    result["noise"] = (
        metrics["noise"]
    )

    return result


# ==========================================================
# SEGMENTATION EVALUATION
# ==========================================================

def evaluate_segmentation(path):
    """
    Evaluate segmentation mask.

    Because there is currently no
    ground-truth mask, this function
    does not calculate IoU, precision,
    recall, or F1.

    Instead it measures:

    - foreground ratio
    - background ratio
    - empty mask
    - full mask
    """

    result = {
        "exists": False,
        "readable": False,
        "foreground_ratio": 0.0,
        "background_ratio": 0.0,
        "empty_mask": True,
        "full_mask": False,
        "status": "invalid"
    }

    if not file_exists(path):
        return result

    result["exists"] = True

    image = cv2.imread(
        path,
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        return result

    result["readable"] = True

    _, binary = cv2.threshold(
        image,
        127,
        255,
        cv2.THRESH_BINARY
    )

    total_pixels = binary.size

    foreground_pixels = cv2.countNonZero(
        binary
    )

    foreground_ratio = (
        foreground_pixels /
        total_pixels
    )

    background_ratio = (
        1.0 -
        foreground_ratio
    )

    result["foreground_ratio"] = round(
        foreground_ratio,
        4
    )

    result["background_ratio"] = round(
        background_ratio,
        4
    )

    result["empty_mask"] = (
        foreground_pixels == 0
    )

    result["full_mask"] = (
        foreground_pixels == total_pixels
    )

    if result["empty_mask"]:

        result["status"] = "empty"

    elif result["full_mask"]:

        result["status"] = "full"

    else:

        result["status"] = "usable"

    return result


# ==========================================================
# EDGE EVALUATION
# ==========================================================

def evaluate_edges(path):
    """
    Evaluate edge density.
    """

    result = {
        "exists": False,
        "readable": False,
        "edge_ratio": 0.0,
        "status": "invalid"
    }

    if not file_exists(path):
        return result

    result["exists"] = True

    image = cv2.imread(
        path,
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        return result

    result["readable"] = True

    _, binary = cv2.threshold(
        image,
        100,
        255,
        cv2.THRESH_BINARY
    )

    total_pixels = binary.size

    edge_pixels = cv2.countNonZero(
        binary
    )

    edge_ratio = (
        edge_pixels /
        total_pixels
    )

    result["edge_ratio"] = round(
        edge_ratio,
        4
    )

    if edge_ratio == 0:

        result["status"] = "empty"

    elif edge_ratio > 0.5:

        result["status"] = "very_dense"

    else:

        result["status"] = "usable"

    return result


# ==========================================================
# SVG EVALUATION
# ==========================================================

def evaluate_svg(path):
    """
    Evaluate SVG structure.

    Checks:

    - file exists
    - XML validity
    - SVG root
    - path count
    - polyline count
    - total vector elements
    - embedded raster images
    """

    result = {
        "exists": False,
        "readable": False,
        "valid_svg": False,
        "path_count": 0,
        "polyline_count": 0,
        "vector_element_count": 0,
        "embedded_raster_count": 0,
        "file_size_bytes": 0,
        "status": "invalid"
    }

    if not file_exists(path):
        return result

    result["exists"] = True

    result["file_size_bytes"] = (
        get_file_size(path)
    )

    try:

        tree = ET.parse(path)

        root = tree.getroot()

    except (
        ET.ParseError,
        OSError
    ):

        return result

    result["readable"] = True

    root_tag = root.tag.split("}")[-1]

    if root_tag != "svg":

        return result

    result["valid_svg"] = True

    path_count = 0

    polyline_count = 0

    embedded_raster_count = 0

    for element in root.iter():

        tag = element.tag.split("}")[-1]

        if tag == "path":

            path_count += 1

        elif tag == "polyline":

            polyline_count += 1

        elif tag == "image":

            embedded_raster_count += 1

    result["path_count"] = path_count

    result["polyline_count"] = polyline_count

    result["vector_element_count"] = (
        path_count +
        polyline_count
    )

    result["embedded_raster_count"] = (
        embedded_raster_count
    )

    if (
        result["vector_element_count"] > 0
        and embedded_raster_count == 0
    ):

        result["status"] = "usable"

    elif (
        result["vector_element_count"] > 0
        and embedded_raster_count > 0
    ):

        result["status"] = "mixed"

    else:

        result["status"] = "empty"

    return result


# ==========================================================
# PIPELINE COMPLETENESS
# ==========================================================

def evaluate_pipeline_completeness():
    """
    Check whether all pipeline outputs exist.
    """

    total_steps = len(FILES)

    completed_steps = 0

    step_status = {}

    for step, path in FILES.items():

        exists = file_exists(path)

        step_status[step] = exists

        if exists:

            completed_steps += 1

    completeness_ratio = (
        completed_steps /
        total_steps
    )

    completeness_percent = (
        completeness_ratio * 100
    )

    return {

        "completed_steps": completed_steps,

        "total_steps": total_steps,

        "completeness_ratio": round(
            completeness_ratio,
            4
        ),

        "completeness_percent": round(
            completeness_percent,
            2
        ),

        "steps": step_status
    }


# ==========================================================
# OVERALL STATUS
# ==========================================================

def calculate_overall_status(
    segmentation,
    edges,
    vectorized,
    normalized,
    completeness
):
    """
    Determine whether the current prototype
    pipeline requires review.
    """

    problems = []

    # --------------------------------------------------
    # Segmentation
    # --------------------------------------------------

    if not segmentation["exists"]:

        problems.append(
            "Segmentation mask is missing."
        )

    elif not segmentation["readable"]:

        problems.append(
            "Segmentation mask cannot be read."
        )

    elif segmentation["empty_mask"]:

        problems.append(
            "Segmentation mask is empty."
        )

    elif segmentation["full_mask"]:

        problems.append(
            "Segmentation mask is completely filled."
        )

    # --------------------------------------------------
    # Edges
    # --------------------------------------------------

    if not edges["exists"]:

        problems.append(
            "Edge image is missing."
        )

    elif not edges["readable"]:

        problems.append(
            "Edge image cannot be read."
        )

    elif edges["edge_ratio"] == 0:

        problems.append(
            "No edges were detected."
        )

    # --------------------------------------------------
    # Vectorization
    # --------------------------------------------------

    if not vectorized["valid_svg"]:

        problems.append(
            "Vectorized SVG is invalid or missing."
        )

    elif vectorized["vector_element_count"] == 0:

        problems.append(
            "Vectorized SVG contains no vector elements."
        )

    # --------------------------------------------------
    # Normalization
    # --------------------------------------------------

    if not normalized["valid_svg"]:

        problems.append(
            "Normalized SVG is invalid or missing."
        )

    elif normalized["vector_element_count"] == 0:

        problems.append(
            "Normalized SVG contains no vector elements."
        )

    # --------------------------------------------------
    # Pipeline completeness
    # --------------------------------------------------

    if (
        completeness["completeness_percent"]
        < 100
    ):

        problems.append(
            "Pipeline is incomplete."
        )

    # --------------------------------------------------
    # Overall status
    # --------------------------------------------------

    if len(problems) == 0:

        status = "PASS"

    else:

        status = "REVIEW_REQUIRED"

    return {

        "status": status,

        "problems": problems
    }


# ==========================================================
# MAIN EVALUATION
# ==========================================================

def run_evaluation():

    print(
        "Starting VietHeritage Data Engine evaluation..."
    )

    # ==================================================
    # BASIC IMAGE INFORMATION
    # ==================================================

    image_results = {}

    for name in [
        "cleaning",
        "restoration",
        "edges",
        "segmentation_mask",
        "segmented"
    ]:

        image_results[name] = (
            evaluate_image(
                FILES[name]
            )
        )

    # ==================================================
    # IMAGE QUALITY
    # ==================================================

    image_quality_results = {}

    for name in [
        "cleaning",
        "restoration",
        "segmented"
    ]:

        image_quality_results[name] = (
            evaluate_image_quality(
                FILES[name]
            )
        )

    # ==================================================
    # SEGMENTATION
    # ==================================================

    segmentation_result = (
        evaluate_segmentation(
            FILES["segmentation_mask"]
        )
    )

    # ==================================================
    # EDGES
    # ==================================================

    edge_result = (
        evaluate_edges(
            FILES["edges"]
        )
    )

    # ==================================================
    # SVG
    # ==================================================

    vectorized_result = (
        evaluate_svg(
            FILES["vectorization"]
        )
    )

    normalized_result = (
        evaluate_svg(
            FILES["normalization"]
        )
    )

    # ==================================================
    # PIPELINE COMPLETENESS
    # ==================================================

    completeness_result = (
        evaluate_pipeline_completeness()
    )

    # ==================================================
    # OVERALL RESULT
    # ==================================================

    overall_result = (
        calculate_overall_status(
            segmentation_result,
            edge_result,
            vectorized_result,
            normalized_result,
            completeness_result
        )
    )

    # ==================================================
    # BUILD REPORT
    # ==================================================

    report = {

        "project": (
            "VietHeritage Data Engine"
        ),

        "evaluation_type": (
            "Prototype pipeline evaluation"
        ),

        "ground_truth_available": False,

        "note": (
            "Accuracy metrics such as IoU, "
            "precision, recall, and F1 are "
            "not calculated because a manually "
            "annotated ground-truth dataset "
            "is not available yet."
        ),

        "images": image_results,

        "image_quality": (
            image_quality_results
        ),

        "segmentation": (
            segmentation_result
        ),

        "edges": (
            edge_result
        ),

        "vectorization": (
            vectorized_result
        ),

        "normalization": (
            normalized_result
        ),

        "pipeline": (
            completeness_result
        ),

        "overall": (
            overall_result
        )
    }

    # ==================================================
    # SAVE REPORT
    # ==================================================

    os.makedirs(
        EVALUATION_DIR,
        exist_ok=True
    )

    with open(
        REPORT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=4
        )

    # ==================================================
    # TERMINAL SUMMARY
    # ==================================================

    print()
    print("=" * 60)
    print(
        "VIETHERITAGE DATA ENGINE EVALUATION"
    )
    print("=" * 60)

    # --------------------------------------------------
    # Pipeline
    # --------------------------------------------------

    print(
        f"Pipeline completeness: "
        f"{completeness_result['completeness_percent']}%"
    )

    # --------------------------------------------------
    # Image quality
    # --------------------------------------------------

    print()
    print("IMAGE QUALITY")
    print("-" * 60)

    for name, metrics in (
        image_quality_results.items()
    ):

        print()
        print(name)

        print(
            f"  Sharpness : "
            f"{metrics['sharpness']}"
        )

        print(
            f"  Brightness: "
            f"{metrics['brightness']}"
        )

        print(
            f"  Contrast  : "
            f"{metrics['contrast']}"
        )

        print(
            f"  Noise     : "
            f"{metrics['noise']}"
        )

    # --------------------------------------------------
    # Segmentation
    # --------------------------------------------------

    print()
    print("SEGMENTATION")
    print("-" * 60)

    print(
        f"Status: "
        f"{segmentation_result['status']}"
    )

    print(
        f"Foreground ratio: "
        f"{segmentation_result['foreground_ratio']}"
    )

    print(
        f"Background ratio: "
        f"{segmentation_result['background_ratio']}"
    )

    # --------------------------------------------------
    # Edges
    # --------------------------------------------------

    print()
    print("EDGES")
    print("-" * 60)

    print(
        f"Status: "
        f"{edge_result['status']}"
    )

    print(
        f"Edge ratio: "
        f"{edge_result['edge_ratio']}"
    )

    # --------------------------------------------------
    # Vectorization
    # --------------------------------------------------

    print()
    print("VECTORIZATION")
    print("-" * 60)

    print(
        f"Status: "
        f"{vectorized_result['status']}"
    )

    print(
        f"Vector elements: "
        f"{vectorized_result['vector_element_count']}"
    )

    print(
        f"Embedded raster images: "
        f"{vectorized_result['embedded_raster_count']}"
    )

    # --------------------------------------------------
    # Normalization
    # --------------------------------------------------

    print()
    print("NORMALIZATION")
    print("-" * 60)

    print(
        f"Status: "
        f"{normalized_result['status']}"
    )

    print(
        f"Vector elements: "
        f"{normalized_result['vector_element_count']}"
    )

    # --------------------------------------------------
    # Overall
    # --------------------------------------------------

    print()
    print("=" * 60)

    print(
        f"OVERALL STATUS: "
        f"{overall_result['status']}"
    )

    if overall_result["problems"]:

        print()
        print(
            "ITEMS REQUIRING REVIEW:"
        )

        for problem in (
            overall_result["problems"]
        ):

            print(
                f"- {problem}"
            )

    print()
    print(
        "Evaluation report:"
    )

    print(
        REPORT_PATH
    )

    print("=" * 60)


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    run_evaluation()