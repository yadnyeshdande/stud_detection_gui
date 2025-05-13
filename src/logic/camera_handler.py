import cv2
from PyQt5.QtCore import QObject, pyqtSignal
import os
from datetime import datetime


class CameraHandler(QObject):
    image_captured = pyqtSignal(str)  # Signal emitted when an image is captured and saved

    def __init__(self, output_directory):

        # Initialize the CameraHandler.
        # :param output_directory: Directory where captured images will be saved.

        super(CameraHandler, self).__init__()
        self.output_directory = output_directory
        self.cap = None  # Webcam capture object
        self.timer = None
        self.current_frame = None
        os.path.join("stud_detection_gui/input")

    def start_camera_preview(self):

        # Start the camera preview.

        self.cap = cv2.VideoCapture(0)  # Open the webcam (0 for default camera)
        if not self.cap.isOpened():
            raise RuntimeError("Unable to access the camera")

    def stop_camera_preview(self):

        # Stop the camera preview and release the webcam.

        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
            self.cap = None
            cv2.destroyAllWindows()
        if not self.cap.isOpened():
            raise RuntimeError("Unable to access the camera")
        print("[DEBUG] Camera started successfully")

    def capture_image(self):

        # Captures the current frame from the camera and saves it to the output directory.
        # Emits a signal with the path of the saved image.

        if self.cap is not None: # Checks if the camera object is initialized
            ret, frame = self.cap.read()
            if ret:
                # Save the captured frame
                from datetime import datetime
                import os

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = os.path.join(self.output_directory, f"captured_{timestamp}.jpg")
                cv2.imwrite(image_path, frame)
                self.image_captured.emit(image_path)
                return image_path
            else:
                raise RuntimeError("Failed to capture an image from the camera")
        else:
            raise RuntimeError("Camera is not active")