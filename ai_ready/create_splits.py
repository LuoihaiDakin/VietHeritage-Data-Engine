import os
import sys
import json
import random
import hashlib
from collections import Counter
from datetime import datetime


# ============================================================
# PROJECT ROOT
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if BASE_DIR not in sys.path:
    sys.path.insert(
        0,
        BASE_DIR
    )


# ============================================================
# PATHS
# ============================================================

AI_READY_DIR = os.path.join(
    BASE_DIR,
    "ai_ready"
)

MANIFEST_FILE = os.path.join(
    AI_READY_DIR,
    "manifest.json"
)

VALIDATION_REPORT = os.path.join(
    AI_READY_DIR,
    "dataset_report.json"
)

SPLITS_DIR = os.path.join(
    AI_READY_DIR,
    "splits"
)

TRAIN_FILE = os.path.join(
    SPLITS_DIR,
    "train.json"
)

VALIDATION_FILE = os.path.join(
    SPLITS_DIR,
    "validation.json"
)

TEST_FILE = os.path.join(
    SPLITS_DIR,
    "test.json"
)

SPLIT_REPORT_FILE = os.path.join(
    SPLITS_DIR,
    "split_report.json"
)


# ============================================================
# SPLIT CONFIGURATION
# ============================================================

SEED = 42

TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15
TEST_RATIO = 0.15


# ============================================================
# LOAD JSON
# ============================================================

def load_json(path):

    if not os.path.isfile(
        path
    ):
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(
            file
        )


# ============================================================
# SAVE JSON
# ============================================================

def save_json(
    path,
    data
):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# FILE HASH
# ============================================================

def calculate_hash(
    path
):

    sha256 = hashlib.sha256()

    with open(
        path,
        "rb"
    ) as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            sha256.update(
                chunk
            )

    return sha256.hexdigest()


# ============================================================
# VALIDATE RATIOS
# ============================================================

def validate_ratios():

    total = (
        TRAIN_RATIO
        + VALIDATION_RATIO
        + TEST_RATIO
    )

    if abs(
        total - 1.0
    ) > 0.0001:

        raise ValueError(
            "TRAIN_RATIO + "
            "VALIDATION_RATIO + "
            "TEST_RATIO must equal 1.0"
        )


# ============================================================
# CHECK DATASET VALIDATION
# ============================================================

def check_validation_report():

    if not os.path.isfile(
        VALIDATION_REPORT
    ):

        raise FileNotFoundError(
            "dataset_report.json not found. "
            "Run validate_dataset.py first."
        )

    report = load_json(
        VALIDATION_REPORT
    )

    status = report.get(
        "validation_status"
    )

    if status != "VALID":

        raise RuntimeError(
            "Dataset validation did not pass. "
            "Fix validation issues before creating splits."
        )

    return report


# ============================================================
# GET IMAGE PATH
# ============================================================

def get_absolute_image_path(
    asset
):

    image_path = asset.get(
        "image"
    )

    if not image_path:
        return None

    return os.path.join(
        BASE_DIR,
        image_path.replace(
            "/",
            os.sep
        )
    )


# ============================================================
# BUILD DUPLICATE GROUPS
# ============================================================

def build_duplicate_groups(
    assets
):

    hash_groups = {}

    for asset in assets:

        image_path = get_absolute_image_path(
            asset
        )

        if not image_path:
            continue

        if not os.path.isfile(
            image_path
        ):
            continue

        image_hash = calculate_hash(
            image_path
        )

        if image_hash not in hash_groups:

            hash_groups[
                image_hash
            ] = []

        hash_groups[
            image_hash
        ].append(
            asset
        )

    return hash_groups


# ============================================================
# GROUP DATA BY CATEGORY
# ============================================================

def group_by_category(
    assets
):

    categories = {}

    for asset in assets:

        category = asset.get(
            "category",
            "unknown"
        )

        if category not in categories:

            categories[
                category
            ] = []

        categories[
            category
        ].append(
            asset
        )

    return categories


