import os
import json


# ==========================================
# CONFIGURATION
# ==========================================

def get_project_root():
    return os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )


# ==========================================
# LOAD JSON
# ==========================================

def load_json(path):
    if not os.path.exists(path):
        return []

    try:
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except Exception as error:
        print(
            f"WARNING: Cannot read {path}"
        )
        print(error)

        return []


# ==========================================
# BUILD QUALITY INDEX
# ==========================================

def build_quality_index(
    quality_report
):
    index = {}

    if isinstance(
        quality_report,
        dict
    ):
        results = quality_report.get(
            "results",
            []
        )

    else:
        results = []

    for item in results:

        filename = item.get(
            "filename"
        )

        if filename:
            index[filename] = item

    return index


# ==========================================
# BUILD CATALOG
# ==========================================

def build_catalog(
    metadata,
    quality_report
):

    quality_index = build_quality_index(
        quality_report
    )

    catalog = []

    for item in metadata:

        filename = item.get(
            "filename",
            ""
        )

        category = item.get(
            "category",
            "unknown"
        )

        record = {
            "id": (
                f"{category}_"
                f"{os.path.splitext(filename)[0]}"
            ),

            "filename": filename,

            "path": item.get(
                "path",
                ""
            ),

            "category": category,

            "period": item.get(
                "period",
                "unknown"
            ),

            "dynasty": item.get(
                "dynasty",
                "unknown"
            ),

            "motif": item.get(
                "motif",
                "unknown"
            ),

            "region": item.get(
                "region",
                "unknown"
            ),

            "source": item.get(
                "source",
                "unknown"
            ),

            "license": item.get(
                "license",
                "unknown"
            ),

            "original": {
                "width": item.get(
                    "width"
                ),
                "height": item.get(
                    "height"
                ),
                "format": item.get(
                    "format"
                ),
                "file_size_kb": item.get(
                    "file_size_kb"
                ),
                "brightness": item.get(
                    "brightness"
                ),
                "contrast": item.get(
                    "contrast"
                ),
                "sharpness": item.get(
                    "sharpness"
                )
            },

            "processing": {
                "preprocessed": False,
                "restored": False,
                "normalized": False,
                "segmented": False,
                "vectorized": False
            },

            "outputs": {}
        }

        # ----------------------------------
        # Quality
        # ----------------------------------

        if filename in quality_index:

            quality = quality_index[
                filename
            ]

            record["quality"] = quality

        else:

            record["quality"] = None

        catalog.append(
            record
        )

    return catalog


# ==========================================
# CHECK OUTPUTS
# ==========================================

def update_processing_status(
    catalog,
    project_root
):

    directories = {
        "preprocessed":
            os.path.join(
                project_root,
                "outputs",
                "preprocessing"
            ),

        "restored":
            os.path.join(
                project_root,
                "outputs",
                "restoration"
            ),

        "normalized":
            os.path.join(
                project_root,
                "outputs",
                "normalization"
            ),

        "segmented":
            os.path.join(
                project_root,
                "outputs",
                "segmentation"
            ),

        "vectorized":
            os.path.join(
                project_root,
                "outputs",
                "vectorization"
            )
    }

    for record in catalog:

        filename = record[
            "filename"
        ]

        base_name = os.path.splitext(
            filename
        )[0]

        category = record[
            "category"
        ]

        for stage, directory in directories.items():

            category_directory = os.path.join(
                directory,
                category
            )

            if not os.path.exists(
                category_directory
            ):
                continue

            found = False

            for root, dirs, files in os.walk(
                category_directory
            ):

                for current_file in files:

                    current_base = os.path.splitext(
                        current_file
                    )[0]

                    if current_base == base_name:

                        found = True
                        break

                if found:
                    break

            if found:

                record[
                    "processing"
                ][stage] = True

    return catalog


# ==========================================
# SAVE CATALOG
# ==========================================

def save_catalog(
    catalog,
    output_path
):

    os.makedirs(
        os.path.dirname(
            output_path
        ),
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            catalog,
            file,
            indent=4,
            ensure_ascii=False
        )


# ==========================================
# MAIN
# ==========================================

def main():

    project_root = get_project_root()

    metadata_path = os.path.join(
        project_root,
        "dataset",
        "metadata",
        "metadata.json"
    )

    quality_path = os.path.join(
        project_root,
        "dataset",
        "metadata",
        "quality_report.json"
    )

    output_path = os.path.join(
        project_root,
        "metadata",
        "heritage_catalog.json"
    )

    print(
        "========================================"
    )

    print(
        "      VietHeritage Heritage Catalog"
    )

    print(
        "========================================"
    )

    print()

    print(
        f"Metadata: {metadata_path}"
    )

    print(
        f"Quality:  {quality_path}"
    )

    print()

    metadata = load_json(
        metadata_path
    )

    quality_report = load_json(
        quality_path
    )

    if not metadata:

        print(
            "ERROR: metadata.json is empty "
            "or does not exist."
        )

        return

    catalog = build_catalog(
        metadata,
        quality_report
    )

    catalog = update_processing_status(
        catalog,
        project_root
    )

    save_catalog(
        catalog,
        output_path
    )

    # --------------------------------------
    # Statistics
    # --------------------------------------

    total = len(
        catalog
    )

    vectorized = sum(
        1
        for item in catalog
        if item[
            "processing"
        ][
            "vectorized"
        ]
    )

    segmented = sum(
        1
        for item in catalog
        if item[
            "processing"
        ][
            "segmented"
        ]
    )

    print(
        f"Images in catalog: {total}"
    )

    print(
        f"Segmented: {segmented}"
    )

    print(
        f"Vectorized: {vectorized}"
    )

    print()

    print(
        f"Catalog saved to:"
    )

    print(
        output_path
    )

    print()

    print(
        "Catalog generation completed."
    )


if __name__ == "__main__":
    main()