import os
import json
import cv2
import numpy as np


# ==========================================
# CONFIGURATION
# ==========================================

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff"
}


# ==========================================
# IMAGE LOADING
# ==========================================

def load_image(image_path):
    """
    Load image as color image.
    """

    image = cv2.imread(
        image_path,
        cv2.IMREAD_COLOR
    )

    return image


# ==========================================
# IMAGE METRICS
# ==========================================

def calculate_metrics(image):
    """
    Calculate basic image quality metrics.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    brightness = float(
        np.mean(gray)
    )

    contrast = float(
        np.std(gray)
    )

    sharpness = float(
        cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()
    )

    return {
        "brightness": round(
            brightness,
            2
        ),
        "contrast": round(
            contrast,
            2
        ),
        "sharpness": round(
            sharpness,
            2
        ),
        "width": int(
            image.shape[1]
        ),
        "height": int(
            image.shape[0]
        )
    }


# ==========================================
# IMAGE QUALITY SCORE
# ==========================================

def calculate_quality_score(metrics):
    """
    Calculate a simple normalized quality score.

    This score is intended for comparison
    between pipeline stages, not as a
    replacement for the dataset quality scorer.
    """

    sharpness = metrics["sharpness"]
    contrast = metrics["contrast"]
    brightness = metrics["brightness"]

    # --------------------------------------
    # Sharpness score
    # --------------------------------------

    sharpness_score = min(
        sharpness / 400.0 * 100.0,
        100.0
    )

    # --------------------------------------
    # Contrast score
    # --------------------------------------

    if contrast < 10:

        contrast_score = (
            contrast / 10.0 * 30.0
        )

    elif contrast < 30:

        contrast_score = (
            30.0 +
            (contrast - 10.0) /
            20.0 *
            50.0
        )

    elif contrast <= 65:

        contrast_score = (
            80.0 +
            (contrast - 30.0) /
            35.0 *
            20.0
        )

    else:

        contrast_score = 100.0

    # --------------------------------------
    # Brightness score
    # --------------------------------------

    brightness_distance = abs(
        brightness - 128.0
    )

    brightness_score = max(
        0.0,
        100.0 -
        brightness_distance /
        128.0 *
        100.0
    )

    # --------------------------------------
    # Overall
    # --------------------------------------

    overall = (
        sharpness_score * 0.50 +
        contrast_score * 0.25 +
        brightness_score * 0.25
    )

    return round(
        overall,
        2
    )


# ==========================================
# COMPARE TWO IMAGES
# ==========================================

def compare_images(
    original,
    processed
):
    """
    Compare metrics between two images.
    """

    original_metrics = calculate_metrics(
        original
    )

    processed_metrics = calculate_metrics(
        processed
    )

    result = {
        "original": original_metrics,
        "processed": processed_metrics,
        "change": {
            "brightness": round(
                processed_metrics["brightness"] -
                original_metrics["brightness"],
                2
            ),
            "contrast": round(
                processed_metrics["contrast"] -
                original_metrics["contrast"],
                2
            ),
            "sharpness": round(
                processed_metrics["sharpness"] -
                original_metrics["sharpness"],
                2
            )
        },
        "quality_score": {
            "original": calculate_quality_score(
                original_metrics
            ),
            "processed": calculate_quality_score(
                processed_metrics
            )
        }
    }

    result["quality_score"]["change"] = round(
        result["quality_score"]["processed"] -
        result["quality_score"]["original"],
        2
    )

    return result


# ==========================================
# FIND IMAGES
# ==========================================

def find_images(directory):
    """
    Recursively find image files.
    """

    image_files = []

    if not os.path.exists(directory):
        return image_files

    for root, directories, files in os.walk(
        directory
    ):

        for filename in files:

            extension = os.path.splitext(
                filename
            )[1].lower()

            if extension not in SUPPORTED_EXTENSIONS:
                continue

            image_files.append(
                os.path.join(
                    root,
                    filename
                )
            )

    return image_files


# ==========================================
# FIND MATCHING IMAGE
# ==========================================

def find_matching_image(
    filename,
    directory
):
    """
    Find an image with the same filename
    inside a directory tree.
    """

    for root, directories, files in os.walk(
        directory
    ):

        if filename in files:

            return os.path.join(
                root,
                filename
            )

    return None


# ==========================================
# EVALUATE RESTORATION
# ==========================================

def evaluate_restoration(
    original_path,
    processed_path
):
    """
    Compare original image with
    normalized/restored result.
    """

    original = load_image(
        original_path
    )

    processed = load_image(
        processed_path
    )

    if original is None:
        return None

    if processed is None:
        return None

    return compare_images(
        original,
        processed
    )


# ==========================================
# EVALUATE SEGMENTATION
# ==========================================

def evaluate_segmentation(mask_path):
    """
    Evaluate segmentation mask statistics.
    """

    mask = cv2.imread(
        mask_path,
        cv2.IMREAD_GRAYSCALE
    )

    if mask is None:
        return None

    total_pixels = (
        mask.shape[0] *
        mask.shape[1]
    )

    foreground_pixels = np.count_nonzero(
        mask
    )

    background_pixels = (
        total_pixels -
        foreground_pixels
    )

    foreground_ratio = (
        foreground_pixels /
        total_pixels
    )

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    valid_contours = []

    for contour in contours:

        area = cv2.contourArea(
            contour
        )

        if area >= 20:
            valid_contours.append(
                contour
            )

    return {
        "width": int(
            mask.shape[1]
        ),
        "height": int(
            mask.shape[0]
        ),
        "foreground_pixels": int(
            foreground_pixels
        ),
        "background_pixels": int(
            background_pixels
        ),
        "foreground_ratio": round(
            float(foreground_ratio),
            4
        ),
        "contour_count": len(
            valid_contours
        )
    }


# ==========================================
# EVALUATE VECTORIZATION
# ==========================================

def evaluate_vectorization(
    json_path
):
    """
    Read vectorization metadata.
    """

    if not os.path.exists(
        json_path
    ):
        return None

    try:

        with open(
            json_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(
                file
            )

    except Exception as error:

        print(
            f"WARNING: Cannot read {json_path}"
        )

        print(
            error
        )

        return None

    vectors = data.get(
        "vectors",
        []
    )

    total_original_points = 0
    total_simplified_points = 0

    for vector in vectors:

        total_original_points += vector.get(
            "original_points",
            0
        )

        total_simplified_points += vector.get(
            "simplified_points",
            0
        )

    if total_original_points > 0:

        reduction_ratio = (
            1 -
            total_simplified_points /
            total_original_points
        )

    else:

        reduction_ratio = 0

    return {
        "vector_count": len(
            vectors
        ),
        "original_points": int(
            total_original_points
        ),
        "simplified_points": int(
            total_simplified_points
        ),
        "point_reduction_ratio": round(
            float(reduction_ratio),
            4
        )
    }


# ==========================================
# EVALUATE ONE IMAGE
# ==========================================

def evaluate_one_image(
    original_path,
    normalized_path,
    mask_path,
    vector_json_path
):
    """
    Evaluate one complete pipeline result.
    """

    result = {
        "filename": os.path.basename(
            original_path
        )
    }

    # --------------------------------------
    # Image quality
    # --------------------------------------

    original = load_image(
        original_path
    )

    normalized = load_image(
        normalized_path
    )

    if (
        original is not None and
        normalized is not None
    ):

        result["image_quality"] = compare_images(
            original,
            normalized
        )

    else:

        result["image_quality"] = None

    # --------------------------------------
    # Segmentation
    # --------------------------------------

    result["segmentation"] = (
        evaluate_segmentation(
            mask_path
        )
        if mask_path
        else None
    )

    # --------------------------------------
    # Vectorization
    # --------------------------------------

    result["vectorization"] = (
        evaluate_vectorization(
            vector_json_path
        )
        if vector_json_path
        else None
    )

    return result


# ==========================================
# CREATE SUMMARY
# ==========================================

def create_summary(results):
    """
    Create overall evaluation summary.
    """

    total = len(
        results
    )

    quality_changes = []

    foreground_ratios = []

    vector_counts = []

    reduction_ratios = []

    for result in results:

        image_quality = result.get(
            "image_quality"
        )

        if image_quality:

            quality_change = (
                image_quality
                .get(
                    "quality_score",
                    {}
                )
                .get(
                    "change"
                )
            )

            if quality_change is not None:

                quality_changes.append(
                    quality_change
                )

        segmentation = result.get(
            "segmentation"
        )

        if segmentation:

            foreground_ratios.append(
                segmentation[
                    "foreground_ratio"
                ]
            )

        vectorization = result.get(
            "vectorization"
        )

        if vectorization:

            vector_counts.append(
                vectorization[
                    "vector_count"
                ]
            )

            reduction_ratios.append(
                vectorization[
                    "point_reduction_ratio"
                ]
            )

    summary = {
        "total_images": total,
        "evaluated_images": len(
            quality_changes
        ),
        "average_quality_change": round(
            float(
                np.mean(
                    quality_changes
                )
            ),
            2
        )
        if quality_changes
        else None,
        "average_foreground_ratio": round(
            float(
                np.mean(
                    foreground_ratios
                )
            ),
            4
        )
        if foreground_ratios
        else None,
        "average_vector_count": round(
            float(
                np.mean(
                    vector_counts
                )
            ),
            2
        )
        if vector_counts
        else None,
        "average_point_reduction_ratio": round(
            float(
                np.mean(
                    reduction_ratios
                )
            ),
            4
        )
        if reduction_ratios
        else None
    }

    return summary


# ==========================================
# SAVE REPORT
# ==========================================

def save_report(
    report,
    output_path
):
    """
    Save evaluation report.
    """

    os.makedirs(
        os.path.dirname(
            output_path
        ),
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )


# ==========================================
# MAIN
# ==========================================

def main():

    project_root = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    original_directory = os.path.join(
        project_root,
        "dataset",
        "images"
    )

    normalized_directory = os.path.join(
        project_root,
        "outputs",
        "normalization"
    )

    mask_directory = os.path.join(
        project_root,
        "outputs",
        "segmentation_masks"
    )

    vector_directory = os.path.join(
        project_root,
        "outputs",
        "vector_metadata"
    )

    output_directory = os.path.join(
        project_root,
        "outputs",
        "evaluation"
    )

    report_path = os.path.join(
        output_directory,
        "evaluation_report.json"
    )

    print(
        "========================================"
    )

    print(
        "       VietHeritage Evaluation"
    )

    print(
        "========================================"
    )

    print()

    print(
        f"Original:    {original_directory}"
    )

    print(
        f"Normalized:  {normalized_directory}"
    )

    print(
        f"Masks:       {mask_directory}"
    )

    print(
        f"Vectors:     {vector_directory}"
    )

    print()

    if not os.path.exists(
        original_directory
    ):

        print(
            "ERROR: Dataset image directory "
            "does not exist."
        )

        return

    # --------------------------------------
    # Find original images
    # --------------------------------------

    original_files = find_images(
        original_directory
    )

    print(
        f"Original images found: "
        f"{len(original_files)}"
    )

    print()

    results = []

    success_count = 0

    for original_path in original_files:

        filename = os.path.basename(
            original_path
        )

        print(
            f"Evaluating: {filename}"
        )

        # ----------------------------------
        # Matching normalized image
        # ----------------------------------

        normalized_path = (
            find_matching_image(
                filename,
                normalized_directory
            )
        )

        # ----------------------------------
        # Matching mask
        # ----------------------------------

        mask_filename = (
            os.path.splitext(
                filename
            )[0]
            + "_mask.png"
        )

        mask_path = (
            find_matching_image(
                mask_filename,
                mask_directory
            )
        )

        # ----------------------------------
        # Matching vector JSON
        # ----------------------------------

        vector_filename = (
            os.path.splitext(
                filename
            )[0]
            + ".json"
        )

        vector_json_path = (
            find_matching_image(
                vector_filename,
                vector_directory
            )
        )

        # ----------------------------------
        # Evaluate
        # ----------------------------------

        result = evaluate_one_image(
            original_path,
            normalized_path,
            mask_path,
            vector_json_path
        )

        results.append(
            result
        )

        success_count += 1

        print(
            "  -> OK"
        )

    # --------------------------------------
    # Summary
    # --------------------------------------

    summary = create_summary(
        results
    )

    report = {
        "project": (
            "VietHeritage Data Engine"
        ),
        "evaluation_type": (
            "Pipeline Evaluation"
        ),
        "summary": summary,
        "results": results
    }

    # --------------------------------------
    # Save
    # --------------------------------------

    save_report(
        report,
        report_path
    )

    # --------------------------------------
    # Print results
    # --------------------------------------

    print()

    print(
        "========================================"
    )

    print(
        "EVALUATION COMPLETED"
    )

    print(
        f"Images evaluated: "
        f"{success_count}"
    )

    print()

    print(
        f"Average quality change: "
        f"{summary['average_quality_change']}"
    )

    print(
        f"Average foreground ratio: "
        f"{summary['average_foreground_ratio']}"
    )

    print(
        f"Average vector count: "
        f"{summary['average_vector_count']}"
    )

    print(
        f"Average point reduction: "
        f"{summary['average_point_reduction_ratio']}"
    )

    print()

    print(
        f"Report saved to:"
    )

    print(
        report_path
    )

    print(
        "========================================"
    )


if __name__ == "__main__":
    main()