
"""Video Detection with hid relay"""
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, pyqtSlot, QThread, pyqtSignal
import cv2
import time
from logic.stud_detection import detect_studs
from logic.reference_positions import get_reference_positions
from logic.stud_analysis import find_missing_and_extra_studs
import pyhid_usb_relay

class CameraPreview(QThread):
    """
    A thread that continuously fetches video frames and performs stud detection only once per minute.
    """
    frame_ready = pyqtSignal(object)  # Signal to send raw or detected frames to the main window

    def __init__(self):
        super(CameraPreview, self).__init__()
        self.running = True
        self.camera = cv2.VideoCapture(0)
        self.last_detection_time = 0  # Tracks the last detection time
        self.last_detected_frame = None  # Stores the last detected frame (to display during idle time)

    def run(self):
        while self.running:
            ret, frame = self.camera.read()
            if ret:
                current_time = time.time()

                # Perform detection only once every minute
                if current_time - self.last_detection_time >=5: # 60 seconds interval
                    self.last_detection_time = current_time
                    self.last_detected_frame = self.perform_detection(frame)  # Run the detection logic

                # Show the last detected frame (or raw input frame if never detected)
                display_frame = self.last_detected_frame if self.last_detected_frame is not None else frame
                rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                self.frame_ready.emit(rgb_frame)  # Emit the frame to the GUI window

            else:
                break
    #
    # def perform_detection(self, frame):
    #     """
    #     Perform stud detection on the current frame and return the processed (annotated) frame.
    #     """
    #     reference_studs = get_reference_positions()
    #     try:
    #         detected_studs = detect_studs(frame)  # Detect studs in the frame
    #         matched, missing, extra = find_missing_and_extra_studs(reference_studs, detected_studs)
    #
    #         # Annotate the frame with detection results
    #         for ref in reference_studs:
    #             # Draw a reference circle (red) around the reference stud
    #             cv2.circle(frame, ref, 10, (0, 255, 0),0) # Thickness 2 for an outlined circle
    #
    #         for det, ref in matched:
    #             # Draw a green circle for matched studs
    #             cv2.circle(frame, det, 10, (0, 255, 0), 2)  # Green circle for detected matched studs
    #
    #         for miss in missing:
    #             # Draw a red circle for missing studs
    #             cv2.circle(frame, miss, 10, (0, 0, 255), 2)  # Red circle for missing studs
    #
    #         for ext in extra:
    #             # Draw a purple circle for extra studs
    #             # cv2.circle(frame, ext, 10, (255, 0, 255), 2)  # Purple circle for extra studs
    #
    #             # Check if all 18 studs are matched
    #             if len(matched) == 18 and len(missing) == 0:
    #                 status_text = "OK"
    #                 status_color = (0, 255, 0)  # Green
    #             else:
    #                 status_text = "NOT OK"
    #                 status_color = (0, 0, 255)  # Red
    #
    #             # Write "OK" or "NOT OK" in large text
    #             font = cv2.FONT_HERSHEY_SIMPLEX
    #             cv2.putText(frame, status_text, (50, 50), font, 2, status_color, 3, cv2.LINE_AA)
    #
    #             # Write regular status information for matched/missing/extra studs
    #             info_text = f"Matched: {len(matched)}, Missing: {len(missing)}" #Extra: {len(extra)}
    #             cv2.putText(frame, info_text, (50, 100), font, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    #
    #         print("Detection performed.")
    #         return frame
    #     except Exception as e:
    #         print(f"Error in detection: {e}")
    #         return frame  # Return the unannotated frame if detection fails

    def perform_detection(self, frame):
        """
        Perform stud detection on the current frame and return the processed (annotated) frame.
        """

        reference_studs = get_reference_positions()
        try:
            detected_studs = detect_studs(frame)  # Detect studs in the frame
            matched, missing, extra = find_missing_and_extra_studs(reference_studs, detected_studs)

            # Annotate the frame with detection results
            for ref in reference_studs:
                cv2.circle(frame, ref, 10, (0, 255, 0), 0)  # Reference positions in green

            for det, ref in matched:
                cv2.circle(frame, det, 10, (0, 255, 0), 2)  # Matched in green

            for miss in missing:
                cv2.circle(frame, miss, 10, (0, 0, 255), 2)  # Missing in red

            # Relay control logic
            try:
                relay = pyhid_usb_relay.find()
                if len(matched) == 18 and len(missing) == 0:
                    status_text = "OK"
                    status_color = (0, 255, 0)
                    relay.set_state(1, True)  # Turn ON Relay 1
                    relay.set_state(2, False)  # Turn OFF Relay 2
                else:
                    status_text = "NOT OK"
                    status_color = (0, 0, 255)
                    relay.set_state(1, False)  # Turn OFF Relay 1
                    relay.set_state(2, True)  # Turn ON Relay 2
            except Exception as relay_error:
                print(f"Relay control error: {relay_error}")
                status_text = "NOT OK"
                status_color = (0, 0, 255)

            # Draw text overlays
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, status_text, (50, 50), font, 2, status_color, 3, cv2.LINE_AA)
            info_text = f"Matched: {len(matched)}, Missing: {len(missing)}"
            cv2.putText(frame, info_text, (50, 100), font, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

            print("Detection performed.")
            return frame
        except Exception as e:
            print(f"Error in detection: {e}")
            return frame  # Return the unannotated frame if detection fails

    def stop(self):
        """
        Stops the camera and thread safely.
        """
        self.running = False
        self.quit()
        self.wait()
        self.camera.release()


class MainWindow(QMainWindow):
    """
    The main GUI window for displaying the real-time video feed and stud detection results.
    """

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Real-Time Stud Detection (Once per Minute)")
        self.setGeometry(100, 100, 800, 600)

        # Main Layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Image Display
        self.image_display = QLabel(self)
        self.image_display.setScaledContents(True)  # Scale image to fit QLabel
        self.layout.addWidget(self.image_display)

        # Status Label
        self.status_label = QLabel("Status: Waiting for detection...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        # Inspection Label for OK/NOT OK
        self.inspection_label = QLabel("", self)
        self.inspection_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.inspection_label.setAlignment(Qt.AlignCenter)  # Center-align the label text
        self.layout.addWidget(self.inspection_label)

        # Start the camera thread
        self.camera_thread = CameraPreview()
        self.camera_thread.frame_ready.connect(self.update_frame)
        self.camera_thread.start()

    @pyqtSlot(object)
    def update_frame(self, frame):
        """
        Updates the QLabel with the latest frame (processed or unprocessed) from the camera.
        """
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.image_display.setPixmap(QPixmap.fromImage(q_image))

    def closeEvent(self, event):
        """
        Clean up resources when the window is closed.
        """
        self.camera_thread.stop()
        super(MainWindow, self).closeEvent(event)

# Relay input
"""import os
import time
import cv2
import threading
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, pyqtSlot, QThread, pyqtSignal
from logic.stud_detection import detect_studs
from logic.reference_positions import get_reference_positions
from logic.stud_analysis import find_missing_and_extra_studs
import hid  # For USB relay control

class CameraPreview(QThread):
    frame_ready = pyqtSignal(object)

    def __init__(self, relay_sensor, relay_indicator):
        super(CameraPreview, self).__init__()
        self.running = False
        self.camera = None
        self.relay_sensor = relay_sensor
        self.relay_indicator = relay_indicator

    def run(self):
        while True:
            # Check if the sensor relay is triggered
            if self.is_object_detected():
                self.running = True
                self.camera = cv2.VideoCapture(0)
                time.sleep(30)  # Wait for 30 seconds
                ret, frame = self.camera.read()
                if ret:
                    processed_frame = self.perform_detection(frame)
                    rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                    self.frame_ready.emit(rgb_frame)
                self.stop_camera()
            time.sleep(1)  # Polling interval for sensor

    def is_object_detected(self):

        # Check if the proximity sensor relay is triggered.

        try:
            data = self.relay_sensor.read(8)
            return data[0] == 1  # Assuming relay sends 1 when triggered
        except Exception as e:
            print(f"Error reading sensor relay: {e}")
            return False

    def perform_detection(self, frame):
        reference_studs = get_reference_positions()
        try:
            detected_studs = detect_studs(frame)
            matched, missing, extra = find_missing_and_extra_studs(reference_studs, detected_studs)

            # Annotate the frame
            for ref in reference_studs:
                cv2.circle(frame, ref, 10, (0, 0, 255), 2)
            for det, ref in matched:
                cv2.circle(frame, det, 10, (0, 255, 0), 2)
            for miss in missing:
                cv2.circle(frame, miss, 10, (0, 0, 255), 2)
            for ext in extra:
                cv2.circle(frame, ext, 10, (255, 0, 255), 2)

            # Determine OK/NOT OK status
            if len(matched) == 18 and len(missing) == 0:
                self.set_indicator("OK")
            else:
                self.set_indicator("NOT OK")

            return frame
        except Exception as e:
            print(f"Error in detection: {e}")
            return frame

    def set_indicator(self, status):

        # Control the RYB light lamp based on the detection status.

        try:
            if status == "OK":
                self.relay_indicator.write([0x00, 0x01])  # Green light
            else:
                self.relay_indicator.write([0x00, 0x02])  # Red light
        except Exception as e:
            print(f"Error controlling indicator relay: {e}")

    def stop_camera(self):

        # Stop the camera safely.

        if self.camera:
            self.camera.release()
        self.running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Production-Ready Stud Detection")
        self.setGeometry(100, 100, 800, 600)

        # Main Layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Image Display
        self.image_display = QLabel(self)
        self.image_display.setScaledContents(True)
        self.layout.addWidget(self.image_display)

        # Status Label
        self.status_label = QLabel("Status: Waiting for detection...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        # Initialize relays
        self.relay_sensor = hid.device()
        self.relay_indicator = hid.device()
        self.relay_sensor.open(0x16C0, 0x05DF)  # Replace with your sensor relay's VID and PID
        self.relay_indicator.open(0x16C0, 0x05DF)  # Replace with your indicator relay's VID and PID

        # Start the camera thread
        self.camera_thread = CameraPreview(self.relay_sensor, self.relay_indicator)
        self.camera_thread.frame_ready.connect(self.update_frame)
        self.camera_thread.start()

    @pyqtSlot(object)
    def update_frame(self, frame):
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.image_display.setPixmap(QPixmap.fromImage(q_image))

    def closeEvent(self, event):
        self.camera_thread.running = False
        self.camera_thread.wait()
        self.relay_sensor.close()
        self.relay_indicator.close()
        super(MainWindow, self).closeEvent(event)"""

# video detection
"""from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, pyqtSlot, QThread, pyqtSignal
import cv2
import time
from logic.stud_detection import detect_studs
from logic.reference_positions import get_reference_positions
from logic.stud_analysis import find_missing_and_extra_studs


class CameraPreview(QThread):

    # A thread that continuously fetches video frames and performs stud detection only once per minute.

    frame_ready = pyqtSignal(object)  # Signal to send raw or detected frames to the main window

    def __init__(self):
        super(CameraPreview, self).__init__()
        self.running = True
        self.camera = cv2.VideoCapture(0)
        self.last_detection_time = 0  # Tracks the last detection time
        self.last_detected_frame = None  # Stores the last detected frame (to display during idle time)

    def run(self):
        while self.running:
            ret, frame = self.camera.read()
            if ret:
                current_time = time.time()

                # Perform detection only once every minute
                if current_time - self.last_detection_time >= 120:  # 60 seconds interval
                    self.last_detection_time = current_time
                    self.last_detected_frame = self.perform_detection(frame)  # Run the detection logic

                # Show the last detected frame (or raw input frame if never detected)
                display_frame = self.last_detected_frame if self.last_detected_frame is not None else frame
                rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                self.frame_ready.emit(rgb_frame)  # Emit the frame to the GUI window

            else:
                break

    def perform_detection(self, frame):

        # Perform stud detection on the current frame and return the processed (annotated) frame.

        reference_studs = get_reference_positions()
        try:
            detected_studs = detect_studs(frame)  # Detect studs in the frame
            matched, missing, extra = find_missing_and_extra_studs(reference_studs, detected_studs)

            # Annotate the frame with detection results
            for ref in reference_studs:
                # Draw a reference circle (red) around the reference stud
                cv2.circle(frame, ref, 10, (0, 255, 0), -1)  # Thickness 2 for an outlined circle

            for det, ref in matched:
                # Draw a green circle for matched studs
                cv2.circle(frame, det, 10, (0, 255, 0), 2)  # Green circle for detected matched studs

            for miss in missing:
                # Draw a red circle for missing studs
                cv2.circle(frame, miss, 10, (0, 0, 255), 2)  # Red circle for missing studs

            for ext in extra:
                # Draw a purple circle for extra studs
                # cv2.circle(frame, ext, 10, (255, 0, 255), 2)  # Purple circle for extra studs

                # Check if all 18 studs are matched
                if len(matched) == 18 and len(missing) == 0:
                    status_text = "OK"
                    status_color = (0, 255, 0)  # Green
                else:
                    status_text = "NOT OK"
                    status_color = (0, 0, 255)  # Red

                # Write "OK" or "NOT OK" in large text
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, status_text, (50, 50), font, 2, status_color, 3, cv2.LINE_AA)

                # Write regular status information for matched/missing/extra studs
                info_text = f"Matched: {len(matched)}, Missing: {len(missing)}"  # Extra: {len(extra)}
                cv2.putText(frame, info_text, (50, 100), font, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

            print("Detection performed.")
            return frame
        except Exception as e:
            print(f"Error in detection: {e}")
            return frame  # Return the unannotated frame if detection fails

    def stop(self):

        # Stops the camera and thread safely.

        self.running = False
        self.quit()
        self.wait()
        self.camera.release()


class MainWindow(QMainWindow):

    # The main GUI window for displaying the real-time video feed and stud detection results.


    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Real-Time Stud Detection (Once per Minute)")
        self.setGeometry(100, 100, 800, 600)

        # Main Layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Image Display
        self.image_display = QLabel(self)
        self.image_display.setScaledContents(True)  # Scale image to fit QLabel
        self.layout.addWidget(self.image_display)

        # Status Label
        self.status_label = QLabel("Status: Waiting for detection...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        # Inspection Label for OK/NOT OK
        self.inspection_label = QLabel("", self)
        self.inspection_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.inspection_label.setAlignment(Qt.AlignCenter)  # Center-align the label text
        self.layout.addWidget(self.inspection_label)

        # Start the camera thread
        self.camera_thread = CameraPreview()
        self.camera_thread.frame_ready.connect(self.update_frame)
        self.camera_thread.start()

    @pyqtSlot(object)
    def update_frame(self, frame):

        # Updates the QLabel with the latest frame (processed or unprocessed) from the camera.

        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.image_display.setPixmap(QPixmap.fromImage(q_image))

    def closeEvent(self, event):

        # Clean up resources when the window is closed.

        self.camera_thread.stop()
        super(MainWindow, self).closeEvent(event)
"""


"""Running Code Best Code"""
# from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QMessageBox
# from PyQt5.QtGui import QPixmap
# from PyQt5.QtCore import Qt, pyqtSlot, QThread, pyqtSignal
# import cv2
# import os
# from datetime import datetime
# from logic.stud_detection import detect_studs
# from logic.image_annotation import annotate_image
# from logic.reference_positions import get_reference_positions
# from logic.stud_analysis import find_missing_and_extra_studs
#
#
# class CameraPreview(QThread):
#     """
#     A thread for handling the live camera preview using OpenCV.
#     """
#     frame_ready = pyqtSignal(object)  # Frame update signal
#
#     def __init__(self):
#         super(CameraPreview, self).__init__()
#         self.running = True
#         self.camera = cv2.VideoCapture(0)
#
#     def run(self):
#         while self.running:
#             ret, frame = self.camera.read()
#             if ret:
#                 # Emit the frame in RGB format (PyQt handles RGB images)
#                 rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#                 self.frame_ready.emit(rgb_frame)
#             else:
#                 break
#
#     def stop(self):
#         self.running = False
#         self.quit()
#         self.wait()
#         self.camera.release()
#
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super(MainWindow, self).__init__()
#         self.setWindowTitle("Stud Detection Application")
#         self.setGeometry(100, 100, 800, 600)
#
#         self.image_path = None
#         self.output_path = "stud_detection_gui/output"
#
#         # Ensure the output directory exists
#         os.makedirs(self.output_path, exist_ok=True)
#
#         # Main Layout
#         self.central_widget = QWidget(self)
#         self.setCentralWidget(self.central_widget)
#         self.layout = QVBoxLayout(self.central_widget)
#
#         # Welcome Label
#         self.label = QLabel("Welcome to the Stud Detection Application", self)
#         self.layout.addWidget(self.label)
#
#         # Image Display
#         self.image_display = QLabel(self)
#         self.image_display.setScaledContents(True)  # Scale image to fit QLabel
#         self.layout.addWidget(self.image_display)
#
#         # Open Camera Button
#         self.open_camera_button = QPushButton("Open Camera", self)
#         self.layout.addWidget(self.open_camera_button)
#         self.open_camera_button.clicked.connect(self.open_camera_preview)
#
#         # Status Label
#         self.status_label = QLabel("Status: Ready", self)
#         self.layout.addWidget(self.status_label)
#
#         self.camera_window = None  # Placeholder for camera preview window
#
#     @pyqtSlot()
#     def open_camera_preview(self):
#         """
#         Opens a new window with a live camera preview for capturing images.
#         """
#         self.camera_window = CameraWindow(self.process_captured_image)
#         self.camera_window.show()
#
#     def process_captured_image(self, image_path):
#         """
#         Processes the captured image for stud detection and annotation.
#         """
#         self.image_path = image_path
#         self.status_label.setText("Status: Processing image...")
#         try:
#             reference_studs = get_reference_positions()
#             detected_studs = detect_studs(self.image_path)
#             matched, missing, extra = find_missing_and_extra_studs(reference_studs, detected_studs)
#
#             output_path = annotate_image(self.image_path, reference_studs, detected_studs, matched, missing, extra)
#             self.status_label.setText(f"Annotated image saved to: {output_path}")
#
#             # Show annotated image
#             pixmap = QPixmap(output_path)
#             self.image_display.setPixmap(pixmap)
#             self.label.setText(f"Matched: {len(matched)}, Missing: {len(missing)}, Extra: {len(extra)}")
#         except Exception as e:
#             self.status_label.setText(f"Error: {str(e)}")
#
#
# class CameraWindow(QWidget):
#     """
#     A window displaying a live camera preview and providing a capture button.
#     """
#
#     def __init__(self, callback):
#         super(CameraWindow, self).__init__()
#         self.setWindowTitle("Camera Preview")
#         self.setGeometry(150, 150, 640, 480)
#         self.callback = callback
#
#         # Layout
#         self.layout = QVBoxLayout(self)
#
#         # Live Camera Feed Display
#         self.camera_label = QLabel(self)
#         self.camera_label.setScaledContents(True)
#         self.layout.addWidget(self.camera_label)
#
#         # Capture Button
#         self.capture_button = QPushButton("Capture", self)
#         self.layout.addWidget(self.capture_button)
#         self.capture_button.clicked.connect(self.capture_image)
#
#         # Camera Thread
#         self.camera_thread = CameraPreview()
#         self.camera_thread.frame_ready.connect(self.update_frame)
#         self.camera_thread.start()
#
#         self.latest_frame = None  # Store the last frame displayed in the preview
#
#     @pyqtSlot(object)
#     def update_frame(self, frame):
#         """
#         Updates the camera preview label with the latest frame.
#         """
#         from PyQt5.QtGui import QImage
#         height, width, channel = frame.shape
#         bytes_per_line = 3 * width
#         q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
#         self.camera_label.setPixmap(QPixmap.fromImage(q_image))
#
#         # Update the latest frame here
#         self.latest_frame = frame
#
#     def capture_image(self):
#         """
#         Captures the current frame being displayed in the camera preview and processes it.
#         """
#         if self.latest_frame is not None:
#             # Save the last frame as an image file
#             timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#             image_path = os.path.join(os.getcwd(), f"captured_image_{timestamp}.jpg")
#             frame_bgr = cv2.cvtColor(self.latest_frame, cv2.COLOR_RGB2BGR)  # Convert RGB back to BGR for saving
#             cv2.imwrite(image_path, frame_bgr)
#
#             QMessageBox.information(self, "Image Captured", f"Image saved to: {image_path}")
#
#             # Callback to process the captured image
#             self.camera_thread.stop()
#             self.callback(image_path)
#             self.close()
#         else:
#             QMessageBox.critical(self, "Capture Error", "No frame available to capture.")
#
#     def closeEvent(self, event):
#         """
#         Cleans up resources when the window is closed.
#         """
#         self.camera_thread.stop()
#         super(CameraWindow, self).closeEvent(event)


"""from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QMessageBox
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

    # A thread for handling the live camera preview using OpenCV.

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

    @pyqtSlot()
    def open_camera_preview(self):

        # Opens a new window with a live camera preview for capturing images.

        self.camera_window = CameraWindow(self.process_captured_image)
        self.camera_window.show()

    def process_captured_image(self, image_path):

        # Processes the captured image for stud detection and annotation.

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
            self.label.setText(f"Matched: {len(matched)}, Missing: {len(missing)}, Extra: {len(extra)}")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")


class CameraWindow(QWidget):

    # A window displaying a live camera preview and providing a capture button.


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

        # Updates the camera preview label with the latest frame.

        from PyQt5.QtGui import QImage
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.camera_label.setPixmap(QPixmap.fromImage(q_image))

        # Update the latest frame here
        self.latest_frame = frame

    def capture_image(self):

        # Captures the current frame being displayed in the camera preview and processes it.

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

        # Cleans up resources when the window is closed.

        self.camera_thread.stop()
        super(CameraWindow, self).closeEvent(event)
"""