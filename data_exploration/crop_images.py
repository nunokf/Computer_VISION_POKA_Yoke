from PIL import Image
import os

def parse_txt_file(txt_file):
    """
    Parses a YOLO detection .txt file to extract bounding box coordinates.

    Parameters:
    - txt_file (str): Path to the .txt file containing YOLO detection results.

    Returns:
    - List of tuples: Each tuple contains (class_id, x_center, y_center, width, height)
    """
    detections = []
    with open(txt_file, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) >= 5:
                class_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])
                detections.append((class_id, x_center, y_center, width, height))
    return detections


from PIL import Image
import os


def crop_hand_region(image_path, detections, output_dir, width_reduction=0.8, height_reduction=0.6, move_factor=1):
    """
    Crops the region around both hands based on YOLO detections and saves the cropped image with reduced bounding box size.
    Moves the bounding box inward to be more distant from the body.

    Parameters:
    - image_path (str): Path to the original image.
    - detections (list): List of tuples containing YOLO detections.
    - output_dir (str): Directory to save the cropped image.
    - width_reduction (float): Fraction of the bounding box width to reduce.
    - height_reduction (float): Fraction of the bounding box height to reduce.
    - move_factor (float): Fraction to adjust the bounding box position to move it away from the body.
    """
    image = Image.open(image_path)
    width, height = image.size

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize variables for the combined bounding box
    min_x = width
    min_y = height
    max_x = 0
    max_y = 0

    for class_id, x_center, y_center, box_width, box_height in detections:
        if class_id not in [0, 1]:  # Assuming class_id 0 and 1 represent hands
            continue

        # Convert YOLO format to pixel coordinates
        x_center *= width
        y_center *= height
        box_width *= width
        box_height *= height

        # Compute the bounding box coordinates
        x_min = int(x_center - box_width / 2)
        y_min = int(y_center - box_height / 2)
        x_max = int(x_center + box_width / 2)
        y_max = int(y_center + box_height / 2)

        # Update the combined bounding box
        min_x = min(min_x, x_min)
        min_y = min(min_y, y_min)
        max_x = max(max_x, x_max)
        max_y = max(max_y, y_max)

    # Adjust the width and height of the bounding box
    box_width = max_x - min_x
    box_height = max_y - min_y

    # Calculate new dimensions
    new_box_width = box_width - width_reduction * box_width
    new_box_height = box_height - height_reduction * box_height

    # Compute the amount to reduce for width and height
    width_reduction_amount = (box_width - new_box_width) / 2
    height_reduction_amount = (box_height - new_box_height) / 2

    # Adjust coordinates
    min_x += width_reduction_amount  # Move the left side inward
    max_x -= width_reduction_amount  # Move the right side inward
    min_y += height_reduction_amount  # Move the top side inward
    max_y -= height_reduction_amount  # Move the bottom side inward

    # Move the bounding box further from the center to avoid body
    move_x = (max_x - min_x) * move_factor
    move_y = (max_y - min_y) * move_factor

    min_x -= move_x
    max_x += move_x
    min_y -= move_y
    max_y += move_y

    # Ensure that the adjusted bounding box is within image bounds
    min_x = max(min_x, 0)
    min_y = max(min_y, 0)
    max_x = min(max_x, width)
    max_y = min(max_y, height)

    cropped_image = image.crop((min_x, min_y, max_x, max_y))

    return cropped_image

# example usage
#txt_dir = '/Users/nunofernandes/PycharmProjects/challenge_vc/runs/detect/predict4/labels/frame_00644.txt'
#image_path = '/Users/nunofernandes/PycharmProjects/challenge_vc/frames_5_xyz_w/frame_00646.jpg'
#image_path = '/Users/nunofernandes/PycharmProjects/challenge_vc/challenge_hands/train/images/epedal_cima_mp4-0016_jpg.rf.e399ff5981fb3a9a926720c8d0517d3d.jpg'
#output_dir = '/Users/nunofernandes/PycharmProjects/challenge_vc/cropped'

#detections = parse_txt_file(txt_dir)
#crop_hand_region(image_path, detections, output_dir, width_reduction=0.8,height_reduction=0.6, move_factor = 1)