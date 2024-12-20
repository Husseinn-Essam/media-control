import cv2
import numpy as np
import math
from segmenterFunc import segmenter
from customAlgos import convexity_defects, angle_between_points

# Initialize webcam
current_camera = 0 # default webcam
cap = cv2.VideoCapture(current_camera)

def toggle_camera():
    # Using the global variables
    global cap, current_camera
    # Release the current camera
    cap.release()
    
    # Switch between cameras
    if current_camera == 0:
        current_camera = 1
    else:
        current_camera = 0

    # Reinitialize the capture with the new camera
    cap = cv2.VideoCapture(current_camera)

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
    # roi, thresh, contours = imageFiltering(frame)
    frame = cv2.GaussianBlur(frame, (5, 5), 0)
    thresh, roi = segmenter(frame)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
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
            if  angle < 90:  # Allow a small margin around 90 degrees
                count_defects += 1
                filtered_defects.append(defect)

        # Draw filtered convexity defects
        for defect in filtered_defects:
            start_idx, end_idx, far_idx, depth = defect
            start = tuple(contour[start_idx][0])
            end = tuple(contour[end_idx][0])
            far = tuple(contour[far_idx][0])
            cv2.line(drawing, start, end, (255, 0, 0), 1)  # Blue line for defect
            cv2.circle(drawing, far, 5, (0, 255, 255), -1)  # Yellow circle for defect point

        # Determine gesture based on defect count
        
        if count_defects == 0:
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

        cv2.putText(frame, f"Gesture: {gesture}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    except:
        pass
    
    # Show the processed frames
    cv2.imshow("ROI", cv2.resize(roi, (300, 400)))
    cv2.imshow("Threshold", cv2.resize(thresh, (300, 400)))
    cv2.imshow("Drawing", cv2.resize(drawing, (300, 400)))
    cv2.imshow("Frame", frame)
    
    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Switch camera if 's' pressed
    if cv2.waitKey(1) & 0xFF == ord('s'):
        toggle_camera()

cap.release()
cv2.destroyAllWindows()
