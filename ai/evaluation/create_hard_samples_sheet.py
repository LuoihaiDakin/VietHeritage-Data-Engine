from pathlib import Path
import json
import math
from collections import Counter

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

PREDICTIONS_FILE = (
    BASE_DIR
    / "ai"
    / "evaluation"
    / "test_predictions_v5.json"
)

CATALOG_FILE = (
    BASE_DIR
    / "catalog"
    / "catalog.json"
)

ERROR_ANALYSIS_FILE = (
    BASE_DIR
    / "ai"
    / "evaluation"
    / "error_analysis_v5.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "ai"
    / "evaluation"
    / "error_contact_sheet_v5.png"
)


# ============================================================
# SETTINGS
# ============================================================

THUMB_WIDTH = 420
THUMB_HEIGHT = 320

LABEL_HEIGHT = 120

COLUMNS = 3

BACKGROUND_COLOR = "white"
TEXT_COLOR = "black"
BORDER_COLOR = "black"


# ============================================================
# FONT
# ============================================================

def load_font(size, bold=False):

    if bold:
        possible_fonts = [
            "arialbd.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ]
    else:
        possible_fonts = [
            "arial.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]

    for font_path in possible_fonts:

        try:
            return ImageFont.truetype(
                font_path,
                size
            )

        except OSError:
            continue

    return ImageFont.load_default()


FONT_TITLE = load_font(20, bold=True)
FONT_LABEL = load_font(16)
FONT_SMALL = load_font(14)


# ============================================================
# LOAD JSON
# ============================================================

def load_json(path):

    if not path.exists():

        raise FileNotFoundError(
            f"File not found:\n{path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# BUILD ERROR ANALYSIS
# ============================================================

def build_error_analysis(predictions):

    errors = [
        item
        for item in predictions
        if not item.get("correct", False)
    ]

    confusion = Counter()

    for item in errors:

        true_label = item.get(
            "true_label",
            "UNKNOWN"
        )

        predicted_label = item.get(
            "predicted_label",
            "UNKNOWN"
        )

        confusion[
            (
                true_label,
                predicted_label
            )
        ] += 1

    true_distribution = Counter(
        item.get("true_label", "UNKNOWN")
        for item in predictions
    )

    predicted_distribution = Counter(
        item.get("predicted_label", "UNKNOWN")
        for item in predictions
    )

    error_by_true_class = Counter(
        item.get("true_label", "UNKNOWN")
        for item in errors
    )

    error_by_predicted_class = Counter(
        item.get("predicted_label", "UNKNOWN")
        for item in errors
    )

    confusion_pairs = []

    for (
        (true_label, predicted_label),
        count
    ) in sorted(
        confusion.items(),
        key=lambda x: (-x[1], x[0])
    ):

        confusion_pairs.append(
            {
                "true_label": true_label,
                "predicted_label": predicted_label,
                "count": count
            }
        )

    return {
        "model": "baseline_svm_v5",
        "experiment": "normalized_images_hog_svm",
        "dataset": "VietHeritage Classification Dataset V5",
        "split": "test",
        "total_samples": len(predictions),
        "correct_samples": len(predictions) - len(errors),
        "incorrect_samples": len(errors),
        "accuracy": (
            (len(predictions) - len(errors))
            / len(predictions)
            if predictions
            else 0
        ),
        "true_class_distribution": dict(
            sorted(true_distribution.items())
        ),
        "predicted_class_distribution": dict(
            sorted(predicted_distribution.items())
        ),
        "errors_by_true_class": dict(
            sorted(error_by_true_class.items())
        ),
        "errors_by_predicted_class": dict(
            sorted(error_by_predicted_class.items())
        ),
        "confusion_pairs": confusion_pairs,
        "hard_samples": errors
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 72)
    print("VIETHERITAGE - V5 ERROR ANALYSIS")
    print("=" * 72)
    print()

    # --------------------------------------------------------
    # Load predictions
    # --------------------------------------------------------

    prediction_data = load_json(
        PREDICTIONS_FILE
    )

    predictions = prediction_data.get(
        "predictions",
        []
    )

    if not predictions:

        raise RuntimeError(
            "No predictions found in test_predictions_v5.json"
        )

    print(
        f"Test samples: {len(predictions)}"
    )

    # --------------------------------------------------------
    # Build error analysis
    # --------------------------------------------------------

    analysis = build_error_analysis(
        predictions
    )

    hard_samples = analysis[
        "hard_samples"
    ]

    print(
        f"Correct samples: "
        f"{analysis['correct_samples']}"
    )

    print(
        f"Incorrect samples: "
        f"{analysis['incorrect_samples']}"
    )

    print()

    print("CONFUSION PAIRS")
    print("-" * 72)

    for pair in analysis[
        "confusion_pairs"
    ]:

        print(
            f"{pair['true_label']:<20}"
            f" -> "
            f"{pair['predicted_label']:<20}"
            f"{pair['count']}"
        )

    print()

    # --------------------------------------------------------
    # Save error analysis JSON
    # --------------------------------------------------------

    ERROR_ANALYSIS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        ERROR_ANALYSIS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            analysis,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        "Error analysis saved:"
    )

    print(
        ERROR_ANALYSIS_FILE
    )

    print()

    # --------------------------------------------------------
    # Load catalog
    # --------------------------------------------------------

    catalog = load_json(
        CATALOG_FILE
    )

    assets = catalog.get(
        "assets",
        []
    )

    catalog_assets = {
        asset.get("asset_id"): asset
        for asset in assets
        if asset.get("asset_id")
    }

    print(
        f"Catalog assets: {len(catalog_assets)}"
    )

    print()

    # --------------------------------------------------------
    # Canvas
    # --------------------------------------------------------

    if not hard_samples:

        print(
            "No hard samples found."
        )

        return

    rows = math.ceil(
        len(hard_samples) / COLUMNS
    )

    cell_width = THUMB_WIDTH

    cell_height = (
        THUMB_HEIGHT
        + LABEL_HEIGHT
    )

    canvas_width = (
        COLUMNS
        * cell_width
    )

    canvas_height = (
        rows
        * cell_height
    )

    sheet = Image.new(
        "RGB",
        (
            canvas_width,
            canvas_height
        ),
        BACKGROUND_COLOR
    )

    draw = ImageDraw.Draw(
        sheet
    )

    # --------------------------------------------------------
    # Render samples
    # --------------------------------------------------------

    rendered = 0
    failed = 0

    for index, sample in enumerate(
        hard_samples
    ):

        asset_id = sample.get(
            "asset_id",
            "UNKNOWN"
        )

        true_label = sample.get(
            "true_label",
            "UNKNOWN"
        )

        predicted_label = sample.get(
            "predicted_label",
            "UNKNOWN"
        )

        asset = catalog_assets.get(
            asset_id
        )

        x_index = (
            index
            % COLUMNS
        )

        y_index = (
            index
            // COLUMNS
        )

        cell_x = (
            x_index
            * cell_width
        )

        cell_y = (
            y_index
            * cell_height
        )

        # ----------------------------------------------------
        # Cell border
        # ----------------------------------------------------

        draw.rectangle(
            [
                cell_x,
                cell_y,
                cell_x + cell_width - 1,
                cell_y + cell_height - 1,
            ],
            outline=BORDER_COLOR,
            width=2
        )

        if asset is None:

            failed += 1

            draw.text(
                (
                    cell_x + 10,
                    cell_y + 20
                ),
                "ASSET NOT FOUND",
                fill=TEXT_COLOR,
                font=FONT_TITLE
            )

            draw.text(
                (
                    cell_x + 10,
                    cell_y + 55
                ),
                asset_id,
                fill=TEXT_COLOR,
                font=FONT_LABEL
            )

            continue

        # ----------------------------------------------------
        # Original image path
        # ----------------------------------------------------

        original = asset.get(
            "original",
            {}
        )

        image_path = original.get(
            "path"
        )

        if not image_path:

            failed += 1

            draw.text(
                (
                    cell_x + 10,
                    cell_y + 20
                ),
                "IMAGE PATH MISSING",
                fill=TEXT_COLOR,
                font=FONT_TITLE
            )

            draw.text(
                (
                    cell_x + 10,
                    cell_y + 55
                ),
                asset_id,
                fill=TEXT_COLOR,
                font=FONT_LABEL
            )

            continue

        absolute_path = (
            BASE_DIR
            / image_path
        )

        # ----------------------------------------------------
        # Check image
        # ----------------------------------------------------

        if not absolute_path.is_file():

            failed += 1

            draw.text(
                (
                    cell_x + 10,
                    cell_y + 20
                ),
                "IMAGE NOT FOUND",
                fill=TEXT_COLOR,
                font=FONT_TITLE
            )

            draw.text(
                (
                    cell_x + 10,
                    cell_y + 55
                ),
                str(absolute_path),
                fill=TEXT_COLOR,
                font=FONT_SMALL
            )

            print(
                f"WARNING: image not found:"
                f"\n  {absolute_path}"
            )

            continue

        # ----------------------------------------------------
        # Open image
        # ----------------------------------------------------

        try:

            image = Image.open(
                absolute_path
            ).convert("RGB")

            image.thumbnail(
                (
                    THUMB_WIDTH - 20,
                    THUMB_HEIGHT - 20
                ),
                Image.Resampling.LANCZOS
            )

            image_x = (
                cell_x
                + (
                    THUMB_WIDTH
                    - image.width
                )
                // 2
            )

            image_y = (
                cell_y
                + (
                    THUMB_HEIGHT
                    - image.height
                )
                // 2
            )

            sheet.paste(
                image,
                (
                    image_x,
                    image_y
                )
            )

            # Image border

            draw.rectangle(
                [
                    image_x - 1,
                    image_y - 1,
                    image_x + image.width,
                    image_y + image.height,
                ],
                outline=BORDER_COLOR,
                width=1
            )

            rendered += 1

        except Exception as e:

            failed += 1

            draw.text(
                (
                    cell_x + 10,
                    cell_y + 20
                ),
                "IMAGE ERROR",
                fill=TEXT_COLOR,
                font=FONT_TITLE
            )

            draw.text(
                (
                    cell_x + 10,
                    cell_y + 55
                ),
                str(e),
                fill=TEXT_COLOR,
                font=FONT_SMALL
            )

            print(
                f"WARNING: cannot open "
                f"{absolute_path}: {e}"
            )

        # ----------------------------------------------------
        # Labels
        # ----------------------------------------------------

        text_x = (
            cell_x + 8
        )

        text_y = (
            cell_y
            + THUMB_HEIGHT
            + 5
        )

        draw.text(
            (
                text_x,
                text_y
            ),
            asset_id,
            fill=TEXT_COLOR,
            font=FONT_LABEL
        )

        draw.text(
            (
                text_x,
                text_y + 22
            ),
            f"TRUE: {true_label}",
            fill=TEXT_COLOR,
            font=FONT_SMALL
        )

        draw.text(
            (
                text_x,
                text_y + 42
            ),
            f"PREDICTED: {predicted_label}",
            fill=TEXT_COLOR,
            font=FONT_SMALL
        )

        draw.text(
            (
                text_x,
                text_y + 62
            ),
            "ERROR",
            fill=TEXT_COLOR,
            font=FONT_SMALL
        )

    # --------------------------------------------------------
    # Save contact sheet
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    sheet.save(
        OUTPUT_FILE,
        format="PNG"
    )

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("V5 ERROR ANALYSIS COMPLETE")
    print("=" * 72)

    print()
    print(
        f"Total test samples : "
        f"{len(predictions)}"
    )

    print(
        f"Correct            : "
        f"{analysis['correct_samples']}"
    )

    print(
        f"Incorrect          : "
        f"{analysis['incorrect_samples']}"
    )

    print(
        f"Rendered images    : "
        f"{rendered}"
    )

    print(
        f"Failed images      : "
        f"{failed}"
    )

    print()
    print("Files:")

    print(
        ERROR_ANALYSIS_FILE
    )

    print(
        OUTPUT_FILE
    )

    print()

    if rendered == len(hard_samples):

        print(
            "All hard samples rendered successfully."
        )

    elif rendered > 0:

        print(
            "WARNING: Some hard samples "
            "could not be rendered."
        )

    else:

        print(
            "WARNING: 0 images were rendered."
        )

    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()