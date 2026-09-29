import json
from pathlib import Path

import cv2
import joblib
import numpy as np
import matplotlib.pyplot as plt

from skimage.feature import hog
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

AI_READY_DIR = BASE_DIR / "ai_ready"
SPLITS_DIR = AI_READY_DIR / "splits"

MODEL_DIR = BASE_DIR / "ai" / "models"
EVALUATION_DIR = BASE_DIR / "ai" / "evaluation"

# ============================================================
# V3 MODEL
# ============================================================

MODEL_FILE = (
    MODEL_DIR / "baseline_svm_v3.joblib"
)

LABEL_ENCODER_FILE = (
    MODEL_DIR / "label_encoder_v3.joblib"
)

TEST_FILE = (
    SPLITS_DIR / "test.json"
)

# ============================================================
# V3 OUTPUT FILES
# ============================================================

PREDICTIONS_FILE = (
    EVALUATION_DIR / "test_predictions_v3.json"
)

REPORT_FILE = (
    EVALUATION_DIR / "evaluation_report_v3.json"
)

CONFUSION_MATRIX_FILE = (
    EVALUATION_DIR / "confusion_matrix_v3.png"
)


# ============================================================
# CONFIG
# ============================================================

IMAGE_SIZE = (128, 128)

HOG_ORIENTATIONS = 9
HOG_PIXELS_PER_CELL = (8, 8)
HOG_CELLS_PER_BLOCK = (2, 2)

# Must match V3 train_baseline.py
#
# "other" and "uploaded" are not part of the
# classification task.
#
# They remain in the broader VietHeritage dataset.
EXCLUDED_CATEGORIES = {
    "other",
    "uploaded"
}


# ============================================================
# LOAD TEST SPLIT
# ============================================================

