import json
import os

import cv2

from processing.cleaning import clean_image
from processing.restoration import restore_image
from processing.edge_processing import process_edges
from processing.segmentation import segment_image
from processing.vectorization import vectorize_mask
from processing.evaluation import evaluate_image


def process_image(
    input_path,
    output_dir
):
    """
    Complete VietHeritage image processing pipeline.

    Input:
        input_path  -> original image

    Output:
        restored.png
        segmented.png
        edges.png
        pattern.svg
        quality_report.json
    """

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    # ==================================================
    # 1. LOAD IMAGE
    # ==================================================

    image = cv2.imread(
        input_path
    )

    if image is None:
        raise ValueError(
            f"Cannot read image: {input_path}"
        )

    # ==================================================
    # 2. QUALITY CHECK - ORIGINAL
    # ==================================================

    original_metrics = evaluate_image(
        image
    )

    # ==================================================
    # 3. DATA CLEANING
    # ==================================================

    cleaned = clean_image(
        image
    )

    # ==================================================
    # 4. RESTORATION
    # ==================================================

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

    # ==================================================
    # 5. EDGE PROCESSING
    # ==================================================

    edges = process_edges(
        restored
    )

    edges_path = os.path.join(
        output_dir,
        "edges.png"
    )

    cv2.imwrite(
        edges_path,
        edges
    )

    # ==================================================
    # 6. SEGMENTATION
    # ==================================================

    segmented, mask = segment_image(
        restored
    )

    segmented_path = os.path.join(
        output_dir,
        "segmented.png"
    )

    cv2.imwrite(
        segmented_path,
        segmented
    )

    # ==================================================
    # 7. VECTORIZATION
    # ==================================================

    svg_path = os.path.join(
        output_dir,
        "pattern.svg"
    )

    vectorize_mask(
        mask,
        svg_path
    )

    # ==================================================
    # 8. EVALUATION
    # ==================================================

    restored_metrics = evaluate_image(
        restored
    )

    quality_report = {
        "input": {
            "path": input_path,
            "metrics": original_metrics
        },

        "restored": {
            "path": restored_path,
            "metrics": restored_metrics
        },

        "outputs": {
            "restored": restored_path,
            "segmented": segmented_path,
            "edges": edges_path,
            "svg": svg_path
        },

        "status": "completed"
    }

    # ==================================================
    # 9. SAVE REPORT
    # ==================================================

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