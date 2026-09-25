import json
import os
import cv2

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
    Cleaning
        ↓
    Restoration
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

    # ========================================
    # 1. CREATE OUTPUT DIRECTORY
    # ========================================

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    # ========================================
    # 2. LOAD IMAGE
    # ========================================

    image = cv2.imread(
        input_path
    )

    if image is None:
        raise ValueError(
            f"Cannot read image: {input_path}"
        )

    # ========================================
    # 3. EVALUATE ORIGINAL IMAGE
    # ========================================

    original_metrics = evaluate_image(
        image
    )

    # ========================================
    # 4. CLEANING
    # ========================================

    cleaned = clean_image(
        image
    )

    # ========================================
    # 5. RESTORATION
    # ========================================

    restored = restore_image(
        cleaned
    )

    restored_path = os.path.join(
        output_dir,
        "restored.png"
    )

    cv2.imwrite(
        restored_path,
        restored
    )

    # ========================================
    # 6. NORMALIZATION
    # ========================================

    normalized = normalize_image(
        restored
    )

    normalized_path = os.path.join(
        output_dir,
        "normalized.png"
    )

    cv2.imwrite(
        normalized_path,
        normalized
    )

    # ========================================
    # 7. EDGE PROCESSING
    # ========================================

    edges = process_edges(
        normalized
    )

    edges_path = os.path.join(
        output_dir,
        "edges.png"
    )

    cv2.imwrite(
        edges_path,
        edges
    )

    # ========================================
    # 8. SEGMENTATION
    # ========================================

    segmented, mask = segment_image(
        normalized
    )

    segmented_path = os.path.join(
        output_dir,
        "segmented.png"
    )

    cv2.imwrite(
        segmented_path,
        segmented
    )

    # ========================================
    # 9. VECTORIZATION
    # ========================================

    svg_path = os.path.join(
        output_dir,
        "pattern.svg"
    )

    vectorize_mask(
        mask,
        svg_path
    )

    # ========================================
    # 10. EVALUATE RESTORED IMAGE
    # ========================================

    restored_metrics = evaluate_image(
        restored
    )

    # ========================================
    # 11. EVALUATE NORMALIZED IMAGE
    # ========================================

    normalized_metrics = evaluate_image(
        normalized
    )

    # ========================================
    # 12. QUALITY REPORT
    # ========================================

    quality_report = {

        "input": {
            "path": input_path,
            "metrics": original_metrics
        },

        "restored": {
            "path": restored_path,
            "metrics": restored_metrics
        },

        "normalized": {
            "path": normalized_path,
            "metrics": normalized_metrics
        },

        "outputs": {
            "restored": restored_path,
            "normalized": normalized_path,
            "segmented": segmented_path,
            "edges": edges_path,
            "svg": svg_path
        },

        "status": "completed"
    }

    # ========================================
    # 13. SAVE QUALITY REPORT
    # ========================================

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