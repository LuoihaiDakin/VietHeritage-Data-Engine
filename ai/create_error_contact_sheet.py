import json
from pathlib import Path
import math

from PIL import Image, ImageOps, ImageDraw, ImageFont


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PREDICTIONS_FILE = (
    BASE_DIR
    / "ai"
    / "evaluation"
    / "test_predictions_v3.json"
)

CATALOG_FILE = (
    BASE_DIR
    / "catalog"
    / "catalog.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "ai"
    / "evaluation"
    / "error_contact_sheet_v3.png"
)


# ============================================================
# CONFIG
# ============================================================

COLUMNS = 3

CELL_WIDTH = 520
CELL_HEIGHT = 430

PADDING = 20
HEADER_HEIGHT = 70

BACKGROUND_COLOR = "white"
TEXT_COLOR = "black"
BORDER_COLOR = "black"


# ============================================================
# FONT
# ============================================================

def load_font(size, bold=False):

    possible_fonts = []

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


FONT_TITLE = load_font(22, bold=True)
FONT_ID = load_font(17, bold=False)
FONT_PATH = load_font(13, bold=False)


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
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("VIETHERITAGE - V3 ERROR CONTACT SHEET")
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # Load prediction results
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
            "No predictions found in test_predictions_v3.json"
        )

    # --------------------------------------------------------
    # Load catalog
    # --------------------------------------------------------

    catalog_data = load_json(
        CATALOG_FILE
    )

    assets = catalog_data.get(
        "assets",
        []
    )

    catalog_by_id = {
        asset.get("asset_id"): asset
        for asset in assets
        if asset.get("asset_id")
    }

    # --------------------------------------------------------
    # Find errors
    # --------------------------------------------------------

    errors = []

    for prediction in predictions:

        actual = prediction.get(
            "actual_category"
        )

        predicted = prediction.get(
            "predicted_category"
        )

        asset_id = prediction.get(
            "asset_id"
        )

        if actual == predicted:
            continue

        if not asset_id:
            print(
                "WARNING: prediction without asset_id"
            )
            continue

        asset = catalog_by_id.get(
            asset_id
        )

        if asset is None:

            print(
                f"WARNING: asset not found in catalog: "
                f"{asset_id}"
            )

            continue

        original = asset.get(
            "original",
            {}
        )

        image_path = original.get(
            "path"
        )

        if not image_path:

            print(
                f"WARNING: image path missing: "
                f"{asset_id}"
            )

            continue

        absolute_path = (
            BASE_DIR / image_path
        )

        errors.append(
            {
                "asset_id": asset_id,
                "actual": actual,
                "predicted": predicted,
                "image_path": image_path,
                "absolute_path": absolute_path,
            }
        )

    # --------------------------------------------------------
    # Check errors
    # --------------------------------------------------------

    if not errors:

        print(
            "No prediction errors found."
        )

        return

    print(
        f"Prediction records : {len(predictions)}"
    )

    print(
        f"Errors             : {len(errors)}"
    )

    print()

    # --------------------------------------------------------
    # Contact sheet dimensions
    # --------------------------------------------------------

    rows = math.ceil(
        len(errors) / COLUMNS
    )

    sheet_width = (
        COLUMNS * CELL_WIDTH
        + (COLUMNS + 1) * PADDING
    )

    sheet_height = (
        rows * CELL_HEIGHT
        + (rows + 1) * PADDING
    )

    sheet = Image.new(
        "RGB",
        (
            sheet_width,
            sheet_height
        ),
        BACKGROUND_COLOR
    )

    draw = ImageDraw.Draw(
        sheet
    )

    # --------------------------------------------------------
    # Draw each error
    # --------------------------------------------------------

    for index, item in enumerate(errors):

        row = index // COLUMNS
        column = index % COLUMNS

        x = (
            PADDING
            + column * CELL_WIDTH
        )

        y = (
            PADDING
            + row * CELL_HEIGHT
        )

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        title = (
            f"{item['actual']} -> "
            f"{item['predicted']}"
        )

        draw.text(
            (x, y),
            title,
            fill=TEXT_COLOR,
            font=FONT_TITLE
        )

        draw.text(
            (x, y + 29),
            item["asset_id"],
            fill=TEXT_COLOR,
            font=FONT_ID
        )

        # ----------------------------------------------------
        # Load image
        # ----------------------------------------------------

        image_path = item[
            "absolute_path"
        ]

        try:

            image = Image.open(
                image_path
            ).convert("RGB")

            available_width = (
                CELL_WIDTH - 20
            )

            available_height = (
                CELL_HEIGHT
                - HEADER_HEIGHT
                - 35
            )

            image = ImageOps.contain(
                image,
                (
                    available_width,
                    available_height
                )
            )

            image_x = (
                x
                + (
                    CELL_WIDTH
                    - image.width
                ) // 2
            )

            image_y = (
                y
                + HEADER_HEIGHT
                + (
                    available_height
                    - image.height
                ) // 2
            )

            sheet.paste(
                image,
                (
                    image_x,
                    image_y
                )
            )

            # Border
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

        except Exception as e:

            error_text = (
                "IMAGE ERROR\n"
                f"{e}"
            )

            draw.multiline_text(
                (
                    x + 10,
                    y + HEADER_HEIGHT
                ),
                error_text,
                fill=TEXT_COLOR,
                font=FONT_ID,
                spacing=5
            )

        # ----------------------------------------------------
        # Image path
        # ----------------------------------------------------

        path_text = item[
            "image_path"
        ]

        # Keep path readable
        max_chars = 65

        if len(path_text) > max_chars:

            path_text = (
                "..."
                + path_text[-(max_chars - 3):]
            )

        draw.text(
            (
                x,
                y + CELL_HEIGHT - 25
            ),
            path_text,
            fill=TEXT_COLOR,
            font=FONT_PATH
        )

    # --------------------------------------------------------
    # Save
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
    # Summary
    # --------------------------------------------------------

    print(
        "Contact sheet created:"
    )

    print(
        f"  {OUTPUT_FILE}"
    )

    print()

    print(
        "Errors included:"
    )

    for item in errors:

        print(
            f"  {item['asset_id']} | "
            f"{item['actual']} -> "
            f"{item['predicted']}"
        )

    print()
    print("=" * 70)
    print("COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()