def load_test_split():

    if not TEST_FILE.exists():

        raise FileNotFoundError(
            f"Test split not found:\n{TEST_FILE}"
        )

    with open(
        TEST_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# LOAD IMAGE
# ============================================================

def load_image(image_path):

    image_path = Path(image_path)

    # ai_ready/images/...
    if (
        image_path.parts
        and image_path.parts[0] == "ai_ready"
    ):

        full_path = BASE_DIR / image_path

    # images/...
    elif (
        image_path.parts
        and image_path.parts[0] == "images"
    ):

        full_path = AI_READY_DIR / image_path

    # fallback
    else:

        full_path = AI_READY_DIR / image_path

    if not full_path.exists():

        raise FileNotFoundError(
            f"Image not found:\n{full_path}"
        )

    image = cv2.imread(
        str(full_path),
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:

        raise ValueError(
            f"Cannot read image:\n{full_path}"
        )

    image = cv2.resize(
        image,
        IMAGE_SIZE,
        interpolation=cv2.INTER_AREA
    )

    return image


# ============================================================
# HOG FEATURE EXTRACTION
# ============================================================

def extract_features(image):

    features = hog(
        image,
        orientations=HOG_ORIENTATIONS,
        pixels_per_cell=HOG_PIXELS_PER_CELL,
        cells_per_block=HOG_CELLS_PER_BLOCK,
        block_norm="L2-Hys"
    )

    return features.astype(
        np.float32
    )


# ============================================================
# CATEGORY DISTRIBUTION
# ============================================================

def category_distribution(labels):

    distribution = {}

    for label in labels:

        distribution[label] = (
            distribution.get(
                label,
                0
            ) + 1
        )

    return distribution


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "VIETHERITAGE BASELINE AI - V3 TEST EVALUATION"
    )
    print("=" * 70)

    EVALUATION_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================
    # 1. LOAD MODEL
    # ========================================================

    print(
        "\n[1/6] Loading trained V3 model..."
    )

    if not MODEL_FILE.exists():

        raise FileNotFoundError(
            f"V3 model not found:\n{MODEL_FILE}"
        )

    if not LABEL_ENCODER_FILE.exists():

        raise FileNotFoundError(
            f"V3 label encoder not found:\n"
            f"{LABEL_ENCODER_FILE}"
        )

    model = joblib.load(
        MODEL_FILE
    )

    label_encoder = joblib.load(
        LABEL_ENCODER_FILE
    )

    print(
        f"Model loaded: {MODEL_FILE}"
    )

    print(
        "Categories:"
    )

    for category in label_encoder.classes_:

        print(
            f"  - {category}"
        )

    # ========================================================
    # 2. LOAD TEST DATA
    # ========================================================

    print(
        "\n[2/6] Loading V3 test dataset..."
    )

    test_data = load_test_split()

    all_assets = test_data.get(
        "assets",
        []
    )

    if not all_assets:

        raise RuntimeError(
            "Test dataset is empty."
        )

    # --------------------------------------------------------
    # Exclude categories that are not part
    # of the V3 classification task.
    # --------------------------------------------------------

    assets = [
        item
        for item in all_assets
        if item["category"]
        not in EXCLUDED_CATEGORIES
    ]

    excluded_assets = [
        item
        for item in all_assets
        if item["category"]
        in EXCLUDED_CATEGORIES
    ]

    print(
        f"Test assets       : "
        f"{len(all_assets)}"
    )

    print(
        f"Usable test assets: "
        f"{len(assets)}"
    )

    print(
        f"Excluded assets   : "
        f"{len(excluded_assets)}"
    )

    if excluded_assets:

        print(
            "\nExcluded categories:"
        )

        for item in excluded_assets:

            print(
                f"  - "
                f"{item['asset_id']} "
                f"({item['category']})"
            )

    # ========================================================
    # 3. EXTRACT FEATURES
    # ========================================================

    print(
        "\n[3/6] Extracting HOG features..."
    )

    X_test = []
    y_test = []

    asset_ids = []
    image_paths = []

    for item in assets:

        asset_id = item["asset_id"]
        category = item["category"]
        image_path = item["image"]

        # ----------------------------------------------------
        # Safety check:
        # category must exist in V3 model labels.
        # ----------------------------------------------------

        if category not in label_encoder.classes_:

            raise RuntimeError(
                f"Category '{category}' is not "
                f"present in V3 trained model labels."
            )

        image = load_image(
            image_path
        )

        features = extract_features(
            image
        )

        X_test.append(
            features
        )

        y_test.append(
            category
        )

        asset_ids.append(
            asset_id
        )

        image_paths.append(
            image_path
        )

    X_test = np.array(
        X_test
    )

    y_test = np.array(
        y_test
    )

    print(
        f"Test feature shape: "
        f"{X_test.shape}"
    )

    # ========================================================
    # 4. PREDICTION
    # ========================================================

    print(
        "\n[4/6] Running V3 predictions..."
    )

    y_test_encoded = (
        label_encoder.transform(
            y_test
        )
    )

    predictions_encoded = (
        model.predict(
            X_test
        )
    )

    predictions = (
        label_encoder.inverse_transform(
            predictions_encoded
        )
    )

    accuracy = accuracy_score(
        y_test_encoded,
        predictions_encoded
    )

    print(
        f"Test accuracy: "
        f"{accuracy:.4f}"
    )

    # ========================================================
    # 5. METRICS
    # ========================================================

    print(
        "\n[5/6] Calculating V3 metrics..."
    )

    classes = list(
        label_encoder.classes_
    )

    precision, recall, f1, _ = (
        precision_recall_fscore_support(
            y_test,
            predictions,
            labels=classes,
            average="weighted",
            zero_division=0
        )
    )

    report = classification_report(
        y_test,
        predictions,
        labels=classes,
        output_dict=True,
        zero_division=0
    )

    cm = confusion_matrix(
        y_test,
        predictions,
        labels=classes
    )

    print(
        f"Accuracy  : "
        f"{accuracy:.4f}"
    )

    print(
        f"Precision : "
        f"{precision:.4f}"
    )

    print(
        f"Recall    : "
        f"{recall:.4f}"
    )

    print(
        f"F1-score  : "
        f"{f1:.4f}"
    )

    print(
        "\nClassification report:"
    )

    print(
        classification_report(
            y_test,
            predictions,
            labels=classes,
            zero_division=0
        )
    )

    # ========================================================
    # 6. SAVE RESULTS
    # ========================================================

    print(
        "\n[6/6] Saving V3 evaluation results..."
    )

    # --------------------------------------------------------
    # Prediction records
    # --------------------------------------------------------

    prediction_records = []

    for i in range(
        len(asset_ids)
    ):

        prediction_records.append(
            {
                "asset_id":
                    asset_ids[i],

                "image":
                    image_paths[i],

                "actual_category":
                    y_test[i],

                "predicted_category":
                    predictions[i],

                "correct":
                    bool(
                        y_test[i]
                        == predictions[i]
                    )
            }
        )

    with open(
        PREDICTIONS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "model":
                    "HOG + SVM",

                "experiment":
                    "v3",

                "dataset":
                    "VietHeritage Classification Dataset V3",

                "split":
                    "test",

                "count":
                    len(
                        prediction_records
                    ),

                "excluded_categories":
                    sorted(
                        EXCLUDED_CATEGORIES
                    ),

                "predictions":
                    prediction_records
            },

            f,

            ensure_ascii=False,

            indent=4
        )

    # --------------------------------------------------------
    # Evaluation report
    # --------------------------------------------------------

    evaluation_report = {

        "model": {

            "name":
                "HOG + SVM",

            "algorithm":
                "Support Vector Machine",

            "kernel":
                "RBF",

            "class_weight":
                "balanced"
        },

        "experiment": {

            "version":
                "v3",

            "dataset":
                "VietHeritage Classification Dataset V3",

            "purpose":
                "Evaluate HOG + SVM "
                "on the task-specific "
                "cultural motif classification "
                "dataset excluding other "
                "and uploaded categories"
        },

        "dataset": {

            "split":
                "test",

            "original_samples":
                len(all_assets),

            "evaluated_samples":
                len(assets),

            "excluded_samples":
                len(excluded_assets),

            "excluded_categories":
                sorted(
                    EXCLUDED_CATEGORIES
                ),

            "category_distribution":
                category_distribution(
                    y_test
                )
        },

        "feature_extraction": {

            "method":
                "HOG",

            "image_size":
                list(
                    IMAGE_SIZE
                ),

            "orientations":
                HOG_ORIENTATIONS,

            "pixels_per_cell":
                list(
                    HOG_PIXELS_PER_CELL
                ),

            "cells_per_block":
                list(
                    HOG_CELLS_PER_BLOCK
                ),

            "feature_dimension":
                int(
                    X_test.shape[1]
                )
        },

        "metrics": {

            "accuracy":
                float(
                    accuracy
                ),

            "precision_weighted":
                float(
                    precision
                ),

            "recall_weighted":
                float(
                    recall
                ),

            "f1_weighted":
                float(
                    f1
                )
        },

        "classification_report":
            report,

        "confusion_matrix":
            cm.tolist(),

        "classes":
            classes,

        "predictions_file":
            str(
                PREDICTIONS_FILE.relative_to(
                    BASE_DIR
                )
            ),

        "confusion_matrix_file":
            str(
                CONFUSION_MATRIX_FILE.relative_to(
                    BASE_DIR
                )
            )
    }

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            evaluation_report,
            f,
            ensure_ascii=False,
            indent=4
        )

    # ========================================================
    # CONFUSION MATRIX
    # ========================================================

    plt.figure(
        figsize=(10, 8)
    )

    plt.imshow(
        cm,
        interpolation="nearest"
    )

    plt.title(
        "VietHeritage Baseline V3 - Confusion Matrix"
    )

    plt.colorbar()

    tick_marks = np.arange(
        len(classes)
    )

    plt.xticks(
        tick_marks,
        classes,
        rotation=45,
        ha="right"
    )

    plt.yticks(
        tick_marks,
        classes
    )

    threshold = (
        cm.max() / 2.0
        if cm.size > 0
        else 0
    )

    for i in range(
        cm.shape[0]
    ):

        for j in range(
            cm.shape[1]
        ):

            plt.text(
                j,
                i,
                str(cm[i, j]),
                horizontalalignment="center",
                color="white"
                if cm[i, j] > threshold
                else "black"
            )

    plt.ylabel(
        "Actual Category"
    )

    plt.xlabel(
        "Predicted Category"
    )

    plt.tight_layout()

    plt.savefig(
        CONFUSION_MATRIX_FILE,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "V3 TEST EVALUATION COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"\nOriginal test assets : "
        f"{len(all_assets)}"
    )

    print(
        f"Evaluated assets     : "
        f"{len(assets)}"
    )

    print(
        f"Excluded assets      : "
        f"{len(excluded_assets)}"
    )

    print(
        f"\nAccuracy  : "
        f"{accuracy:.4f}"
    )

    print(
        f"Precision : "
        f"{precision:.4f}"
    )

    print(
        f"Recall    : "
        f"{recall:.4f}"
    )

    print(
        f"F1-score  : "
        f"{f1:.4f}"
    )

    print(
        f"\nPredictions:"
        f"\n{PREDICTIONS_FILE}"
    )

    print(
        f"\nEvaluation report:"
        f"\n{REPORT_FILE}"
    )

    print(
        f"\nConfusion matrix:"
        f"\n{CONFUSION_MATRIX_FILE}"
    )


if __name__ == "__main__":
    main()