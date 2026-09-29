import json
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

V3_FILE = BASE_DIR / "ai" / "evaluation" / "test_predictions_v3.json"
V4_FILE = BASE_DIR / "ai" / "evaluation" / "test_predictions_v4.json"

OUTPUT_FILE = BASE_DIR / "ai" / "evaluation" / "comparison_v3_v4.json"


# ============================================================
# LOAD
# ============================================================

with open(V3_FILE, "r", encoding="utf-8") as f:
    v3 = json.load(f)

with open(V4_FILE, "r", encoding="utf-8") as f:
    v4 = json.load(f)


v3_predictions = {
    item["asset_id"]: item
    for item in v3["predictions"]
}

v4_predictions = {
    item["asset_id"]: item
    for item in v4["predictions"]
}


# ============================================================
# FIELD HANDLERS
# ============================================================

def get_true_label(item):
    """
    V3:
        actual_category

    V4:
        true_label
    """

    if "actual_category" in item:
        return item["actual_category"]

    if "true_label" in item:
        return item["true_label"]

    raise KeyError(
        f"Cannot find actual/true label. "
        f"Available keys: {list(item.keys())}"
    )


def get_prediction(item):
    """
    V3:
        predicted_category

    V4:
        predicted_label
    """

    if "predicted_category" in item:
        return item["predicted_category"]

    if "predicted_label" in item:
        return item["predicted_label"]

    raise KeyError(
        f"Cannot find prediction field. "
        f"Available keys: {list(item.keys())}"
    )


def get_correct(item):
    return bool(item["correct"])


# ============================================================
# TEST SET CHECK
# ============================================================

v3_ids = set(v3_predictions.keys())
v4_ids = set(v4_predictions.keys())

common_ids = sorted(v3_ids & v4_ids)

v3_only = sorted(v3_ids - v4_ids)
v4_only = sorted(v4_ids - v3_ids)


print("=" * 72)
print("VIETHERITAGE V3 vs V4 COMPARISON")
print("=" * 72)

print()
print("TEST SET CHECK")
print("-" * 72)

print(f"V3 test samples:       {len(v3_ids)}")
print(f"V4 test samples:       {len(v4_ids)}")
print(f"Common test samples:    {len(common_ids)}")

if v3_only:
    print()
    print("WARNING: V3-only assets:")
    for asset_id in v3_only:
        print(f"  {asset_id}")

if v4_only:
    print()
    print("WARNING: V4-only assets:")
    for asset_id in v4_only:
        print(f"  {asset_id}")


# ============================================================
# COMPARE
# ============================================================

both_correct = []
v3_correct_v4_wrong = []
v3_wrong_v4_correct = []
both_wrong = []


for asset_id in common_ids:

    v3_item = v3_predictions[asset_id]
    v4_item = v4_predictions[asset_id]

    v3_true = get_true_label(v3_item)
    v4_true = get_true_label(v4_item)

    # --------------------------------------------------------
    # Sanity check
    # --------------------------------------------------------

    if v3_true != v4_true:
        raise ValueError(
            f"True label mismatch for {asset_id}: "
            f"V3={v3_true}, V4={v4_true}"
        )

    true_label = v3_true

    v3_prediction = get_prediction(v3_item)
    v4_prediction = get_prediction(v4_item)

    v3_correct = get_correct(v3_item)
    v4_correct = get_correct(v4_item)

    record = {
        "asset_id": asset_id,
        "true_label": true_label,

        "v3_prediction": v3_prediction,
        "v4_prediction": v4_prediction,

        "v3_correct": v3_correct,
        "v4_correct": v4_correct,

        "image": v3_item.get("image"),
    }

    # --------------------------------------------------------
    # 4 groups
    # --------------------------------------------------------

    if v3_correct and v4_correct:

        both_correct.append(record)

    elif v3_correct and not v4_correct:

        v3_correct_v4_wrong.append(record)

    elif not v3_correct and v4_correct:

        v3_wrong_v4_correct.append(record)

    else:

        both_wrong.append(record)


# ============================================================
# SUMMARY
# ============================================================

total = len(common_ids)

summary = {
    "total_common_test_samples": total,

    "both_correct": len(both_correct),

    "v3_correct_v4_wrong": len(
        v3_correct_v4_wrong
    ),

    "v3_wrong_v4_correct": len(
        v3_wrong_v4_correct
    ),

    "both_wrong": len(
        both_wrong
    ),
}


# ============================================================
# OUTPUT JSON
# ============================================================

result = {
    "experiment": "V3 RAW vs V4 NORMALIZED",

    "summary": summary,

    "both_correct": both_correct,

    "v3_correct_v4_wrong": (
        v3_correct_v4_wrong
    ),

    "v3_wrong_v4_correct": (
        v3_wrong_v4_correct
    ),

    "both_wrong": both_wrong,
}


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
# PRINT HELPER
# ============================================================

def print_group(title, items):

    print()
    print(title)
    print("-" * 72)

    if not items:
        print("None")
        return

    for item in items:

        print(
            f"{item['asset_id']:<28} "
            f"{item['true_label']:<18} "
            f"V3={item['v3_prediction']:<18} "
            f"V4={item['v4_prediction']}"
        )


# ============================================================
# RESULTS
# ============================================================

print()
print("SUMMARY")
print("-" * 72)

print(
    f"Total common test samples: "
    f"{total}"
)

print(
    f"Both correct:             "
    f"{len(both_correct)}"
)

print(
    f"V3 correct -> V4 wrong:   "
    f"{len(v3_correct_v4_wrong)}"
)

print(
    f"V3 wrong -> V4 correct:   "
    f"{len(v3_wrong_v4_correct)}"
)

print(
    f"Both wrong:               "
    f"{len(both_wrong)}"
)


print_group(
    "V3 CORRECT -> V4 WRONG",
    v3_correct_v4_wrong,
)

print_group(
    "V3 WRONG -> V4 CORRECT",
    v3_wrong_v4_correct,
)

print_group(
    "BOTH CORRECT",
    both_correct,
)

print_group(
    "BOTH WRONG",
    both_wrong,
)


# ============================================================
# OUTPUT PATH
# ============================================================

print()
print("=" * 72)
print("OUTPUT")
print("=" * 72)

print(OUTPUT_FILE)