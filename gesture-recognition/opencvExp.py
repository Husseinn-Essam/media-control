import cv2
import numpy as np
import math
from segmenterFunc import segmenter
from customAlgos import convexity_defects, angle_between_points ,detect_pointing_direction, is_rock_on, get_palm_center,calcSolidity

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
    result = segmenter(frame)
    if len(result) == 3:
        thresh, roi, handSegment = result
    else:
        thresh, roi = result
        handSegment = None
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    drawing = np.zeros(roi.shape, np.uint8)

    try:
        contour = max(contours, key=lambda c: cv2.contourArea(c), default=0)
        hull = cv2.convexHull(contour)
        cv2.drawContours(drawing, [contour], -1, (0, 255, 0), 1)
        cv2.drawContours(drawing, [hull], -1, (0, 0, 255), 1)
        palm_center = get_palm_center(contour)
        ## calculate the solidity of the hand and direction of the hand
        direction = detect_pointing_direction(frame, contour)
        solidity = calcSolidity(contour)
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
     
        
        if is_rock_on(contour,drawing,palm_center[0],palm_center[1], count_defects)==True and direction!="Left" and direction!="Right" and solidity<=0.6:
            gesture = "ROCK ON"
        elif count_defects == 0:
            if solidity > 0.6:  # Fist: High solidity (compact shape)
                gesture = "FIST"
            else:  # Open hand with one finger extended
                gesture = "ONE"
            # check direction
            direction = detect_pointing_direction(frame, contour)
            cv2.putText(frame, f"Direction: {direction}", (10, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
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
