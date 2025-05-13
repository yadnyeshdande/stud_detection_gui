from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import pyqtSlot, QTimer, Qt
import cv2
import os
from datetime import datetime



class CameraWindow(QDialog):
    def __init__(self, save_directory, parent=None):
        super(CameraWindow, self).__init__(parent)

        self.setWindowTitle("Camera Preview")
        self.setGeometry(100, 100, 640, 480)
        self.save_directory = save_directory
        self.image_captured = None  # Stores the path of the captured image
        self.timer = None
        self.cap = None

        # Set up the layout
        self.layout = QVBoxLayout(self)

        # Display widget for the live camera preview
        self.camera_preview_label = QLabel(self)
        self.camera_preview_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.camera_preview_label)

        # Capture button to take a photo
        self.capture_button = QPushButton("Capture", self)
        self.layout.addWidget(self.capture_button)
        self.capture_button.clicked.connect(self.capture_image)

        # Start the camera on initialization
        self.start_camera()

    @pyqtSlot()
    def start_camera(self):
        """
        Starts the camera feed and updates the preview label.
        """
        try:
            self.cap = cv2.VideoCapture(0)  # Open the default camera (camera index 0)
            if not self.cap.isOpened():
                raise Exception("Could not access the camera.")

            # Start a timer to update the preview periodically
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_preview)
            self.timer.start(30)  # Update preview every 30 milliseconds
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start the camera: {str(e)}")
            self.close()

    @pyqtSlot()
    def update_preview(self):
        """
        Captures a frame from the camera feed and updates the QLabel with the live preview.
        """
        ret, frame = self.cap.read()
        if ret:
            # Convert the frame to RGB and create a QImage
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, channel = rgb_image.shape
            step = channel * w
            q_image = QImage(rgb_image.data, w, h, step, QImage.Format_RGB888)

            # Display the live preview in the QLabel
            self.camera_preview_label.setPixmap(QPixmap.fromImage(q_image))
        else:
            QMessageBox.warning(self, "Warning", "Failed to read frame from the camera.")

    @pyqtSlot()
    def capture_image(self):
        """
        Captures the current frame, saves it, and closes the camera window.
        """
        try:
            ret, frame = self.cap.read()
            if ret:
                # Generate a unique file name using datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"captured_image_{timestamp}.jpg"
                save_path = os.path.join(self.save_directory, file_name)

                # Save the image to the directory
                cv2.imwrite(save_path, frame)
                self.image_captured = save_path

                QMessageBox.information(self, "Success", f"Image captured and saved at:\n{save_path}")
                self.close()
            else:
                QMessageBox.warning(self, "Warning", "Failed to capture the image.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while capturing the image: {str(e)}")

    def closeEvent(self, event):
        """
        Handles cleanup when the dialog is closed. Stops the camera and releases resources.
        """
        if self.timer:
            self.timer.stop()
        if self.cap and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        event.accept()