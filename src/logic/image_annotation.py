import cv2
import os


def get_unique_filename(output_dir, base_name="annotated_image", extension=".jpg"):
    """
    Generates a unique filename to prevent overwriting existing files.

    Parameters:
        output_dir (str): Directory where the file will be saved.
        base_name (str): Base name of the file (default: "annotated_image").
        extension (str): File extension (default: ".jpg").

    Returns:
        str: Unique filename (e.g., "annotated_image(1).jpg").
    """
    counter = 0
    while True:
        # Generate file name
        if counter == 0:
            file_name = f"{base_name}{extension}"
        else:
            file_name = f"{base_name}({counter}){extension}"

        file_path = os.path.join(output_dir, file_name)
        if not os.path.exists(file_path):
            return file_path  # Return as soon as an unused file name is found
        counter += 1


def annotate_image(image_path, reference_studs, detected_studs, matched, missing, extra,
                   output_dir="stud_detection_gui/output"):
    """
    Annotates an image with detection results and saves it with a unique name.

    Parameters:
        image_path (str): Path to the input image.
        reference_studs (list): Reference stud positions as (x, y).
        detected_studs (list): Detected stud positions.
        matched (list): List of matched studs as [(detected, reference)].
        missing (list): List of missing studs as (x, y).
        extra (list): List of extra studs as (x, y).
        output_dir (str): Directory to save the output annotated image.

    Returns:
        str: Path to the saved annotated image.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create unique filename for the output image
    output_path = get_unique_filename(output_dir)

    # Load the image
    image = cv2.imread(image_path)

    # Draw annotations
    # for ref in reference_studs:
    #     cv2.circle(image, ref, 5, (255, 0, 0), 1)  # Blue for reference studs

    for det, ref in matched:
        cv2.circle(image, det, 5, (0, 255, 0), 1)  # Green for matched studs

    for miss in missing:
        cv2.circle(image, miss, 5, (0, 0, 255), 1)  # Red for missing studs

    for ext in extra:
        cv2.circle(image, ext, 5, (255, 0, 255), 1)  # Purple for extra studs

    # Save the annotated image with the unique file name
    cv2.imwrite(output_path, image)
    print(f"Annotated image saved at: {output_path}")
    return output_path

"""import cv2


def annotate_image(image_path, reference_studs, detected_studs, matched, missing, extra,
                   output_path="output/annotated_image.jpg"):
    
    # Annotates an image with detection results, highlighting:
    #     - Reference positions (Blue).
    #     - Matched studs (Green).
    #     - Missing studs (Red).
    #     - Extra detected studs (Purple).
    # 
    # Parameters:
    #     image_path (str): Path to the input image.
    #     reference_studs (list): Reference stud positions as (x, y).
    #     detected_studs (list): Detected stud positions.
    #     matched (list): List of matched studs as [(detected, reference)].
    #     missing (list): List of missing studs as (x, y).
    #     extra (list): List of extra studs as (x, y).
    #     output_path (str): Path to save the output annotated image.
    # 
    # Load the image
    image = cv2.imread(image_path)

    # Draw reference positions (Blue)
    for ref in reference_studs:
        cv2.circle(image, ref, radius=5, color=(255, 0, 0), thickness=1)

    # Draw matched studs (Green)
    for det, ref in matched:
        cv2.circle(image, det, radius=5, color=(0, 255, 0), thickness=1)

    # Draw missing studs (Red)
    for miss in missing:
        cv2.circle(image, miss, radius=5, color=(0, 0, 255), thickness=1)

    # Draw extra detections (Purple)
    for ext in extra:
        cv2.circle(image, ext, radius=5, color=(255, 0, 255), thickness=1)

    # Save the annotated image
    output_path = "stud_detection_gui/output/annotated_image.jpg"
    cv2.imwrite(output_path, image)
    print(f"Annotated image saved to {output_path}")
    return output_path
"""

"""def annotate_image(image_path, reference, detected, matched, missing, extra, output_path):
    
    # Annotates an image with reference, detected, missing, and extra studs.
    # 
    # Parameters:
    # image_path (str): Path to the input image.
    # reference (list of tuples): Reference stud positions as (x, y).
    # detected (list of tuples): Detected stud positions.
    # matched (list of tuples): Matched studs [(detected, reference)].
    # missing (list of tuples): Missing reference studs.
    # extra (list of tuples): Extra detected studs.
    # output_path (str): Path to save the output annotated image.
    # 
    import cv2

    image = cv2.imread(image_path)

    # Draw reference positions (Blue)
    for ref in reference:
        cv2.circle(image, ref, radius=5, color=(255, 0, 0), thickness=1)  # Blue

    # Draw matched studs (Green)
    for det, ref in matched:
        cv2.circle(image, det, radius=5, color=(0, 255, 0), thickness=1)  # Green

    # Draw missing studs (Red)
    for miss in missing:
        cv2.circle(image, miss, radius=5, color=(0, 0, 255), thickness=1)  # Red

    # Draw extra detections (Purple)
    for ext in extra:
        cv2.circle(image, ext, radius=5, color=(255, 0, 255), thickness=1)  # Purple

    cv2.imwrite(output_path, image)
    print(f"Annotated image saved to {output_path}")"""