import cv2

from processing.edge_processing import process_edges


input_path = "outputs/test_001/restored.png"
output_path = "outputs/test_001/edges_test.png"


image = cv2.imread(input_path)

if image is None:
    raise ValueError(
        f"Cannot read image: {input_path}"
    )

edges = process_edges(image)

cv2.imwrite(
    output_path,
    edges
)

print("Edge processing completed.")
print(f"Output: {output_path}")