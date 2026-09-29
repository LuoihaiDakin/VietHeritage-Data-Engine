import json
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

MODEL_DIR = BASE_DIR / "ai" / "models"

TRAIN_FILE = SPLITS_DIR / "train.json"
VALIDATION_FILE = SPLITS_DIR / "validation.json"

# ------------------------------------------------------------
# V3 model files
# ------------------------------------------------------------

MODEL_FILE = MODEL_DIR / "baseline_svm_v3.joblib"

LABEL_ENCODER_FILE = (
    MODEL_DIR / "label_encoder_v3.joblib"
)

REPORT_FILE = (
    MODEL_DIR / "training_report_v3.json"
)


# ============================================================
# CONFIG
# ============================================================

IMAGE_SIZE = (128, 128)

HOG_ORIENTATIONS = 9

HOG_PIXELS_PER_CELL = (
    8,
    8
)

HOG_CELLS_PER_BLOCK = (
    2,
    2
)

RANDOM_STATE = 42


# ============================================================
# DATASET POLICY
# ============================================================

DATASET_NAME = (
    "VietHeritage Classification Dataset V3"
)

SOURCE_MANIFEST = (
    "ai_ready/classification_manifest.json"
)

EXCLUDED_CATEGORIES = {
    "other",
    "uploaded"
}


# ============================================================
# LOAD SPLIT
# ============================================================

