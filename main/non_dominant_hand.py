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

def analyze_disappearance_and_position(txt_dir):
    """
    Analyzes .txt files in a directory to determine:
    - Which hand (left or right) disappears more frequently.
    - If the non-dominant hand is more often to the left or right of the dominant hand.

    Parameters:
    - txt_dir (str): Directory containing .txt files with YOLO detections.

    Returns:
    - Tuple: (dominant_hand_position, non_dominant_hand_position)
    """
    txt_files = sorted([os.path.join(txt_dir, f) for f in os.listdir(txt_dir) if f.endswith('.txt')])

    disappearance_counts = [0, 0]  # Count of disappearances for hand 0 and hand 1
    non_dominant_left_count = 0  # Non-dominant hand to the left of dominant hand
    non_dominant_right_count = 0  # Non-dominant hand to the right of dominant hand

    # Track previous hand detections
    previous_hand_detections = [False, False]

    for txt_file in txt_files:
        detections = parse_txt_file(txt_file)

        # Track hand detections
        hand_detections = [d for d in detections if d[0] == 0 or d[0] == 1]  # Assuming class_id 0 and 1 for hands
        hand_ids_detected = {d[0] for d in hand_detections}

        # Check if any hand disappeared
        for hand_id in range(2):
            if hand_id not in hand_ids_detected and previous_hand_detections[hand_id]:
                # Hand disappeared
                disappearance_counts[hand_id] += 1
                previous_hand_detections[hand_id] = False
            elif hand_id in hand_ids_detected:
                # Hand is detected
                previous_hand_detections[hand_id] = True

        # If both hands are detected, compare their X positions
        if len(hand_ids_detected) == 2:
            try:
                hand_0_x = next(d[1] for d in hand_detections if d[0] == 0)
                hand_1_x = next(d[1] for d in hand_detections if d[0] == 1)
            except StopIteration:
                continue  # Skip to the next frame if one hand is missing

            # Determine which hand is non-dominant and which is dominant
            non_dominant_hand = disappearance_counts.index(max(disappearance_counts))
            dominant_hand = 1 - non_dominant_hand

            # Check if the non-dominant hand is to the left or right of the dominant hand
            if non_dominant_hand == 0:
                if hand_0_x < hand_1_x:
                    non_dominant_left_count += 1
                else:
                    non_dominant_right_count += 1
            else:
                if hand_1_x < hand_0_x:
                    non_dominant_left_count += 1
                else:
                    non_dominant_right_count += 1

    # Determine the dominant hand's position
    dominant_hand_position = "left" if non_dominant_left_count > non_dominant_right_count else "right"
    non_dominant_hand_position = "left" if dominant_hand_position == "right" else "right"

    #print(f"Dominant hand: {dominant_hand_position}")
    #print(f"Non-dominant hand: {non_dominant_hand_position}")

    return dominant_hand_position, non_dominant_hand_position

# Example usage:
#txt_dir = '/Users/nunofernandes/PycharmProjects/challenge_vc/runs/detect/predict4/labels/'
#analyze_disappearance_and_position(txt_dir)