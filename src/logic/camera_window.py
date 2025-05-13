import os

os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.dirname(os.__file__) + "/Qt/plugins"

from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer
from logic.camera_handler import CameraHandler
import cv2


class CameraWindow(QDialog):
    def __init__(self, output_directory, parent=None):
        """
        Initialize the CameraWindow.

        :param output_directory: Directory to save captured images.
        :param parent: Parent widget.
        """
        super(CameraWindow, self).__init__(parent)
        self.setWindowTitle("Camera Capture")
        self.setGeometry(200, 200, 640, 480)
        self.camera_handler = CameraHandler(output_directory)
        self.output_directory = output_directory
        self.image_captured = None  # For storing path of captured image

        # UI Elements
        self.layout = QVBoxLayout(self)
        self.camera_preview_label = QLabel(self)  # For displaying the camera preview
        self.camera_preview_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.camera_preview_label)

        # Capture Button
        self.capture_button = QPushButton("Capture Image", self)
        self.layout.addWidget(self.capture_button)
        self.capture_button.clicked.connect(self.capture_image)

        # Stop Camera Button
        self.stop_button = QPushButton("Stop Camera", self)
        self.layout.addWidget(self.stop_button)
        self.stop_button.clicked.connect(self.stop_camera)

        # Camera Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera_preview)

        # Start capturing preview
        self.start_camera()

    def start_camera(self):
        """
        Start the camera preview and the timer.
        """
        try:
            self.camera_handler.start_camera_preview()
            self.timer.start(30)  # Timer triggers preview update every 30ms
        except RuntimeError as e:
            QMessageBox.critical(self, "Camera Error", str(e))

    def update_camera_preview(self):
        """
        Get the latest frame from the camera and update the QLabel for live preview.
        """
        if self.camera_handler.cap is not None:
            ret, frame = self.camera_handler.cap.read()
            if ret:
                # Convert the frame to RGB and create a QImage
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = rgb_frame.shape
                bytes_per_line = channel * width
                qt_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

                # Update QLabel with the new frame
                self.camera_preview_label.setPixmap(QPixmap.fromImage(qt_image))

    def capture_image(self):
        """
        Use CameraHandler to capture the current frame and save it.
        """
        try:
            image_path = self.camera_handler.capture_image()
            QMessageBox.information(self, "Image Captured", f"Image saved to: {image_path}")
            self.image_captured = image_path  # Pass the captured image path to main window if needed
        except RuntimeError as e:
            QMessageBox.critical(self, "Capture Error", str(e))

    def stop_camera(self):
        """
        Stop the camera and close the window.
        """
        self.timer.stop()
        self.camera_handler.stop_camera_preview()
        self.close()




"""from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt
from logic.camera_handler import CameraHandler
import cv2


class CameraWindow(QDialog):
    def __init__(self, output_directory, parent=None):
        
        # Initialize the CameraWindow.
        # 
        # :param output_directory: Directory to save captured images.
        # :param parent: Parent widget.
        
        super(CameraWindow, self).__init__(parent)
        self.setWindowTitle("Camera Capture")
        self.setGeometry(200, 200, 640, 480)
        self.camera_handler = CameraHandler(output_directory)
        self.output_directory = output_directory

        # UI Elements
        self.layout = QVBoxLayout(self)
        self.camera_preview = QLabel(self)  # For displaying the camera preview
        self.layout.addWidget(self.camera_preview)

        self.capture_button = QPushButton("Capture Image", self)
        self.layout.addWidget(self.capture_button)
        self.capture_button.clicked.connect(self.capture_image)

        self.stop_button = QPushButton("Stop Camera", self)
        self.layout.addWidget(self.stop_button)
        self.stop_button.clicked.connect(self.stop_camera)

        # Camera Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera_preview)

    def start_camera_preview(self):
        
            # Start the camera preview.
            
        self.cap = cv2.VideoCapture(0)  # Open the webcam (default camera)
        if not self.cap.isOpened():
            raise RuntimeError("Unable to access the camera")
        print("[DEBUG] Camera started successfully")

    def start_camera(self):
        
        # Start the camera and timer for live preview.
        
        try:
            print("[DEBUG] Starting camera...")
            self.camera_handler.start_camera_preview() # Start camera preview
            self.timer.start(30)  # Update every 30ms for smooth preview
            print("[DEBUG] Timer started for camera preview")
        except RuntimeError as e:
            QMessageBox.critical(self, "Camera Error", str(e))

    def update_camera_preview(self):

        # Updates the camera preview display in the QLabel.

        if self.camera_handler.cap is not None:
            ret, frame = self.camera_handler.cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB for PyQt
                height, width, channel = rgb_image.shape
                bytes_per_line = channel * width
                qt_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)
                self.camera_preview.setPixmap(pixmap)

    def capture_image(self):

        # Capture an image from the live preview.

        try:
            image_path = self.camera_handler.capture_image()
            QMessageBox.information(self, "Image Captured", f"Image saved to: {image_path}")
            # Assign the captured image path so it can be worked with in the main window
            self.image_captured = image_path

        except RuntimeError as e:
            QMessageBox.critical(self, "Capture Error", str(e))

    def stop_camera(self):

        # Stops the camera preview and closes the window.

        self.timer.stop()
        self.camera_handler.stop_camera_preview()
        self.close()"""