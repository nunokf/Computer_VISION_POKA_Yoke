import numpy as np
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

import math
def distance_moved(current_x,current_y,previous_x,previous_y, hand = "dominant"):
    x_distance_moved = current_x - previous_x
    y_distance_moved = current_y - previous_y
    distance = math.sqrt(x_distance_moved ** 2 + y_distance_moved ** 2)
    return distance


def detect_pick_up(current_x_center, current_y_center, x_centers, y_centers, non_dominant_hand_detections, frame_number,
                   height_decrease):
    """
    Detects if a pick-up movement has occurred based on changes in x, y coordinates and height.
    """
    if height_decrease > 0.02:
        x_movement = current_x_center - x_centers[-2]
        y_movement = y_centers[-2] - current_y_center
        if abs(x_movement) > 0.03 or abs(y_movement) > 0.03:
            non_dominant_hand_detections.append(frame_number)


def detect_initial_movement(current_x_center, current_y_center, x_centers, y_centers, heights, current_height,
                            hand_detections, frame_number):
    """
    Detecta o movimento inicial calculando a distância movida e invocando a detecção de levantamento se as condições forem atendidas.
    """
    distance = distance_moved(current_x_center, current_y_center, x_centers[i], y_centers[i])
    if distance > 0.2 and current_y_center < y_centers[i]:
        height_decrease = heights[-1] - current_height
        detect_pick_up(current_x_center, current_y_center, x_centers, y_centers, hand_detections, frame_number,
                       height_decrease)
        # break  # Interrompe o loop após detectar o levantamento


def get_hand_data(hand_detection):
    """Extracts the x, y coordinates and height from a hand detection."""
    x_center = hand_detection[1]
    y_center = hand_detection[2]
    height = hand_detection[4]
    width = hand_detection[3]
    return x_center, y_center, height, width


def determine_hand(hand_detections, dominant_hand_position, return_dominant=True):
    """
    Determines which hand detection to return based on the dominant hand position.

    Parameters:
    - hand_detections: List of hand detections.
    - dominant_hand_position: Either 'right' or 'left'.
    - return_dominant: If True, return the dominant hand; otherwise, return the non-dominant hand.
    """
    # Assume that the right hand is always dominant
    if dominant_hand_position == "right":
        dominant_hand = hand_detections[1] if hand_detections[1][1] > hand_detections[0][1] else hand_detections[0]
    else:
        dominant_hand = hand_detections[0] if hand_detections[0][1] > hand_detections[1][1] else hand_detections[1]

    non_dominant_hand = hand_detections[0] if dominant_hand == hand_detections[1] else hand_detections[1]

    return dominant_hand if return_dominant else non_dominant_hand

def detect_initial_movement_non_dominant(current_x_center_non_dominant, current_y_center_non_dominant, x_centers_non_dominant, y_centers_non_dominant, heights_non_dominant, current_height_non_dominant, non_dominant_hand_detections, frame_number, phases,metrics):
    """
    Detects initial movement for the non-dominant hand based on distance moved and height changes.
    Used to detect Start/Pick-up.
    """
    if len(x_centers_non_dominant) < 2:
        # Not enough data to compare, exit early
        return

    for i in range(len(x_centers_non_dominant) - 1):  #
        x_distance_moved = current_x_center_non_dominant - x_centers_non_dominant[i]
        y_distance_moved = y_centers_non_dominant[i] - current_y_center_non_dominant
        distance = math.sqrt(x_distance_moved ** 2 + y_distance_moved ** 2)
        #detects an initial large movement
        if distance > 0.2 and current_y_center_non_dominant < y_centers_non_dominant[i]:
            height_decrease = heights_non_dominant[-1] - current_height_non_dominant
            #wait for and contraction
            if height_decrease > 0.02:
                x_movement = current_x_center_non_dominant - x_centers_non_dominant[-2]
                y_movement = y_centers_non_dominant[-2] - current_y_center_non_dominant
                #and a small pick up movement
                if abs(x_movement) > 0.03 or abs(y_movement) > 0.03:
                    non_dominant_hand_detections.append(frame_number)
                    #update counter
                    if phases['start'] <= phases['end']:
                        phases['start'] += 1
                        metrics['duration'][0]=0   #reset trial duration
                    # Reset lists after detection
                    x_centers_non_dominant.clear()
                    y_centers_non_dominant.clear()
                    heights_non_dominant.clear()
                    break  # Exit loop after detecting movement

    # Update lists for non-dominant hand, if no movement detected
    if len(x_centers_non_dominant) == 0 or (x_centers_non_dominant[-1] != current_x_center_non_dominant or y_centers_non_dominant[-1] != current_y_center_non_dominant):
        x_centers_non_dominant.append(current_x_center_non_dominant)
        y_centers_non_dominant.append(current_y_center_non_dominant)
        heights_non_dominant.append(current_height_non_dominant)


def update_buffer_frame(frame_number, buffer, phases, end_frames, last_valid_frame, metrics, durations,
                        non_dominant_hand_detections):
    """
    Handles frame buffering and updates the phases and end_frames if conditions are met.

    Parameters:
    - frame_number (int): Current frame number.
    - buffer (int): Buffer flag indicating if a frame should be processed.
    - phases (dict): Dictionary holding the phases information.
    - end_frames (list): List to store end frames.
    - last_valid_frame (int): The last valid frame number.

    Returns:
    - Updated buffer value (int).
    """
    if buffer == 1:
        if phases['end'] < phases['start']:
            phases['end'] += 1
            end_frames.append(frame_number + 1)  # Add frame with buffer
            last_valid_frame = frame_number + 1  # Update last valid frame
            buffer = 0  # Reset buffer
            duration = last_valid_frame - non_dominant_hand_detections[
                -1]  # calculate interval in frames and convert to ms
            durations.append(duration)  # update durations
            # metrics
            metrics['duration'][0] = duration  # reset duration
            metrics['duration'][1] = np.mean(durations)  # mean durations
            metrics['total'][0] += 1  # update metrics

    return buffer, last_valid_frame


