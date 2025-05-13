from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSlot, QThread, pyqtSignal
import cv2
import os
from datetime import datetime
from logic.stud_detection import detect_studs
from logic.image_annotation import annotate_image
from logic.reference_positions import get_reference_positions
from logic.stud_analysis import find_missing_and_extra_studs


class CameraPreview(QThread):
    """
    A thread for handling the live camera preview using OpenCV.
    """
    frame_ready = pyqtSignal(object)  # Frame update signal

    def __init__(self):
        super(CameraPreview, self).__init__()
        self.running = True
        self.camera = cv2.VideoCapture(0)

    def run(self):
        while self.running:
            ret, frame = self.camera.read()
            if ret:
                # Emit the frame in RGB format (PyQt handles RGB images)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.frame_ready.emit(rgb_frame)
            else:
                break

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
        self.camera.release()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Stud Detection Application")
        self.setGeometry(100, 100, 800, 600)

        self.image_path = None
        self.output_path = "stud_detection_gui/output"

        # Ensure the output directory exists
        os.makedirs(self.output_path, exist_ok=True)

        # Main Layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Welcome Label
        self.label = QLabel("Welcome to the Stud Detection Application", self)
        self.layout.addWidget(self.label)

        # Image Display
        self.image_display = QLabel(self)
        self.image_display.setScaledContents(True)  # Scale image to fit QLabel
        self.layout.addWidget(self.image_display)

        # Open Camera Button
        self.open_camera_button = QPushButton("Open Camera", self)
        self.layout.addWidget(self.open_camera_button)
        self.open_camera_button.clicked.connect(self.open_camera_preview)

        # Status Label
        self.status_label = QLabel("Status: Ready", self)
        self.layout.addWidget(self.status_label)

        self.camera_window = None  # Placeholder for camera preview window

        # Inspection Label for OK/NOT OK
        self.inspection_label = QLabel("", self)
        self.inspection_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.inspection_label.setAlignment(Qt.AlignCenter)  # Center-align the label text
        self.layout.addWidget(self.inspection_label)

        self.camera_window = None  # Placeholder for camera preview window

    @pyqtSlot()
    def open_camera_preview(self):
        """
        Opens a new window with a live camera preview for capturing images.
        """
        self.camera_window = CameraWindow(self.process_captured_image)
        self.camera_window.show()

    def process_captured_image(self, image_path):
        """
        Processes the captured image for stud detection and annotation.
        """
        self.image_path = image_path
        self.status_label.setText("Status: Processing image...")
        try:
            reference_studs = get_reference_positions()
            detected_studs = detect_studs(self.image_path)
            matched, missing, extra = find_missing_and_extra_studs(reference_studs, detected_studs)

            output_path = annotate_image(self.image_path, reference_studs, detected_studs, matched, missing, extra)
            self.status_label.setText(f"Annotated image saved to: {output_path}")

            # Show annotated image
            pixmap = QPixmap(output_path)
            self.image_display.setPixmap(pixmap)

            # Update the inspection label
            if missing:
                self.inspection_label.setText("NOT OK")
                self.inspection_label.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")
            else:
                self.inspection_label.setText("OK")
                self.inspection_label.setStyleSheet("color: green; font-size: 18px; font-weight: bold;")

            self.label.setText(f"Matched: {len(matched)}, Missing: {len(missing)}, Extra: {len(extra)}")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")


