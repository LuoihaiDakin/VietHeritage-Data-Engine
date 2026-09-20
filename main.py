import cv2
from restoration.edge_restoration import restore_edges
from preprocessing.cleaning import (
    denoise_image,
    adjust_brightness_contrast
)

from preprocessing.quality_check import quality_check


IMAGE_PATH = "test.jpg"
OUTPUT_PATH = "cleaned_test.jpg"


# Load image
image = cv2.imread(IMAGE_PATH)

if image is None:
    print("Cannot load image.")
    exit()


# Cleaning
cleaned_image = denoise_image(image)

cleaned_image = adjust_brightness_contrast(cleaned_image)

cleaned_image = denoise_image(image)

cleaned_image = adjust_brightness_contrast(cleaned_image)

# Save cleaned image
cv2.imwrite(OUTPUT_PATH, cleaned_image)

# Edge restoration
restored_image, edges = restore_edges(cleaned_image)

# Save results
cv2.imwrite("restored_test.jpg", restored_image)
cv2.imwrite("edges_test.jpg", edges)

print("=== VietHeritage Data Engine ===")
print()
print("Cleaning completed!")
print(f"Saved: {OUTPUT_PATH}")
print()

print("=== Quality Check: Cleaned Image ===")

quality_check(OUTPUT_PATH)