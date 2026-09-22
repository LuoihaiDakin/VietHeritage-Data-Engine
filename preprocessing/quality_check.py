import cv2
import os


def quality_check(image_path):
    """
    Check the basic quality of a heritage image.

    Checks:
    - File existence
    - Image readability
    - Resolution
    - Brightness
    - Contrast
    - Blur
    - File size
    """

    print("========================================")
    print("        IMAGE QUALITY CHECK")
    print("========================================")

    # Check file existence
    if not os.path.exists(image_path):
        print("ERROR: File does not exist.")
        return False

    # Read image
    image = cv2.imread(image_path)

    if image is None:
        print("ERROR: Cannot read image.")
        return False

    # Image dimensions
    height, width = image.shape[:2]

    print(f"Resolution: {width} x {height}")

    # File size
    file_size = os.path.getsize(image_path)

    print(
        f"File size: {file_size / (1024 * 1024):.2f} MB"
    )

    # Convert to grayscale
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Brightness
    brightness = gray.mean()

    print(
        f"Brightness: {brightness:.2f}",
        end=" "
    )

    if brightness < 50:
        print("(Too dark)")
    elif brightness > 200:
        print("(Too bright)")
    else:
        print("(OK)")

    # Contrast
    contrast = gray.std()

    print(
        f"Contrast: {contrast:.2f}",
        end=" "
    )

    if contrast < 30:
        print("(Low contrast)")
    else:
        print("(OK)")

    # Blur detection
    blur_score = cv2.Laplacian(
        gray,
        cv2.CV_64F
    ).var()

    print(
        f"Sharpness score: {blur_score:.2f}",
        end=" "
    )

    if blur_score < 100:
        print("(Possibly blurry)")
    else:
        print("(OK)")

    # Resolution check
    print(
        f"Resolution check: ",
        end=""
    )

    if width < 500 or height < 500:
        print("(Low resolution)")
    else:
        print("(OK)")

    print("========================================")

    return True