class CameraWindow(QWidget):
    """
    A window displaying a live camera preview and providing a capture button.
    """

    def __init__(self, callback):
        super(CameraWindow, self).__init__()
        self.setWindowTitle("Camera Preview")
        self.setGeometry(150, 150, 640, 480)
        self.callback = callback

        # Layout
        self.layout = QVBoxLayout(self)

        # Live Camera Feed Display
        self.camera_label = QLabel(self)
        self.camera_label.setScaledContents(True)
        self.layout.addWidget(self.camera_label)

        # Capture Button
        self.capture_button = QPushButton("Capture", self)
        self.layout.addWidget(self.capture_button)
        self.capture_button.clicked.connect(self.capture_image)

        # Camera Thread
        self.camera_thread = CameraPreview()
        self.camera_thread.frame_ready.connect(self.update_frame)
        self.camera_thread.start()

        self.latest_frame = None  # Store the last frame displayed in the preview

    @pyqtSlot(object)
    def update_frame(self, frame):
        """
        Updates the camera preview label with the latest frame.
        """
        from PyQt5.QtGui import QImage
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.camera_label.setPixmap(QPixmap.fromImage(q_image))

        # Update the latest frame here
        self.latest_frame = frame

    def capture_image(self):
        """
        Captures the current frame being displayed in the camera preview and processes it.
        """
        if self.latest_frame is not None:
            # Save the last frame as an image file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = os.path.join(os.getcwd(), f"captured_image_{timestamp}.jpg")
            frame_bgr = cv2.cvtColor(self.latest_frame, cv2.COLOR_RGB2BGR)  # Convert RGB back to BGR for saving
            cv2.imwrite(image_path, frame_bgr)

            QMessageBox.information(self, "Image Captured", f"Image saved to: {image_path}")

            # Callback to process the captured image
            self.camera_thread.stop()
            self.callback(image_path)
            self.close()
        else:
            QMessageBox.critical(self, "Capture Error", "No frame available to capture.")

    def closeEvent(self, event):
        """
        Cleans up resources when the window is closed.
        """
        self.camera_thread.stop()
        super(CameraWindow, self).closeEvent(event)



"""
10:30 PM

from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSlot, Qt
from logic.stud_detection import detect_studs
from logic.image_annotation import annotate_image
from logic.reference_positions import get_reference_positions
from logic.stud_analysis import find_missing_and_extra_studs
from logic.camera_window import CameraWindow
import os
from datetime import datetime
import cv2


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Stud Detection Application")
        self.setGeometry(100, 100, 800, 600)

        self.image_path = "stud_detection_gui/input"
        self.output_path = "stud_detection_gui/output"

        # Ensure output directory exists
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        # Main Layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Welcome Label
        self.label = QLabel("Welcome to the Stud Detection Application", self)
        self.layout.addWidget(self.label)

        # Image Display
        self.image_display = QLabel(self)
        self.image_display.setScaledContents(True)  # Scale image to fit QLabel
        self.layout.addWidget(self.image_display)

        # Load Image Button
        self.load_image_button = QPushButton("Load Image", self)
        self.layout.addWidget(self.load_image_button)
        self.load_image_button.clicked.connect(self.load_image)

        # Capture from Camera Button
        self.capture_image_button = QPushButton("Capture from Camera", self)
        self.capture_image_button.setStyleSheet("QPushButton { text-decoration: underline; color: blue; }")
        self.capture_image_button.setFlat(True)
        self.layout.addWidget(self.capture_image_button)
        self.capture_image_button.clicked.connect(self.capture_from_camera)

        # Status Label
        self.status_label = QLabel("Status: Ready", self)
        self.layout.addWidget(self.status_label)

    @pyqtSlot()
    def load_image(self):
        
        # Allow the user to load an image and process it.
        
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Image", "", "Images (*.png *.jpg *.jpeg);;All Files (*)", options=options
        )

        if file_path:
            self.image_path = file_path
            self.status_label.setText("Status: Processing image...")
            self.detect_and_annotate()

    @pyqtSlot()
    def capture_from_camera(self):
        try:
            # Initialize camera (use cv2.VideoCapture for PiCamera or USB cameras)
            camera = cv2.VideoCapture(0)  # Argument can be different based on camera setup

            if not camera.isOpened():
                raise ValueError("Unable to access the camera")

            # Read a frame from the camera
            ret, frame = camera.read()

            if not ret:
                raise ValueError("Failed to capture image from camera")

            # Release the camera resource
            camera.release()

            # Generate a unique filename for the captured image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            input_image_name = f"captured_image_{timestamp}.jpg"
            input_image_path = os.path.join(os.getcwd(), input_image_name)

            # Save the captured frame
            cv2.imwrite(input_image_path, frame)
            self.image_path = input_image_path  # Also update the image path attribute

            # Update the UI to display the captured image
            self.image_display.setPixmap(QPixmap(input_image_path))
            self.status_label.setText(f"Captured image saved to: {input_image_path}")

            # Perform stud detection and annotation
            self.detect_and_annotate(input_image_path)

        except Exception as e:
            QMessageBox.critical(self, "Camera Error", f"An error occurred: {str(e)}")
            self.status_label.setText("Camera capture failed.")


    def detect_and_annotate(self):
        
        # Detects and annotates studs on the loaded image.
        
        try:
            # Detect studs and annotate the image
            reference_studs = get_reference_positions()
            detected_studs = detect_studs(self.image_path)
            matched, missing, extra = find_missing_and_extra_studs(reference_studs, detected_studs)

            output_path = annotate_image(self.image_path, reference_studs, detected_studs, matched, missing, extra)
            self.status_label.setText(f"Annotated image saved to: {output_path}")

            # Show annotated image
            pixmap = QPixmap(output_path)
            self.image_display.setPixmap(pixmap)
            self.label.setText(f"Matched: {len(matched)}, Missing: {len(missing)}, Extra: {len(extra)}")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
"""



