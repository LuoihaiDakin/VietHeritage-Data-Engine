import cv2

from processing.evaluation import evaluate_image
from processing.quality_classifier import classify_quality


images = {
    "original": "dataset/images/dong_ho/dong_ho_001.jpg",
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

    result = classify_quality(
        metrics
    )

    print()
    print("=" * 60)
    print(name.upper())
    print("=" * 60)

    print(
        f"Quality: {result['quality']}"
    )

    print(
        f"Score: {result['score']}"
    )

    print(
        "Component scores:"
    )

    for key, value in result[
        "component_scores"
    ].items():

        print(
            f"  {key}: {value}"
        )