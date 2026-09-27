import os
import json
from datetime import datetime


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

CATALOG_FILE = os.path.join(
    BASE_DIR,
    "catalog",
    "catalog.json"
)


# ============================================================
# LOAD / SAVE
# ============================================================

def load_catalog():
    """
    Load catalog.json.
    """

    if not os.path.isfile(CATALOG_FILE):
        return {
            "assets": []
        }

    with open(
        CATALOG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_catalog(catalog):
    """
    Save catalog.json.
    """

    with open(
        CATALOG_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            catalog,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# TIMESTAMP
# ============================================================

def current_timestamp():
    """
    Return ISO 8601 timestamp.
    """

    return datetime.now().astimezone().isoformat(
        timespec="seconds"
    )


# ============================================================
# CREATE LINEAGE
# ============================================================

def build_lineage(asset):
    """
    Build processing lineage for one asset.

    The lineage describes how the raw asset was transformed
    through the VietHeritage processing pipeline.
    """

    asset_id = asset.get(
        "asset_id"
    )

    original = asset.get(
        "original",
        {}
    )

    processing = asset.get(
        "processing",
        {}
    )

    outputs = asset.get(
        "outputs",
        {}
    )

    quality = asset.get(
        "quality",
        {}
    )


    lineage = []


    # ========================================================
    # 1. RAW
    # ========================================================

    raw_path = original.get(
        "path"
    )

    lineage.append({

        "stage": "RAW",

        "status": "available"
        if raw_path
        else "missing",

        "input": None,

        "output": raw_path,

        "description":
            "Original raw image collected from dataset.",

        "timestamp": None
    })


    # ========================================================
    # 2. RESTORATION
    # ========================================================

    restored_path = outputs.get(
        "restored"
    )

    restored_status = processing.get(
        "restored",
        False
    )

    lineage.append({

        "stage": "RESTORATION",

        "status":
            "completed"
            if restored_status
            else "pending",

        "input": raw_path,

        "output": restored_path,

        "description":
            "Restore and enhance the original image.",

        "timestamp": None
    })


    # ========================================================
    # 3. CLEANING
    # ========================================================

    cleaned_path = outputs.get(
        "cleaned"
    )

    cleaning_available = bool(
        cleaned_path
    )

    lineage.append({

        "stage": "CLEANING",

        "status":
            "completed"
            if cleaning_available
            else "pending",

        "input":
            restored_path,

        "output":
            cleaned_path,

        "description":
            "Remove unwanted artifacts and prepare the image "
            "for downstream processing.",

        "timestamp": None
    })


    # ========================================================
    # 4. NORMALIZATION
    # ========================================================

    normalized_path = outputs.get(
        "normalized"
    )

    normalized_status = processing.get(
        "normalized",
        False
    )

    lineage.append({

        "stage": "NORMALIZATION",

        "status":
            "completed"
            if normalized_status
            else "pending",

        "input":
            cleaned_path,

        "output":
            normalized_path,

        "description":
            "Normalize visual characteristics for consistent "
            "downstream processing.",

        "timestamp": None
    })


    # ========================================================
    # 5. EDGE PROCESSING
    # ========================================================

    edges_path = outputs.get(
        "edges"
    )

    lineage.append({

        "stage": "EDGE_PROCESSING",

        "status":
            "completed"
            if edges_path
            else "pending",

        "input":
            normalized_path,

        "output":
            edges_path,

        "description":
            "Extract structural edge information from the "
            "normalized image.",

        "timestamp": None
    })


    # ========================================================
    # 6. SEGMENTATION
    # ========================================================

    segmented_path = outputs.get(
        "segmented"
    )

    mask_path = outputs.get(
        "mask"
    )

    segmentation_status = processing.get(
        "segmented",
        False
    )

    lineage.append({

        "stage": "SEGMENTATION",

        "status":
            "completed"
            if segmentation_status
            else "pending",

        "input":
            normalized_path,

        "output": {
            "segmented": segmented_path,
            "mask": mask_path
        },

        "description":
            "Separate the heritage pattern from the "
            "background.",

        "timestamp": None
    })


    # ========================================================
    # 7. VECTORIZATION
    # ========================================================

    svg_path = outputs.get(
        "svg"
    )

    vectorized_status = processing.get(
        "vectorized",
        False
    )

    lineage.append({

        "stage": "VECTORIZATION",

        "status":
            "completed"
            if vectorized_status
            else "pending",

        "input":
            mask_path,

        "output":
            svg_path,

        "description":
            "Convert the segmented pattern into a vector "
            "representation.",

        "timestamp": None
    })


    # ========================================================
    # 8. QUALITY EVALUATION
    # ========================================================

    quality_report = outputs.get(
        "quality_report"
    )

    quality_label = quality.get(
        "label"
    )

    quality_score = quality.get(
        "overall_score"
    )

    quality_status = (
        "completed"
        if quality_label is not None
        else "pending"
    )

    lineage.append({

        "stage": "QUALITY_EVALUATION",

        "status":
            quality_status,

        "input":
            normalized_path,

        "output":
            quality_report,

        "quality": {
            "label": quality_label,
            "score": quality_score
        },

        "description":
            "Evaluate technical quality and determine "
            "whether the asset is suitable for downstream use.",

        "timestamp": None
    })


    # ========================================================
    # 9. FINAL DATA STATE
    # ========================================================

    completed_stages = sum(
        1
        for item in lineage
        if item["status"] == "completed"
        or item["status"] == "available"
    )

    total_stages = len(
        lineage
    )

    if total_stages > 0:

        completion_ratio = round(
            completed_stages / total_stages,
            2
        )

    else:

        completion_ratio = 0.0


    final_state = {

        "completed_stages":
            completed_stages,

        "total_stages":
            total_stages,

        "completion_ratio":
            completion_ratio,

        "quality_label":
            quality_label,

        "quality_score":
            quality_score
    }


    return {
        "asset_id": asset_id,

        "created_at":
            current_timestamp(),

        "pipeline": [
            "RAW",
            "RESTORATION",
            "CLEANING",
            "NORMALIZATION",
            "EDGE_PROCESSING",
            "SEGMENTATION",
            "VECTORIZATION",
            "QUALITY_EVALUATION"
        ],

        "stages": lineage,

        "final_state": final_state
    }


# ============================================================
# UPDATE ONE ASSET
# ============================================================

def update_asset_lineage(asset):
    """
    Generate and attach lineage information to an asset.
    """

    asset["lineage"] = build_lineage(
        asset
    )

    return asset


# ============================================================
# UPDATE ENTIRE CATALOG
# ============================================================

def update_catalog_lineage():

    catalog = load_catalog()

    assets = catalog.get(
        "assets",
        []
    )

    for asset in assets:

        update_asset_lineage(
            asset
        )

    save_catalog(
        catalog
    )

    return catalog


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("VIETHERITAGE DATA LINEAGE")
    print("=" * 70)
    print()

    catalog = update_catalog_lineage()

    assets = catalog.get(
        "assets",
        []
    )

    print(
        f"Assets updated: {len(assets)}"
    )

    print()
    print(
        "Data lineage has been added to catalog.json."
    )

    print()
    print("=" * 70)