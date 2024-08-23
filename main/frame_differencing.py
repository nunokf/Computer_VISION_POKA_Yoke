import cv2
import numpy as np
import matplotlib.pyplot as plt


import cv2
import numpy as np

def detect_poke_pen_lines(image_before, image_after, target_size=(224, 224), line_threshold=100,
                          min_length_threshold=10, max_length_threshold=50, angle_range=(0, np.pi / 4), type="poka"):
    """
    Detect and visualize the pickup action by comparing two images.

    Parameters:
    - image_before: Image before the pickup action (PIL or numpy array).
    - image_after: Image after the pickup action (PIL or numpy array).
    - target_size: Tuple indicating the size to which both images should be resized.
    - line_threshold: Threshold for the Hough Line Transform.
    - min_length_threshold: Minimum length of lines to consider.
    - max_length_threshold: Maximum length of lines to consider.
    - angle_range: Tuple (min_angle, max_angle) defining the range of angles to keep in radians.
    - type: Specifies "poka" or "pen" movement.
    """
    # Convert the PIL image to a numpy array if necessary
    img_np_before = np.array(image_before)
    img_np_after = np.array(image_after)

    # Convert to RGB if the image is in grayscale
    if img_np_before.ndim == 2 or img_np_before.shape[2] == 1:  # Check if image is grayscale
        img_before = cv2.cvtColor(img_np_before, cv2.COLOR_GRAY2RGB)
    else:
        img_before = img_np_before

    if img_np_after.ndim == 2 or img_np_after.shape[2] == 1:  # Check if image is grayscale
        img_after = cv2.cvtColor(img_np_after, cv2.COLOR_GRAY2RGB)
    else:
        img_after = img_np_after

    # Resize the images to the target size
    img_before = cv2.resize(img_np_before, target_size)
    img_after = cv2.resize(img_np_after, target_size)

    # Convert to grayscale
    gray_before = cv2.cvtColor(img_before, cv2.COLOR_BGR2GRAY)
    gray_after = cv2.cvtColor(img_after, cv2.COLOR_BGR2GRAY)

    # Compute the absolute difference between the images
    diff = cv2.absdiff(gray_after, gray_before)

    # Apply Canny edge detection to the difference image
    edges = cv2.Canny(diff, 150, 160, apertureSize=3)

    # Apply Hough Line Transform to detect lines in the edge-detected image
    lines = cv2.HoughLines(edges, 1.5, np.pi / 180, line_threshold)

    small_lines = []

    # Initialize variables for the line length and angle
    detected_line_length = None
    detected_theta = None


    # Offset to shift the line position if needed
    x_offset = 0  # Adjust this value as needed
    y_offset = 0

    # Set angle ranges based on the type
    if type == "pen":
        angle_range = [0.1, np.pi/2]  # Approx range for pen movement
    elif type == "poka":
        angle_range = [np.pi / 2, np.pi]  # Approx range for poka movement

    if lines is not None:
        height, width = img_after.shape[:2]

        # Set a scaling factor based on the image resolution
        scale_factor = np.sqrt(height ** 2 + width ** 2) / 2000  # Adjust this scaling factor as needed

        for line in lines:
            rho, theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho

            # Adjust the length of the line based on the image resolution
            length = 100 * scale_factor  # Dynamically adjust the length

            # Calculate the endpoints of the line
            x1 = int(x0 + length * (-b)) + x_offset
            y1 = int(y0 + length * (a)) + y_offset
            x2 = int(x0 - length * (-b)) + x_offset
            y2 = int(y0 - length * (a)) + y_offset

            # Calculate the actual length of the line segment
            line_length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


            # Filter lines based on length and angle orientation
            # Filter lines based on length and angle orientation
            if min_length_threshold <= line_length <= max_length_threshold and angle_range[0] <= theta <= angle_range[1]:
                detected_line_length = line_length
                detected_theta = theta
                #print(f"Detected Line Length: {line_length}, Angle: {theta}")
                break  # Exit after finding the first valid line


    return detected_line_length, detected_theta
                #print(f"Line length Target : {line_length}, Angle: {theta}, THIS")

    # Return lines were detected


# Example usage
#image_path_before = '/Users/nunofernandes/PycharmProjects/challenge_vc/frames_5_xyz_w_cropped/frame_00051.jpg'
#image_path_after = '/Users/nunofernandes/PycharmProjects/challenge_vc/frames_5_xyz_w_cropped/frame_00052.jpg'

#detect_and_visualize_pickup(image_path_before, image_path_after, length_threshold=63, type="pen")