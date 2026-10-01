import json
from pathlib import Path
from collections import Counter, defaultdict

import matplotlib.pyplot as plt


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

PREDICTIONS_FILE = BASE_DIR / "ai" / "evaluation" / "test_predictions_v5.json"

CONFUSION_JSON = BASE_DIR / "ai" / "evaluation" / "confusion_matrix_v5.json"
CONFUSION_PNG = BASE_DIR / "ai" / "evaluation" / "confusion_matrix_v5.png"
ERROR_JSON = BASE_DIR / "ai" / "evaluation" / "error_analysis_v5.json"


# ============================================================
# LOAD PREDICTIONS
# ============================================================

with open(PREDICTIONS_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

predictions = data["predictions"]

if not predictions:
    raise ValueError("No predictions found in test_predictions_v5.json")


# ============================================================
# CLASSES
# ============================================================

classes = sorted(
    set(
        [x["true_label"] for x in predictions]
        + [x["predicted_label"] for x in predictions]
    )
)

# Keep all expected V5 classes if present in metadata/predictions.
preferred_order = [
    "dong_ho",
    "phu_dieu_rong",
    "phuong",
    "rong_viet_nam",
    "sen",
    "trong_dong",
]

ordered_classes = [c for c in preferred_order if c in classes]

# Add anything unexpected at the end.
ordered_classes += [c for c in classes if c not in ordered_classes]

classes = ordered_classes


# ============================================================
# CONFUSION MATRIX
# ============================================================

matrix = {
    true_label: {
        predicted_label: 0
        for predicted_label in classes
    }
    for true_label in classes
}

for item in predictions:
    true_label = item["true_label"]
    predicted_label = item["predicted_label"]

    matrix[true_label][predicted_label] += 1


# ============================================================
# BASIC METRICS
# ============================================================

total = len(predictions)
correct = sum(1 for x in predictions if x["correct"])
errors = total - correct

accuracy = correct / total if total else 0.0


# ============================================================
# CLASS STATISTICS
# ============================================================

class_stats = {}

for label in classes:
    total_class = sum(
        1
        for x in predictions
        if x["true_label"] == label
    )

    correct_class = sum(
        1
        for x in predictions
        if x["true_label"] == label
        and x["correct"]
    )

    error_class = total_class - correct_class

    class_stats[label] = {
        "total": total_class,
        "correct": correct_class,
        "errors": error_class,
        "accuracy": (
            correct_class / total_class
            if total_class
            else 0.0
        ),
        "error_rate": (
            error_class / total_class
            if total_class
            else 0.0
        ),
    }


# ============================================================
# CONFUSION PAIRS
# ============================================================

confusion_pairs = Counter()

for item in predictions:
    true_label = item["true_label"]
    predicted_label = item["predicted_label"]

    if true_label != predicted_label:
        confusion_pairs[
            f"{true_label} -> {predicted_label}"
        ] += 1


confusion_pairs_list = [
    {
        "true_label": pair.split(" -> ")[0],
        "predicted_label": pair.split(" -> ")[1],
        "count": count,
    }
    for pair, count in confusion_pairs.most_common()
]


# ============================================================
# CONFUSION MATRIX JSON
# ============================================================

confusion_output = {
    "experiment": data.get("experiment", "V5"),
    "model": data.get("model"),
    "dataset": data.get("dataset"),
    "split": data.get("split"),
    "total_predictions": total,
    "correct": correct,
    "errors": errors,
    "accuracy": accuracy,
    "classes": classes,
    "matrix": matrix,
    "class_statistics": class_stats,
    "confusion_pairs": confusion_pairs_list,
}

with open(CONFUSION_JSON, "w", encoding="utf-8") as f:
    json.dump(
        confusion_output,
        f,
        ensure_ascii=False,
        indent=2,
    )


# ============================================================
# ERROR ANALYSIS
# ============================================================

error_samples = [
    {
        "asset_id": x["asset_id"],
        "category": x.get("category"),
        "image": x.get("image"),
        "true_label": x["true_label"],
        "predicted_label": x["predicted_label"],
        "error_type": (
            f"{x['true_label']} -> {x['predicted_label']}"
        ),
    }
    for x in predictions
    if not x["correct"]
]


# Group errors by true label.
errors_by_true_label = defaultdict(list)

for error in error_samples:
    errors_by_true_label[error["true_label"]].append(error)


# Group errors by predicted label.
errors_by_predicted_label = defaultdict(list)

for error in error_samples:
    errors_by_predicted_label[
        error["predicted_label"]
    ].append(error)


# ============================================================
# ERROR COUNTS
# ============================================================

error_counts = Counter(
    error["error_type"]
    for error in error_samples
)


error_summary = [
    {
        "true_label": pair.split(" -> ")[0],
        "predicted_label": pair.split(" -> ")[1],
        "count": count,
    }
    for pair, count in error_counts.most_common()
]


# ============================================================
# ERROR ANALYSIS JSON
# ============================================================

error_output = {
    "experiment": "V5",
    "model": data.get("model"),
    "dataset": data.get("dataset"),
    "split": data.get("split"),

    "summary": {
        "total_predictions": total,
        "correct": correct,
        "errors": errors,
        "accuracy": accuracy,
        "error_rate": (
            errors / total
            if total
            else 0.0
        ),
    },

    "class_statistics": class_stats,

    "error_summary": error_summary,

    "errors_by_true_label": dict(errors_by_true_label),

    "errors_by_predicted_label": dict(errors_by_predicted_label),

    "errors": error_samples,
}


with open(ERROR_JSON, "w", encoding="utf-8") as f:
    json.dump(
        error_output,
        f,
        ensure_ascii=False,
        indent=2,
    )


# ============================================================
# CONFUSION MATRIX PNG
# ============================================================

n = len(classes)

fig_size = max(6, n * 1.5)

fig, ax = plt.subplots(
    figsize=(fig_size, fig_size)
)

matrix_values = [
    [matrix[true_label][predicted_label] for predicted_label in classes]
    for true_label in classes
]

image = ax.imshow(matrix_values)

ax.set_xticks(range(n))
ax.set_yticks(range(n))

ax.set_xticklabels(
    classes,
    rotation=45,
    ha="right",
)

ax.set_yticklabels(classes)

ax.set_xlabel("Predicted label")
ax.set_ylabel("True label")

ax.set_title(
    f"V5 Confusion Matrix — Accuracy: {accuracy:.4f}"
)

# Write values inside cells.
for i in range(n):
    for j in range(n):
        value = matrix_values[i][j]

        ax.text(
            j,
            i,
            str(value),
            ha="center",
            va="center",
        )

fig.colorbar(image, ax=ax)

plt.tight_layout()

plt.savefig(
    CONFUSION_PNG,
    dpi=200,
    bbox_inches="tight",
)

plt.close()


# ============================================================
# CONSOLE SUMMARY
# ============================================================

print("=" * 70)
print("VIETHERITAGE V5 ERROR ANALYSIS")
print("=" * 70)

print(f"Total predictions : {total}")
print(f"Correct           : {correct}")
print(f"Errors            : {errors}")
print(f"Accuracy          : {accuracy:.4f}")
print(f"Error rate        : {errors / total:.4f}")
print()

print("CLASS STATISTICS")
print("-" * 70)

for label in classes:
    s = class_stats[label]

    print(
        f"{label:20} "
        f"{s['correct']}/{s['total']} correct | "
        f"accuracy = {s['accuracy']:.4f} | "
        f"errors = {s['errors']}"
    )

print()

print("CONFUSION PAIRS")
print("-" * 70)

if confusion_pairs_list:
    for pair in confusion_pairs_list:
        print(
            f"{pair['true_label']} -> "
            f"{pair['predicted_label']} : "
            f"{pair['count']}"
        )
else:
    print("No errors.")

print()

print("ERROR SAMPLES")
print("-" * 70)

for error in error_samples:
    print(
        f"{error['asset_id']:25} "
        f"{error['true_label']:18} -> "
        f"{error['predicted_label']}"
    )

print()
print("OUTPUT FILES")
print("-" * 70)

print(f"Confusion JSON : {CONFUSION_JSON}")
print(f"Confusion PNG  : {CONFUSION_PNG}")
print(f"Error JSON     : {ERROR_JSON}")

print("=" * 70)