import os
import sys
import json
import hashlib
from collections import Counter
from datetime import datetime

import cv2


# ============================================================
# PROJECT ROOT
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if BASE_DIR not in sys.path:
    sys.path.insert(
        0,
        BASE_DIR
    )


# ============================================================
# PATHS
# ============================================================

AI_READY_DIR = os.path.join(
    BASE_DIR,
    "ai_ready"
)

MANIFEST_FILE = os.path.join(
    AI_READY_DIR,
    "manifest.json"
)

IMAGES_DIR = os.path.join(
    AI_READY_DIR,
    "images"
)

REPORT_JSON = os.path.join(
    AI_READY_DIR,
    "dataset_report.json"
)

REPORT_MD = os.path.join(
    AI_READY_DIR,
    "dataset_report.md"
)


# ============================================================
# LOAD MANIFEST
# ============================================================

def load_manifest():

    if not os.path.isfile(
        MANIFEST_FILE
    ):

        raise FileNotFoundError(
            f"Manifest not found: {MANIFEST_FILE}"
        )

    with open(
        MANIFEST_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(
            file
        )


# ============================================================
# HASH
# ============================================================

def calculate_file_hash(path):

    sha256 = hashlib.sha256()

    with open(
        path,
        "rb"
    ) as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            sha256.update(
                chunk
            )

    return sha256.hexdigest()


# ============================================================
# IMAGE VALIDATION
# ============================================================

def validate_image(path):

    result = {
        "exists": False,
        "readable": False,
        "width": None,
        "height": None,
        "channels": None,
        "file_size_bytes": None,
        "sha256": None
    }

    if not os.path.isfile(
        path
    ):
        return result

    result["exists"] = True

    result["file_size_bytes"] = os.path.getsize(
        path
    )

    try:

        image = cv2.imread(
            path,
            cv2.IMREAD_UNCHANGED
        )

        if image is None:
            return result

        result["readable"] = True

        result["height"] = image.shape[0]

        result["width"] = image.shape[1]

        if len(image.shape) == 2:

            result["channels"] = 1

        else:

            result["channels"] = image.shape[2]

        result["sha256"] = calculate_file_hash(
            path
        )

    except Exception:
        pass

    return result


# ============================================================
# MAIN VALIDATION
# ============================================================

def validate_dataset():

    print()
    print("=" * 70)
    print("VIETHERITAGE AI-READY DATASET VALIDATION")
    print("=" * 70)
    print()

    manifest = load_manifest()

    assets = manifest.get(
        "assets",
        []
    )

    # --------------------------------------------------------
    # Basic counters
    # --------------------------------------------------------

    total_assets = len(
        assets
    )

    valid_assets = 0
    invalid_assets = 0

    missing_files = []
    unreadable_files = []

    asset_results = []

    categories = Counter()
    quality_labels = Counter()

    dimensions = Counter()

    hashes = {}

    duplicate_groups = []

    total_size = 0

    # ========================================================
    # VALIDATE EVERY ASSET
    # ========================================================

    for asset in assets:

        asset_id = asset.get(
            "asset_id"
        )

        category = asset.get(
            "category",
            "unknown"
        )

        quality = asset.get(
            "quality",
            {}
        )

        label = quality.get(
            "label",
            "UNKNOWN"
        )

        image_relative_path = asset.get(
            "image"
        )

        categories[
            category
        ] += 1

        quality_labels[
            label
        ] += 1

        # ----------------------------------------------------
        # Missing image path
        # ----------------------------------------------------

        if not image_relative_path:

            missing_files.append(
                asset_id
            )

            asset_results.append(
                {
                    "asset_id": asset_id,
                    "category": category,
                    "status": "MISSING_PATH"
                }
            )

            invalid_assets += 1

            continue

        image_path = os.path.join(
            BASE_DIR,
            image_relative_path.replace(
                "/",
                os.sep
            )
        )

        # ----------------------------------------------------
        # Validate image
        # ----------------------------------------------------

        image_result = validate_image(
            image_path
        )

        # ----------------------------------------------------
        # Missing file
        # ----------------------------------------------------

        if not image_result["exists"]:

            missing_files.append(
                asset_id
            )

            asset_results.append(
                {
                    "asset_id": asset_id,
                    "category": category,
                    "status": "MISSING_FILE",
                    "image": image_relative_path
                }
            )

            invalid_assets += 1

            continue

        # ----------------------------------------------------
        # Unreadable file
        # ----------------------------------------------------

        if not image_result["readable"]:

            unreadable_files.append(
                asset_id
            )

            asset_results.append(
                {
                    "asset_id": asset_id,
                    "category": category,
                    "status": "UNREADABLE",
                    "image": image_relative_path
                }
            )

            invalid_assets += 1

            continue

        # ----------------------------------------------------
        # Valid image
        # ----------------------------------------------------

        valid_assets += 1

        total_size += image_result[
            "file_size_bytes"
        ]

        dimension_key = (
            f"{image_result['width']}"
            f"x"
            f"{image_result['height']}"
        )

        dimensions[
            dimension_key
        ] += 1

        image_hash = image_result[
            "sha256"
        ]

        if image_hash:

            if image_hash not in hashes:

                hashes[
                    image_hash
                ] = []

            hashes[
                image_hash
            ].append(
                asset_id
            )

        asset_results.append(
            {
                "asset_id":
                    asset_id,

                "category":
                    category,

                "status":
                    "VALID",

                "image":
                    image_relative_path,

                "quality":
                    label,

                "overall_score":
                    quality.get(
                        "overall_score"
                    ),

                "width":
                    image_result[
                        "width"
                    ],

                "height":
                    image_result[
                        "height"
                    ],

                "channels":
                    image_result[
                        "channels"
                    ],

                "file_size_bytes":
                    image_result[
                        "file_size_bytes"
                    ],

                "sha256":
                    image_hash
            }
        )

    # ========================================================
    # DUPLICATE DETECTION
    # ========================================================

    for image_hash, asset_ids in hashes.items():

        if len(asset_ids) > 1:

            duplicate_groups.append(
                {
                    "sha256":
                        image_hash,

                    "asset_ids":
                        asset_ids
                }
            )

    duplicate_asset_count = sum(
        len(group["asset_ids"])
        for group in duplicate_groups
    )

    # ========================================================
    # DATASET HEALTH
    # ========================================================

    checks = {

        "manifest_exists":
            os.path.isfile(
                MANIFEST_FILE
            ),

        "images_directory_exists":
            os.path.isdir(
                IMAGES_DIR
            ),

        "all_images_exist":
            len(
                missing_files
            ) == 0,

        "all_images_readable":
            len(
                unreadable_files
            ) == 0,

        "no_duplicates":
            len(
                duplicate_groups
            ) == 0,

        "has_assets":
            total_assets > 0
    }

    dataset_valid = all(
        checks.values()
    )

    # ========================================================
    # REPORT
    # ========================================================

    report = {

        "dataset_name":
            manifest.get(
                "dataset_name"
            ),

        "version":
            manifest.get(
                "version"
            ),

        "validated_at":
            datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),

        "validation_status":
            "VALID"
            if dataset_valid
            else "ISSUES_FOUND",

        "statistics": {

            "total_assets":
                total_assets,

            "valid_assets":
                valid_assets,

            "invalid_assets":
                invalid_assets,

            "missing_files":
                len(
                    missing_files
                ),

            "unreadable_files":
                len(
                    unreadable_files
                ),

            "duplicate_groups":
                len(
                    duplicate_groups
                ),

            "duplicate_assets":
                duplicate_asset_count,

            "total_size_bytes":
                total_size,

            "total_size_mb":
                round(
                    total_size /
                    (1024 * 1024),
                    2
                )
        },

        "categories":
            dict(
                categories
            ),

        "quality_distribution":
            dict(
                quality_labels
            ),

        "image_dimensions":
            dict(
                dimensions
            ),

        "checks":
            checks,

        "missing_files":
            missing_files,

        "unreadable_files":
            unreadable_files,

        "duplicate_groups":
            duplicate_groups,

        "assets":
            asset_results
    }

    # ========================================================
    # SAVE JSON REPORT
    # ========================================================

    with open(
        REPORT_JSON,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=4
        )

    # ========================================================
    # MARKDOWN REPORT
    # ========================================================

    create_markdown_report(
        report
    )

    # ========================================================
    # PRINT RESULTS
    # ========================================================

    print(
        f"Total assets       : {total_assets}"
    )

    print(
        f"Valid assets       : {valid_assets}"
    )

    print(
        f"Invalid assets     : {invalid_assets}"
    )

    print(
        f"Missing files      : "
        f"{len(missing_files)}"
    )

    print(
        f"Unreadable files   : "
        f"{len(unreadable_files)}"
    )

    print(
        f"Duplicate groups   : "
        f"{len(duplicate_groups)}"
    )

    print(
        f"Dataset size       : "
        f"{report['statistics']['total_size_mb']} MB"
    )

    print()

    print(
        "Categories:"
    )

    for category, count in categories.items():

        print(
            f"  {category:<25} {count}"
        )

    print()

    print(
        "Quality:"
    )

    for label, count in quality_labels.items():

        print(
            f"  {label:<25} {count}"
        )

    print()

    if dataset_valid:

        print(
            "STATUS: DATASET VALID"
        )

    else:

        print(
            "STATUS: ISSUES FOUND"
        )

    print()

    print(
        f"JSON report: "
        f"{relative_path(REPORT_JSON)}"
    )

    print(
        f"Markdown report: "
        f"{relative_path(REPORT_MD)}"
    )

    print()
    print("=" * 70)


