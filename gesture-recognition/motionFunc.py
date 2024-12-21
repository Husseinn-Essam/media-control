import time

# Point buffer
point_buffer = []

# Time tracking variables for resetting the buffer
last_check_time = time.time()
interval_duration = 2  # Seconds

# Buffer settings
BUFFER_LIMIT = 40  # Maximum number of points in the buffer before reset
X_THRESHOLD = 120  # Minimum movement in the X direction to be considered as motion
Y_THRESHOLD = 120 # Minimum movement in the Y direction to be considered as motion

def motion_handle_buffer_reset():
    """Reset the point buffer after motion is detected and direction is determined."""
    global point_buffer
    print("Motion detected. Resetting point buffer.")
    point_buffer.clear()  # Reset the buffer after determining direction

def motion_add_point_to_buffer(point):
    """Add new point data to the buffer."""
    global point_buffer
    
    # Ignore invalid points (e.g., negative coordinates)
    if point[0] < 0 or point[1] < 0:
        return

    # Add the new point to the buffer
    point_buffer.append(point)

    # If the buffer exceeds the limit, remove the oldest point
    if len(point_buffer) > BUFFER_LIMIT:
        point_buffer.pop(0)  # Keep the buffer size manageable

def motion_detected():
    """Check if motion has been detected based on the buffer and threshold."""
    global point_buffer

    # If the buffer has fewer than 2 points, no motion can be detected
    if len(point_buffer) < 2:
        return False

    # Iterate over all consecutive points in the buffer
    for i in range(1, len(point_buffer)):
        current_point = point_buffer[i]
        previous_point = point_buffer[i - 1]

        # Check if the movement in X or Y exceeds the threshold
        move_x = abs(current_point[0] - previous_point[0])
        move_y = abs(current_point[1] - previous_point[1])

        # If either X or Y movement exceeds the threshold, motion is detected
        if move_x > X_THRESHOLD or move_y > Y_THRESHOLD:
            return True  # Motion detected

    return False  # No significant motion

def detect_motion_direction(prev_point, curr_point):
    """Compare two consecutive points to detect motion direction."""
    prev_x, prev_y = prev_point
    curr_x, curr_y = curr_point

    # Compare X positions
    if curr_x > prev_x + X_THRESHOLD:
        return "RIGHT"
    elif curr_x < prev_x - X_THRESHOLD:
        return "LEFT"

    # Compare Y positions
    elif curr_y > prev_y + Y_THRESHOLD:
        return "DOWN"
    elif curr_y < prev_y - Y_THRESHOLD:
        return "UP"

    return "NO MOTION"  # No significant movement

def motion_track_points():
    """Track the motion of points and detect motion direction based on the buffer."""
    global point_buffer

    if len(point_buffer) > 1:
        # print(f"Tracking {len(point_buffer)} points")

        # First, check if motion is detected using the threshold
        if motion_detected():
            # Motion detected, now determine the direction
            for i in range(1, len(point_buffer)):
                current_point = point_buffer[i]
                previous_point = point_buffer[i - 1]

                # Detect the motion direction
                motion_direction = detect_motion_direction(previous_point, current_point)
                if motion_direction != "NO MOTION":
                    print(f"Motion detected: {motion_direction}")
                    motion_handle_buffer_reset()  # Reset the buffer after direction is determined
                    return motion_direction
                    break  # Stop further checks after detecting motion and direction
