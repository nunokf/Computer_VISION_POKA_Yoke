def detect_poke_phase(predictions, previous_image, image_cropped, current_x_center_dominant, current_y_center_dominant,
                      phases, line_lengths, thetas, first_poke_x, first_poke_y):
    """
    Detects 'poke' phase based on predictions and updates relevant parameters.

    Parameters:
    - predictions (list): List of model predictions.
    - previous_image (ndarray): Previous frame image.
    - image_cropped (ndarray): Current frame image.
    - current_x_center_dominant (float): X-coordinate of the dominant hand's center in the current frame.
    - current_y_center_dominant (float): Y-coordinate of the dominant hand's center in the current frame.
    - phases (dict): Dictionary holding the phase status.
    - line_lengths (list): List of line lengths from recent detections.
    - thetas (list): List of angles from recent detections.
    - first_poke_x (float): X-coordinate of the first poke action.
    - first_poke_y (float): Y-coordinate of the first poke action.

    Returns:
    - tuple: Updated phases, line_lengths, thetas, first_poke_x, first_poke_y.
    """
    # Ensure line_lengths and thetas are initialized as lists
    if line_lengths is None:
        line_lengths = []
    if thetas is None:
        thetas = []

    line_length = None
    theta = None

    for prediction in predictions[:-3]:  # Analyzing the last few predictions
        if prediction[1] > 0.3:  # Poke detection condition
            # Detect poke lines
            line_length, theta = detect_poke_pen_lines(
                image_before=previous_image,
                image_after=image_cropped,
                type="poke",
                min_length_threshold=31.14,
                max_length_threshold=31.149
            )

            if line_length is not None:
                # Check if the current line length is approximately equal to any of the last three
                for i in range(len(line_lengths)):
                    previous_line_length = line_lengths[i]
                    previous_theta = thetas[i]
                    if previous_line_length is not None and abs(previous_line_length - line_length) < 0.03:
                        if phases['poke'] == 0 and previous_theta is not None and abs(previous_theta - theta) < 0.01:
                            # First poke detected
                            phases['poke'] += 1
                            line_lengths = [0, 0, 0]  # Reset line lengths
                            thetas = [0, 0, 0]  # Reset thetas
                            first_poke_x = current_x_center_dominant
                            first_poke_y = current_y_center_dominant
                        elif phases['poke'] == 1 and previous_theta is not None and abs(previous_theta - theta) < 0.05:
                            # Calculate distance to the first poke
                            distance_hands = distance_moved(first_poke_x, first_poke_y, current_x_center_dominant,
                                                            current_y_center_dominant)
                            if distance_hands > 0.01:
                                # Update poke phase if distance is significant
                                phases['poke'] += 1

        # Update the line lengths and thetas lists
        if line_length is not None:
            line_lengths.append(line_length)
        if theta is not None:
            thetas.append(theta)

        # Ensure line_lengths and thetas do not exceed length of 3
        if len(line_lengths) > 3:
            line_lengths.pop(0)
        if len(thetas) > 3:
            thetas.pop(0)

    return phases, line_lengths, thetas, first_poke_x, first_poke_y

