import json
from pathlib import Path
from datetime import datetime

import cv2
import joblib
import numpy as np

from skimage.feature import hog
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
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

OUTPUT_DIR = BASE_DIR / "ai" / "models"

TRAIN_FILE = SPLITS_DIR / "train.json"
VALIDATION_FILE = SPLITS_DIR / "validation.json"
TEST_FILE = SPLITS_DIR / "test.json"

MODEL_FILE = OUTPUT_DIR / "baseline_svm_v5.joblib"
LABEL_ENCODER_FILE = OUTPUT_DIR / "label_encoder_v5.joblib"
REPORT_FILE = OUTPUT_DIR / "training_report_v5.json"

TEST_PREDICTIONS_FILE = (
    BASE_DIR / "ai" / "evaluation" / "test_predictions_v5.json"
)


# ============================================================
# CONFIG
# ============================================================

IMAGE_SIZE = (128, 128)

HOG_ORIENTATIONS = 9
HOG_PIXELS_PER_CELL = (8, 8)
HOG_CELLS_PER_BLOCK = (2, 2)

SVM_KERNEL = "rbf"
SVM_C = 10.0
SVM_GAMMA = "scale"
SVM_CLASS_WEIGHT = "balanced"

RANDOM_STATE = 42

EXCLUDED_CATEGORIES = {
    "other",
    "uploaded",
}


# ============================================================
# DIRECTORIES
# ============================================================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEST_PREDICTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD SPLIT
# ============================================================

def load_split(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Split file not found:\n{path}"
        )

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected split JSON object:\n{path}"
        )

    if "assets" not in data:
        raise ValueError(
            f"Missing 'assets' in split:\n{path}"
        )

    return data


# ============================================================
# LOAD NORMALIZED IMAGE
# ============================================================

def load_normalized_image(asset):
    asset_id = asset["asset_id"]

    image_path = (
        BASE_DIR
        / "outputs"
        / asset_id
        / "normalized.png"
    )

    if not image_path.exists():
        raise FileNotFoundError(
            f"Normalized image not found:\n{image_path}"
        )

    image = cv2.imread(
        str(image_path),
        cv2.IMREAD_GRAYSCALE,
    )

    if image is None:
        raise ValueError(
            f"Cannot read normalized image:\n{image_path}"
        )

    image = cv2.resize(
        image,
        IMAGE_SIZE,
        interpolation=cv2.INTER_AREA,
    )

    return image, image_path


# ============================================================
# HOG FEATURES
# ============================================================

def extract_features(image):
    features = hog(
        image,
        orientations=HOG_ORIENTATIONS,
        pixels_per_cell=HOG_PIXELS_PER_CELL,
        cells_per_block=HOG_CELLS_PER_BLOCK,
        block_norm="L2-Hys",
        feature_vector=True,
    )

    return features.astype(np.float32)


# ============================================================
# PREPARE DATASET
# ============================================================

def prepare_dataset(split_data, split_name):
    assets = split_data["assets"]

    print()
    print("=" * 72)
    print(f"PREPARING {split_name.upper()} DATASET")
    print("=" * 72)

    X = []
    y = []
    metadata = []

    print(f"Assets declared: {len(assets)}")

    for index, asset in enumerate(assets, start=1):

        asset_id = asset["asset_id"]
        category = asset["category"]

        if category in EXCLUDED_CATEGORIES:
            print(
                f"[SKIP] {asset_id} | excluded category: {category}"
            )
            continue

        image, image_path = load_normalized_image(asset)

        features = extract_features(image)

        X.append(features)
        y.append(category)

        metadata.append(
            {
                "asset_id": asset_id,
                "category": category,
                "image": str(
                    image_path.relative_to(BASE_DIR)
                ).replace("\\", "/"),
                "split": split_name,
            }
        )

        print(
            f"[{index:03d}/{len(assets):03d}] "
            f"{asset_id:<28} "
            f"{category:<18} "
            f"HOG={features.shape[0]}"
        )

    X = np.array(X, dtype=np.float32)
    y = np.array(y)

    print()
    print(f"{split_name} samples: {len(X)}")
    print(f"Feature shape: {X.shape}")

    if len(X) > 0:
        print(
            f"Feature vector length: {X.shape[1]}"
        )

    return X, y, metadata


# ============================================================
# CATEGORY DISTRIBUTION
# ============================================================

def category_distribution(labels):
    result = {}

    for label in sorted(set(labels)):
        result[label] = int(
            np.sum(labels == label)
        )

    return result


# ============================================================
# VALIDATION
# ============================================================

