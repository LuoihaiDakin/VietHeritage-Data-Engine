import json
from pathlib import Path
from collections import Counter


BASE_DIR = Path(__file__).resolve().parent.parent

CATALOG_FILE = BASE_DIR / "catalog" / "catalog.json"
MANIFEST_FILE = BASE_DIR / "ai_ready" / "classification_manifest.json"


EXCLUDED_CATEGORIES = {
    "other",
    "uploaded",
}


CLASSIFICATION_CATEGORIES = {
    "dong_ho",
    "phu_dieu_rong",
    "rong_viet_nam",
    "phuong",
    "sen",
    "trong_dong",
}


def load_catalog():
    if not CATALOG_FILE.exists():
        raise FileNotFoundError(
            f"Catalog not found:\n{CATALOG_FILE}"
        )

    with open(CATALOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def build_manifest():

    catalog = load_catalog()

    assets = catalog.get("assets", [])

    if not assets:
        raise RuntimeError("No assets found in catalog.")

    classification_assets = []

    for asset in assets:

        category = asset.get("category")

        if category in EXCLUDED_CATEGORIES:
            continue

        if category not in CLASSIFICATION_CATEGORIES:
            continue

        asset_id = asset.get("asset_id")

        original = asset.get("original", {})
        image_path = original.get("path")

        if not asset_id:
            print("WARNING: asset without asset_id")
            continue

        if not image_path:
            print(
                f"WARNING: image path missing for {asset_id}"
            )
            continue

        absolute_path = BASE_DIR / image_path

        if not absolute_path.is_file():
            print(
                f"WARNING: image not found: {image_path}"
            )
            continue

        # --------------------------------------------------
        # IMPORTANT:
        # train_baseline.py resolves image paths relative to
        # ai_ready/ directory.
        #
        # Actual image is:
        #   dataset/images/...
        #
        # Therefore manifest must contain:
        #   ../dataset/images/...
        # --------------------------------------------------

        manifest_image_path = "../" + image_path.replace("\\", "/")

        classification_assets.append(
            {
                "asset_id": asset_id,
                "category": category,
                "image": manifest_image_path,
                "quality": {
                    "label": asset.get("quality", {}).get("label"),
                    "overall_score": asset.get("quality", {}).get(
                        "overall_score"
                    ),
                },
            }
        )

    classification_assets.sort(
        key=lambda x: x["asset_id"]
    )

    manifest = {
        "dataset": "VietHeritage Classification Dataset V3",
        "version": "3.0",
        "source": "catalog/catalog.json",
        "excluded_categories": sorted(EXCLUDED_CATEGORIES),
        "categories": sorted(CLASSIFICATION_CATEGORIES),
        "total_assets": len(classification_assets),
        "assets": classification_assets,
    }

    with open(
        MANIFEST_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            manifest,
            f,
            ensure_ascii=False,
            indent=4
        )

    return manifest


def main():

    print()
    print("=" * 70)
    print("VIETHERITAGE CLASSIFICATION MANIFEST V3")
    print("=" * 70)
    print()

    manifest = build_manifest()

    assets = manifest["assets"]

    print(
        f"Classification assets : {len(assets)}"
    )

    print()

    print("Categories:")

    distribution = Counter(
        asset["category"]
        for asset in assets
    )

    for category, count in sorted(
        distribution.items()
    ):
        print(
            f"  {category:<25} {count}"
        )

    print()

    print(
        "Excluded categories : "
        + ", ".join(
            manifest["excluded_categories"]
        )
    )

    print()

    print("Manifest created:")
    print(
        "  ai_ready/classification_manifest.json"
    )

    print()

    print("=" * 70)


if __name__ == "__main__":
    main()