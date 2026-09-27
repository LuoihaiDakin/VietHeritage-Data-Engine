import json
import os
import sys


# ============================================================
# PROJECT ROOT
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
# FIX
# ============================================================

OLD_ID = "phu_dieu_rong_004"
NEW_ID = "phu_dieu_rong_005"


def main():

    print("=" * 70)
    print("FIX CATALOG ASSET ID")
    print("=" * 70)

    with open(
        CATALOG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        catalog = json.load(file)


    assets = catalog.get(
        "assets",
        []
    )


    # --------------------------------------------------------
    # Check duplicate NEW_ID
    # --------------------------------------------------------

    existing_new_id = [
        asset
        for asset in assets
        if asset.get("asset_id") == NEW_ID
    ]

    if existing_new_id:

        print()
        print(
            f"[ERROR] {NEW_ID} already exists in catalog."
        )

        print(
            "No changes were made."
        )

        return


    # --------------------------------------------------------
    # Find OLD_ID
    # --------------------------------------------------------

    target = None

    for asset in assets:

        if asset.get("asset_id") == OLD_ID:

            target = asset
            break


    if target is None:

        print()
        print(
            f"[ERROR] {OLD_ID} not found."
        )

        return


    # --------------------------------------------------------
    # Show current information
    # --------------------------------------------------------

    print()
    print("Current record:")

    print(
        f"asset_id : {target.get('asset_id')}"
    )

    print(
        f"filename : {target.get('filename')}"
    )

    print(
        f"category : {target.get('category')}"
    )


    # --------------------------------------------------------
    # Fix ID
    # --------------------------------------------------------

    target["asset_id"] = NEW_ID


    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

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


    print()
    print(
        f"[FIXED] {OLD_ID} -> {NEW_ID}"
    )

    print(
        f"Catalog: {CATALOG_FILE}"
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()