# ============================================================
# SPLIT ONE CATEGORY
# ============================================================

def split_category(
    assets,
    rng
):

    assets = list(
        assets
    )

    rng.shuffle(
        assets
    )

    count = len(
        assets
    )

    # --------------------------------------------------------
    # Very small classes
    # --------------------------------------------------------

    if count == 1:

        return (
            assets,
            [],
            []
        )

    if count == 2:

        return (
            [assets[0]],
            [],
            [assets[1]]
        )

    # --------------------------------------------------------
    # Normal split
    # --------------------------------------------------------

    test_count = max(
        1,
        round(
            count * TEST_RATIO
        )
    )

    validation_count = max(
        1,
        round(
            count * VALIDATION_RATIO
        )
    )

    # Keep at least one training sample
    while (
        count
        - test_count
        - validation_count
        < 1
    ):

        if test_count > validation_count:

            test_count -= 1

        else:

            validation_count -= 1

    test_assets = assets[
        :test_count
    ]

    validation_assets = assets[
        test_count:
        test_count + validation_count
    ]

    train_assets = assets[
        test_count + validation_count:
    ]

    return (
        train_assets,
        validation_assets,
        test_assets
    )


# ============================================================
# BUILD SPLIT RECORD
# ============================================================

def build_split_record(
    asset,
    split_name
):

    quality = asset.get(
        "quality",
        {}
    )

    return {

        "asset_id":
            asset.get(
                "asset_id"
            ),

        "category":
            asset.get(
                "category"
            ),

        "image":
            asset.get(
                "image"
            ),

        "quality":
            {
                "label":
                    quality.get(
                        "label"
                    ),

                "overall_score":
                    quality.get(
                        "overall_score"
                    )
            },

        "split":
            split_name
    }


# ============================================================
# CREATE SPLITS
# ============================================================

