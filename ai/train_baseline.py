import json
import hashlib
from pathlib import Path

import cv2
import joblib
import numpy as np

from skimage.feature import hog
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

AI_READY_DIR = BASE_DIR / "ai_ready"
SPLITS_DIR = AI_READY_DIR / "splits"
IMAGES_DIR = AI_READY_DIR / "images"

MODEL_DIR = BASE_DIR / "ai" / "models"

TRAIN_FILE = SPLITS_DIR / "train.json"
VALIDATION_FILE = SPLITS_DIR / "validation.json"

MODEL_FILE = MODEL_DIR / "baseline_svm.joblib"
LABEL_ENCODER_FILE = MODEL_DIR / "label_encoder.joblib"
REPORT_FILE = MODEL_DIR / "training_report.json"


# ============================================================
# CONFIG
# ============================================================

IMAGE_SIZE = (128, 128)

HOG_ORIENTATIONS = 9
HOG_PIXELS_PER_CELL = (8, 8)
HOG_CELLS_PER_BLOCK = (2, 2)

RANDOM_STATE = 42


# ============================================================
# LOAD SPLIT
# ============================================================

def load_split(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Split file not found:\n{path}"
        )

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# LOAD IMAGE
# ============================================================

def load_image(image_path):
    """
    Resolve image path from split/manifest.

    Supports both:
    - ai_ready/images/...
    - images/...
    """

    image_path = Path(image_path)

    # Case 1:
    # Split stores:
    # ai_ready/images/category/file.png
    if image_path.parts and image_path.parts[0] == "ai_ready":
        full_path = BASE_DIR / image_path

    # Case 2:
    # Split stores:
    # images/category/file.png
    elif image_path.parts and image_path.parts[0] == "images":
        full_path = AI_READY_DIR / image_path

    # Case 3:
    # Fallback
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
# EXTRACT HOG FEATURES
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
# BUILD DATASET
# ============================================================

def build_dataset(split_data):

    X = []
    y = []
    asset_ids = []

    assets = split_data.get("assets", [])

    for item in assets:

        asset_id = item["asset_id"]
        category = item["category"]
        image_path = item["image"]

        image = load_image(image_path)

        features = extract_features(image)

        X.append(features)
        y.append(category)
        asset_ids.append(asset_id)

    if not X:
        raise RuntimeError(
            "No images found in split."
        )

    return (
        np.array(X),
        np.array(y),
        asset_ids
    )


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
    print("VIETHERITAGE BASELINE AI MODEL")
    print("=" * 70)

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\n[1/6] Loading dataset...")

    train_data = load_split(TRAIN_FILE)
    validation_data = load_split(VALIDATION_FILE)

    print(
        f"Train assets      : "
        f"{train_data.get('count', len(train_data.get('assets', [])))}"
    )

    print(
        f"Validation assets : "
        f"{validation_data.get('count', len(validation_data.get('assets', [])))}"
    )

    print("\n[2/6] Extracting HOG features...")

    X_train, y_train, train_ids = build_dataset(
        train_data
    )

    X_validation, y_validation, validation_ids = build_dataset(
        validation_data
    )

    print(f"Train feature shape      : {X_train.shape}")
    print(f"Validation feature shape : {X_validation.shape}")

    print("\n[3/6] Encoding categories...")

    label_encoder = LabelEncoder()

    y_train_encoded = label_encoder.fit_transform(
        y_train
    )

    unknown_validation = set(y_validation) - set(
        label_encoder.classes_
    )

    if unknown_validation:

        raise RuntimeError(
            "Validation contains categories "
            "not present in training set:\n"
            f"{sorted(unknown_validation)}"
        )

    y_validation_encoded = label_encoder.transform(
        y_validation
    )

    print(
        "Categories:"
    )

    for index, category in enumerate(
        label_encoder.classes_
    ):
        print(
            f"  {index}: {category}"
        )

    print("\n[4/6] Training SVM...")

    model = SVC(
        kernel="rbf",
        C=10,
        gamma="scale",
        probability=True,
        random_state=RANDOM_STATE
    )

    model.fit(
        X_train,
        y_train_encoded
    )

    print("Model training completed.")

    print("\n[5/6] Validation...")

    validation_predictions = model.predict(
        X_validation
    )

    validation_accuracy = accuracy_score(
        y_validation_encoded,
        validation_predictions
    )

    print(
        f"Validation accuracy : "
        f"{validation_accuracy:.4f}"
    )

    print("\n[6/6] Saving model...")

    joblib.dump(
        model,
        MODEL_FILE
    )

    joblib.dump(
        label_encoder,
        LABEL_ENCODER_FILE
    )

    report = {
        "model": {
            "name": "HOG + SVM",
            "algorithm": "Support Vector Machine",
            "kernel": "RBF"
        },
        "feature_extraction": {
            "method": "HOG",
            "image_size": list(IMAGE_SIZE),
            "orientations": HOG_ORIENTATIONS,
            "pixels_per_cell": list(
                HOG_PIXELS_PER_CELL
            ),
            "cells_per_block": list(
                HOG_CELLS_PER_BLOCK
            )
        },
        "training": {
            "samples": len(X_train),
            "feature_dimension": X_train.shape[1],
            "categories": list(
                label_encoder.classes_
            ),
            "category_distribution": (
                category_distribution(y_train)
            )
        },
        "validation": {
            "samples": len(X_validation),
            "accuracy": float(
                validation_accuracy
            ),
            "category_distribution": (
                category_distribution(y_validation)
            )
        },
        "assets": {
            "train": train_ids,
            "validation": validation_ids
        }
    }

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            report,
            f,
            ensure_ascii=False,
            indent=4
        )

    print("\n" + "=" * 70)
    print("BASELINE MODEL TRAINING COMPLETE")
    print("=" * 70)

    print(
        f"\nModel          : {MODEL_FILE}"
    )

    print(
        f"Label encoder  : {LABEL_ENCODER_FILE}"
    )

    print(
        f"Training report: {REPORT_FILE}"
    )

    print(
        f"\nValidation accuracy: "
        f"{validation_accuracy:.4f}"
    )


if __name__ == "__main__":
    main()