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


def analyze_moments(txt_dir):
    """
    Analyzes .txt files in a directory to detect specific moments for both hands.

    Parameters:
    - txt_dir (str): Directory containing .txt files with YOLO detections.
    """
    txt_files = sorted([os.path.join(txt_dir, f) for f in os.listdir(txt_dir) if f.endswith('.txt')])

    previous_hand_y_center = [None, None]  # Track Y centers for two hands
    first_moment_frame = None
    last_moment_frame = None

    for i, txt_file in enumerate(txt_files):
        detections = parse_txt_file(txt_file)

        # Track hand detections
        hand_detections = [d for d in detections if d[0] == 0]  # Assuming class_id for hand is 0
        hand_centers = [d[2] for d in hand_detections]  # Extract Y centers of hands

        # Update Y centers and check for first moment
        if len(hand_centers) >= 1:
            for j, y_center in enumerate(hand_centers):
                if previous_hand_y_center[j] is not None:
                    # Check for Y-axis movement
                    if y_center > previous_hand_y_center[j] + 0.05:  # Example threshold
                        if first_moment_frame is None:
                            first_moment_frame = i
                previous_hand_y_center[j] = y_center

        # Check if hands have disappeared from the image
        if len(hand_centers) == 0:
            if any(center is not None for center in previous_hand_y_center):
                last_moment_frame = i - 1
                break

    print(f"First moment (hand moves forward) detected at frame: {first_moment_frame}")
    print(f"Last moment (hand disappears) detected at frame: {last_moment_frame}")


# Example usage:
txt_dir = '/path/to/txt/files'

analyze_moments(txt_dir)
