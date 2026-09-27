import os
import sys
import cv2


# ============================================================
# PROJECT ROOT
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# Add project root to Python import path
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


from catalog.catalog_manager import (
    get_all_assets,
    create_asset
)


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_IMAGES_DIR = os.path.join(
    BASE_DIR,
    "dataset",
    "images"
)

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}


# ============================================================
# HELPERS
# ============================================================

def get_file_format(filename):
    """
    Return file extension without the dot.
    """

    extension = os.path.splitext(
        filename
    )[1].lower()

    return extension.replace(".", "")


def is_image_file(filename):
    """
    Check whether a file is a supported image.
    """

    extension = os.path.splitext(
        filename
    )[1].lower()

    return extension in SUPPORTED_EXTENSIONS


def get_existing_paths():
    """
    Get all image paths already present in the catalog.
    """

    assets = get_all_assets()

    paths = set()

    for asset in assets:

        original = asset.get(
            "original",
            {}
        )

        path = original.get("path")

        if path:
            paths.add(
                os.path.normpath(path)
            )

    return paths


# ============================================================
# INDEX ONE IMAGE
# ============================================================

def index_image(
    image_path,
    category,
    existing_paths
):
    """
    Read one image and add it to the catalog.
    """

    filename = os.path.basename(
        image_path
    )

    relative_path = os.path.relpath(
        image_path,
        BASE_DIR
    )

    relative_path = relative_path.replace(
        "\\",
        "/"
    )

    normalized_path = os.path.normpath(
        relative_path
    )

    # --------------------------------------------------------
    # Prevent duplicate assets
    # --------------------------------------------------------

    if normalized_path in existing_paths:

        print(
            f"[SKIP] Already indexed: {filename}"
        )

        return None

    # --------------------------------------------------------
    # Read image
    # --------------------------------------------------------

    image = cv2.imread(
        image_path
    )

    if image is None:

        print(
            f"[ERROR] Cannot read image: {image_path}"
        )

        return None

    # --------------------------------------------------------
    # Dimensions
    # --------------------------------------------------------

    height, width = image.shape[:2]

    # --------------------------------------------------------
    # File information
    # --------------------------------------------------------

    file_size = os.path.getsize(
        image_path
    )

    file_format = get_file_format(
        filename
    )

    # --------------------------------------------------------
    # Create catalog asset
    # --------------------------------------------------------

    asset = create_asset(
        category=category,
        filename=filename,
        path=relative_path,
        width=width,
        height=height,
        file_format=file_format,
        size_bytes=file_size,
        source_type="dataset",
        source_name=filename
    )

    existing_paths.add(
        normalized_path
    )

    print(
        f"[ADDED] "
        f"{asset['asset_id']} "
        f"-> {filename} "
        f"({width}x{height})"
    )

    return asset


# ============================================================
# INDEX CATEGORY
# ============================================================

def index_category(
    category_path,
    category,
    existing_paths
):
    """
    Index every image inside one category folder.
    """

    print()
    print(
        f"Category: {category}"
    )

    image_count = 0
    added_count = 0

    for filename in sorted(
        os.listdir(category_path)
    ):

        image_path = os.path.join(
            category_path,
            filename
        )

        if not os.path.isfile(
            image_path
        ):
            continue

        if not is_image_file(
            filename
        ):
            continue

        image_count += 1

        asset = index_image(
            image_path,
            category,
            existing_paths
        )

        if asset is not None:
            added_count += 1

    print(
        f"Found: {image_count} images"
    )

    print(
        f"Added: {added_count} assets"
    )

    return image_count, added_count


# ============================================================
# INDEX ENTIRE DATASET
# ============================================================

def index_dataset():
    """
    Scan dataset/images and add all images
    to the catalog.
    """

    print("=" * 70)
    print("VIETHERITAGE DATASET INDEXER")
    print("=" * 70)

    print()
    print("Dataset directory:")
    print(DATASET_IMAGES_DIR)

    # --------------------------------------------------------
    # Check dataset directory
    # --------------------------------------------------------

    if not os.path.exists(
        DATASET_IMAGES_DIR
    ):

        print()
        print(
            "[ERROR] Dataset directory does not exist."
        )

        return

    # --------------------------------------------------------
    # Existing catalog paths
    # --------------------------------------------------------

    existing_paths = get_existing_paths()

    print()
    print(
        f"Already indexed: {len(existing_paths)}"
    )

    # --------------------------------------------------------
    # Scan categories
    # --------------------------------------------------------

    total_images = 0
    total_added = 0

    for category in sorted(
        os.listdir(DATASET_IMAGES_DIR)
    ):

        category_path = os.path.join(
            DATASET_IMAGES_DIR,
            category
        )

        if not os.path.isdir(
            category_path
        ):
            continue

        image_count, added_count = index_category(
            category_path,
            category,
            existing_paths
        )

        total_images += image_count
        total_added += added_count

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    final_assets = get_all_assets()

    print()
    print("=" * 70)
    print("INDEXING COMPLETE")
    print("=" * 70)

    print(
        f"Images found:   {total_images}"
    )

    print(
        f"Assets added:   {total_added}"
    )

    print(
        f"Catalog assets: {len(final_assets)}"
    )

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    index_dataset()