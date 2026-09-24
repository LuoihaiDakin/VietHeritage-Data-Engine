import os

from processing.pipeline import process_image


INPUT_IMAGE = "dataset/images/dong_ho/dong_ho_001.jpg"

OUTPUT_DIR = "outputs/test_001"


def main():

    if not os.path.exists(INPUT_IMAGE):
        print(
            f"Input image not found: {INPUT_IMAGE}"
        )
        return

    print("Starting VietHeritage pipeline...")

    result = process_image(
        INPUT_IMAGE,
        OUTPUT_DIR
    )

    print()
    print("Pipeline completed.")
    print()

    print(
        "Original metrics:"
    )

    print(
        result["input"]["metrics"]
    )

    print()

    print(
        "Restored metrics:"
    )

    print(
        result["restored"]["metrics"]
    )

    print()

    print(
        "Outputs:"
    )

    for key, value in result[
        "outputs"
    ].items():

        print(
            f"{key}: {value}"
        )


if __name__ == "__main__":
    main()