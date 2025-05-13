# Stud Detection GUI

This project is a graphical user interface (GUI) application for detecting studs in images using a YOLO model. It is designed to run on a Raspberry Pi 5 and provides an intuitive interface for users to interact with the stud detection functionality.

## Project Structure

```
stud_detection_gui
├── src
│   ├── main.py                # Entry point of the application
│   ├── gui
│   │   ├── main_window.py     # Main window GUI logic
│   │   └── ui_main_window.ui   # Qt Designer file for the main window layout
│   ├── logic
│   │   ├── stud_detection.py   # Logic for detecting studs in images
│   │   │── stud_analysis.py     # Logic for position of studs with Predefined reference stud positions in images
│   │   ├── image_annotation.py  # Logic for annotating images
│   │   └── reference_positions.py # Predefined reference stud positions
│   └── resources
│       └── __init__.py        # Initialization file for resources package
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
└── .gitignore                  # Files to ignore in version control
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd stud_detection_gui
   ```

2. **Install dependencies**:
   It is recommended to use a virtual environment. You can create one using `venv` or `virtualenv`.
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Run the application**:
   Execute the main script to start the application.
   ```
   python src/main.py
   ```

## Usage

- The application allows users to load images and detect studs using the YOLO model.
- Detected studs will be annotated on the images, and users can view matched, missing, and extra studs based on predefined reference positions.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.