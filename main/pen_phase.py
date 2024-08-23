def detect_pen_phase(predictions, previous_image, image_cropped, current_x_center_dominant, current_y_center_dominant,
                     phases, last_valid_pen_length, first_pen_x, first_pen_y, line_lengths_pen):
    # Ensure line_lengths and thetas are initialized as lists
    if line_lengths_pen is None:
        line_lengths_pen = []

    line_length_pen = None

    for pred in predictions[:-3]:  # Analyzing the last few predictions
        if pred[2] > 0.8:  # Pen detection condition
            # Detect pen lines
            line_length_pen, theta_pen = detect_poke_pen_lines(
                image_before=previous_image,
                image_after=image_cropped,
                type="pen",
                min_length_threshold=31.3209195267316 - 1,
                max_length_threshold=31.33 + 1
            )

            # Handle pen phase detection
            if line_length_pen is not None:
                if 31 <= line_length_pen <= 32.202484376209236:
                    if phases['pen'] == 0:
                        # Start of the pen phase
                        phases['pen'] += 1
                        first_pen_x = current_x_center_dominant
                        first_pen_y = current_y_center_dominant
                        last_valid_pen_length = line_length_pen  # Store the valid pen length
                    elif phases['pen'] == 1:
                        # Calculate distance to the first pen action
                        distance_hands = distance_moved(first_pen_x, first_pen_y, current_x_center_dominant,
                                                        current_y_center_dominant)
                        # Update pen phase if distance is significant and if line length is less than the threshold
                        if distance_hands > 0.05 and (
                                last_valid_pen_length is None or line_length_pen < 32.202484376209235):
                            phases['pen'] += 1
                            last_valid_pen_length = line_length_pen  # Update the last valid pen length

        # Update the line_lengths_pen list
        if line_length_pen is not None:
            line_lengths_pen.append(line_length_pen)
        if len(line_lengths_pen) > 3:
            line_lengths_pen.pop(0)

    return phases, line_lengths_pen, last_valid_pen_length, first_pen_x, first_pen_y