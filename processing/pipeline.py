import json
import os
import cv2
from processing.quality_classifier import classify_quality
from processing.cleaning import clean_image
from processing.restoration import restore_image
from processing.normalization import normalize_image
from processing.edge_processing import process_edges
from processing.segmentation import segment_image
from processing.vectorization import vectorize_mask
from processing.evaluation import evaluate_image


def process_image(input_path, output_dir):
    """
    Complete VietHeritage image processing pipeline.

    Pipeline:

    Original
        ↓
    Restoration / Real-ESRGAN
        ↓
    Cleaning
        ↓
    Normalization
        ↓
    Edge Processing
        ↓
    Segmentation
        ↓
    Vectorization
        ↓
    Evaluation
    """

    # ========================================================
    # 1. CREATE OUTPUT DIRECTORY
    # ========================================================

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    # ========================================================
    # 2. LOAD IMAGE
    # ========================================================

    image = cv2.imread(
        input_path
    )

    if image is None:
        raise ValueError(
            f"Cannot read image: {input_path}"
        )

    # ========================================================
    # 3. EVALUATE ORIGINAL IMAGE
    # ========================================================

    original_metrics = evaluate_image(
        image
    )

    # ========================================================
    # 4. RESTORATION / REAL-ESRGAN
    # ========================================================

    restored = restore_image(
        image
    )

    restored_path = os.path.join(
        output_dir,
        "restored.png"
    )

    if not cv2.imwrite(
        restored_path,
        restored
    ):
        raise RuntimeError(
            f"Failed to save: {restored_path}"
        )

    # ========================================================
    # 5. CLEANING
    # ========================================================

    cleaned = clean_image(
        restored
    )

    cleaned_path = os.path.join(
        output_dir,
        "cleaned.png"
    )

    if not cv2.imwrite(
        cleaned_path,
        cleaned
    ):
        raise RuntimeError(
            f"Failed to save: {cleaned_path}"
        )

    # ========================================================
    # 6. NORMALIZATION
    # ========================================================

    normalized = normalize_image(
        cleaned
    )

    normalized_path = os.path.join(
        output_dir,
        "normalized.png"
    )

    if not cv2.imwrite(
        normalized_path,
        normalized
    ):
        raise RuntimeError(
            f"Failed to save: {normalized_path}"
        )

    # ========================================================
    # 7. EDGE PROCESSING
    # ========================================================

    edges = process_edges(
        normalized
    )

    edges_path = os.path.join(
        output_dir,
        "edges.png"
    )

    if not cv2.imwrite(
        edges_path,
        edges
    ):
        raise RuntimeError(
            f"Failed to save: {edges_path}"
        )

    # ========================================================
    # 8. SEGMENTATION
    # ========================================================

    segmented, mask = segment_image(
        normalized
    )

    segmented_path = os.path.join(
        output_dir,
        "segmented.png"
    )

    mask_path = os.path.join(
        output_dir,
        "mask.png"
    )

    if not cv2.imwrite(
        segmented_path,
        segmented
    ):
        raise RuntimeError(
            f"Failed to save: {segmented_path}"
        )

    if not cv2.imwrite(
        mask_path,
        mask
    ):
        raise RuntimeError(
            f"Failed to save: {mask_path}"
        )

    # ========================================================
    # 9. VECTORIZATION
    # ========================================================

    svg_path = os.path.join(
        output_dir,
        "pattern.svg"
    )

    vectorize_mask(
        mask,
        svg_path
    )

    # ========================================================
    # 10. EVALUATE RESTORED IMAGE
    # ========================================================

    restored_metrics = evaluate_image(
        restored
    )

    # ========================================================
    # 11. EVALUATE CLEANED IMAGE
    # ========================================================

    cleaned_metrics = evaluate_image(
        cleaned
    )

    # ========================================================
    # 12. EVALUATE NORMALIZED IMAGE
    # ========================================================

    normalized_metrics = evaluate_image(
        normalized
    )

    # ========================================================
    # 13. QUALITY REPORT
    # ========================================================

    quality_report = {

        "input": {
            "path": input_path,
            "metrics": original_metrics
        },

        "restored": {
            "path": restored_path,
            "metrics": restored_metrics
        },

        "cleaned": {
            "path": cleaned_path,
            "metrics": cleaned_metrics
        },

        "normalized": {
            "path": normalized_path,
            "metrics": normalized_metrics
        },

        "outputs": {
            "restored": restored_path,
            "cleaned": cleaned_path,
            "normalized": normalized_path,
            "edges": edges_path,
            "segmented": segmented_path,
            "mask": mask_path,
            "svg": svg_path
        },

        "status": "completed"
    }

    # ========================================================
    # 14. SAVE QUALITY REPORT
    # ========================================================

    report_path = os.path.join(
        output_dir,
        "quality_report.json"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            quality_report,
            file,
            indent=4,
            ensure_ascii=False
        )

    return quality_report