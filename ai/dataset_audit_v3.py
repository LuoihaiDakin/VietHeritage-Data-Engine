import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CATALOG_FILE = BASE_DIR / "catalog" / "catalog.json"

OUTPUT_DIR = BASE_DIR / "ai" / "evaluation"

REPORT_JSON = OUTPUT_DIR / "dataset_audit_v3.json"
REPORT_CSV = OUTPUT_DIR / "dataset_audit_v3.csv"

SHEET_DIR = OUTPUT_DIR / "audit_sheets"


# ============================================================
# DATASET CONFIG
# ============================================================

CLASSIFICATION_CATEGORIES = [
    "dong_ho",
    "phu_dieu_rong",
    "phuong",
    "rong_viet_nam",
    "sen",
    "trong_dong",
]


# ============================================================
# CONTACT SHEET CONFIG
# ============================================================

COLUMNS = 4

CELL_WIDTH = 330
CELL_HEIGHT = 300

PADDING = 15

IMAGE_WIDTH = 300
IMAGE_HEIGHT = 220


# ============================================================
# FONT
# ============================================================

def load_font(size, bold=False):

    if bold:
        candidates = [
            "C:/Windows/Fonts/arialbd.ttf",
            "arialbd.ttf",
        ]
    else:
        candidates = [
            "C:/Windows/Fonts/arial.ttf",
            "arial.ttf",
        ]

    for font_path in candidates:
        try:
            return ImageFont.truetype(
                font_path,
                size
            )
        except OSError:
            continue

    return ImageFont.load_default()


FONT_ID = load_font(16, bold=True)
FONT_INFO = load_font(13)
FONT_SMALL = load_font(11)


# ============================================================
# HELPERS
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


def calculate_sha256(path):

    sha256 = hashlib.sha256()

    with open(path, "rb") as f:

        while True:

            chunk = f.read(1024 * 1024)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def safe_round(value, digits=2):

    if value is None:
        return None

    return round(value, digits)


def get_quality(asset):

    quality = asset.get(
        "quality",
        {}
    )

    return {
        "label": quality.get("label"),
        "overall_score": quality.get(
            "overall_score"
        ),
        "brightness": quality.get(
            "brightness"
        ),
        "contrast": quality.get(
            "contrast"
        ),
        "sharpness": quality.get(
            "sharpness"
        ),
        "resolution": quality.get(
            "resolution"
        ),
    }


# ============================================================
# CONTACT SHEET
# ============================================================

def create_contact_sheet(
    category,
    records
):

    if not records:
        return

    rows = math.ceil(
        len(records) / COLUMNS
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
        "white"
    )

    draw = ImageDraw.Draw(sheet)

    for index, record in enumerate(records):

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
        # Asset ID
        # ----------------------------------------------------

        draw.text(
            (x, y),
            record["asset_id"],
            fill="black",
            font=FONT_ID
        )

        # ----------------------------------------------------
        # Image
        # ----------------------------------------------------

        image_path = Path(
            record["absolute_path"]
        )

        try:

            image = Image.open(
                image_path
            ).convert("RGB")

            image.thumbnail(
                (
                    IMAGE_WIDTH,
                    IMAGE_HEIGHT
                ),
                Image.Resampling.LANCZOS
            )

            image_x = (
                x
                + (
                    CELL_WIDTH
                    - image.width
                ) // 2
            )

            image_y = (
                y + 28
            )

            sheet.paste(
                image,
                (
                    image_x,
                    image_y
                )
            )

            draw.rectangle(
                [
                    image_x - 1,
                    image_y - 1,
                    image_x + image.width,
                    image_y + image.height,
                ],
                outline="black",
                width=1
            )

        except Exception as e:

            draw.text(
                (
                    x + 10,
                    y + 50
                ),
                f"IMAGE ERROR: {e}",
                fill="black",
                font=FONT_SMALL
            )

        # ----------------------------------------------------
        # Information
        # ----------------------------------------------------

        info_y = y + 255

        size_text = (
            f"{record['width']}x"
            f"{record['height']}  "
            f"{record['extension']}"
        )

        draw.text(
            (
                x,
                info_y
            ),
            size_text,
            fill="black",
            font=FONT_INFO
        )

        quality_text = (
            f"Quality: "
            f"{record['quality_label']}  "
            f"Score: "
            f"{record['quality_score']}"
        )

        draw.text(
            (
                x,
                info_y + 18
            ),
            quality_text,
            fill="black",
            font=FONT_INFO
        )

        draw.text(
            (
                x,
                info_y + 36
            ),
            f"Path: {record['image_path']}",
            fill="black",
            font=FONT_SMALL
        )

    output_file = (
        SHEET_DIR
        / f"{category}.png"
    )

    sheet.save(
        output_file,
        format="PNG"
    )

    print(
        f"  Contact sheet: {output_file}"
    )


