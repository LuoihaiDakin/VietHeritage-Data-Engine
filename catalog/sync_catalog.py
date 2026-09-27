import os
import json
import sys


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


from catalog.catalog_manager import (
    get_all_assets,
    update_asset,
    update_quality,
    update_processing_status,
    update_output
)


# ============================================================
# PATHS
# ============================================================

OUTPUTS_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)


# ============================================================
# HELPERS
# ============================================================

def normalize_path(path):
    """
    Convert a path to a normalized project-relative path.

    This makes paths consistent on Windows and avoids
    storing different slash styles in catalog.json.
    """

    if not path:
        return None

    path = os.path.normpath(path)

    try:
        relative_path = os.path.relpath(
            path,
            BASE_DIR
        )

        return relative_path.replace(
            "\\",
            "/"
        )

    except ValueError:
        return path.replace(
            "\\",
            "/"
        )


def load_quality_report(report_path):
    """
    Load one quality_report.json file.
    """

    try:
        with open(
            report_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as error:

        print(
            f"[ERROR] Cannot read report: "
            f"{report_path}"
        )

        print(
            f"        {error}"
        )

        return None


def find_quality_report(asset_id):
    """
    Find the quality report belonging to an asset.

    Expected structure:

        outputs/
            asset_id/
                quality_report.json
    """

    report_path = os.path.join(
        OUTPUTS_DIR,
        asset_id,
        "quality_report.json"
    )

    if not os.path.isfile(report_path):
        return None

    return report_path


# ============================================================
# SYNC ONE ASSET
# ============================================================

def sync_asset(asset):
    """
    Synchronize one catalog asset with its existing
    processing results.
    """

    asset_id = asset.get(
        "asset_id"
    )

    if not asset_id:

        print(
            "[SKIP] Asset without asset_id"
        )

        return False


    # --------------------------------------------------------
    # Find quality report
    # --------------------------------------------------------

    report_path = find_quality_report(
        asset_id
    )

    if report_path is None:

        print(
            f"[SKIP] {asset_id}"
            f" -> quality_report.json not found"
        )

        return False


    # --------------------------------------------------------
    # Load report
    # --------------------------------------------------------

    report = load_quality_report(
        report_path
    )

    if report is None:
        return False


    # --------------------------------------------------------
    # Get original/input quality
    # --------------------------------------------------------

    input_data = report.get(
        "input",
        {}
    )

    input_metrics = input_data.get(
        "metrics",
        {}
    )

    input_quality = input_data.get(
        "quality",
        {}
    )


    # --------------------------------------------------------
    # Quality values
    # --------------------------------------------------------

    component_scores = input_quality.get(
        "component_scores",
        {}
    )

    quality_data = {

        "brightness": component_scores.get(
            "brightness"
        ),

        "contrast": component_scores.get(
            "contrast"
        ),

        "sharpness": input_metrics.get(
            "sharpness"
        ),

        "resolution": component_scores.get(
            "resolution"
        ),

        "overall_score": input_quality.get(
            "score"
        ),

        "label": input_quality.get(
            "quality"
        )
    }


    # --------------------------------------------------------
    # Update quality
    # --------------------------------------------------------

    update_quality(
        asset_id,
        quality_data
    )


    # --------------------------------------------------------
    # Processing status
    # --------------------------------------------------------

    processing_stages = {

        "preprocessed": True,

        "restored": os.path.isfile(
            os.path.join(
                OUTPUTS_DIR,
                asset_id,
                "restored.png"
            )
        ),

        "normalized": os.path.isfile(
            os.path.join(
                OUTPUTS_DIR,
                asset_id,
                "normalized.png"
            )
        ),

        "segmented": os.path.isfile(
            os.path.join(
                OUTPUTS_DIR,
                asset_id,
                "segmented.png"
            )
        ),

        "vectorized": os.path.isfile(
            os.path.join(
                OUTPUTS_DIR,
                asset_id,
                "pattern.svg"
            )
        )
    }


    for stage, status in processing_stages.items():

        update_processing_status(
            asset_id,
            stage,
            status
        )


    # --------------------------------------------------------
    # Output files
    # --------------------------------------------------------

    asset_output_dir = os.path.join(
        OUTPUTS_DIR,
        asset_id
    )


    output_files = {

        "restored": "restored.png",

        "cleaned": "cleaned.png",

        "normalized": "normalized.png",

        "edges": "edges.png",

        "segmented": "segmented.png",

        "mask": "mask.png",

        "svg": "pattern.svg",

        "quality_report": "quality_report.json"
    }


    for output_name, filename in output_files.items():

        full_path = os.path.join(
            asset_output_dir,
            filename
        )

        if os.path.isfile(full_path):

            relative_path = normalize_path(
                full_path
            )

            update_output(
                asset_id,
                output_name,
                relative_path
            )


    # --------------------------------------------------------
    # Print result
    # --------------------------------------------------------

    label = quality_data.get(
        "label"
    )

    score = quality_data.get(
        "overall_score"
    )


    print(
        f"[SYNC] {asset_id:<25}"
        f" {label:<12}"
        f" score={score}"
    )

    return True


# ============================================================
# SYNC ALL ASSETS
# ============================================================

def sync_catalog():
    """
    Synchronize all assets currently registered
    in catalog.json.
    """

    print()
    print("=" * 70)
    print("VIETHERITAGE CATALOG SYNCHRONIZATION")
    print("=" * 70)
    print()

    if not os.path.isdir(
        OUTPUTS_DIR
    ):

        print(
            "[ERROR] outputs directory not found:"
        )

        print(
            OUTPUTS_DIR
        )

        return


    assets = get_all_assets()

    if not assets:

        print(
            "[INFO] No assets found in catalog."
        )

        return


    total = len(
        assets
    )

    synced = 0
    skipped = 0


    print(
        f"Catalog assets: {total}"
    )

    print(
        f"Outputs directory: {OUTPUTS_DIR}"
    )

    print()


    for asset in assets:

        success = sync_asset(
            asset
        )

        if success:

            synced += 1

        else:

            skipped += 1


    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("SYNCHRONIZATION COMPLETE")
    print("=" * 70)

    print(
        f"Total assets : {total}"
    )

    print(
        f"Synced       : {synced}"
    )

    print(
        f"Skipped      : {skipped}"
    )

    print("=" * 70)
    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    sync_catalog()