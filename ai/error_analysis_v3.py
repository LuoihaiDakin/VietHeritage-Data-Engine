import json
from pathlib import Path
from collections import Counter


BASE_DIR = Path(__file__).resolve().parent
EVALUATION_DIR = BASE_DIR / "evaluation"

PREDICTIONS_FILE = EVALUATION_DIR / "test_predictions_v3.json"
OUTPUT_FILE = EVALUATION_DIR / "error_analysis_v3.json"


def load_predictions():
    if not PREDICTIONS_FILE.exists():
        raise FileNotFoundError(
            f"Prediction file not found:\n{PREDICTIONS_FILE}"
        )

    with open(PREDICTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("=" * 70)
    print("VIETHERITAGE - V3 ERROR ANALYSIS")
    print("=" * 70)

    data = load_predictions()

    predictions = data.get("predictions", [])

    if not isinstance(predictions, list):
        raise ValueError(
            "Invalid prediction format: 'predictions' must be a list."
        )

    print(f"\nPrediction records: {len(predictions)}")

    correct_predictions = []
    incorrect_predictions = []

    class_total = Counter()
    class_correct = Counter()
    class_errors = Counter()

    confusion_pairs = Counter()

    for record in predictions:
        asset_id = record.get("asset_id")
        image = record.get("image")

        actual = record.get("actual_category")
        predicted = record.get("predicted_category")

        if actual is None or predicted is None:
            continue

        item = {
            "asset_id": asset_id,
            "image": image,
            "actual": actual,
            "predicted": predicted,
            "correct": actual == predicted
        }

        class_total[actual] += 1

        if actual == predicted:
            correct_predictions.append(item)
            class_correct[actual] += 1
        else:
            incorrect_predictions.append(item)
            class_errors[actual] += 1
            confusion_pairs[(actual, predicted)] += 1

    # ==============================================================
    # CLASS ANALYSIS
    # ==============================================================

    class_analysis = {}

    all_classes = sorted(class_total.keys())

    for category in all_classes:
        total = class_total[category]
        correct = class_correct[category]
        errors = class_errors[category]

        accuracy = correct / total if total > 0 else 0

        class_analysis[category] = {
            "total": total,
            "correct": correct,
            "errors": errors,
            "accuracy": round(accuracy, 4)
        }

    # ==============================================================
    # CONFUSION PAIRS
    # ==============================================================

    confusion_analysis = []

    for (actual, predicted), count in sorted(
        confusion_pairs.items(),
        key=lambda x: (-x[1], x[0][0], x[0][1])
    ):
        confusion_analysis.append({
            "actual": actual,
            "predicted": predicted,
            "count": count
        })

    # ==============================================================
    # SUMMARY
    # ==============================================================

    total_evaluated = len(correct_predictions) + len(incorrect_predictions)
    total_correct = len(correct_predictions)
    total_errors = len(incorrect_predictions)

    accuracy = (
        total_correct / total_evaluated
        if total_evaluated > 0
        else 0
    )

    error_rate = (
        total_errors / total_evaluated
        if total_evaluated > 0
        else 0
    )

    result = {
        "experiment": data.get("experiment", "v3"),
        "model": data.get("model", "HOG + SVM"),
        "dataset": data.get(
            "dataset",
            "VietHeritage Classification Dataset V3"
        ),
        "split": data.get("split", "test"),
        "excluded_categories": data.get(
            "excluded_categories",
            []
        ),
        "summary": {
            "total_evaluated": total_evaluated,
            "correct": total_correct,
            "errors": total_errors,
            "accuracy": round(accuracy, 4),
            "error_rate": round(error_rate, 4)
        },
        "class_analysis": class_analysis,
        "confusion_pairs": confusion_analysis,
        "correct_predictions": correct_predictions,
        "incorrect_predictions": incorrect_predictions
    }

    # ==============================================================
    # SAVE
    # ==============================================================

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=4
        )

    # ==============================================================
    # TERMINAL OUTPUT
    # ==============================================================

    print("\n" + "=" * 70)
    print("V3 ERROR ANALYSIS SUMMARY")
    print("=" * 70)

    print(f"Total evaluated : {total_evaluated}")
    print(f"Correct         : {total_correct}")
    print(f"Errors          : {total_errors}")
    print(f"Accuracy        : {accuracy:.4f}")
    print(f"Error rate      : {error_rate:.4f}")

    print("\nCLASS ANALYSIS")
    print("-" * 70)

    for category, stats in class_analysis.items():
        print(
            f"{category:<20} "
            f"total={stats['total']:<3} "
            f"correct={stats['correct']:<3} "
            f"errors={stats['errors']:<3} "
            f"accuracy={stats['accuracy']:.2f}"
        )

    print("\nTOP CONFUSION PAIRS")
    print("-" * 70)

    if confusion_analysis:
        for item in confusion_analysis:
            print(
                f"{item['actual']} -> "
                f"{item['predicted']} : "
                f"{item['count']}"
            )
    else:
        print("No classification errors.")

    print("\n" + "=" * 70)
    print("ERROR ANALYSIS COMPLETE")
    print("=" * 70)

    print(f"\nSaved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()