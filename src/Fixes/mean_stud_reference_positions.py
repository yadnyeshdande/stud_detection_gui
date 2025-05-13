import os
import numpy as np


def calculate_generalized_reference_positions(labels_dir):
    """
    Calculates generalized reference positions (mean coordinates) for studs based on YOLO annotation files.

    Parameters:
        labels_dir (str): Path to the directory containing YOLO annotation .txt files.

    Returns:
        list of tuples: Generalized reference positions as (x, y).
    """
    all_positions = []

    # Fetch all .txt files in the directory
    all_files = [f for f in os.listdir(labels_dir) if f.endswith('.txt')]

    # Iterate through each file and extract stud center positions
    for file_name in all_files:
        file_path = os.path.join(labels_dir, file_name)
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Extract center positions (x, y) from YOLO annotations
        positions = []
        for line in lines:
            data = line.strip().split()
            if len(data) >= 5:
                # YOLO file format: <class> <x_center> <y_center> <width> <height>
                x_center, y_center = float(data[1]), float(data[2])
                positions.append((x_center, y_center))

        # Append positions for this file
        all_positions.append(positions)

    # Calculate mean positions for each stud index
    generalized_positions = []
    num_labels = len(all_positions[0])  # Assuming each file has the same number of labeled studs

    for i in range(num_labels):
        x_coords = [positions[i][0] for positions in all_positions]
        y_coords = [positions[i][1] for positions in all_positions]

        # Calculate mean x and y
        mean_x = np.mean(x_coords)
        mean_y = np.mean(y_coords)
        generalized_positions.append((mean_x, mean_y))

    return generalized_positions


# Example Usage
if __name__ == "__main__":
    labels_directory = r"D:\Digitalization\Python\stud_detection_gui\src\labels"
    generalized_positions = calculate_generalized_reference_positions(labels_directory)
    print("Generalized Reference Positions:")
    for idx, pos in enumerate(generalized_positions, start=1):
        print(f"Stud {idx}: {pos}")