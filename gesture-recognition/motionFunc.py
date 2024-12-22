# Centroid point buffer
point_buffer = []

BUFFER_LIMIT = 40

# Pixel deltas that if surpassed indicate movement
X_THRESHOLD = 120
Y_THRESHOLD = 120

# Last detected consecutive points
# They are only accessed when motion is successfully detected
point_1 = 0,0
point_2 = 0,0

def motion_handle_buffer_reset():
    global point_buffer
    print("Motion detected. Resetting point buffer.")
    point_buffer.clear()

def motion_add_point_to_buffer(point):
    global point_buffer
    point_buffer.append(point)

    if len(point_buffer) > BUFFER_LIMIT:
        print("Buffer limit exceeded. Resetting buffer but retaining last 4 points.")
        point_buffer = point_buffer[-4:]

def motion_detected():
    global point_buffer, point_1, point_2

    # If the buffer has fewer than 2 points, no motion can be detected
    if len(point_buffer) < 2:
        return False

    for i in range(1, len(point_buffer)):
        current_point = point_buffer[i]
        previous_point = point_buffer[i - 1]

        # Between each two consecutive points
        move_x = abs(current_point[0] - previous_point[0])
        move_y = abs(current_point[1] - previous_point[1])

        # If either X or Y movement exceeds the threshold, motion is detected
        if move_x > X_THRESHOLD or move_y > Y_THRESHOLD:
            point_1 = previous_point
            point_2 = current_point
            return True

    return False  # No significant motion

def detect_motion_direction(prev_point, curr_point):
    print(f"Previous point: {prev_point}, Current point: {curr_point}")
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

    return "NO MOTION"

def motion_track_points():
    """Track the motion of points and detect motion direction based on the buffer."""
    global point_buffer, point_1, point_2

    if len(point_buffer) > 1:
        # Was there a change in centroid of the hand that has surpassed the threshold?
        if motion_detected():
            # If yes, a motion has happened, lets see in which direction
            motion_direction = detect_motion_direction(point_1, point_2)
            if motion_direction != "NO MOTION":
                print(f"Motion detected: {motion_direction}")
                motion_handle_buffer_reset()
                return motion_direction