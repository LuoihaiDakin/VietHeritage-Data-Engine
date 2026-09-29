import json
from pathlib import Path
from processing.pipeline import process_image


BASE_DIR = Path(__file__).resolve().parent

# Load manifest
with open(
    BASE_DIR / "ai_ready" / "classification_manifest.json",
    "r",
    encoding="utf-8",
) as f:
    data = json.load(f)


# Find assets missing normalized.png
missing = []

for asset in data["assets"]:
    asset_id = asset["asset_id"]
    output_dir = BASE_DIR / "outputs" / asset_id
    normalized_path = output_dir / "normalized.png"

    if not normalized_path.exists():
        missing.append(asset)


print("=" * 70)
print("PROCESSING MISSING NORMALIZED OUTPUTS")
print("=" * 70)
print("Missing assets:", len(missing))
print()


for i, asset in enumerate(missing, 1):
    asset_id = asset["asset_id"]

    # Category is stored in the manifest
    category = asset["category"]

    # Find original image
    image_dir = BASE_DIR / "dataset" / "images" / category

    candidates = list(image_dir.glob(f"{asset_id}.*"))

    if not candidates:
        print(f"[{i:02d}/{len(missing)}] {asset_id}")
        print("      ERROR: Original image not found")
        continue

    input_path = candidates[0]
    output_dir = BASE_DIR / "outputs" / asset_id

    print(f"[{i:02d}/{len(missing)}] Processing {asset_id}...")
    print(f"      Input:  {input_path}")

    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        process_image(
            str(input_path),
            str(output_dir),
        )

        normalized_path = output_dir / "normalized.png"

        if normalized_path.exists():
            print("      OK")
        else:
            print("      ERROR: normalized.png was not created")

    except Exception as e:
        print("      ERROR:", e)


# Verify
print()
print("=" * 70)
print("VERIFYING")
print("=" * 70)

still_missing = []

for asset in data["assets"]:
    asset_id = asset["asset_id"]

    normalized_path = (
        BASE_DIR
        / "outputs"
        / asset_id
        / "normalized.png"
    )

    if not normalized_path.exists():
        still_missing.append(asset_id)


print("Missing normalized:", len(still_missing))

for asset_id in still_missing:
    print(asset_id)

print()