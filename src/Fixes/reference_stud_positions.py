# Predefined reference stud positions based on YOLO annotations
reference_studs = [
    (57, 60), (140, 61), (187, 128), (159, 212), (123, 322),
    (114, 344), (109, 355), (296, 231), (346, 224), (344, 267),
    (315, 225), (368, 219), (515, 210), (531, 276), (546, 284),
    (519, 256), (555, 259)
]
"""
   Returns the predefined reference stud positions.

   Returns:
       list of tuples: Reference stud positions as (x, y).
   """


def get_reference_positions():
    return reference_studs