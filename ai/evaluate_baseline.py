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

MODEL_FILE = MODEL_DIR / "baseline_svm.joblib"
LABEL_ENCODER_FILE = MODEL_DIR / "label_encoder.joblib"

TEST_FILE = SPLITS_DIR / "test.json"

PREDICTIONS_FILE = EVALUATION_DIR / "test_predictions.json"
REPORT_FILE = EVALUATION_DIR / "evaluation_report.json"
CONFUSION_MATRIX_FILE = EVALUATION_DIR / "confusion_matrix.png"


# ============================================================
# CONFIG
# ============================================================

IMAGE_SIZE = (128, 128)

HOG_ORIENTATIONS = 9
HOG_PIXELS_PER_CELL = (8, 8)
HOG_CELLS_PER_BLOCK = (2, 2)


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

    # Path already contains:
    # ai_ready/images/...
    if image_path.parts and image_path.parts[0] == "ai_ready":

        full_path = BASE_DIR / image_path

    # Path contains:
    # images/...
    elif image_path.parts and image_path.parts[0] == "images":

        full_path = AI_READY_DIR / image_path

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

    return features.astype(np.float32)


# ============================================================
# CATEGORY DISTRIBUTION
# ============================================================

def category_distribution(labels):

    distribution = {}

    for label in labels:

        distribution[label] = (
            distribution.get(label, 0) + 1
        )

    return distribution


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("VIETHERITAGE BASELINE AI - TEST EVALUATION")
    print("=" * 70)

    EVALUATION_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # 1. Load model
    # --------------------------------------------------------

    print("\n[1/6] Loading trained model...")

    if not MODEL_FILE.exists():

        raise FileNotFoundError(
            f"Model not found:\n{MODEL_FILE}"
        )

    if not LABEL_ENCODER_FILE.exists():

        raise FileNotFoundError(
            f"Label encoder not found:\n"
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

    # --------------------------------------------------------
    # 2. Load test data
    # --------------------------------------------------------

    print("\n[2/6] Loading test dataset...")

    test_data = load_test_split()

    assets = test_data.get(
        "assets",
        []
    )

    if not assets:

        raise RuntimeError(
            "Test dataset is empty."
        )

    print(
        f"Test assets: {len(assets)}"
    )

    # --------------------------------------------------------
    # 3. Extract features
    # --------------------------------------------------------

    print("\n[3/6] Extracting HOG features...")

    X_test = []
    y_test = []
    asset_ids = []
    image_paths = []

    for item in assets:

        asset_id = item["asset_id"]
        category = item["category"]
        image_path = item["image"]

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

    # --------------------------------------------------------
    # 4. Prediction
    # --------------------------------------------------------

    print("\n[4/6] Running predictions...")

    y_test_encoded = label_encoder.transform(
        y_test
    )

    predictions_encoded = model.predict(
        X_test
    )

    predictions = label_encoder.inverse_transform(
        predictions_encoded
    )

    accuracy = accuracy_score(
        y_test_encoded,
        predictions_encoded
    )

    print(
        f"Test accuracy: {accuracy:.4f}"
    )

    # --------------------------------------------------------
    # 5. Metrics
    # --------------------------------------------------------

    print("\n[5/6] Calculating metrics...")

    precision, recall, f1, _ = (
        precision_recall_fscore_support(
            y_test,
            predictions,
            labels=label_encoder.classes_,
            average="weighted",
            zero_division=0
        )
    )

    report = classification_report(
        y_test,
        predictions,
        labels=label_encoder.classes_,
        output_dict=True,
        zero_division=0
    )

    cm = confusion_matrix(
        y_test,
        predictions,
        labels=label_encoder.classes_
    )

    print(
        f"Accuracy  : {accuracy:.4f}"
    )

    print(
        f"Precision : {precision:.4f}"
    )

    print(
        f"Recall    : {recall:.4f}"
    )

    print(
        f"F1-score  : {f1:.4f}"
    )

    print("\nClassification report:")

    print(
        classification_report(
            y_test,
            predictions,
            labels=label_encoder.classes_,
            zero_division=0
        )
    )

    # --------------------------------------------------------
    # 6. Save results
    # --------------------------------------------------------

    print("\n[6/6] Saving evaluation results...")

    prediction_records = []

    for i in range(
        len(asset_ids)
    ):

        prediction_records.append(
            {
                "asset_id": asset_ids[i],
                "image": image_paths[i],
                "actual_category": y_test[i],
                "predicted_category": predictions[i],
                "correct": bool(
                    y_test[i] == predictions[i]
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
                "model": "HOG + SVM",
                "split": "test",
                "count": len(
                    prediction_records
                ),
                "predictions": prediction_records
            },
            f,
            ensure_ascii=False,
            indent=4
        )

    evaluation_report = {
        "model": {
            "name": "HOG + SVM",
            "algorithm": "Support Vector Machine",
            "kernel": "RBF"
        },
        "dataset": {
            "split": "test",
            "samples": len(assets),
            "category_distribution": (
                category_distribution(y_test)
            )
        },
        "metrics": {
            "accuracy": float(
                accuracy
            ),
            "precision_weighted": float(
                precision
            ),
            "recall_weighted": float(
                recall
            ),
            "f1_weighted": float(
                f1
            )
        },
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "classes": list(
            label_encoder.classes_
        ),
        "predictions_file": str(
            PREDICTIONS_FILE.relative_to(
                BASE_DIR
            )
        ),
        "confusion_matrix_file": str(
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

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    plt.figure(
        figsize=(10, 8)
    )

    plt.imshow(
        cm,
        interpolation="nearest"
    )

    plt.title(
        "VietHeritage Baseline - Confusion Matrix"
    )

    plt.colorbar()

    tick_marks = np.arange(
        len(label_encoder.classes_)
    )

    plt.xticks(
        tick_marks,
        label_encoder.classes_,
        rotation=45,
        ha="right"
    )

    plt.yticks(
        tick_marks,
        label_encoder.classes_
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

    # --------------------------------------------------------
    # FINAL OUTPUT
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("TEST EVALUATION COMPLETE")
    print("=" * 70)

    print(
        f"\nAccuracy  : {accuracy:.4f}"
    )

    print(
        f"Precision : {precision:.4f}"
    )

    print(
        f"Recall    : {recall:.4f}"
    )

    print(
        f"F1-score  : {f1:.4f}"
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