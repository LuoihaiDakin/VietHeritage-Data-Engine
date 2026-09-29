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

THUMB_WIDTH = 260
THUMB_HEIGHT = 220
LABEL_HEIGHT = 80
COLUMNS = 3


# ============================================================
# LOAD COMPARISON
# ============================================================

with open(
    COMPARISON_FILE,
    "r",
    encoding="utf-8",
) as f:
    comparison = json.load(f)


hard_samples = comparison["both_wrong"]


# ============================================================
# LOAD CATALOG
# ============================================================

with open(
    CATALOG_FILE,
    "r",
    encoding="utf-8",
) as f:
    catalog = json.load(f)


# ============================================================
# BUILD ASSET LOOKUP
# ============================================================

assets = catalog.get("assets", [])

catalog_assets = {}

for asset in assets:

    # Current catalog uses asset_id
    asset_id = asset.get("asset_id")

    if asset_id:
        catalog_assets[asset_id] = asset


# ============================================================
# FONT
# ============================================================

try:

    font = ImageFont.truetype(
        "arial.ttf",
        16,
    )

    small_font = ImageFont.truetype(
        "arial.ttf",
        13,
    )

except Exception:

    font = ImageFont.load_default()
    small_font = ImageFont.load_default()


# ============================================================
# CREATE CANVAS
# ============================================================

rows = math.ceil(
    len(hard_samples) / COLUMNS
)

cell_width = THUMB_WIDTH
cell_height = THUMB_HEIGHT + LABEL_HEIGHT

canvas_width = COLUMNS * cell_width
canvas_height = rows * cell_height

sheet = Image.new(
    "RGB",
    (
        canvas_width,
        canvas_height,
    ),
    "white",
)

draw = ImageDraw.Draw(sheet)


# ============================================================
# RENDER
# ============================================================

for index, sample in enumerate(hard_samples):

    asset_id = sample["asset_id"]

    true_label = sample["true_label"]

    v3_prediction = sample["v3_prediction"]

    v4_prediction = sample["v4_prediction"]


    # --------------------------------------------------------
    # FIND ASSET
    # --------------------------------------------------------

    asset = catalog_assets.get(asset_id)

    if asset is None:

        print(
            f"WARNING: asset not found in catalog: "
            f"{asset_id}"
        )

        continue


    # --------------------------------------------------------
    # IMAGE PATH
    # --------------------------------------------------------

    image_path = asset.get("path")

    if not image_path:

        print(
            f"WARNING: no image path for "
            f"{asset_id}"
        )

        continue


    image_path = (
        BASE_DIR
        / image_path
    )


    if not image_path.exists():

        print(
            f"WARNING: image not found: "
            f"{image_path}"
        )

        continue


    # --------------------------------------------------------
    # OPEN IMAGE
    # --------------------------------------------------------

    try:

        image = Image.open(
            image_path
        ).convert("RGB")

    except Exception as e:

        print(
            f"WARNING: cannot open "
            f"{image_path}: {e}"
        )

        continue


    # --------------------------------------------------------
    # THUMBNAIL
    # --------------------------------------------------------

    image.thumbnail(
        (
            THUMB_WIDTH - 20,
            THUMB_HEIGHT - 20,
        )
    )


    x_index = index % COLUMNS
    y_index = index // COLUMNS

    cell_x = (
        x_index
        * cell_width
    )

    cell_y = (
        y_index
        * cell_height
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
            image_y,
        ),
    )


    # --------------------------------------------------------
    # LABEL
    # --------------------------------------------------------

    text_x = cell_x + 8

    text_y = (
        cell_y
        + THUMB_HEIGHT
        + 4
    )


    draw.text(
        (
            text_x,
            text_y,
        ),
        asset_id,
        fill="black",
        font=font,
    )


    draw.text(
        (
            text_x,
            text_y + 20,
        ),
        f"TRUE: {true_label}",
        fill="black",
        font=small_font,
    )


    draw.text(
        (
            text_x,
            text_y + 38,
        ),
        (
            f"V3: {v3_prediction} "
            f"| V4: {v4_prediction}"
        ),
        fill="black",
        font=small_font,
    )


# ============================================================
# SAVE
# ============================================================

sheet.save(
    OUTPUT_FILE
)


# ============================================================
# RESULT
# ============================================================

print("=" * 72)
print("HARD SAMPLE CONTACT SHEET")
print("=" * 72)

print()
print(
    f"Samples: {len(hard_samples)}"
)

print()
print(
    f"Catalog assets loaded: "
    f"{len(catalog_assets)}"
)

print()
print(OUTPUT_FILE)