def evaluate_validation(
    model,
    label_encoder,
    X_validation,
    y_validation,
):
    encoded_true = label_encoder.transform(
        y_validation
    )

    encoded_pred = model.predict(
        X_validation
    )

    accuracy = accuracy_score(
        encoded_true,
        encoded_pred,
    )

    precision, recall, f1, _ = (
        precision_recall_fscore_support(
            encoded_true,
            encoded_pred,
            average="weighted",
            zero_division=0,
        )
    )

    predicted_labels = label_encoder.inverse_transform(
        encoded_pred
    )

    report = classification_report(
        y_validation,
        predicted_labels,
        output_dict=True,
        zero_division=0,
    )

    return {
        "accuracy": float(accuracy),
        "precision_weighted": float(precision),
        "recall_weighted": float(recall),
        "f1_weighted": float(f1),
        "classification_report": report,
    }


# ============================================================
# TEST EVALUATION
# ============================================================

def evaluate_test(
    model,
    label_encoder,
    X_test,
    y_test,
    test_metadata,
):
    encoded_true = label_encoder.transform(
        y_test
    )

    encoded_pred = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        encoded_true,
        encoded_pred,
    )

    precision, recall, f1, _ = (
        precision_recall_fscore_support(
            encoded_true,
            encoded_pred,
            average="weighted",
            zero_division=0,
        )
    )

    predicted_labels = label_encoder.inverse_transform(
        encoded_pred
    )

    report = classification_report(
        y_test,
        predicted_labels,
        output_dict=True,
        zero_division=0,
    )

    cm = confusion_matrix(
        y_test,
        predicted_labels,
        labels=label_encoder.classes_,
    )

    predictions = []

    for index, metadata in enumerate(test_metadata):

        predictions.append(
            {
                "asset_id": metadata["asset_id"],
                "category": metadata["category"],
                "image": metadata["image"],
                "true_label": str(
                    y_test[index]
                ),
                "predicted_label": str(
                    predicted_labels[index]
                ),
                "correct": bool(
                    y_test[index]
                    == predicted_labels[index]
                ),
            }
        )

    prediction_output = {
        "model": "baseline_svm_v5",
        "experiment": "normalized_images_hog_svm",
        "dataset": "VietHeritage Classification Dataset V5",
        "split": "test",
        "count": len(predictions),
        "excluded_categories": sorted(
            EXCLUDED_CATEGORIES
        ),
        "input": "outputs/<asset_id>/normalized.png",
        "predictions": predictions,
    }

    with open(
        TEST_PREDICTIONS_FILE,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            prediction_output,
            f,
            ensure_ascii=False,
            indent=2,
        )

    return {
        "accuracy": float(accuracy),
        "precision_weighted": float(precision),
        "recall_weighted": float(recall),
        "f1_weighted": float(f1),
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "labels": label_encoder.classes_.tolist(),
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 72)
    print("VIETHERITAGE BASELINE AI - V5 TRAINING")
    print("=" * 72)

    print()
    print("Experiment:")
    print("RAW → Processing → NORMALIZED → HOG → SVM")

    print()
    print("Input:")
    print("outputs/<asset_id>/normalized.png")

    print()
    print(f"Image size: {IMAGE_SIZE}")
    print(
        f"HOG orientations: {HOG_ORIENTATIONS}"
    )
    print(
        f"HOG pixels/cell: {HOG_PIXELS_PER_CELL}"
    )
    print(
        f"HOG cells/block: {HOG_CELLS_PER_BLOCK}"
    )
    print(f"SVM kernel: {SVM_KERNEL}")
    print(f"SVM C: {SVM_C}")
    print(f"SVM gamma: {SVM_GAMMA}")
    print(
        f"SVM class weight: {SVM_CLASS_WEIGHT}"
    )
    print(f"Random state: {RANDOM_STATE}")

    # --------------------------------------------------------
    # LOAD SPLITS
    # --------------------------------------------------------

    print()
    print("[1/6] Loading existing splits...")

    train_data = load_split(
        TRAIN_FILE
    )

    validation_data = load_split(
        VALIDATION_FILE
    )

    test_data = load_split(
        TEST_FILE
    )

    print(
        f"Train:      {train_data['count']}"
    )

    print(
        f"Validation: {validation_data['count']}"
    )

    print(
        f"Test:       {test_data['count']}"
    )

    # --------------------------------------------------------
    # PREPARE TRAIN
    # --------------------------------------------------------

    print()
    print("[2/6] Preparing training data...")

    X_train, y_train, _ = prepare_dataset(
        train_data,
        "train",
    )

    # --------------------------------------------------------
    # PREPARE VALIDATION
    # --------------------------------------------------------

    print()
    print("[3/6] Preparing validation data...")

    X_validation, y_validation, _ = (
        prepare_dataset(
            validation_data,
            "validation",
        )
    )

    # --------------------------------------------------------
    # PREPARE TEST
    # --------------------------------------------------------

    print()
    print("[4/6] Preparing test data...")

    X_test, y_test, test_metadata = (
        prepare_dataset(
            test_data,
            "test",
        )
    )

    # --------------------------------------------------------
    # LABEL ENCODER
    # --------------------------------------------------------

    label_encoder = LabelEncoder()

    label_encoder.fit(
        np.concatenate(
            [
                y_train,
                y_validation,
                y_test,
            ]
        )
    )

    y_train_encoded = label_encoder.transform(
        y_train
    )

    print()
    print("Classes:")

    for index, label in enumerate(
        label_encoder.classes_
    ):
        print(
            f"  {index}: {label}"
        )

    # --------------------------------------------------------
    # TRAIN MODEL
    # --------------------------------------------------------

    print()
    print("[5/6] Training V5 SVM...")

    model = SVC(
        kernel=SVM_KERNEL,
        C=SVM_C,
        gamma=SVM_GAMMA,
        class_weight=SVM_CLASS_WEIGHT,
        probability=True,
        random_state=RANDOM_STATE,
    )

    model.fit(
        X_train,
        y_train_encoded,
    )

    print("Training completed.")

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    validation_result = evaluate_validation(
        model,
        label_encoder,
        X_validation,
        y_validation,
    )

    print()
    print("Validation results:")
    print(
        f"Accuracy:  {validation_result['accuracy']:.4f}"
    )
    print(
        f"Precision: {validation_result['precision_weighted']:.4f}"
    )
    print(
        f"Recall:    {validation_result['recall_weighted']:.4f}"
    )
    print(
        f"F1:        {validation_result['f1_weighted']:.4f}"
    )

    # --------------------------------------------------------
    # TEST
    # --------------------------------------------------------

    test_result = evaluate_test(
        model,
        label_encoder,
        X_test,
        y_test,
        test_metadata,
    )

    print()
    print("Test results:")
    print(
        f"Accuracy:  {test_result['accuracy']:.4f}"
    )
    print(
        f"Precision: {test_result['precision_weighted']:.4f}"
    )
    print(
        f"Recall:    {test_result['recall_weighted']:.4f}"
    )
    print(
        f"F1:        {test_result['f1_weighted']:.4f}"
    )

    # --------------------------------------------------------
    # SAVE MODEL
    # --------------------------------------------------------

    joblib.dump(
        model,
        MODEL_FILE,
    )

    joblib.dump(
        label_encoder,
        LABEL_ENCODER_FILE,
    )

    # --------------------------------------------------------
    # TRAINING REPORT
    # --------------------------------------------------------

    report = {
        "model": "baseline_svm_v5",
        "experiment": "normalized_images_hog_svm",
        "dataset": "VietHeritage Classification Dataset V5",

        "created_at": datetime.now().isoformat(),

        "input": {
            "type": "normalized",
            "path_template": (
                "outputs/<asset_id>/normalized.png"
            ),
        },

        "dataset_config": {
            "total_classification_assets": 123,
            "classes": label_encoder.classes_.tolist(),
            "excluded_categories": sorted(
                EXCLUDED_CATEGORIES
            ),
        },

        "splits": {
            "train": int(len(X_train)),
            "validation": int(
                len(X_validation)
            ),
            "test": int(len(X_test)),
            "seed": RANDOM_STATE,
        },

        "feature_extraction": {
            "image_size": list(IMAGE_SIZE),
            "method": "HOG",
            "orientations": HOG_ORIENTATIONS,
            "pixels_per_cell": list(
                HOG_PIXELS_PER_CELL
            ),
            "cells_per_block": list(
                HOG_CELLS_PER_BLOCK
            ),
            "feature_dimension": int(
                X_train.shape[1]
            ),
        },

        "model_config": {
            "algorithm": "SVM",
            "kernel": SVM_KERNEL,
            "C": SVM_C,
            "gamma": SVM_GAMMA,
            "class_weight": SVM_CLASS_WEIGHT,
            "probability": True,
            "random_state": RANDOM_STATE,
        },

        "class_distribution": {
            "train": category_distribution(
                y_train
            ),
            "validation": category_distribution(
                y_validation
            ),
            "test": category_distribution(
                y_test
            ),
        },

        "validation": validation_result,

        "test": test_result,

        "artifacts": {
            "model": str(
                MODEL_FILE.relative_to(BASE_DIR)
            ).replace("\\", "/"),
            "label_encoder": str(
                LABEL_ENCODER_FILE.relative_to(
                    BASE_DIR
                )
            ).replace("\\", "/"),
            "test_predictions": str(
                TEST_PREDICTIONS_FILE.relative_to(
                    BASE_DIR
                )
            ).replace("\\", "/"),
        },
    }

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            report,
            f,
            ensure_ascii=False,
            indent=2,
        )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("V5 TRAINING COMPLETE")
    print("=" * 72)

    print()
    print("Artifacts:")

    print(
        f"Model:          {MODEL_FILE}"
    )

    print(
        f"Label encoder:  {LABEL_ENCODER_FILE}"
    )

    print(
        f"Training report:{REPORT_FILE}"
    )

    print(
        f"Test predictions:{TEST_PREDICTIONS_FILE}"
    )

    print()
    print("V5 comparison baseline:")
    print(
        "V3 Test Accuracy = 31.58%"
    )
    print(
        f"V5 Test Accuracy = "
        f"{test_result['accuracy'] * 100:.2f}%"
    )


if __name__ == "__main__":
    main()