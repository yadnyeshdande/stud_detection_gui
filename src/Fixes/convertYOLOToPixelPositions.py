def convert_to_pixel_positions(generalized_positions, image_width, image_height):
    """
    Converts generalized YOLO coordinates (normalized) into pixel positions.

    Parameters:
        generalized_positions (list of tuples): Normalized positions [(x, y), ...].
        image_width (int): Width of the image in pixels.
        image_height (int): Height of the image in pixels.

    Returns:
        list of tuples: Pixel positions as [(x_pixel, y_pixel), ...].
    """
    pixel_positions = []

    for x_center, y_center in generalized_positions:
        # Convert normalized coordinates to pixel values
        x_pixel = int(round(x_center * image_width))
        y_pixel = int(round(y_center * image_height))
        pixel_positions.append((x_pixel, y_pixel))

    return pixel_positions


if __name__ == "__main__":
    # Generalized reference positions from YOLO output
    generalized_positions = [
        (0.0887474368, 0.12600166720000003),
        (0.21943122880000002, 0.1280516672),
        (0.29191503839999994, 0.2657183296),
        (0.2490487424, 0.4411533264),
        (0.1918725152, 0.6718666784),
        (0.17859752, 0.7165416848),
        (0.1701349888, 0.7403766672),
        (0.46220624800000004, 0.4802633216),
        (0.54057256, 0.46753167840000004),
        (0.5381125072, 0.557069976),
        (0.4919850176, 0.46839167359999995),
        (0.574521288, 0.45714000159999996),
        (0.8048825232, 0.4384216704),
        (0.8292112831999999, 0.5741099872000001),
        (0.8523700288, 0.5919749984),
        (0.8112600176, 0.5338399952),
        (0.8679012736, 0.5390433344),
    ]

    # Define image dimensions (typically taken from a test image or training dataset)
    image_width = 640  # Example image width in pixels
    image_height = 480  # Example image height in pixels

    # Convert YOLO normalized coordinates into pixel positions
    pixel_positions = convert_to_pixel_positions(generalized_positions, image_width, image_height)

    # Print the pixel positions
    print("Generalized Reference Positions in Pixels:")
    for idx, pos in enumerate(pixel_positions, start=1):
        print(f"Stud {idx}: {pos}")