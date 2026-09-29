import json
from pathlib import Path
from collections import Counter, defaultdict


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PREDICTIONS_FILE = (
    BASE_DIR
    / "ai"
    / "evaluation"
    / "test_predictions_v4.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "ai"
    / "evaluation"
    / "error_analysis_v4.json"
)


# ============================================================
# LOAD
# ============================================================

with open(
    PREDICTIONS_FILE,
    "r",
    encoding="utf-8",
) as f:
    data = json.load(f)


predictions = data["predictions"]


# ============================================================
# BASIC COUNTS
# ============================================================

total = len(predictions)

correct = [
    p for p in predictions
    if p["correct"]
]

errors = [
    p for p in predictions
    if not p["correct"]
]


accuracy = (
    len(correct) / total
    if total
    else 0
)

error_rate = (
    len(errors) / total
    if total
    else 0
)


# ============================================================
# CLASS STATISTICS
# ============================================================

class_stats = defaultdict(
    lambda: {
        "total": 0,
        "correct": 0,
        "errors": 0,
        "error_rate": 0.0,
    }
)


for p in predictions:

    true_label = p["true_label"]

    class_stats[true_label]["total"] += 1

    if p["correct"]:
        class_stats[true_label]["correct"] += 1
    else:
        class_stats[true_label]["errors"] += 1


for label, stats in class_stats.items():

    stats["error_rate"] = (
        stats["errors"]
        / stats["total"]
        if stats["total"]
        else 0
    )


# ============================================================
# CONFUSION PAIRS
# ============================================================

confusion_counter = Counter()

for p in errors:

    pair = (
        p["true_label"],
        p["predicted_label"],
    )

    confusion_counter[pair] += 1


# ============================================================
# TOP CONFUSIONS
# ============================================================

top_confusions = []

for (true_label, predicted_label), count in (
    confusion_counter.most_common()
):

    top_confusions.append(
        {
            "true": true_label,
            "predicted": predicted_label,
            "count": count,
        }
    )


# ============================================================
# ERROR LIST
# ============================================================

error_list = []

for p in errors:

    error_list.append(
        {
            "asset_id": p["asset_id"],
            "true_label": p["true_label"],
            "predicted_label": p[
                "predicted_label"
            ],
            "image": p["image"],
        }
    )


# ============================================================
# CORRECT LIST
# ============================================================

correct_list = []

for p in correct:

    correct_list.append(
        {
            "asset_id": p["asset_id"],
            "label": p["true_label"],
            "image": p["image"],
        }
    )


# ============================================================
# OUTPUT
# ============================================================

result = {
    "model": "baseline_svm_v4",
    "experiment": "normalized_images_hog_svm",

    "dataset": data.get(
        "dataset",
        "VietHeritage Classification Dataset V4",
    ),

    "split": "test",

    "summary": {
        "total": total,
        "correct": len(correct),
        "errors": len(errors),
        "accuracy": accuracy,
        "error_rate": error_rate,
    },

    "class_statistics": dict(
        sorted(class_stats.items())
    ),

    "top_confusions": top_confusions,

    "errors": error_list,

    "correct": correct_list,
}


# ============================================================
# SAVE
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        result,
        f,
        ensure_ascii=False,
        indent=2,
    )


# ============================================================
# CONSOLE REPORT
# ============================================================

print("=" * 72)
print("VIETHERITAGE V4 ERROR ANALYSIS")
print("=" * 72)

print()
print("SUMMARY")
print("-" * 72)

print(f"Total:      {total}")
print(f"Correct:    {len(correct)}")
print(f"Errors:     {len(errors)}")
print(f"Accuracy:   {accuracy:.4f}")
print(f"Error rate: {error_rate:.4f}")


print()
print("CLASS STATISTICS")
print("-" * 72)

for label, stats in sorted(
    class_stats.items()
):

    print(
        f"{label:<20} "
        f"{stats['correct']}/{stats['total']} correct "
        f"| error rate = "
        f"{stats['error_rate']:.4f}"
    )


print()
print("TOP CONFUSIONS")
print("-" * 72)

if top_confusions:

    for item in top_confusions:

        print(
            f"{item['true']} "
            f"-> "
            f"{item['predicted']} "
            f": "
            f"{item['count']}"
        )

else:

    print("No confusion.")


print()
print("ERRORS")
print("-" * 72)

if error_list:

    for item in error_list:

        print(
            f"{item['asset_id']:<28} "
            f"{item['true_label']:<18} "
            f"-> "
            f"{item['predicted_label']}"
        )

else:

    print("No errors.")


print()
print("=" * 72)
print("OUTPUT")
print("=" * 72)

print(OUTPUT_FILE)