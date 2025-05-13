# Predefined reference stud positions based on YOLO annotations
reference_studs = [
    (39, 59), (125, 59), (173, 125), (146, 214), (30, 329),
    (162, 327), (111, 386), (327, 255), (290, 291), (352, 290),
    (594, 207), (520, 216), (461, 264), (480, 324), (566, 337),
    (553, 43), (277, 154), (335, 156)
]
"""
   Returns the predefined reference stud positions.

   Returns:
       list of tuples: Reference stud positions as (x, y).
   """
# Additional parameters for range and circle detection
DETECTION_RANGE = 20  # Increase the range for matching stud positions
CIRCLE_DIAMETER = 50  # Enlarge the circle diameter for stud visualization


def get_reference_positions():
    """
    Function to get predefined reference stud positions.

    Returns:
        list of tuples: Reference stud positions as (x, y).
    """
    return reference_studs


def get_detection_parameters():
    """
    Function to get detection parameters like range and circle diameter.

    Returns:
        dict: A dictionary containing 'DETECTION_RANGE' and 'CIRCLE_DIAMETER'.
    """
    return {
        "DETECTION_RANGE": DETECTION_RANGE,
        "CIRCLE_DIAMETER": CIRCLE_DIAMETER,
    }

