import os
from non_dominant_hand import analyze_disappearance_and_position

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
def analyze_single_hand_frames(txt_dir='/Users/nunofernandes/PycharmProjects/challenge_vc/runs/detect/predict4/labels'):
    """
    Analyzes .txt files in a directory to identify frames with only one hand detected,
    and check the direction of movement based on previous y_center values.

    Parameters:
    - txt_dir (str): Directory containing .txt files with YOLO detections.

    Returns:
    - List of frame numbers where only one hand is detected and the vertical movement direction is evaluated.
    """
    txt_files = sorted([os.path.join(txt_dir, f) for f in os.listdir(txt_dir) if f.endswith('.txt')])

    single_hand_frames = []
    last_valid_frame = -5  # Initialize to ensure the first valid frame is always added

    y_positions = []  # List to keep track of y_center values

    for frame_number, txt_file in enumerate(txt_files):
        detections = parse_txt_file(txt_file)

        # Filter out the hand detections (assuming class_id 0 and 1 represent the hands)
        hand_detections = [d for d in detections if d[0] == 0 or d[0] == 1]

        if len(hand_detections) == 2:
            # Determine dominant hand based on position
            hand_0_x = hand_detections[0][1]  # X-center of hand 0
            hand_0_y = hand_detections[0][2]  # Y-center of hand 0
            hand_1_x = hand_detections[1][1]  # X-center of hand 1
            hand_1_y = hand_detections[1][2]  # Y-center of hand 1

            if analyze_disappearance_and_position(txt_dir)[0] == "right":
                if hand_1_x > hand_0_x:
                    dominant_hand_detection = hand_detections[0]  # Hand 1 is on the right
                else:
                    dominant_hand_detection = hand_detections[1]  # Hand 0 is on the right
            else:
                if hand_1_x > hand_0_x:
                    dominant_hand_detection = hand_detections[1]  # Hand 1 is on the right
                else:
                    dominant_hand_detection = hand_detections[0]  # Hand 0 is on the right

            current_y_center = dominant_hand_detection[2]

            y_positions.append(current_y_center)

        if len(hand_detections) == 1:
            # Only one hand detected
            hand_detection = hand_detections[0]
            hand_y_center = hand_detection[2]

            movement_direction = "positive"

            if len(y_positions) >= 2:
                # Calculate the distance between the last two y positions
                previous_y_center = y_positions[-2]
                distance = current_y_center - previous_y_center

                # Check if the movement direction is positive or negative
                movement_direction = "positive" if distance > 0 else "negative"

            # Ensure frame is at least 4 frames apart from the last valid frame
            if movement_direction == "positive" and abs(frame_number - last_valid_frame) > 4:
                if len(y_positions) > 1:
                    # Append the frame if it meets the movement criteria
                    single_hand_frames.append(frame_number)
                    last_valid_frame = frame_number

    # it takes approximately 1 frame to enter the box
    single_hand_frames = [x + 1 for x in single_hand_frames]

    #print(single_hand_frames)

    return single_hand_frames


# Example usage:
txt_dir = '/Users/nunofernandes/PycharmProjects/challenge_vc/runs/detect/predict4/labels'

analyze_single_hand_frames(txt_dir)