# ============================================================
# MAIN AUDIT
# ============================================================

def main():

    print()
    print("=" * 70)
    print("VIETHERITAGE - CLASSIFICATION DATASET V3 AUDIT")
    print("=" * 70)
    print()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    SHEET_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    catalog = load_json(
        CATALOG_FILE
    )

    assets = catalog.get(
        "assets",
        []
    )

    print(
        f"Catalog assets: {len(assets)}"
    )

    print()

    # --------------------------------------------------------
    # Select classification assets
    # --------------------------------------------------------

    selected_assets = [
        asset
        for asset in assets
        if asset.get("category")
        in CLASSIFICATION_CATEGORIES
    ]

    print(
        f"Classification assets: "
        f"{len(selected_assets)}"
    )

    print()

    records = []

    missing_files = []
    unreadable_files = []

    # --------------------------------------------------------
    # Analyze each asset
    # --------------------------------------------------------

    for asset in selected_assets:

        asset_id = asset.get(
            "asset_id"
        )

        category = asset.get(
            "category"
        )

        original = asset.get(
            "original",
            {}
        )

        image_path = original.get(
            "path"
        )

        if not image_path:

            missing_files.append(
                {
                    "asset_id": asset_id,
                    "reason": "missing path"
                }
            )

            continue

        absolute_path = (
            BASE_DIR / image_path
        )

        if not absolute_path.is_file():

            missing_files.append(
                {
                    "asset_id": asset_id,
                    "path": image_path,
                    "reason": "file not found"
                }
            )

            continue

        # ----------------------------------------------------
        # Image metadata
        # ----------------------------------------------------

        try:

            with Image.open(
                absolute_path
            ) as image:

                width, height = image.size

                image_format = (
                    image.format
                    or ""
                )

                mode = image.mode

        except Exception as e:

            unreadable_files.append(
                {
                    "asset_id": asset_id,
                    "path": image_path,
                    "reason": str(e)
                }
            )

            continue

        file_size = (
            absolute_path.stat().st_size
        )

        extension = (
            absolute_path.suffix
            .lower()
        )

        aspect_ratio = (
            width / height
            if height
            else None
        )

        quality = get_quality(
            asset
        )

        record = {
            "asset_id": asset_id,
            "category": category,
            "image_path": image_path,
            "absolute_path": str(
                absolute_path
            ),
            "filename": absolute_path.name,
            "extension": extension,
            "format": image_format,
            "mode": mode,
            "width": width,
            "height": height,
            "aspect_ratio": safe_round(
                aspect_ratio,
                3
            ),
            "file_size_bytes": file_size,
            "quality_label": quality[
                "label"
            ],
            "quality_score": quality[
                "overall_score"
            ],
            "brightness": quality[
                "brightness"
            ],
            "contrast": quality[
                "contrast"
            ],
            "sharpness": quality[
                "sharpness"
            ],
            "resolution_score": quality[
                "resolution"
            ],
        }

        records.append(
            record
        )

    # --------------------------------------------------------
    # Duplicate detection
    # --------------------------------------------------------

    print(
        "Calculating SHA-256 hashes..."
    )

    hash_groups = defaultdict(list)

    for record in records:

        path = Path(
            record["absolute_path"]
        )

        file_hash = calculate_sha256(
            path
        )

        record["sha256"] = file_hash

        hash_groups[
            file_hash
        ].append(
            record["asset_id"]
        )

    duplicate_groups = [
        {
            "sha256": file_hash,
            "asset_ids": asset_ids
        }
        for file_hash, asset_ids
        in hash_groups.items()
        if len(asset_ids) > 1
    ]

    # --------------------------------------------------------
    # Category statistics
    # --------------------------------------------------------

    category_records = defaultdict(list)

    for record in records:

        category_records[
            record["category"]
        ].append(
            record
        )

    category_stats = {}

    for category in CLASSIFICATION_CATEGORIES:

        category_items = category_records.get(
            category,
            []
        )

        widths = [
            r["width"]
            for r in category_items
        ]

        heights = [
            r["height"]
            for r in category_items
        ]

        sizes = [
            r["file_size_bytes"]
            for r in category_items
        ]

        scores = [
            r["quality_score"]
            for r in category_items
            if isinstance(
                r["quality_score"],
                (int, float)
            )
        ]

        labels = Counter(
            r["quality_label"]
            for r in category_items
        )

        extensions = Counter(
            r["extension"]
            for r in category_items
        )

        category_stats[
            category
        ] = {
            "count": len(category_items),

            "min_width": min(widths)
            if widths else None,

            "max_width": max(widths)
            if widths else None,

            "min_height": min(heights)
            if heights else None,

            "max_height": max(heights)
            if heights else None,

            "average_width": safe_round(
                sum(widths) / len(widths),
                2
            )
            if widths else None,

            "average_height": safe_round(
                sum(heights) / len(heights),
                2
            )
            if heights else None,

            "average_file_size_kb": safe_round(
                sum(sizes)
                / len(sizes)
                / 1024,
                2
            )
            if sizes else None,

            "average_quality_score": safe_round(
                sum(scores)
                / len(scores),
                2
            )
            if scores else None,

            "quality_distribution": dict(
                labels
            ),

            "extensions": dict(
                extensions
            ),
        }

    # --------------------------------------------------------
    # Suspicious samples
    # --------------------------------------------------------

    low_quality = [
        r
        for r in records
        if isinstance(
            r["quality_score"],
            (int, float)
        )
        and r["quality_score"] < 70
    ]

    small_images = [
        r
        for r in records
        if (
            r["width"] < 300
            or r["height"] < 300
        )
    ]

    unusual_formats = [
        r
        for r in records
        if r["extension"]
        not in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        }
    ]

    # --------------------------------------------------------
    # Asset ID / filename differences
    # --------------------------------------------------------

    id_filename_differences = []

    for record in records:

        filename_stem = Path(
            record["filename"]
        ).stem

        if filename_stem != record[
            "asset_id"
        ]:

            id_filename_differences.append(
                {
                    "asset_id": record[
                        "asset_id"
                    ],
                    "filename": record[
                        "filename"
                    ],
                    "path": record[
                        "image_path"
                    ],
                }
            )

    # --------------------------------------------------------
    # Create contact sheets
    # --------------------------------------------------------

    print()
    print(
        "Creating category contact sheets..."
    )

    for category in CLASSIFICATION_CATEGORIES:

        create_contact_sheet(
            category,
            category_records.get(
                category,
                []
            )
        )

    # --------------------------------------------------------
    # Report
    # --------------------------------------------------------

    report = {
        "dataset": (
            "VietHeritage "
            "Classification Dataset V3"
        ),
        "catalog_total": len(assets),
        "classification_total": len(
            selected_assets
        ),
        "evaluated_total": len(records),

        "categories": category_stats,

        "missing_files": missing_files,
        "unreadable_files": unreadable_files,

        "duplicate_groups": duplicate_groups,

        "low_quality_assets": [
            {
                "asset_id": r[
                    "asset_id"
                ],
                "category": r[
                    "category"
                ],
                "quality_score": r[
                    "quality_score"
                ],
                "quality_label": r[
                    "quality_label"
                ],
            }
            for r in low_quality
        ],

        "small_images": [
            {
                "asset_id": r[
                    "asset_id"
                ],
                "category": r[
                    "category"
                ],
                "width": r[
                    "width"
                ],
                "height": r[
                    "height"
                ],
            }
            for r in small_images
        ],

        "unusual_formats": [
            {
                "asset_id": r[
                    "asset_id"
                ],
                "category": r[
                    "category"
                ],
                "extension": r[
                    "extension"
                ],
            }
            for r in unusual_formats
        ],

        "asset_id_filename_differences": (
            id_filename_differences
        ),

        "records": records,
    }

    with open(
        REPORT_JSON,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            report,
            f,
            ensure_ascii=False,
            indent=2
        )

    # --------------------------------------------------------
    # CSV
    # --------------------------------------------------------

    if records:

        csv_fields = [
            "asset_id",
            "category",
            "image_path",
            "filename",
            "extension",
            "format",
            "mode",
            "width",
            "height",
            "aspect_ratio",
            "file_size_bytes",
            "quality_label",
            "quality_score",
            "brightness",
            "contrast",
            "sharpness",
            "resolution_score",
            "sha256",
        ]

        with open(
            REPORT_CSV,
            "w",
            encoding="utf-8-sig",
            newline=""
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=csv_fields
            )

            writer.writeheader()

            for record in records:

                writer.writerow(
                    {
                        field: record.get(
                            field
                        )
                        for field
                        in csv_fields
                    }
                )

    # --------------------------------------------------------
    # Console summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("DATASET AUDIT SUMMARY")
    print("=" * 70)

    print()
    print(
        f"Catalog total       : {len(assets)}"
    )

    print(
        f"Classification      : "
        f"{len(selected_assets)}"
    )

    print(
        f"Evaluated           : "
        f"{len(records)}"
    )

    print(
        f"Missing files       : "
        f"{len(missing_files)}"
    )

    print(
        f"Unreadable files    : "
        f"{len(unreadable_files)}"
    )

    print(
        f"Duplicate groups    : "
        f"{len(duplicate_groups)}"
    )

    print()

    print("CATEGORY DISTRIBUTION")
    print("-" * 70)

    for category in CLASSIFICATION_CATEGORIES:

        stats = category_stats[
            category
        ]

        print(
            f"{category:<20} "
            f"{stats['count']:>3} images"
        )

    print()

    print("QUALITY DISTRIBUTION")
    print("-" * 70)

    overall_quality = Counter(
        r["quality_label"]
        for r in records
    )

    for label, count in sorted(
        overall_quality.items(),
        key=lambda item: str(item[0])
    ):

        print(
            f"{str(label):<20} "
            f"{count:>3}"
        )

    print()

    print("POTENTIAL AUDIT FLAGS")
    print("-" * 70)

    print(
        f"Low quality (<70)  : "
        f"{len(low_quality)}"
    )

    print(
        f"Small images        : "
        f"{len(small_images)}"
    )

    print(
        f"Unusual formats     : "
        f"{len(unusual_formats)}"
    )

    print(
        f"ID/filename differs : "
        f"{len(id_filename_differences)}"
    )

    print()

    if duplicate_groups:

        print("DUPLICATE GROUPS")

        for group in duplicate_groups:

            print(
                f"  {group['asset_ids']}"
            )

        print()

    print("Reports created:")

    print(
        f"  {REPORT_JSON}"
    )

    print(
        f"  {REPORT_CSV}"
    )

    print()

    print("Contact sheets:")

    print(
        f"  {SHEET_DIR}"
    )

    print()
    print("=" * 70)
    print("DATASET AUDIT COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()