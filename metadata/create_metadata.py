import json
import os
from datetime import datetime


def file_exists(path):
    """
    Check whether a file exists.
    """
    return os.path.exists(path)


def get_file_size(path):
    """
    Get file size in bytes.
    """
    if not os.path.exists(path):
        return 0

    return os.path.getsize(path)


def create_metadata():
    """
    Create metadata for a processed Vietnamese
    cultural heritage asset.
    """

    # --------------------------------------------------
    # Project paths
    # --------------------------------------------------

    project_root = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    outputs_dir = os.path.join(
        project_root,
        "outputs"
    )

    metadata_dir = os.path.join(
        project_root,
        "metadata"
    )

    # --------------------------------------------------
    # Input / output files
    # --------------------------------------------------

    original_file = None

    cleaned_file = os.path.join(
        outputs_dir,
        "cleaned_test.jpg"
    )

    restored_file = os.path.join(
        outputs_dir,
        "restored_test.jpg"
    )

    edge_file = os.path.join(
        outputs_dir,
        "edges_test.jpg"
    )

    segmentation_file = os.path.join(
        outputs_dir,
        "segmentation_mask.jpg"
    )

    segmented_file = os.path.join(
        outputs_dir,
        "segmented_test.jpg"
    )

    vector_file = os.path.join(
        outputs_dir,
        "vectorized_test.svg"
    )

    normalized_file = os.path.join(
        outputs_dir,
        "normalized_test.svg"
    )

    # --------------------------------------------------
    # Processing status
    # --------------------------------------------------

    processing = {
        "cleaning": file_exists(
            cleaned_file
        ),

        "restoration": file_exists(
            restored_file
        ),

        "edge_extraction": file_exists(
            edge_file
        ),

        "segmentation": file_exists(
            segmentation_file
        ),

        "vectorization": file_exists(
            vector_file
        ),

        "normalization": file_exists(
            normalized_file
        )
    }

    # --------------------------------------------------
    # Asset information
    # --------------------------------------------------

    metadata = {

        "asset_id": "VHDE_0001",

        "name": "Dong Ho Rooster",

        "title_vi": "Gà Đông Hồ",

        "category": "Dong Ho",

        "sub_category": "Vietnamese Folk Art",

        "culture": "Vietnamese",

        "asset_type": "Cultural Graphic Pattern",

        "description": (
            "A Vietnamese cultural graphic asset "
            "derived from a Dong Ho folk-art image."
        ),

        "source": {
            "type": "Test Dataset",
            "original_file": original_file
        },

        "processing": processing,

        "files": {

            "cleaned": (
                "outputs/cleaned_test.jpg"
                if file_exists(cleaned_file)
                else None
            ),

            "restored": (
                "outputs/restored_test.jpg"
                if file_exists(restored_file)
                else None
            ),

            "edges": (
                "outputs/edges_test.jpg"
                if file_exists(edge_file)
                else None
            ),

            "segmentation_mask": (
                "outputs/segmentation_mask.jpg"
                if file_exists(segmentation_file)
                else None
            ),

            "segmented": (
                "outputs/segmented_test.jpg"
                if file_exists(segmented_file)
                else None
            ),

            "vectorized": (
                "outputs/vectorized_test.svg"
                if file_exists(vector_file)
                else None
            ),

            "normalized": (
                "outputs/normalized_test.svg"
                if file_exists(normalized_file)
                else None
            )
        },

        "file_sizes": {

            "cleaned_bytes": get_file_size(
                cleaned_file
            ),

            "restored_bytes": get_file_size(
                restored_file
            ),

            "edges_bytes": get_file_size(
                edge_file
            ),

            "segmentation_mask_bytes": get_file_size(
                segmentation_file
            ),

            "segmented_bytes": get_file_size(
                segmented_file
            ),

            "vectorized_bytes": get_file_size(
                vector_file
            ),

            "normalized_bytes": get_file_size(
                normalized_file
            )
        },

        "intended_use": [

            "Game development",

            "Animation",

            "Digital art",

            "Graphic design",

            "Cultural education",

            "Digital cultural preservation"
        ],

        "status": "prototype",

        "created_at": datetime.now().isoformat(),

        "notes": (
            "This asset is currently a prototype "
            "processed through the VietHeritage "
            "Data Engine pipeline. Source information "
            "should be updated when the original "
            "historical source is verified."
        )
    }

    # --------------------------------------------------
    # Save metadata
    # --------------------------------------------------

    os.makedirs(
        metadata_dir,
        exist_ok=True
    )

    output_file = os.path.join(
        metadata_dir,
        "metadata.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=4
        )

    # --------------------------------------------------
    # Print result
    # --------------------------------------------------

    print(
        "Metadata creation completed."
    )

    print(
        f"Asset ID: {metadata['asset_id']}"
    )

    print(
        f"Asset name: {metadata['name']}"
    )

    print(
        f"Output: {output_file}"
    )

    print(
        "\nProcessing status:"
    )

    for step, status in processing.items():

        symbol = "OK" if status else "MISSING"

        print(
            f"[{symbol}] {step}"
        )


if __name__ == "__main__":

    print(
        "Starting metadata generation..."
    )

    create_metadata()

    print(
        "Metadata generation completed."
    )