import os
import sys
import json
import shutil
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
    sys.path.insert(0, BASE_DIR)


# ============================================================
# PATHS
# ============================================================

CATALOG_FILE = os.path.join(
    BASE_DIR,
    "catalog",
    "catalog.json"
)

AI_READY_DIR = os.path.join(
    BASE_DIR,
    "ai_ready"
)

IMAGES_DIR = os.path.join(
    AI_READY_DIR,
    "images"
)

MANIFEST_FILE = os.path.join(
    AI_READY_DIR,
    "manifest.json"
)


# ============================================================
# QUALITY POLICY
# ============================================================

ALLOWED_QUALITIES = {
    "GOOD",
    "ACCEPTABLE"
}


# ============================================================
# LOAD CATALOG
# ============================================================

def load_catalog():

    if not os.path.isfile(CATALOG_FILE):
        raise FileNotFoundError(
            f"Catalog not found: {CATALOG_FILE}"
        )

    with open(
        CATALOG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# PATH HELPERS
# ============================================================

def absolute_path(relative_path):

    if not relative_path:
        return None

    # Catalog currently stores paths like:
    # /outputs/dong_ho_001/normalized.png
    # /dataset/images/dong_ho/dong_ho_001.jpg

    clean_path = relative_path.replace("/", os.sep).lstrip(
        "\\/"
    )

    return os.path.join(
        BASE_DIR,
        clean_path
    )


def relative_path(path):

    return os.path.relpath(
        path,
        BASE_DIR
    ).replace(
        "\\",
        "/"
    )


# ============================================================
# QUALITY CHECK
# ============================================================

def get_quality_info(asset):

    quality = asset.get(
        "quality",
        {}
    )

    # Current catalog structure:
    #
    # "quality": {
    #     "quality": "GOOD",
    #     "overall_score": 83.5,
    #     ...
    # }
    #
    # Backward compatibility:
    # old structure used "label".

    label = quality.get("quality")

    if label is None:
        label = quality.get("label")

    overall_score = quality.get(
        "overall_score"
    )

    return label, overall_score


def get_processing_outputs(asset):

    # Current catalog structure:
    #
    # "processing_outputs": {
    #     "normalized": "/outputs/.../normalized.png",
    #     ...
    # }

    processing_outputs = asset.get(
        "processing_outputs",
        {}
    )

    # Backward compatibility with old structure.
    if not processing_outputs:
        processing_outputs = asset.get(
            "outputs",
            {}
        )

    return processing_outputs


def is_ai_ready(asset):

    label, _ = get_quality_info(asset)

    processing = asset.get(
        "processing",
        {}
    )

    required_stages = [
        "restored",
        "normalized",
        "segmented",
        "vectorized"
    ]

    processing_complete = all(
        processing.get(
            stage,
            False
        )
        for stage in required_stages
    )

    quality_passed = (
        label in ALLOWED_QUALITIES
    )

    processing_outputs = get_processing_outputs(
        asset
    )

    normalized_output = processing_outputs.get(
        "normalized"
    )

    normalized_exists = False

    if normalized_output:

        normalized_exists = os.path.isfile(
            absolute_path(
                normalized_output
            )
        )

    return (
        quality_passed
        and processing_complete
        and normalized_exists
    )


# ============================================================
# COPY NORMALIZED IMAGE
# ============================================================

def copy_normalized_image(asset):

    asset_id = asset.get(
        "asset_id"
    )

    category = asset.get(
        "category",
        "unknown"
    )

    # Sanitize category for Windows folder names
    invalid_chars = '<>:"/\\|?*'

    for char in invalid_chars:
        category = category.replace(char, "_")

    category = category.strip().strip(".")

    processing_outputs = get_processing_outputs(
        asset
    )

    normalized_output = processing_outputs.get(
        "normalized"
    )

    if not normalized_output:
        return None

    source_path = absolute_path(
        normalized_output
    )

    if not source_path:
        return None

    if not os.path.isfile(
        source_path
    ):
        return None

    # --------------------------------------------------------
    # Category directory
    # --------------------------------------------------------

    category_dir = os.path.join(
        IMAGES_DIR,
        category
    )

    os.makedirs(
        category_dir,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Preserve PNG format
    # --------------------------------------------------------

    destination_path = os.path.join(
        category_dir,
        f"{asset_id}.png"
    )

    shutil.copy2(
        source_path,
        destination_path
    )

    return destination_path


# ============================================================
# BUILD AI-READY RECORD
# ============================================================

def build_ai_ready_record(
    asset,
    exported_image
):

    asset_id = asset.get(
        "asset_id"
    )

    category = asset.get(
        "category"
    )

    original = asset.get(
        "original",
        {}
    )

    quality = asset.get(
        "quality",
        {}
    )

    processing = asset.get(
        "processing",
        {}
    )

    processing_outputs = get_processing_outputs(
        asset
    )

    lineage = asset.get(
        "lineage",
        {}
    )

    label, overall_score = get_quality_info(
        asset
    )

    return {

        "asset_id":
            asset_id,

        "category":
            category,

        "dataset_role":
            "ai_ready",

        "image":
            relative_path(
                exported_image
            ),

        "source": {
            "original":
                original.get(
                    "path"
                )
        },

        "refined_data": {

            "restored":
                processing_outputs.get(
                    "restored"
                ),

            "cleaned":
                processing_outputs.get(
                    "cleaned"
                ),

            "normalized":
                processing_outputs.get(
                    "normalized"
                ),

            "edges":
                processing_outputs.get(
                    "edges"
                ),

            "segmented":
                processing_outputs.get(
                    "segmented"
                ),

            "mask":
                processing_outputs.get(
                    "mask"
                ),

            "vectorized":
                processing_outputs.get(
                    "svg"
                )
        },

        "quality": {

            "label":
                label,

            "overall_score":
                overall_score,

            "brightness":
                quality.get(
                    "brightness"
                ),

            "contrast":
                quality.get(
                    "contrast"
                ),

            "sharpness":
                quality.get(
                    "sharpness"
                ),

            "resolution":
                quality.get(
                    "resolution"
                )
        },

        "processing":
            processing,

        "lineage":
            lineage.get(
                "pipeline",
                []
            ),

        "ai_ready":
            True
    }


# ============================================================
# EXPORT
# ============================================================

def export_ai_ready():

    print()
    print("=" * 70)
    print("VIETHERITAGE AI-READY DATASET EXPORT")
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # Load catalog
    # --------------------------------------------------------

    catalog = load_catalog()

    assets = catalog.get(
        "assets",
        []
    )

    # --------------------------------------------------------
    # Create directories
    # --------------------------------------------------------

    os.makedirs(
        AI_READY_DIR,
        exist_ok=True
    )

    os.makedirs(
        IMAGES_DIR,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    total = len(
        assets
    )

    ready_assets = []

    rejected_assets = []

    pending_assets = []

    # --------------------------------------------------------
    # Quality Gate
    # --------------------------------------------------------

    for asset in assets:

        asset_id = asset.get(
            "asset_id"
        )

        label, overall_score = get_quality_info(
            asset
        )

        # ====================================================
        # PENDING
        # ====================================================

        if label is None:

            pending_assets.append(
                {
                    "asset_id":
                        asset_id,

                    "reason":
                        "Quality evaluation unavailable."
                }
            )

            print(
                f"[PENDING] {asset_id:<30} "
                f"quality unavailable"
            )

            continue

        # ====================================================
        # QUALITY GATE
        # ====================================================

        if is_ai_ready(
            asset
        ):

            exported_image = (
                copy_normalized_image(
                    asset
                )
            )

            if exported_image is None:

                pending_assets.append(
                    {
                        "asset_id":
                            asset_id,

                        "reason":
                            "Normalized image file not found."
                    }
                )

                print(
                    f"[PENDING] {asset_id:<30} "
                    f"normalized image missing"
                )

                continue

            ready_assets.append(
                build_ai_ready_record(
                    asset,
                    exported_image
                )
            )

            print(
                f"[AI-READY] {asset_id:<28} "
                f"{label:<12} "
                f"score="
                f"{overall_score}"
            )

        # ====================================================
        # REJECTED
        # ====================================================

        else:

            rejected_assets.append(
                {
                    "asset_id":
                        asset_id,

                    "quality":
                        label,

                    "overall_score":
                        overall_score,

                    "reason":
                        "Does not pass AI quality gate."
                }
            )

            print(
                f"[REJECTED] {asset_id:<28} "
                f"{label:<12} "
                f"score="
                f"{overall_score}"
            )

    # ========================================================
    # MANIFEST
    # ========================================================

    manifest = {

        "dataset_name":
            "VietHeritage AI-Ready Dataset",

        "version":
            "1.0",

        "created_at":
            datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),

        "description":
            (
                "Quality-controlled dataset generated "
                "from the VietHeritage Data Engine."
            ),

        "pipeline":
            [
                "RAW",
                "RESTORATION",
                "CLEANING",
                "NORMALIZATION",
                "EDGE_PROCESSING",
                "SEGMENTATION",
                "VECTORIZATION",
                "QUALITY_EVALUATION",
                "AI_READY_EXPORT"
            ],

        "quality_policy": {

            "accepted_labels":
                sorted(
                    ALLOWED_QUALITIES
                ),

            "rejected_label":
                "POOR",

            "pending":
                "Assets without quality evaluation "
                "are excluded."
        },

        "statistics": {

            "total_catalog_assets":
                total,

            "ai_ready":
                len(
                    ready_assets
                ),

            "rejected":
                len(
                    rejected_assets
                ),

            "pending":
                len(
                    pending_assets
                )
        },

        "assets":
            ready_assets,

        "rejected_assets":
            rejected_assets,

        "pending_assets":
            pending_assets
    }

    # ========================================================
    # SAVE MANIFEST
    # ========================================================

    with open(
        MANIFEST_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            manifest,
            file,
            indent=4,
            ensure_ascii=False
        )

    # ========================================================
    # RESULTS
    # ========================================================

    print()

    print(
        f"Catalog assets : {total}"
    )

    print(
        f"AI-ready       : "
        f"{len(ready_assets)}"
    )

    print(
        f"Rejected       : "
        f"{len(rejected_assets)}"
    )

    print(
        f"Pending        : "
        f"{len(pending_assets)}"
    )

    print()

    print(
        "Manifest saved:"
    )

    print(
        f"  {relative_path(MANIFEST_FILE)}"
    )

    print()

    print(
        "Images exported:"
    )

    print(
        f"  {relative_path(IMAGES_DIR)}"
    )

    print()

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    export_ai_ready()