def load_split(path):

    if not path.exists():

        raise FileNotFoundError(
            f"Split file not found:\n{path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# LOAD IMAGE
# ============================================================

def load_image(image_path):

    """
    Resolve image path from split/manifest.

    Supports:
    - ai_ready/images/...
    - images/...
    """

    image_path = Path(
        image_path
    )

    # --------------------------------------------------------
    # Case 1:
    # ai_ready/images/category/file.png
    # --------------------------------------------------------

    if (
        image_path.parts
        and image_path.parts[0] == "ai_ready"
    ):

        full_path = (
            BASE_DIR / image_path
        )

    # --------------------------------------------------------
    # Case 2:
    # images/category/file.png
    # --------------------------------------------------------

    elif (
        image_path.parts
        and image_path.parts[0] == "images"
    ):

        full_path = (
            AI_READY_DIR / image_path
        )

    # --------------------------------------------------------
    # Case 3:
    # Fallback
    # --------------------------------------------------------

    else:

        full_path = (
            AI_READY_DIR / image_path
        )

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

    return features.astype(
        np.float32
    )


# ============================================================
# BUILD DATASET
# ============================================================

def build_dataset(split_data):

    X = []
    y = []
    asset_ids = []

    assets = split_data.get(
        "assets",
        []
    )

    excluded_count = 0

    for item in assets:

        asset_id = item["asset_id"]
        category = item["category"]
        image_path = item["image"]

        # ----------------------------------------------------
        # Safety check:
        # classification splits should already contain only
        # the six intended classes.
        # ----------------------------------------------------

        if category in EXCLUDED_CATEGORIES:

            excluded_count += 1

            continue

        image = load_image(
            image_path
        )

        features = extract_features(
            image
        )

        X.append(
            features
        )

        y.append(
            category
        )

        asset_ids.append(
            asset_id
        )

    if not X:

        raise RuntimeError(
            "No usable images found in split."
        )

    return (
        np.array(X),
        np.array(y),
        asset_ids,
        excluded_count
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
        "VIETHERITAGE BASELINE AI MODEL - V3"
    )
    print("=" * 70)

    print("\nExperiment:")

    print(
        "  Dataset       : "
        "Classification Dataset V3"
    )

    print(
        "  Feature       : HOG"
    )

    print(
        "  Classifier    : SVM RBF"
    )

    print(
        "  Class balance : balanced"
    )

    print(
        "  Classes       : 6"
    )

    print(
        "  Excluded      : other, uploaded"
    )

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================
    # 1. LOAD DATASET
    # ========================================================

    print(
        "\n[1/6] Loading dataset..."
    )

    train_data = load_split(
        TRAIN_FILE
    )

    validation_data = load_split(
        VALIDATION_FILE
    )

    print(
        f"Train assets      : "
        f"{train_data.get('count', len(train_data.get('assets', [])))}"
    )

    print(
        f"Validation assets : "
        f"{validation_data.get('count', len(validation_data.get('assets', [])))}"
    )

    # ========================================================
    # 2. FEATURE EXTRACTION
    # ========================================================

    print(
        "\n[2/6] Extracting HOG features..."
    )

    (
        X_train,
        y_train,
        train_ids,
        train_excluded
    ) = build_dataset(
        train_data
    )

    (
        X_validation,
        y_validation,
        validation_ids,
        validation_excluded
    ) = build_dataset(
        validation_data
    )

    print(
        f"Train feature shape      : "
        f"{X_train.shape}"
    )

    print(
        f"Validation feature shape : "
        f"{X_validation.shape}"
    )

    print(
        f"Excluded from training   : "
        f"{train_excluded}"
    )

    print(
        f"Excluded from validation : "
        f"{validation_excluded}"
    )

    # ========================================================
    # 3. ENCODE CATEGORIES
    # ========================================================

    print(
        "\n[3/6] Encoding categories..."
    )

    label_encoder = LabelEncoder()

    y_train_encoded = (
        label_encoder.fit_transform(
            y_train
        )
    )

    unknown_validation = (
        set(y_validation)
        - set(
            label_encoder.classes_
        )
    )

    if unknown_validation:

        raise RuntimeError(
            "Validation contains categories "
            "not present in training set:\n"
            f"{sorted(unknown_validation)}"
        )

    y_validation_encoded = (
        label_encoder.transform(
            y_validation
        )
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

    # ========================================================
    # 4. TRAIN SVM
    # ========================================================

    print(
        "\n[4/6] Training SVM..."
    )

    model = SVC(
        kernel="rbf",

        C=10,

        gamma="scale",

        class_weight="balanced",

        probability=True,

        random_state=RANDOM_STATE
    )

    model.fit(
        X_train,
        y_train_encoded
    )

    print(
        "Model training completed."
    )

    # ========================================================
    # 5. VALIDATION
    # ========================================================

    print(
        "\n[5/6] Validation..."
    )

    validation_predictions = (
        model.predict(
            X_validation
        )
    )

    validation_accuracy = (
        accuracy_score(
            y_validation_encoded,
            validation_predictions
        )
    )

    print(
        f"Validation accuracy : "
        f"{validation_accuracy:.4f}"
    )

    # ========================================================
    # 6. SAVE MODEL
    # ========================================================

    print(
        "\n[6/6] Saving model..."
    )

    joblib.dump(
        model,
        MODEL_FILE
    )

    joblib.dump(
        label_encoder,
        LABEL_ENCODER_FILE
    )

    # ========================================================
    # TRAINING REPORT
    # ========================================================

    report = {

        "experiment": {

            "version":
                "v3",

            "purpose":
                (
                    "Evaluate HOG + SVM baseline "
                    "using a cleaned six-class "
                    "classification taxonomy."
                )
        },

        "dataset": {

            "name":
                DATASET_NAME,

            "source_manifest":
                SOURCE_MANIFEST,

            "train_split":
                "ai_ready/splits/train.json",

            "validation_split":
                "ai_ready/splits/validation.json"
        },

        "model": {

            "name":
                "HOG + SVM",

            "algorithm":
                "Support Vector Machine",

            "kernel":
                "RBF",

            "C":
                10,

            "gamma":
                "scale",

            "class_weight":
                "balanced",

            "probability":
                True
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
                )
        },

        "dataset_policy": {

            "excluded_categories":
                sorted(
                    EXCLUDED_CATEGORIES
                ),

            "reason":
                (
                    "other and uploaded are "
                    "retained in the broader "
                    "AI-ready dataset but are "
                    "not used as classifier classes "
                    "in V3."
                )
        },

        "training": {

            "samples":
                len(X_train),

            "feature_dimension":
                X_train.shape[1],

            "categories":
                list(
                    label_encoder.classes_
                ),

            "category_distribution":
                category_distribution(
                    y_train
                ),

            "excluded_assets":
                train_excluded,

            "asset_ids":
                train_ids
        },

        "validation": {

            "samples":
                len(
                    X_validation
                ),

            "accuracy":
                float(
                    validation_accuracy
                ),

            "category_distribution":
                category_distribution(
                    y_validation
                ),

            "excluded_assets":
                validation_excluded,

            "asset_ids":
                validation_ids
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

    # ========================================================
    # SUMMARY
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "BASELINE MODEL V3 TRAINING COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"\nModel          : "
        f"{MODEL_FILE}"
    )

    print(
        f"Label encoder  : "
        f"{LABEL_ENCODER_FILE}"
    )

    print(
        f"Training report: "
        f"{REPORT_FILE}"
    )

    print(
        f"\nTraining samples: "
        f"{len(X_train)}"
    )

    print(
        f"Categories      : "
        f"{len(label_encoder.classes_)}"
    )

    print(
        f"Validation accuracy: "
        f"{validation_accuracy:.4f}"
    )


if __name__ == "__main__":

    main()