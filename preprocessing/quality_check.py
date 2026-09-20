import cv2
import os


def quality_check(image_path):
    if not os.path.exists(image_path):
        print("ERROR: Image file not found.")
        return

    image = cv2.imread(image_path)

    if image is None:
        print("ERROR: Cannot read image.")
        return

    height, width, channels = image.shape
    file_size = os.path.getsize(image_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    brightness = gray.mean()
    contrast = gray.std()
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

    print(f"File: {image_path}")
    print(f"Resolution: {width} x {height}")
    print(f"Channels: {channels}")
    print(f"File size: {file_size / 1024:.2f} KB")
    print(f"Brightness: {brightness:.2f}")
    print(f"Contrast: {contrast:.2f}")
    print(f"Blur score: {blur_score:.2f}")

    print()

    if width < 500 or height < 500:
        print("Resolution status: LOW")
    else:
        print("Resolution status: OK")

    if brightness < 50:
        print("Brightness status: TOO DARK")
    elif brightness > 200:
        print("Brightness status: TOO BRIGHT")
    else:
        print("Brightness status: OK")

    if contrast < 30:
        print("Contrast status: LOW")
    else:
        print("Contrast status: OK")

    if blur_score < 100:
        print("Sharpness status: BLURRY")
    else:
        print("Sharpness status: OK")