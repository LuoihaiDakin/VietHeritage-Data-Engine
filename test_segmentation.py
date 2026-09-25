import cv2

from processing.segmentation import segment_image


input_path = "outputs/test_001/normalized.png"

segmented_path = "outputs/test_001/segmented_test.png"
mask_path = "outputs/test_001/mask_test.png"


image = cv2.imread(input_path)

if image is None:
    raise ValueError(
        f"Cannot read image: {input_path}"
    )


segmented, mask = segment_image(image)


cv2.imwrite(
    segmented_path,
    segmented
)

cv2.imwrite(
    mask_path,
    mask
)


print("Segmentation completed.")
print(f"Segmented: {segmented_path}")
print(f"Mask: {mask_path}")