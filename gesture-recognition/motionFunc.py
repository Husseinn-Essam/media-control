import time

# Point buffer
point_buffer = []

# Time tracking variables for resetting the buffer
last_motion_time = time.time()
cooldown_duration = 0.5  # Minimum seconds between motion detections

# Buffer settings
BUFFER_LIMIT = 40  # Maximum number of points in the buffer before reset
X_THRESHOLD = 40  # Minimum movement in the X direction to be considered as motion
Y_THRESHOLD = 40  # Minimum movement in the Y direction to be considered as motion

# Make it easy to understand where the prints are coming from
def motion_print(string = "empty"):
    print(f"motionFunc: {string}")

def motion_handle_buffer_reset():
    """Partially reset the point buffer after motion is detected."""
    global point_buffer
    motion_print("Motion detected. Resetting point buffer.")
    if len(point_buffer) > 5:  # Keep the last 5 points for continuity
        point_buffer = point_buffer[-5:]

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

    # Check the average movement over the last few points
    total_move_x, total_move_y = 0, 0
    for i in range(1, len(point_buffer)):
        current_point = point_buffer[i]
        previous_point = point_buffer[i - 1]

        # Accumulate movement values
        total_move_x += abs(current_point[0] - previous_point[0])
        total_move_y += abs(current_point[1] - previous_point[1])

    # Calculate the average movement
    avg_move_x = total_move_x / (len(point_buffer) - 1)
    avg_move_y = total_move_y / (len(point_buffer) - 1)

    # Check if the average movement exceeds the threshold
    if avg_move_x > X_THRESHOLD or avg_move_y > Y_THRESHOLD:
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
    global point_buffer, last_motion_time

    current_time = time.time()

    if len(point_buffer) > 1:
        # Check if cooldown period has passed
        if current_time - last_motion_time < cooldown_duration:
            #motion_print("Skipping detection due to cooldown.")
            return None  # Skip detection during cooldown

        # First, check if motion is detected using the threshold
        if motion_detected():
            # Motion detected, now determine the direction
            #motion_print("Motion detected. Determining direction...")
            for i in range(1, len(point_buffer)):
                current_point = point_buffer[i]
                previous_point = point_buffer[i - 1]

                # Detect the motion direction
                motion_direction = detect_motion_direction(previous_point, current_point)
                if motion_direction != "NO MOTION":
                    motion_print(f"Motion detected: {motion_direction}")
                    motion_handle_buffer_reset()  # Partially reset the buffer after direction is determined
                    last_motion_time = current_time  # Update the last motion time
                    return motion_direction

    return None  # No motion detected