def analyze_and_update_hand_movement(hand_detection, y_centers_non_dominant, frame_number, last_valid_frame, buffer,
                                     phases, end_frames, metrics, durations, non_dominant_hand_detections):
    """
    Analyze the movement of a single detected hand and update the buffer and frame processing.

    Parameters:
    - hand_detection: The detected hand in the current frame.
    - y_centers_non_dominant: List of previous y-center positions of the non-dominant hand.
    - frame_number: The current frame number.
    - last_valid_frame: The last frame number where valid data was processed.
    - buffer: The current buffer value for processing.
    - phases: The phases list to be updated.
    - end_frames: The end frames list to be updated.
    - metrics: Metrics to be updated.
    - durations: Durations to be updated.
    - non_dominant_hand_detections: Detections of the non-dominant hand.

    Returns:
    - Updated buffer and last_valid_frame values.
    """
    current_x_center_non_dominant, current_y_center_non_dominant, current_height_non_dominant, current_width_non_dominant = get_hand_data(
        hand_detection)

    movement_direction = "positive"
    if len(y_centers_non_dominant) >= 2:
        # Calculate the distance between the last two y positions
        previous_y_center_non_dominant = y_centers_non_dominant[-2]
        distance = current_y_center_non_dominant - previous_y_center_non_dominant

        # Check if the movement direction is positive or negative
        movement_direction = "positive" if distance < 0 else "negative"

    # Ensure frame is at least 4 frames apart from the last valid frame
    if movement_direction == "positive" and abs(frame_number - last_valid_frame) > 4:
        # Set buffer to 1 for processing
        buffer = 1

    # Update buffer and append frame if criteria are met
    buffer, last_valid_frame = update_buffer_frame(frame_number, buffer, phases, end_frames, last_valid_frame, metrics,
                                                   durations, non_dominant_hand_detections)

    return buffer, last_valid_frame


from PIL import Image
import os


def crop_hand_region(image_path, detections, width_reduction=0.8, height_reduction=0.6, move_factor=1):
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

    # if not os.path.exists(output_dir):
    #    os.makedirs(output_dir)

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


def initialize_variables(txt_dir, model_path, input_folder, output_path):
    """
    Initializes and returns all necessary variables.
    """
    # Load and sort .txt files
    txt_files = sorted([os.path.join(txt_dir, f) for f in os.listdir(txt_dir) if f.endswith('.txt')])

    # Initialize variables
    last_valid_pen_length = None
    first_pen_x = None
    first_pen_y = None

    first_poke_x = None
    first_poke_y = None
    line_lengths = []
    thetas = []

    non_dominant_hand_detections = []
    end_frames = []
    durations = []
    poke = []
    pen = []
    frame_numbers = []

    x_centers_non_dominant = []
    y_centers_non_dominant = []
    heights_non_dominant = []

    x_centers_dominant = []
    y_centers_dominant = []

    pokes = []

    previous_image = None

    phases = {
        'start': 0,
        'poke': 0,
        'pen': 0,
        'end': 0
    }

    metrics = {
        'duration': [0, 0],  # actual, mean
        'poke': 0,  # 1/2 or 2/2
        'pen': 0,  # 1/2 or 2/2
        'total': [0, 0]  # n, correct for presenting %
    }

    last_valid_frame = -5  # Initialize to ensure the first valid frame is always added
    buffer = 0

    # Initialize line lengths and angles (thetas)
    line_lengths = [0, 0, 0]
    line_lengths_pen = [0, 0, 0]
    thetas = [0, 0, 0]

    first_poke_x = 0
    first_poke_y = 0

    # Load the model
    model_poke_pen = load_model(model_path)

    # Initialize other paths and variables
    max_line = None
    predictions = []
    store_metrics = {'frame_numbers': [], 'phases': []}

    non_dominant_hand_detections = []

    return {
        'txt_files': txt_files,
        'last_valid_pen_length': last_valid_pen_length,
        'first_pen_x': first_pen_x,
        'first_pen_y': first_pen_y,
        'first_poke_x': first_poke_x,
        'first_poke_y': first_poke_y,
        'line_lengths': line_lengths,
        'line_lengths_pen': line_lengths_pen,
        'thetas': thetas,
        'end_frames': end_frames,
        'durations': durations,
        'poke': poke,
        'pen': pen,
        'frame_numbers': frame_numbers,
        'x_centers_non_dominant': x_centers_non_dominant,
        'y_centers_non_dominant': y_centers_non_dominant,
        'heights_non_dominant': heights_non_dominant,
        'x_centers_dominant': x_centers_dominant,
        'y_centers_dominant': y_centers_dominant,
        'pokes': pokes,
        'previous_image': previous_image,
        'phases': phases,
        'metrics': metrics,
        'last_valid_frame': last_valid_frame,
        'buffer': buffer,
        'model_poke_pen': model_poke_pen,
        'input_folder': input_folder,
        'output_path': output_path,
        'max_line': max_line,
        'predictions': predictions,
        'store_metrics': store_metrics,
        'non_dominant_hand_detections': non_dominant_hand_detections,
    }
