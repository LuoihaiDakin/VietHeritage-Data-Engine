import os
import cv2
import json

from processing.evaluation import evaluate_image


DATASET_DIR = "dataset/images"
OUTPUT_FILE = "dataset_evaluation.json"


results = []


for root, _, files in os.walk(DATASET_DIR):

    for filename in files:

        if not filename.lower().endswith(
            (".jpg", ".jpeg", ".png", ".webp")
        ):
            continue

        image_path = os.path.join(
            root,
            filename
        )

        image = cv2.imread(
            image_path
        )

        if image is None:
            print(
                f"Skipped: {image_path}"
            )
            continue

        metrics = evaluate_image(
            image
        )

        results.append({
            "path": image_path,
            "metrics": metrics
        })


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        results,
        file,
        indent=4,
        ensure_ascii=False
    )


print()
print("=" * 60)
print("DATASET EVALUATION COMPLETED")
print("=" * 60)
print(f"Images evaluated: {len(results)}")
print(f"Output: {OUTPUT_FILE}")