import sys
import json
import os
import cv2
from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Add project root to Python path
sys.path.insert(
    0,
    str(BASE_DIR)
)


# Import after adding project root
from processing.pipeline import process_image


# ============================================================
# PATHS
# ============================================================

CATALOG_FILE = BASE_DIR / "catalog" / "catalog.json"
OUTPUTS_DIR = BASE_DIR / "outputs"


# ============================================================
# LOAD CATALOG
# ============================================================

def load_catalog():

    if not CATALOG_FILE.exists():

        raise FileNotFoundError(
            f"Catalog not found:\n{CATALOG_FILE}"
        )

    with open(
        CATALOG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("VIETHERITAGE - PROCESS NEW DATASET ASSETS")
    print("=" * 70)

    catalog = load_catalog()

    assets = catalog.get(
        "assets",
        []
    )

    print(
        f"\nCatalog assets: {len(assets)}"
    )

    # ========================================================
    # FIND UNPROCESSED ASSETS
    # ========================================================

    pending_assets = []

    for asset in assets:

        asset_id = asset.get(
            "asset_id"
        )

        original = asset.get(
            "original",
            {}
        )

        original_path = original.get(
            "path"
        )

        if not asset_id or not original_path:
            continue

        output_dir = (
            OUTPUTS_DIR / asset_id
        )

        quality_report = (
            output_dir / "quality_report.json"
        )

        # Already processed
        if quality_report.exists():
            continue

        pending_assets.append(
            asset
        )

    print(
        f"Already processed: "
        f"{len(assets) - len(pending_assets)}"
    )

    print(
        f"New assets to process: "
        f"{len(pending_assets)}"
    )

    if not pending_assets:

        print(
            "\nNo new assets need processing."
        )

        return

    # ========================================================
    # PROCESS
    # ========================================================

    success = 0
    failed = 0

    for index, asset in enumerate(
        pending_assets,
        start=1
    ):

        asset_id = asset[
            "asset_id"
        ]

        category = asset.get(
            "category",
            "unknown"
        )

        original_path = Path(
            asset[
                "original"
            ][
                "path"
            ]
        )

        # Convert relative path to absolute path
        if not original_path.is_absolute():

            input_path = (
                BASE_DIR /
                original_path
            )

        else:

            input_path = original_path

        output_dir = (
            OUTPUTS_DIR /
            asset_id
        )

        print("\n" + "-" * 70)

        print(
            f"[{index}/{len(pending_assets)}] "
            f"{asset_id}"
        )

        print(
            f"Category : {category}"
        )

        print(
            f"Input    : {input_path}"
        )

        print(
            f"Output   : {output_dir}"
        )

        # ----------------------------------------------------
        # Check input
        # ----------------------------------------------------

        if not input_path.exists():

            print(
                "STATUS   : FAILED - input image not found"
            )

            failed += 1

            continue

        try:

            process_image(
                str(input_path),
                str(output_dir)
            )

            report_path = (
                output_dir /
                "quality_report.json"
            )

            if report_path.exists():

                print(
                    "STATUS   : SUCCESS"
                )

                success += 1

            else:

                print(
                    "STATUS   : FAILED - "
                    "quality report not created"
                )

                failed += 1

        except Exception as error:

            print(
                "STATUS   : FAILED"
            )

            print(
                f"ERROR    : {error}"
            )

            failed += 1

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("PROCESSING COMPLETE")
    print("=" * 70)

    print(
        f"Total catalog assets : {len(assets)}"
    )

    print(
        f"Processed this run   : {success}"
    )

    print(
        f"Failed               : {failed}"
    )

    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()