# ============================================================
# MARKDOWN REPORT
# ============================================================

def create_markdown_report(
    report
):

    statistics = report[
        "statistics"
    ]

    lines = []

    lines.append(
        "# VietHeritage AI-Ready Dataset Validation Report"
    )

    lines.append("")

    lines.append(
        f"**Validation status:** "
        f"`{report['validation_status']}`"
    )

    lines.append("")

    lines.append(
        f"**Validated at:** "
        f"{report['validated_at']}"
    )

    lines.append("")

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    lines.append(
        "## Dataset Statistics"
    )

    lines.append("")

    lines.append(
        f"- Total assets: {statistics['total_assets']}"
    )

    lines.append(
        f"- Valid assets: {statistics['valid_assets']}"
    )

    lines.append(
        f"- Invalid assets: {statistics['invalid_assets']}"
    )

    lines.append(
        f"- Missing files: {statistics['missing_files']}"
    )

    lines.append(
        f"- Unreadable files: "
        f"{statistics['unreadable_files']}"
    )

    lines.append(
        f"- Duplicate groups: "
        f"{statistics['duplicate_groups']}"
    )

    lines.append(
        f"- Dataset size: "
        f"{statistics['total_size_mb']} MB"
    )

    lines.append("")

    # --------------------------------------------------------
    # Categories
    # --------------------------------------------------------

    lines.append(
        "## Category Distribution"
    )

    lines.append("")

    lines.append(
        "| Category | Assets |"
    )

    lines.append(
        "|---|---:|"
    )

    for category, count in report[
        "categories"
    ].items():

        lines.append(
            f"| {category} | {count} |"
        )

    lines.append("")

    # --------------------------------------------------------
    # Quality
    # --------------------------------------------------------

    lines.append(
        "## Quality Distribution"
    )

    lines.append("")

    lines.append(
        "| Quality | Assets |"
    )

    lines.append(
        "|---|---:|"
    )

    for label, count in report[
        "quality_distribution"
    ].items():

        lines.append(
            f"| {label} | {count} |"
        )

    lines.append("")

    # --------------------------------------------------------
    # Dimensions
    # --------------------------------------------------------

    lines.append(
        "## Image Dimensions"
    )

    lines.append("")

    lines.append(
        "| Resolution | Assets |"
    )

    lines.append(
        "|---|---:|"
    )

    for dimension, count in report[
        "image_dimensions"
    ].items():

        lines.append(
            f"| {dimension} | {count} |"
        )

    lines.append("")

    # --------------------------------------------------------
    # Validation Checks
    # --------------------------------------------------------

    lines.append(
        "## Validation Checks"
    )

    lines.append("")

    lines.append(
        "| Check | Result |"
    )

    lines.append(
        "|---|---|"
    )

    for check, result in report[
        "checks"
    ].items():

        status = (
            "PASS"
            if result
            else "FAIL"
        )

        lines.append(
            f"| {check} | {status} |"
        )

    lines.append("")

    # --------------------------------------------------------
    # Duplicate Groups
    # --------------------------------------------------------

    if report[
        "duplicate_groups"
    ]:

        lines.append(
            "## Duplicate Images"
        )

        lines.append("")

        for group in report[
            "duplicate_groups"
        ]:

            lines.append(
                f"- SHA256: `{group['sha256']}`"
            )

            lines.append(
                f"  - Assets: "
                f"{', '.join(group['asset_ids'])}"
            )

        lines.append("")

    # --------------------------------------------------------
    # Missing / unreadable
    # --------------------------------------------------------

    if report[
        "missing_files"
    ]:

        lines.append(
            "## Missing Files"
        )

        lines.append("")

        for asset_id in report[
            "missing_files"
        ]:

            lines.append(
                f"- `{asset_id}`"
            )

        lines.append("")

    if report[
        "unreadable_files"
    ]:

        lines.append(
            "## Unreadable Files"
        )

        lines.append("")

        for asset_id in report[
            "unreadable_files"
        ]:

            lines.append(
                f"- `{asset_id}`"
            )

        lines.append("")

    # --------------------------------------------------------
    # Write report
    # --------------------------------------------------------

    with open(
        REPORT_MD,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "\n".join(
                lines
            )
        )


# ============================================================
# RELATIVE PATH
# ============================================================

def relative_path(path):

    return os.path.relpath(
        path,
        BASE_DIR
    ).replace(
        "\\",
        "/"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    validate_dataset()