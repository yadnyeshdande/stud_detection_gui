# Input YOLO annotation data
yolo_annotations = """
0 0.061719 0.123958 0.017188 0.031250
0 0.196094 0.123958 0.026562 0.031250
0 0.270313 0.261458 0.031250 0.043750
0 0.228125 0.446875 0.050000 0.043750
0 0.046875 0.686458 0.043750 0.043750
0 0.254688 0.682292 0.043750 0.047917
0 0.174219 0.806250 0.026562 0.050000
0 0.511719 0.532292 0.035937 0.043750
0 0.454688 0.607292 0.037500 0.031250
0 0.550000 0.606250 0.031250 0.037500
0 0.928125 0.433333 0.034375 0.037500
0 0.814063 0.451042 0.050000 0.043750
0 0.721094 0.551042 0.042188 0.052083
0 0.750000 0.675000 0.043750 0.050000
0 0.885938 0.703125 0.050000 0.056250
0 0.865625 0.090625 0.040625 0.043750
0 0.433594 0.321875 0.032813 0.043750
0 0.524219 0.325000 0.035937 0.045833
"""

# Image dimensions (adjust to your values)
image_width = 640  # example image width in pixels
image_height = 480  # example image height in pixels

# Parse annotations and convert to pixel positions
reference_studs = []  # to store (x, y) positions of studs in pixels

for line in yolo_annotations.strip().split('\n'):
    parts = line.split()
    class_id = int(parts[0])  # class ID (not used here since all are "0")
    x_center_norm = float(parts[1])
    y_center_norm = float(parts[2])

    # Convert normalized coordinates to pixel values
    x_pixel = int(x_center_norm * image_width)
    y_pixel = int(y_center_norm * image_height)

    # Add to reference studs list
    reference_studs.append((x_pixel, y_pixel))

# Print the calculated reference positions
print("Reference stud positions (in pixels):")
for stud_position in reference_studs:
    print(stud_position)


"""Reference stud positions (in pixels):
(39, 59)
(125, 59)
(173, 125)
(146, 214)
(30, 329)
(162, 327)
(111, 386)
(327, 255)
(290, 291)
(352, 290)
(594, 207)
(520, 216)
(461, 264)
(480, 324)
(566, 337)
(553, 43)
(277, 154)
(335, 156)"""