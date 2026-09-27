import json
import os
from typing import Optional


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CATALOG_DIR = os.path.join(
    BASE_DIR,
    "catalog"
)

CATALOG_FILE = os.path.join(
    CATALOG_DIR,
    "catalog.json"
)


# ============================================================
# INITIALIZATION
# ============================================================

def ensure_catalog_exists():
    """
    Make sure the catalog directory and catalog.json exist.
    """

    os.makedirs(CATALOG_DIR, exist_ok=True)

    if not os.path.exists(CATALOG_FILE):
        with open(
            CATALOG_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                {"assets": []},
                file,
                indent=4,
                ensure_ascii=False
            )


# ============================================================
# LOAD / SAVE
# ============================================================

def load_catalog():
    """
    Load the entire catalog from catalog.json.
    """

    ensure_catalog_exists()

    try:
        with open(
            CATALOG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

    except (json.JSONDecodeError, OSError):
        data = {
            "assets": []
        }

    if "assets" not in data:
        data["assets"] = []

    return data


def save_catalog(data):
    """
    Save catalog data to catalog.json.
    """

    ensure_catalog_exists()

    with open(
        CATALOG_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# ASSET ID
# ============================================================

def generate_asset_id(category: str) -> str:
    """
    Generate the next available asset ID.

    Example:

        dong_ho_001
        dong_ho_002
        dong_ho_003
    """

    catalog = load_catalog()

    prefix = category.strip().lower()

    existing_ids = []

    for asset in catalog["assets"]:

        asset_id = asset.get("asset_id", "")

        if asset_id.startswith(prefix + "_"):

            existing_ids.append(asset_id)

    next_number = 1

    while True:

        candidate = f"{prefix}_{next_number:03d}"

        if candidate not in existing_ids:
            return candidate

        next_number += 1


# ============================================================
# CREATE ASSET
# ============================================================

def create_asset(
    category: str,
    filename: str,
    path: str,
    width: int,
    height: int,
    file_format: str,
    size_bytes: int,
    source_type: str = "uploaded",
    source_name: Optional[str] = None
):
    """
    Create a new asset record and save it to the catalog.
    """

    catalog = load_catalog()

    asset_id = generate_asset_id(category)

    asset = {
        "asset_id": asset_id,

        "category": category,

        "filename": filename,

        "source": {
            "type": source_type,
            "name": source_name or filename
        },

        "original": {
            "path": path,
            "width": width,
            "height": height,
            "format": file_format,
            "size_bytes": size_bytes
        },

        "processing": {
            "preprocessed": False,
            "restored": False,
            "normalized": False,
            "segmented": False,
            "vectorized": False
        },

        "quality": {
            "brightness": None,
            "contrast": None,
            "sharpness": None,
            "resolution": None,
            "overall_score": None,
            "label": None
        },

        "outputs": {}
    }

    catalog["assets"].append(asset)

    save_catalog(catalog)

    return asset


# ============================================================
# GET ALL ASSETS
# ============================================================

def get_all_assets():
    """
    Return all assets in the catalog.
    """

    catalog = load_catalog()

    return catalog["assets"]


# ============================================================
# GET ASSET BY ID
# ============================================================

def get_asset(asset_id: str):
    """
    Find an asset by asset_id.

    Returns:
        asset dictionary
        or None if not found
    """

    catalog = load_catalog()

    for asset in catalog["assets"]:

        if asset.get("asset_id") == asset_id:
            return asset

    return None


# ============================================================
# UPDATE ASSET
# ============================================================

def update_asset(
    asset_id: str,
    updates: dict
):
    """
    Update an existing asset.

    Example:

        update_asset(
            "dong_ho_001",
            {
                "processing": {
                    "preprocessed": True
                }
            }
        )
    """

    catalog = load_catalog()

    for index, asset in enumerate(catalog["assets"]):

        if asset.get("asset_id") == asset_id:

            asset.update(updates)

            catalog["assets"][index] = asset

            save_catalog(catalog)

            return asset

    return None


# ============================================================
# UPDATE PROCESSING STATUS
# ============================================================

def update_processing_status(
    asset_id: str,
    stage: str,
    status: bool = True
):
    """
    Update one processing stage.

    Example:

        update_processing_status(
            "dong_ho_001",
            "restored",
            True
        )
    """

    catalog = load_catalog()

    for asset in catalog["assets"]:

        if asset.get("asset_id") == asset_id:

            if "processing" not in asset:
                asset["processing"] = {}

            asset["processing"][stage] = status

            save_catalog(catalog)

            return asset

    return None


# ============================================================
# UPDATE QUALITY
# ============================================================

def update_quality(
    asset_id: str,
    brightness=None,
    contrast=None,
    sharpness=None,
    resolution=None,
    overall_score=None,
    label=None
):
    """
    Update quality evaluation results.
    """

    catalog = load_catalog()

    for asset in catalog["assets"]:

        if asset.get("asset_id") == asset_id:

            if "quality" not in asset:
                asset["quality"] = {}

            if brightness is not None:
                asset["quality"]["brightness"] = brightness

            if contrast is not None:
                asset["quality"]["contrast"] = contrast

            if sharpness is not None:
                asset["quality"]["sharpness"] = sharpness

            if resolution is not None:
                asset["quality"]["resolution"] = resolution

            if overall_score is not None:
                asset["quality"]["overall_score"] = overall_score

            if label is not None:
                asset["quality"]["label"] = label

            save_catalog(catalog)

            return asset

    return None


# ============================================================
# UPDATE OUTPUT
# ============================================================

def update_output(
    asset_id: str,
    output_name: str,
    output_path: str
):
    """
    Store the path of a generated processing output.

    Example:

        update_output(
            "dong_ho_001",
            "restored",
            "outputs/dong_ho_001/restored.png"
        )
    """

    catalog = load_catalog()

    for asset in catalog["assets"]:

        if asset.get("asset_id") == asset_id:

            if "outputs" not in asset:
                asset["outputs"] = {}

            asset["outputs"][output_name] = output_path

            save_catalog(catalog)

            return asset

    return None


# ============================================================
# DELETE ASSET
# ============================================================

def delete_asset(asset_id: str):
    """
    Delete an asset from the catalog.

    Note:
    This only removes the catalog record.
    It does NOT delete the actual image file.
    """

    catalog = load_catalog()

    original_count = len(catalog["assets"])

    catalog["assets"] = [
        asset
        for asset in catalog["assets"]
        if asset.get("asset_id") != asset_id
    ]

    if len(catalog["assets"]) == original_count:
        return False

    save_catalog(catalog)

    return True


# ============================================================
# SEARCH ASSETS
# ============================================================

def search_assets(
    query: Optional[str] = None,
    category: Optional[str] = None,
    quality: Optional[str] = None
):
    """
    Search/filter assets in the catalog.
    """

    assets = get_all_assets()

    results = []

    for asset in assets:

        # --------------------------------------------
        # QUERY
        # --------------------------------------------

        if query:

            query_lower = query.lower()

            searchable_text = " ".join([
                str(asset.get("asset_id", "")),
                str(asset.get("filename", "")),
                str(asset.get("category", "")),
            ]).lower()

            if query_lower not in searchable_text:
                continue

        # --------------------------------------------
        # CATEGORY
        # --------------------------------------------

        if category:

            if asset.get("category", "").lower() != category.lower():
                continue

        # --------------------------------------------
        # QUALITY
        # --------------------------------------------

        if quality:

            asset_quality = (
                asset
                .get("quality", {})
                .get("label")
            )

            if not asset_quality:
                continue

            if asset_quality.lower() != quality.lower():
                continue

        results.append(asset)

    return results


# ============================================================
# CATALOG STATISTICS
# ============================================================

def get_catalog_statistics():
    """
    Return basic statistics about the dataset.
    """

    assets = get_all_assets()

    total = len(assets)

    processed = 0
    good = 0
    acceptable = 0
    poor = 0

    for asset in assets:

        processing = asset.get(
            "processing",
            {}
        )

        if all([
            processing.get("preprocessed", False),
            processing.get("restored", False),
            processing.get("normalized", False),
            processing.get("segmented", False),
            processing.get("vectorized", False)
        ]):
            processed += 1

        label = (
            asset
            .get("quality", {})
            .get("label")
        )

        if label == "GOOD":
            good += 1

        elif label == "ACCEPTABLE":
            acceptable += 1

        elif label == "POOR":
            poor += 1

    return {
        "total_assets": total,
        "processed_assets": processed,
        "good": good,
        "acceptable": acceptable,
        "poor": poor
    }


# ============================================================
# INITIALIZE CATALOG
# ============================================================

ensure_catalog_exists()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("VIETHERITAGE CATALOG MANAGER")
    print("=" * 60)

    assets = get_all_assets()

    print(f"Total assets: {len(assets)}")

    statistics = get_catalog_statistics()

    print()
    print("Statistics:")
    print(statistics)

    print()
    print(f"Catalog file:")
    print(CATALOG_FILE)