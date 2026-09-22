import cv2
import os

from preprocessing.quality_check import quality_check
from preprocessing.cleaning import clean_image
from restoration.edge_restoration import restore_edges
from restoration.super_resolution import upscale_image
from enhancement.image_enhancement import enhance_image
from evaluation.image_metrics import compare_images


# ========================================
# Configuration
# ========================================

INPUT_IMAGE = "test.jpg"

OUTPUT_DIR = "output"

CLEANED_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "cleaned_test.jpg"
)

EDGES_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "edges_test.jpg"
)

RESTORED_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "restored_test.jpg"
)

ENHANCED_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "enhanced_test.jpg"
)

UPSCALED_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "upscaled_test.jpg"
)


def main():

    print()
    print("========================================")
    print("      VietHeritage Data Engine")
    print("      Image Processing Pipeline")
    print("========================================")
    print()

    # ========================================
    # Create output directory
    # ========================================

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    # ========================================
    # 1. Quality Check
    # ========================================

    print("[1/6] Running quality check...")

    quality_result = quality_check(
        INPUT_IMAGE
    )

    if not quality_result:
        print()
        print("Pipeline stopped.")
        return

    print("Quality check completed.")
    print()

    # ========================================
    # Load image
    # ========================================

    image = cv2.imread(
        INPUT_IMAGE
    )

    if image is None:
        print(
            "ERROR: Cannot load input image."
        )
        return

    # ========================================
    # 2. Cleaning
    # ========================================

    print("[2/6] Cleaning image...")

    cleaned = clean_image(
        image
    )

    cv2.imwrite(
        CLEANED_OUTPUT,
        cleaned
    )

    print(
        f"Saved: {CLEANED_OUTPUT}"
    )
    print()

    # ========================================
    # 3. Edge Restoration
    # ========================================

    print("[3/6] Restoring edges...")

    restored, edges = restore_edges(
        cleaned
    )

    # Save actual edge map
    cv2.imwrite(
        EDGES_OUTPUT,
        edges
    )

    # Save restored color image
    cv2.imwrite(
        RESTORED_OUTPUT,
        restored
    )

    print(
        f"Saved: {EDGES_OUTPUT}"
    )

    print(
        f"Saved: {RESTORED_OUTPUT}"
    )

    print()

    # ========================================
    # 4. Enhancement
    # ========================================

    print("[4/6] Enhancing image...")

    enhanced = enhance_image(
        restored
    )

    cv2.imwrite(
        ENHANCED_OUTPUT,
        enhanced
    )

    print(
        f"Saved: {ENHANCED_OUTPUT}"
    )

    print()

    # ========================================
    # 5. Upscaling
    # ========================================

    print("[5/6] Upscaling image...")

    upscaled = upscale_image(
        enhanced,
        scale=2
    )

    cv2.imwrite(
        UPSCALED_OUTPUT,
        upscaled
    )

    print(
        f"Saved: {UPSCALED_OUTPUT}"
    )

    print()

    # ========================================
    # 6. Evaluation
    # ========================================

    print("[6/6] Calculating image metrics...")

    metrics = compare_images(
        image,
        upscaled
    )

    print()
    print("========================================")
    print("            IMAGE METRICS")
    print("========================================")

    print(
        f"Original sharpness : "
        f"{metrics['original_sharpness']:.2f}"
    )

    print(
        f"Processed sharpness: "
        f"{metrics['processed_sharpness']:.2f}"
    )

    print(
        f"Original brightness : "
        f"{metrics['original_brightness']:.2f}"
    )

    print(
        f"Processed brightness: "
        f"{metrics['processed_brightness']:.2f}"
    )

    print(
        f"Original contrast : "
        f"{metrics['original_contrast']:.2f}"
    )

    print(
        f"Processed contrast: "
        f"{metrics['processed_contrast']:.2f}"
    )

    print("========================================")

    print()
    print("Pipeline completed successfully.")
    print()

    print("Generated files:")

    print(
        f"- {CLEANED_OUTPUT}"
    )

    print(
        f"- {EDGES_OUTPUT}"
    )

    print(
        f"- {RESTORED_OUTPUT}"
    )

    print(
        f"- {ENHANCED_OUTPUT}"
    )

    print(
        f"- {UPSCALED_OUTPUT}"
    )

    print()


if __name__ == "__main__":
    main()