def create_splits():

    print()
    print("=" * 70)
    print("VIETHERITAGE DATASET SPLIT")
    print("=" * 70)
    print()

    validate_ratios()

    # --------------------------------------------------------
    # Check validation
    # --------------------------------------------------------

    validation_report = (
        check_validation_report()
    )

    print(
        "Dataset validation : PASS"
    )

    # --------------------------------------------------------
    # Load manifest
    # --------------------------------------------------------

    manifest = load_json(
        MANIFEST_FILE
    )

    assets = manifest.get(
        "assets",
        []
    )

    if not assets:

        raise RuntimeError(
            "No AI-ready assets found in manifest."
        )

    print(
        f"AI-ready assets    : {len(assets)}"
    )

    # --------------------------------------------------------
    # Prepare directory
    # --------------------------------------------------------

    os.makedirs(
        SPLITS_DIR,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Duplicate check
    # --------------------------------------------------------

    duplicate_groups = (
        build_duplicate_groups(
            assets
        )
    )

    duplicate_groups = {
        image_hash: group
        for image_hash, group
        in duplicate_groups.items()
        if len(group) > 1
    }

    if duplicate_groups:

        raise RuntimeError(
            "Duplicate images detected. "
            "Resolve duplicates before splitting."
        )

    print(
        "Duplicate check    : PASS"
    )

    # --------------------------------------------------------
    # Group by category
    # --------------------------------------------------------

    categories = group_by_category(
        assets
    )

    print()
    print(
        "Categories:"
    )

    for category, category_assets in categories.items():

        print(
            f"  {category:<25} "
            f"{len(category_assets)}"
        )

    # --------------------------------------------------------
    # Deterministic random generator
    # --------------------------------------------------------

    rng = random.Random(
        SEED
    )

    train_assets = []
    validation_assets = []
    test_assets = []

    # --------------------------------------------------------
    # Stratified split
    # --------------------------------------------------------

    for category, category_assets in categories.items():

        (
            category_train,
            category_validation,
            category_test
        ) = split_category(
            category_assets,
            rng
        )

        train_assets.extend(
            category_train
        )

        validation_assets.extend(
            category_validation
        )

        test_assets.extend(
            category_test
        )

    # --------------------------------------------------------
    # Shuffle each final split
    # --------------------------------------------------------

    rng.shuffle(
        train_assets
    )

    rng.shuffle(
        validation_assets
    )

    rng.shuffle(
        test_assets
    )

    # ========================================================
    # BUILD RECORDS
    # ========================================================

    train_records = [

        build_split_record(
            asset,
            "train"
        )

        for asset in train_assets
    ]

    validation_records = [

        build_split_record(
            asset,
            "validation"
        )

        for asset in validation_assets
    ]

    test_records = [

        build_split_record(
            asset,
            "test"
        )

        for asset in test_assets
    ]

    # ========================================================
    # SAVE SPLITS
    # ========================================================

    save_json(
        TRAIN_FILE,
        {
            "dataset":
                "VietHeritage AI-Ready Dataset",

            "split":
                "train",

            "seed":
                SEED,

            "count":
                len(train_records),

            "assets":
                train_records
        }
    )

    save_json(
        VALIDATION_FILE,
        {
            "dataset":
                "VietHeritage AI-Ready Dataset",

            "split":
                "validation",

            "seed":
                SEED,

            "count":
                len(validation_records),

            "assets":
                validation_records
        }
    )

    save_json(
        TEST_FILE,
        {
            "dataset":
                "VietHeritage AI-Ready Dataset",

            "split":
                "test",

            "seed":
                SEED,

            "count":
                len(test_records),

            "assets":
                test_records
        }
    )

    # ========================================================
    # DISTRIBUTION
    # ========================================================

    def distribution(
        records
    ):

        return dict(
            Counter(
                record["category"]
                for record in records
            )
        )

    split_report = {

        "dataset":
            "VietHeritage AI-Ready Dataset",

        "created_at":
            datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),

        "random_seed":
            SEED,

        "ratios":

            {
                "train":
                    TRAIN_RATIO,

                "validation":
                    VALIDATION_RATIO,

                "test":
                    TEST_RATIO
            },

        "total_assets":
            len(assets),

        "splits":

            {
                "train":
                    {
                        "count":
                            len(
                                train_records
                            ),

                        "distribution":
                            distribution(
                                train_records
                            )
                    },

                "validation":
                    {
                        "count":
                            len(
                                validation_records
                            ),

                        "distribution":
                            distribution(
                                validation_records
                            )
                    },

                "test":
                    {
                        "count":
                            len(
                                test_records
                            ),

                        "distribution":
                            distribution(
                                test_records
                            )
                    }
            },

        "validation_status":
            validation_report.get(
                "validation_status"
            )
    }

    save_json(
        SPLIT_REPORT_FILE,
        split_report
    )

    # ========================================================
    # PRINT RESULTS
    # ========================================================

    print()
    print(
        "=" * 70
    )

    print(
        f"Train       : "
        f"{len(train_records)}"
    )

    print(
        f"Validation  : "
        f"{len(validation_records)}"
    )

    print(
        f"Test        : "
        f"{len(test_records)}"
    )

    print(
        f"Total       : "
        f"{len(train_records) + len(validation_records) + len(test_records)}"
    )

    print()
    print(
        "Train distribution:"
    )

    for category, count in distribution(
        train_records
    ).items():

        print(
            f"  {category:<25} {count}"
        )

    print()
    print(
        "Validation distribution:"
    )

    for category, count in distribution(
        validation_records
    ).items():

        print(
            f"  {category:<25} {count}"
        )

    print()
    print(
        "Test distribution:"
    )

    for category, count in distribution(
        test_records
    ).items():

        print(
            f"  {category:<25} {count}"
        )

    print()
    print(
        "Files created:"
    )

    print(
        f"  ai_ready/splits/train.json"
    )

    print(
        f"  ai_ready/splits/validation.json"
    )

    print(
        f"  ai_ready/splits/test.json"
    )

    print(
        f"  ai_ready/splits/split_report.json"
    )

    print()
    print(
        "=" * 70
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    create_splits()