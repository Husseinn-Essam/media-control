import cv2
import numpy as np
import math

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
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return roi, thresh, contours

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame. Exiting...")
        break
    
    # Draw the ROI rectangle
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    # Apply image filtering and gesture recognition
    roi, thresh, contours = imageFiltering(frame)
    drawing = np.zeros(roi.shape, np.uint8)

    try:
        contour = max(contours, key=lambda c: cv2.contourArea(c), default=0)
        hull = cv2.convexHull(contour)
        cv2.drawContours(drawing, [contour], -1, (0, 255, 0), 1)
        cv2.drawContours(drawing, [hull], -1, (0, 0, 255), 1)
        hull = cv2.convexHull(contour, returnPoints=False)
        defects = cv2.convexityDefects(contour, hull)
        count_defects = 0

        if defects is not None:
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(contour[s][0])
                end = tuple(contour[e][0])
                far = tuple(contour[f][0])
                a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                angle = (math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 180) / 3.14

                if angle <= 90:
                    count_defects += 1
                    cv2.circle(drawing, far, 5, [0, 0, 255], -1)
                cv2.line(drawing, start, end, [0, 255, 0], 2)

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
    cv2.imshow("ROI", roi)
    cv2.imshow("Threshold", thresh)
    cv2.imshow("Drawing", drawing)
    cv2.imshow("Frame", frame)
    
    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
