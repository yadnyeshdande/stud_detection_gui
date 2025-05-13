import cv2
import os

# Test directory
output_dir = "../stud_detection_gui/input"
os.makedirs(output_dir, exist_ok=True)

# Test camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Unable to access the camera")
else:
    ret, frame = cap.read()
    if ret:
        image_path = os.path.join(output_dir, "test_image.jpg")
        print(f"Saving test image to {image_path}")
        cv2.imwrite(image_path, frame)
    else:
        print("Failed to capture image")
    cap.release()