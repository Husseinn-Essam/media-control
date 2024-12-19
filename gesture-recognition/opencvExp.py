import cv2
import numpy as np
import math
from segmenterFunc import segmenter
from customAlgos import convexity_defects, angle_between_points

# Initialize webcam
cap = cv2.VideoCapture(0)

# Dimensions for the region of interest (ROI)
x, y, w, h = 100, 100, 200, 200


def imageFiltering(frame):
    """Apply image filtering and return contours."""
    roi = frame[y:y+h, x:x+w]
    blur = cv2.GaussianBlur(roi, (5, 5), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([2, 50, 50]), np.array([20, 255, 255]))
    filtered = cv2.GaussianBlur(mask, (3, 3), 0)
    ret, thresh = cv2.threshold(filtered, 127, 255, 0)
    thresh = cv2.GaussianBlur(thresh, (5, 5), 0)
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return roi, thresh, contours


while True:
    # Capture the frame twice a second
    cv2.waitKey(50)
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame. Exiting...")
        break
    frame = cv2.flip(frame, 1)

    # Draw the ROI rectangle
    # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Apply image filtering and gesture recognition
    roi, thresh, contours = imageFiltering(frame)
    frame = cv2.GaussianBlur(frame, (5, 5), 0)
    # roi,thresh,contours = imageFiltering(frame)
    thresh, roi = segmenter(frame)
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    drawing = np.zeros(roi.shape, np.uint8)

    try:
        contour = max(contours, key=lambda c: cv2.contourArea(c), default=0)
        hull = cv2.convexHull(contour)
        cv2.drawContours(drawing, [contour], -1, (0, 255, 0), 1)
        cv2.drawContours(drawing, [hull], -1, (0, 0, 255), 1)

        hull_indices = cv2.convexHull(contour, returnPoints=False).flatten()

        defects = convexity_defects(contour[:, 0, :], hull_indices)

        count_defects = 0

        # Filter defects with approximately 90 degrees
        filtered_defects = []
        for defect in defects:
            start_idx, end_idx, far_idx, depth = defect
            start = tuple(contour[start_idx][0])
            end = tuple(contour[end_idx][0])
            far = tuple(contour[far_idx][0])
            angle = angle_between_points(start, end, far)
            if angle < 90:  # Allow a small margin around 90 degrees
                count_defects += 1
                filtered_defects.append(defect)

        # Draw filtered convexity defects
        for defect in filtered_defects:
            start_idx, end_idx, far_idx, depth = defect
            start = tuple(contour[start_idx][0])
            end = tuple(contour[end_idx][0])
            far = tuple(contour[far_idx][0])
            # Blue line for defect
            cv2.line(drawing, start, end, (255, 0, 0), 1)
            # Yellow circle for defect point
            cv2.circle(drawing, far, 5, (0, 255, 255), -1)

        if count_defects == 0:
            # Calculate the bounding rectangle area to detect fist vs open hand
            x, y, w, h = cv2.boundingRect(contour)
            rect_area = w * h
            contour_area = cv2.contourArea(contour)
            solidity = contour_area / rect_area if rect_area != 0 else 0

            if solidity > 0.6:  # Fist: High solidity (compact shape)
                gesture = "FIST"
            else:  # Open hand with one finger extended
                gesture = "ONE"
        elif count_defects == 1:
            gesture = "TWO"
        elif count_defects == 2:
            gesture = "THREE"
        elif count_defects == 3:
            gesture = "FOUR"
        elif count_defects == 4:
            gesture = "FIVE"
        else:
            gesture = "UNKNOWN"

        cv2.putText(frame, f"Gesture: {gesture}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        ## Pointing Direction Stage
        moments = cv2.moments(contour)
        if moments['m00'] != 0:
            cx = int(moments['m10'] / moments['m00'])
            cy = int(moments['m01'] / moments['m00'])
            palm_center = (cx, cy)

            # Draw the palm center
            cv2.circle(frame, palm_center, 5, (255, 0, 0), -1)

            # Detect the fingertip (point farthest from the palm center)
            fingertip = None
            max_distance = 0
        for point in contour:
            point = tuple(point[0])  # Get (x, y) coordinates
            distance = np.linalg.norm(
                np.array(point) - np.array(palm_center))  # Compute distance
            if distance > max_distance:
                max_distance = distance
                fingertip = point
        if fingertip:
            cv2.circle(frame, fingertip, 10, (0, 255, 0), -1)
            cv2.line(frame, palm_center, fingertip, (255, 0, 0), 2)

            # Compute pointing direction
            pointing_vector = np.array(
                [fingertip[0] - palm_center[0], fingertip[1] - palm_center[1]])
            pointing_vector = pointing_vector / np.linalg.norm(pointing_vector)

            # Determine direction
            direction = ""
            if abs(pointing_vector[0]) > abs(pointing_vector[1]):
                if pointing_vector[0] > 0:
                    direction = "Right"
                else:
                    direction = "Left"
            else:
                if pointing_vector[1] > 0:
                    direction = "Down"
                else:
                    direction = "Up"

            # Put direction text on the image
            cv2.putText(frame, f"Direction: {direction}", (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    except Exception as e:
        # print(f"Error in processing frame: {e}")
        pass

    # Show the processed frames
    cv2.imshow("ROI", cv2.resize(roi, (300, 400)))
    cv2.imshow("Threshold", cv2.resize(thresh, (300, 400)))
    cv2.imshow("Drawing", cv2.resize(drawing, (300, 400)))
    cv2.imshow("Frame", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
