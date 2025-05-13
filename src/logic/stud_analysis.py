import numpy as np


def find_missing_and_extra_studs(reference_studs, detected_studs, tolerance_radius=40):
    """
    Compares reference studs with detected studs to find matches, missing, and extra studs.

    Args:
        reference_studs (list): List of reference stud positions as (x, y).
        detected_studs (list): List of detected stud positions as (x, y).
        tolerance_radius (int): Radius to determine if detected studs match a reference stud.

    Returns:
        tuple: (matched, missing, extra), where:
            - matched: List of tuples [(detected, reference)].
            - missing: List of studs in reference but not detected.
            - extra: List of studs detected but not part of the reference.
    """
    matched = []
    missing = []
    extra = list(detected_studs)

    for ref in reference_studs:
        found_match = False
        for det in detected_studs:
            distance = np.linalg.norm(np.array(ref) - np.array(det))  # Euclidean distance
            if distance <= tolerance_radius:
                matched.append((det, ref))
                extra.remove(det)
                found_match = True
                break
        if not found_match:
            missing.append(ref)

    return matched, missing, extra



"""def find_missing_and_extra_studs(reference_studs, detected_studs):
    
    # Compares reference studs with detected studs and identifies matched, missing, and extra studs.
    # 
    # Args:
    #     reference_studs (list): List of reference stud positions.
    #     detected_studs (list): List of detected stud positions.
    # 
    # Returns:
    #     tuple: (matched, missing, extra) where:
    #         - matched: List of studs present in both reference and detected.
    #         - missing: List of studs in reference but not in detected.
    #         - extra: List of studs in detected but not in reference.
    # 
    matched = [stud for stud in detected_studs if stud in reference_studs]
    missing = [stud for stud in reference_studs if stud not in detected_studs]
    extra = [stud for stud in detected_studs if stud not in reference_studs]
    return matched, missing, extra"""