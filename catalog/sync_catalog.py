import json
from pathlib import Path
import sys


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# PATHS
# ============================================================

CATALOG_PATH = PROJECT_ROOT / "catalog" / "catalog.json"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


# ============================================================
# LOAD / SAVE
# ============================================================

def load_catalog():
    with open(
        CATALOG_PATH,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def save_catalog(data):
    with open(
        CATALOG_PATH,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# QUALITY SYNC
# ============================================================

def sync_quality(asset, report):
    """
    Read quality information from:

        quality_report.json
        └── input
            ├── metrics
            └── quality
                ├── quality
                ├── score
                └── component_scores

    Then convert it into the normalized catalog structure.
    """

    input_data = report.get("input", {})

    metrics = input_data.get(
        "metrics",
        {}
    )

    quality_data = input_data.get(
        "quality",
        {}
    )

    component_scores = quality_data.get(
        "component_scores",
        {}
    )

    # --------------------------------------------------------
    # Actual measured values
    # --------------------------------------------------------

    brightness = metrics.get(
        "brightness"
    )

    contrast = metrics.get(
        "contrast"
    )

    sharpness = metrics.get(
        "sharpness"
    )

    # --------------------------------------------------------
    # Component quality scores
    # --------------------------------------------------------

    resolution = component_scores.get(
        "resolution"
    )

    # --------------------------------------------------------
    # Overall quality
    # --------------------------------------------------------

    overall_score = quality_data.get(
        "score"
    )

    label = quality_data.get(
        "quality"
    )

    # --------------------------------------------------------
    # Store clean catalog structure
    # --------------------------------------------------------

    asset["quality"] = {
        "brightness": brightness,
        "contrast": contrast,
        "sharpness": sharpness,
        "resolution": resolution,
        "overall_score": overall_score,
        "label": label
    }

    return label, overall_score


# ============================================================
# PROCESSING SYNC
# ============================================================

def sync_processing(asset, output_dir):

    processing = asset.setdefault(
        "processing",
        {}
    )

    outputs = asset.setdefault(
        "outputs",
        {}
    )

    # --------------------------------------------------------
    # Output files
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Save relative output paths
    # --------------------------------------------------------

    for key, filename in output_files.items():

        path = output_dir / filename

        if path.exists():

            relative_path = (
                Path("outputs")
                / asset["asset_id"]
                / filename
            )

            outputs[key] = relative_path.as_posix()

    # --------------------------------------------------------
    # Processing flags
    # --------------------------------------------------------

    processing["preprocessed"] = (
        output_dir / "cleaned.png"
    ).exists()

    processing["restored"] = (
        output_dir / "restored.png"
    ).exists()

    processing["normalized"] = (
        output_dir / "normalized.png"
    ).exists()

    processing["segmented"] = (
        output_dir / "segmented.png"
    ).exists()

    processing["vectorized"] = (
        output_dir / "pattern.svg"
    ).exists()


# ============================================================
# LINEAGE SYNC
# ============================================================

def sync_lineage(asset):

    lineage = asset.get(
        "lineage"
    )

    if not lineage:
        return

    quality = asset.get(
        "quality",
        {}
    )

    quality_label = quality.get(
        "label"
    )

    quality_score = quality.get(
        "overall_score"
    )

    # --------------------------------------------------------
    # Update QUALITY_EVALUATION stage
    # --------------------------------------------------------

    for stage in lineage.get(
        "stages",
        []
    ):

        if stage.get(
            "stage"
        ) == "QUALITY_EVALUATION":

            if quality_label is not None:

                stage["status"] = "completed"

                stage["quality"] = {
                    "label": quality_label,
                    "score": quality_score
                }

    # --------------------------------------------------------
    # Recalculate lineage completion
    # --------------------------------------------------------

    stages = lineage.get(
        "stages",
        []
    )

    completed_stages = sum(
        1
        for stage in stages
        if stage.get("status")
        in (
            "available",
            "completed"
        )
    )

    total_stages = len(
        stages
    )

    completion_ratio = (
        round(
            completed_stages / total_stages,
            2
        )
        if total_stages > 0
        else 0
    )

    lineage["final_state"] = {
        "completed_stages": completed_stages,
        "total_stages": total_stages,
        "completion_ratio": completion_ratio,
        "quality_label": quality_label,
        "quality_score": quality_score
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("VIETHERITAGE CATALOG SYNC")
    print("=" * 70)

    catalog = load_catalog()

    assets = catalog.get(
        "assets",
        []
    )

    synced = 0
    skipped = 0

    good = 0
    acceptable = 0
    poor = 0

    # ========================================================
    # PROCESS ALL ASSETS
    # ========================================================

    for asset in assets:

        asset_id = asset.get(
            "asset_id"
        )

        if not asset_id:

            skipped += 1
            continue

        output_dir = (
            OUTPUTS_DIR / asset_id
        )

        report_path = (
            output_dir /
            "quality_report.json"
        )

        # ----------------------------------------------------
        # Missing report
        # ----------------------------------------------------

        if not report_path.exists():

            print(
                f"[SKIP] {asset_id:<30} "
                f"quality_report.json not found"
            )

            skipped += 1
            continue

        # ----------------------------------------------------
        # Load report
        # ----------------------------------------------------

        try:

            with open(
                report_path,
                "r",
                encoding="utf-8"
            ) as f:

                report = json.load(f)

        except Exception as e:

            print(
                f"[ERROR] {asset_id:<30} "
                f"{e}"
            )

            skipped += 1
            continue

        # ----------------------------------------------------
        # Sync quality
        # ----------------------------------------------------

        label, score = sync_quality(
            asset,
            report
        )

        # ----------------------------------------------------
        # Sync processing
        # ----------------------------------------------------

        sync_processing(
            asset,
            output_dir
        )

        # ----------------------------------------------------
        # Sync lineage
        # ----------------------------------------------------

        sync_lineage(
            asset
        )

        # ----------------------------------------------------
        # Statistics
        # ----------------------------------------------------

        if label == "GOOD":
            good += 1

        elif label == "ACCEPTABLE":
            acceptable += 1

        elif label == "POOR":
            poor += 1

        synced += 1

        print(
            f"[SYNC] {asset_id:<30} "
            f"{str(label):<12} "
            f"score={score}"
        )

    # ========================================================
    # SAVE
    # ========================================================

    save_catalog(
        catalog
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("SYNC COMPLETE")
    print("=" * 70)

    print(
        f"Total assets : {len(assets)}"
    )

    print(
        f"Synced       : {synced}"
    )

    print(
        f"Skipped      : {skipped}"
    )

    print()
    print("QUALITY")

    print(
        f"GOOD         : {good}"
    )

    print(
        f"ACCEPTABLE   : {acceptable}"
    )

    print(
        f"POOR         : {poor}"
    )

    print()
    print(
        "catalog/catalog.json updated."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()