import cv2

from processing.vectorization import vectorize_mask


input_path = "outputs/test_001/mask_test.png"
output_path = "outputs/test_001/pattern_test.svg"


mask = cv2.imread(
    input_path,
    cv2.IMREAD_GRAYSCALE
)

if mask is None:
    raise ValueError(
        f"Cannot read mask: {input_path}"
    )


vectorize_mask(
    mask,
    output_path
)


print("Vectorization completed.")
print(f"SVG: {output_path}")