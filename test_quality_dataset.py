import json
import os

from processing.quality_classifier import classify_quality


INPUT_FILE = "dataset_evaluation.json"


def main():

    if not os.path.isfile(INPUT_FILE):
        raise FileNotFoundError(
            f"Cannot find: {INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    counts = {
        "GOOD": 0,
        "ACCEPTABLE": 0,
        "POOR": 0
    }

    print()
    print("=" * 80)
    print("VIETHERITAGE DATASET QUALITY CLASSIFICATION")
    print("=" * 80)

    for item in data:

        path = item["path"]
        metrics = item["metrics"]

        result = classify_quality(
            metrics
        )

        quality = result["quality"]

        counts[quality] += 1

        print(
            f"{quality:12} "
            f"{result['score']:6.2f}  "
            f"{path}"
        )

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    total = len(data)

    for quality in [
        "GOOD",
        "ACCEPTABLE",
        "POOR"
    ]:

        count = counts[quality]

        percentage = (
            count / total * 100
            if total > 0
            else 0
        )

        print(
            f"{quality:12}: "
            f"{count:2} "
            f"({percentage:.1f}%)"
        )

    print()
    print(
        f"TOTAL: {total}"
    )


if __name__ == "__main__":
    main()