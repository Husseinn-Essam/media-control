import time

# ROI buffer
roi_buffer = []

# Time tracking variables for resetting the buffer
last_check_time = time.time()
interval_duration = 2  # Seconds

# Buffer settings
BUFFER_LIMIT = 40  # Maximum number of ROIs in the buffer before reset
X_THRESHOLD = 5  # Minimum movement in the X direction to be considered as motion
Y_THRESHOLD = 5  # Minimum movement in the Y direction to be considered as motion

def motion_handle_roi_buffer_reset():
    """Reset the ROI buffer only after motion is detected and direction is determined."""
    global roi_buffer
    print(f"Motion detected. Resetting ROI buffer.")
    roi_buffer.clear()  # Reset the buffer after determining direction

def motion_add_roi_to_buffer(roi_data):
    """Add new ROI data to the buffer."""
    global roi_buffer
    roi_y_range, roi_x_range = roi_data
    
    # Ignore invalid ROI data (if any range is -1)
    if roi_y_range[0] == -1 or roi_y_range[1] == -1 or roi_x_range[0] == -1 or roi_x_range[1] == -1:
        return

    # Add the new ROI to the buffer
    roi_buffer.append(roi_data)

    # If the buffer exceeds the limit, pop the oldest ROI
    if len(roi_buffer) > BUFFER_LIMIT:
        roi_buffer.pop(0)  # Keep the buffer size manageable

def motion_detected():
    """Check if motion has been detected based on the buffer and threshold."""
    global roi_buffer

    # If the buffer has fewer than 2 ROIs, no motion can be detected
    if len(roi_buffer) < 2:
        return False

    # Iterate over all consecutive ROIs in the buffer
    for i in range(1, len(roi_buffer)):
        current_roi = roi_buffer[i]
        previous_roi = roi_buffer[i-1]

        # Check if the movement in X or Y exceeds the threshold
        move_x = abs(current_roi[1][0] - previous_roi[1][0]) + abs(current_roi[1][1] - previous_roi[1][1])
        move_y = abs(current_roi[0][0] - previous_roi[0][0]) + abs(current_roi[0][1] - previous_roi[0][1])

        # If either X or Y movement exceeds the threshold, motion is detected
        if move_x > X_THRESHOLD or move_y > Y_THRESHOLD:
            return True  # Motion detected
    
    return False  # No significant motion

def detect_motion_direction(prev_roi, curr_roi):
    """Compare two consecutive ROIs to detect motion direction."""
    prev_y_range, prev_x_range = prev_roi
    curr_y_range, curr_x_range = curr_roi
    
    # Compare X positions
    if curr_x_range[0] > prev_x_range[1]:
        return "RIGHT"
    elif curr_x_range[1] < prev_x_range[0]:
        return "LEFT"
    
    # Compare Y positions
    elif curr_y_range[0] > prev_y_range[1]:
        return "DOWN"
    elif curr_y_range[1] < prev_y_range[0]:
        return "UP"
    
    return "NO MOTION"  # No significant movement

def motion_track_roi():
    """Track the motion of ROIs and detect motion direction based on the buffer."""
    global roi_buffer

    if len(roi_buffer) > 1:
        print(f"Tracking {len(roi_buffer)} ROIs")

        # First, check if motion is detected using the threshold
        if motion_detected():
            # Motion detected, now determine the direction
            for i in range(1, len(roi_buffer)):
                current_roi = roi_buffer[i]
                previous_roi = roi_buffer[i-1]

                # Detect the motion direction
                motion_direction = detect_motion_direction(previous_roi, current_roi)
                if motion_direction != "NO MOTION":
                    print(f"Motion detected: {motion_direction}")
                    motion_handle_roi_buffer_reset()  # Reset the buffer after direction is determined
                    return motion_direction
                    break  # Stop further checks after detecting motion and direction
