import json
from pathlib import Path
from PIL import Image


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_DIR = PROJECT_ROOT / "dataset" / "images"
CATALOG_FILE = PROJECT_ROOT / "catalog" / "catalog.json"


# ============================================================
# CONFIGURATION
# ============================================================

VALID_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp"
}

VALID_CLASSES = {
    "dong_ho",
    "phuong",
    "rong_viet_nam",
    "sen"
}


# ============================================================
# HELPERS
# ============================================================

def get_file_format(path: Path):
    return path.suffix.lower().replace(".", "").upper()


def generate_asset_id(category, image_path, used_ids):
    """
    Keep the original filename-based ID whenever possible.

    If two files have the same stem but different extensions,
    append the extension to make the ID unique.

    Examples:
        rong_viet_nam_019.jpg
            -> rong_viet_nam_019

        phuong_006.jpg
            -> phuong_006_jpg

        phuong_006.webp
            -> phuong_006_webp
    """

    base_id = image_path.stem

    if base_id not in used_ids:
        return base_id

    extension = image_path.suffix.lower().replace(".", "")

    return f"{base_id}_{extension}"


# ============================================================
# BUILD ASSET
# ============================================================

def build_asset(category, image_path, asset_id):

    try:

        with Image.open(image_path) as image:

            width, height = image.size

            file_format = (
                image.format
                or get_file_format(image_path)
            )

        size_bytes = image_path.stat().st_size

    except Exception as error:

        print(
            f"[ERROR] Cannot read image: "
            f"{image_path} -> {error}"
        )

        return None

    relative_path = image_path.relative_to(PROJECT_ROOT)

    asset = {

        "asset_id": asset_id,

        "category": category,

        "filename": image_path.name,

        "source": {
            "type": "dataset",
            "name": image_path.name
        },

        "original": {

            "path": str(relative_path).replace("\\", "/"),

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

    return asset


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("VIETHERITAGE DATASET -> CATALOG V5")
    print("=" * 70)

    if not DATASET_DIR.exists():

        print()

        print("[ERROR] Dataset directory not found:")

        print(DATASET_DIR)

        return

    print()

    print(f"Dataset: {DATASET_DIR}")

    print(f"Catalog: {CATALOG_FILE}")

    assets = []

    total_images = 0
    used_ids = set()

    print()

    print("Scanning dataset...")

    print("-" * 70)

    for category in sorted(VALID_CLASSES):

        category_dir = DATASET_DIR / category

        if not category_dir.exists():

            print(
                f"[WARNING] Missing category folder: "
                f"{category}"
            )

            continue

        files = sorted(
            [
                path
                for path in category_dir.iterdir()
                if (
                    path.is_file()
                    and path.suffix.lower()
                    in VALID_EXTENSIONS
                )
            ],
            key=lambda path: path.name.lower()
        )

        print(
            f"{category:<20} {len(files):>3} images"
        )

        for image_path in files:

            # IMPORTANT:
            # Asset ID comes directly from filename.
            #
            # Example:
            # rong_viet_nam_019.jpg
            # -> rong_viet_nam_019

            asset_id = generate_asset_id(
                category,
                image_path,
                used_ids
            )

            used_ids.add(asset_id)

            asset = build_asset(
                category,
                image_path,
                asset_id
            )

            if asset is not None:

                assets.append(asset)

                total_images += 1

    # ========================================================
    # CHECK DUPLICATE ASSET IDS
    # ========================================================

    asset_ids = [
        asset["asset_id"]
        for asset in assets
    ]

    duplicate_ids = sorted(
        {
            asset_id
            for asset_id in asset_ids
            if asset_ids.count(asset_id) > 1
        }
    )

    if duplicate_ids:

        print()

        print("=" * 70)

        print("[ERROR] DUPLICATE ASSET IDS")

        print("=" * 70)

        for asset_id in duplicate_ids:

            print(f"  {asset_id}")

        print()

        print(
            "Catalog was NOT written."
        )

        return

    # ========================================================
    # BUILD CATALOG
    # ========================================================

    catalog = {

        "assets": assets
    }

    CATALOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

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

    # ========================================================
    # SUMMARY
    # ========================================================

    print()

    print("=" * 70)

    print("CATALOG V5 CREATED")

    print("=" * 70)

    print()

    print(
        f"Total assets: {total_images}"
    )

    print()

    print("Class distribution:")

    for category in sorted(VALID_CLASSES):

        count = sum(

            1

            for asset in assets

            if asset["category"] == category
        )

        print(
            f"  {category:<20} {count:>3}"
        )

    print()

    print(
        "Asset IDs are now based directly "
        "on filenames."
    )

    print()

    print("Catalog saved to:")

    print(CATALOG_FILE)

    print()

    print("=" * 70)


if __name__ == "__main__":

    main()