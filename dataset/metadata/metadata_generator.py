import os
import json
import cv2


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff"
}


def calculate_image_metrics(image):
    """
    Calculate basic visual metrics.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    brightness = float(gray.mean())

    contrast = float(gray.std())

    sharpness = float(
        cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()
    )

    return {
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
        "sharpness": round(sharpness, 2)
    }


def analyze_image(file_path, dataset_path):
    """
    Extract technical metadata from an image.
    """

    image = cv2.imread(file_path)

    if image is None:
        print(f"WARNING: Cannot read image: {file_path}")
        return None

    height, width = image.shape[:2]

    file_size = os.path.getsize(file_path)

    extension = os.path.splitext(
        file_path
    )[1].lower()

    metrics = calculate_image_metrics(
        image
    )

    # Get relative path inside dataset
    relative_path = os.path.relpath(
        file_path,
        dataset_path
    )

    # Get category from parent folder
    parent_folder = os.path.basename(
        os.path.dirname(file_path)
    )

    metadata = {
        "filename": os.path.basename(
            file_path
        ),

        "path": relative_path.replace(
            "\\",
            "/"
        ),

        "width": width,

        "height": height,

        "format": extension.replace(
            ".",
            ""
        ).upper(),

        "file_size_kb": round(
            file_size / 1024,
            2
        ),

        "aspect_ratio": round(
            width / height,
            4
        ),

        "brightness": metrics[
            "brightness"
        ],

        "contrast": metrics[
            "contrast"
        ],

        "sharpness": metrics[
            "sharpness"
        ],

        "category": parent_folder,

        "period": "unknown",

        "dynasty": "unknown",

        "motif": "unknown",

        "region": "unknown",

        "source": "unknown",

        "license": "unknown"
    }

    return metadata


def scan_dataset(dataset_path):
    """
    Scan all images inside dataset/images.
    """

    metadata_list = []

    images_path = os.path.join(
        dataset_path,
        "images"
    )

    if not os.path.exists(images_path):

        print(
            f"ERROR: Image dataset not found: {images_path}"
        )

        return metadata_list

    for root, directories, files in os.walk(
        images_path
    ):

        for filename in files:

            extension = os.path.splitext(
                filename
            )[1].lower()

            if extension not in IMAGE_EXTENSIONS:
                continue

            file_path = os.path.join(
                root,
                filename
            )

            metadata = analyze_image(
                file_path,
                dataset_path
            )

            if metadata is not None:

                metadata_list.append(
                    metadata
                )

    return metadata_list


def save_metadata(metadata_list, output_path):
    """
    Save metadata as JSON.
    """

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata_list,
            file,
            indent=4,
            ensure_ascii=False
        )


def main():

    # Project root
    project_root = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )

    # Dataset directory
    dataset_path = os.path.join(
        project_root,
        "dataset"
    )

    # Metadata output
    metadata_path = os.path.join(
        dataset_path,
        "metadata",
        "metadata.json"
    )

    print(
        "========================================"
    )

    print(
        "     VietHeritage Dataset Metadata"
    )

    print(
        "========================================"
    )

    print()

    print(
        f"Scanning: {os.path.join(dataset_path, 'images')}"
    )

    print()

    metadata_list = scan_dataset(
        dataset_path
    )

    save_metadata(
        metadata_list,
        metadata_path
    )

    print()

    print(
        f"Images found: {len(metadata_list)}"
    )

    print(
        f"Metadata saved to: {metadata_path}"
    )

    print()

    print(
        "Metadata generation completed."
    )


if __name__ == "__main__":
    main()