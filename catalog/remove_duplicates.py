import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

CATALOG_FILE = ROOT / "catalog" / "catalog.json"

REMOVE_IDS = {
    "rong_viet_nam_017",
    "rong_viet_nam_020",
}


def remove_path(relative_path):
    if not relative_path:
        return

    path = ROOT / relative_path

    if path.exists():
        if path.is_dir():
            shutil.rmtree(path)
            print(f"REMOVED DIR : {relative_path}")
        else:
            path.unlink()
            print(f"REMOVED FILE: {relative_path}")
    else:
        print(f"NOT FOUND   : {relative_path}")


def main():
    print("=" * 70)
    print("VIETHERITAGE - REMOVE EXACT DUPLICATES")
    print("=" * 70)

    with open(CATALOG_FILE, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    assets = catalog.get("assets", [])

    remove_assets = [
        asset
        for asset in assets
        if asset.get("asset_id") in REMOVE_IDS
    ]

    if len(remove_assets) != len(REMOVE_IDS):
        found = {a.get("asset_id") for a in remove_assets}
        missing = REMOVE_IDS - found

        raise RuntimeError(
            f"Expected {len(REMOVE_IDS)} assets, "
            f"found {len(remove_assets)}. Missing: {missing}"
        )

    print("\nAssets to remove:")
    for asset in remove_assets:
        print(f"  - {asset['asset_id']}")

    print("\nRemoving files...")

    for asset in remove_assets:
        asset_id = asset["asset_id"]

        # Original dataset image
        original = asset.get("original", {})
        remove_path(original.get("path"))

        # Processed outputs
        outputs = asset.get("outputs", {})

        output_dir = ROOT / "outputs" / asset_id
        if output_dir.exists():
            shutil.rmtree(output_dir)
            print(f"REMOVED DIR : outputs/{asset_id}")

        # AI-ready image
        category = asset.get("category")

        if category:
            ai_ready_png = (
                ROOT
                / "ai_ready"
                / "images"
                / category
                / f"{asset_id}.png"
            )

            if ai_ready_png.exists():
                ai_ready_png.unlink()
                print(
                    f"REMOVED FILE: "
                    f"ai_ready/images/{category}/{asset_id}.png"
                )
            else:
                print(
                    f"NOT FOUND   : "
                    f"ai_ready/images/{category}/{asset_id}.png"
                )

    # Remove assets from catalog
    original_count = len(assets)

    catalog["assets"] = [
        asset
        for asset in assets
        if asset.get("asset_id") not in REMOVE_IDS
    ]

    new_count = len(catalog["assets"])

    if new_count != original_count - len(REMOVE_IDS):
        raise RuntimeError(
            "Catalog count changed unexpectedly."
        )

    with open(CATALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            catalog,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("\n" + "=" * 70)
    print("DUPLICATE REMOVAL COMPLETE")
    print("=" * 70)

    print(f"Catalog before : {original_count}")
    print(f"Removed        : {len(REMOVE_IDS)}")
    print(f"Catalog after  : {new_count}")

    print("\nRemoved IDs:")
    for asset_id in sorted(REMOVE_IDS):
        print(f"  - {asset_id}")


if __name__ == "__main__":
    main()