"""
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSlot, Qt
from logic.stud_detection import detect_studs
from logic.image_annotation import annotate_image
from logic.reference_positions import get_reference_positions
from logic.stud_analysis import find_missing_and_extra_studs
from logic.camera_window import CameraWindow  # Import CameraWindow dynamically
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Stud Detection Application")
        self.setGeometry(100, 100, 800, 600)

        self.image_path = ""
        self.output_path = "stud_detection_hui/output"
        self.weights_path = "models/best.pt"  # Default YOLO model path

        # Create the output directory if it doesn't exist
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        # Main GUI Layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Labels and Buttons
        self.label = QLabel("Welcome to the Stud Detection Application", self)
        self.layout.addWidget(self.label)

        self.image_display = QLabel(self)
        self.image_display.setScaledContents(True)  # Allows the image to scale with the GUI window
        self.layout.addWidget(self.image_display)

        self.load_image_button = QPushButton("Load Image", self)
        self.layout.addWidget(self.load_image_button)
        self.load_image_button.clicked.connect(self.load_image)

        # "Capture from Camera" button styled as a hyperlink
        self.capture_image_button = QPushButton('Capture from Camera', self)
        self.capture_image_button.setStyleSheet("QPushButton { text-decoration: underline; color: blue; }")
        self.capture_image_button.setFlat(True)
        self.layout.addWidget(self.capture_image_button)
        self.capture_image_button.clicked.connect(self.capture_from_camera)

        self.status_label = QLabel("Status: Ready", self)
        self.layout.addWidget(self.status_label)

    @pyqtSlot()
    def load_image(self):
        
        # Allows the user to load an image and automatically detect and annotate studs.
        
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Image", "", "Images (*.png *.jpg *.jpeg);;All Files (*)", options=options
        )

        if file_path:
            self.image_path = file_path
            self.status_label.setText("Status: Processing image...")
            self.detect_and_annotate()

    @pyqtSlot()
    def capture_from_camera(self):
        
        # Launches the Camera Window to capture an image.
        
        try:
            # Create the output directory for storing images
            output_directory = os.path.join("D:/Digitalization/Python/stud_detection_gui/src/stud_detection_gui/input")
            os.makedirs(output_directory, exist_ok=True)

            # Open the CameraWindow for image capture
            camera_window = CameraWindow(output_directory, self)
            camera_window.exec_()  # Use exec_ to block until the dialog is closed

            # After the dialog closes, check if an image was captured (if needed)
            if hasattr(camera_window, "image_captured") and camera_window.image_captured:
                self.image_path = camera_window.image_captured
                self.status_label.setText("Status: Image captured and saved!")
            else:
                self.status_label.setText("Status: No image captured.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during image capture: {str(e)}")

    def detect_and_annotate(self):
        
        # Detects and annotates studs in the image. Displays the annotated image on the GUI and saves it to the `output` folder.
        
        try:
            # Detect studs and annotate the image
            reference_studs = get_reference_positions()
            detected_studs = detect_studs(self.image_path)
            matched, missing, extra = find_missing_and_extra_studs(reference_studs, detected_studs)

            # Annotate the image and save it with a unique file name
            output_path = annotate_image(self.image_path, reference_studs, detected_studs, matched, missing, extra)
            self.status_label.setText(f"Annotated image saved to: {output_path}")

            # Update GUI to show the annotated image
            pixmap = QPixmap(output_path)
            self.image_display.setPixmap(pixmap)
            self.label.setText(f"Matched: {len(matched)}, Missing: {len(missing)}, Extra: {len(extra)}")

        except Exception as e:
            # Handle exceptions and display error messages
            self.status_label.setText(f"Error: {str(e)}")
"""