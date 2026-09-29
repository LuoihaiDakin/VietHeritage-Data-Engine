from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

COMPARISON_FILE = (
    BASE_DIR
    / "ai"
    / "evaluation"
    / "comparison_v3_v4.json"
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
    / "hard_samples_v3_v4.png"
)


# ============================================================
# SETTINGS
# ============================================================

THUMB_WIDTH = 420
THUMB_HEIGHT = 320

LABEL_HEIGHT = 100

COLUMNS = 3

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
# MAIN
# ============================================================

def main():

    print()
    print("=" * 72)
    print("VIETHERITAGE - HARD SAMPLE CONTACT SHEET")
    print("=" * 72)
    print()

    # --------------------------------------------------------
    # Load comparison
    # --------------------------------------------------------

    comparison = load_json(
        COMPARISON_FILE
    )

    hard_samples = comparison.get(
        "both_wrong",
        []
    )

    if not hard_samples:

        raise RuntimeError(
            "No hard samples found in comparison_v3_v4.json"
        )

    print(
        f"Hard samples: {len(hard_samples)}"
    )

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

        v3_prediction = sample.get(
            "v3_prediction",
            "UNKNOWN"
        )

        v4_prediction = sample.get(
            "v4_prediction",
            "UNKNOWN"
        )

        # ----------------------------------------------------
        # Find catalog asset
        # ----------------------------------------------------

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

        # Border around entire cell

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
        # IMPORTANT:
        # Current catalog structure:
        #
        # asset["original"]["path"]
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

            print(
                f"WARNING: image path missing: {asset_id}"
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
                f"WARNING: cannot open {absolute_path}: {e}"
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
            (
                f"V3: {v3_prediction}"
                f"  |  "
                f"V4: {v4_prediction}"
            ),
            fill=TEXT_COLOR,
            font=FONT_SMALL
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
    # Result
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("HARD SAMPLE CONTACT SHEET COMPLETE")
    print("=" * 72)

    print()
    print(
        f"Total hard samples : {len(hard_samples)}"
    )

    print(
        f"Rendered images    : {rendered}"
    )

    print(
        f"Failed images      : {failed}"
    )

    print()
    print(
        f"Output:"
    )

    print(
        OUTPUT_FILE
    )

    print()

    if rendered == 0:

        print(
            "WARNING: 0 images were rendered."
        )

        print(
            "Check catalog original.path values."
        )

    elif failed > 0:

        print(
            "WARNING: Some images could not be rendered."
        )

    else:

        print(
            "All hard samples rendered successfully."
        )

    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()