import cv2
import numpy as np
from skimage import measure, morphology, filters
from scipy.spatial import ConvexHull

# Initialize webcam capture
cap = cv2.VideoCapture(0)

# Define region of interest (ROI) for hand detection
x, y, w, h = 100, 100, 200, 200

# Function to detect gesture
def detect_gesture(image):
    # Convert to grayscale for easier processing
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Threshold the image to segment the hand
    thresh = filters.threshold_otsu(gray)
    binary = gray < thresh
    
    # Remove small objects (noise)
    cleaned = morphology.remove_small_objects(binary, min_size=500)
    
    # Find contours
    contours = measure.find_contours(cleaned, level=0.5)
    
    if not contours:
        return "No hand detected", None, None
    
    largest_contour = max(contours, key=len)
    hull = ConvexHull(largest_contour)
    
    # Get the hull points
    hull_points = largest_contour[hull.vertices]
    
    # Find convexity defects (farthest points from the hull)
    defects = []
    for i in range(len(hull_points)):
        start = hull_points[i]
        end = hull_points[(i + 1) % len(hull_points)]
        farthest_idx = np.argmax(np.linalg.norm(largest_contour - (start + end) / 2, axis=1))
        farthest_point = largest_contour[farthest_idx]
        defects.append(farthest_point)

    # Identify fingertips
    fingertips = [point for point in hull_points if is_fingertip(point, defects)]
    
    # Classify gesture based on fingertip count
    if len(fingertips) == 0:
        return "Fist", largest_contour, hull_points
    elif len(fingertips) == 5:
        return "Open Palm", largest_contour, hull_points
    elif len(fingertips) == 1:
        return classify_single_finger_direction(fingertips[0], largest_contour), largest_contour, hull_points
    elif len(fingertips) == 2:
        return classify_two_finger_gesture(fingertips), largest_contour, hull_points
    elif is_ok_sign(cleaned):
        return "OK Sign", largest_contour, hull_points
    return "Unknown Gesture", largest_contour, hull_points

# Helper functions for gesture analysis
def is_fingertip(point, defects):
    """Check if a point is a fingertip based on distance from defects."""
    for defect in defects:
        if np.linalg.norm(point - defect) < 20:  # Adjust tolerance as needed
            return False
    return True

def classify_single_finger_direction(fingertip, contour):
    """Classify direction of a single finger (up, down, left, right)."""
    y_coords = contour[:, 0]
    x_coords = contour[:, 1]
    if fingertip[0] < np.percentile(y_coords, 10):
        return "Up"
    elif fingertip[0] > np.percentile(y_coords, 90):
        return "Down"
    elif fingertip[1] < np.percentile(x_coords, 10):
        return "Left"
    elif fingertip[1] > np.percentile(x_coords, 90):
        return "Right"

def classify_two_finger_gesture(fingertips):
    """Classify two-finger gestures (peace or devil horns)."""
    x1, y1 = fingertips[0]
    x2, y2 = fingertips[1]
    angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
    if 30 < angle < 90:
        return "Peace Sign"
    else:
        return "Devil Horns"

def is_ok_sign(binary_image):
    """Detect if the gesture is an OK sign."""
    labeled_image = measure.label(binary_image)
    regions = measure.regionprops(labeled_image)
    for region in regions:
        if region.eccentricity < 0.5 and 100 < region.area < 500:
            return True
    return False

# Start capturing frames from webcam
while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Failed to grab frame")
        break
    
    # Draw the region of interest rectangle
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Crop the ROI and detect the gesture
    roi = frame[y:y + h, x:x + w]
    gesture, contour, hull_points = detect_gesture(roi)

    # Annotate the frame with the detected gesture
    cv2.putText(frame, f"Gesture: {gesture}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Draw the convex hull
    if hull_points is not None:
        hull_points = np.int32(hull_points)
        for point in hull_points:
            cv2.circle(frame, tuple(point), 5, (0, 0, 255), -1)
    
    # Draw the contour using cv2.drawContours to handle orientation automatically
    if contour is not None:
        contour = np.int32(contour)
        cv2.drawContours(frame, [contour], -1, (255, 0, 0), 2)

    # Show the image with defects and hull
    cv2.imshow("Frame with Defects and Hull", frame)
    
    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
