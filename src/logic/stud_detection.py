from ultralytics import YOLO
import numpy as np


def detect_studs(image_path, model_path="models/best.pt"):
    """
    Detect studs in an image using the YOLO model.

    Parameters:
        image_path (str): Path to the input image.
        model_path (str): Path to the trained YOLO model weights.

    Returns:
        list of tuples: List of detected stud positions as (x, y).
    """
    # Load the trained YOLO model
    model = YOLO(model_path)
    results = model.predict(image_path)

    # Extract stud center positions from bounding boxes
    detected_studs = []
    for box in results[0].boxes.xywh.numpy():
        x_center, y_center, _, _ = box
        detected_studs.append((int(x_center), int(y_center)))

    return detected_studs


"""def detect_studs(image_path, model_path=r"D:/Digitalization/Python/stud_counter_app/models/best.pt"):
    
    # Detect studs in an image using the YOLO model.
    # 
    # Parameters:
    # image_path (str): Path to the input image.
    # model_path (str): Path to the trained YOLO model weights.
    # 
    # Returns:
    # detected_studs (list of tuples): List of detected stud positions as (x, y).
    
    from ultralytics import YOLO
    import numpy as np

    model = YOLO(model_path)  # Load the trained YOLO model
    results = model.predict(image_path)

    # Extract detected stud center positions from bounding boxes
    detected_studs = []
    for box in results[0].boxes.xywh.numpy():
        x_center, y_center, _, _ = box
        detected_studs.append((int(x_center), int(y_center)))

    return detected_studs"""