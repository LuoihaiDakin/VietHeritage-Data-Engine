import cv2

from processing.evaluation import evaluate_image


images = {
    "restored": "outputs/test_001/restored.png",
    "cleaned": "outputs/test_001/cleaned.png",
    "normalized": "outputs/test_001/normalized.png"
}


for name, path in images.items():

    image = cv2.imread(
        path
    )

    if image is None:
        raise ValueError(
            f"Cannot read image: {path}"
        )

    metrics = evaluate_image(
        image
    )

    print()
    print("=" * 50)
    print(name.upper())
    print("=" * 50)

    for key, value in metrics.items():
        print(
            f"{key}: {value}"
        )