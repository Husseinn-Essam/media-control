
## JUST for TESTING not actually used
import cv2
import numpy as np

# Step 1: Capture video from the default camera
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Unable to access the camera.")
    exit()

# Optionally set the width and height of the video feed
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Initialize a background frame for subtraction (optional)
background_frame = None

print("Press 'q' to quit the video feed.")

while True:
    # Capture a single frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to read frame from the camera.")
        break

    # Step 2: Preprocessing

    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur to reduce noise
    blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)

    # Background subtraction (optional for motion detection)
    if background_frame is None:
        background_frame = blurred_frame
        continue  # Skip processing until the background is initialized

    diff_frame = cv2.absdiff(background_frame, blurred_frame)

    # Apply thresholding to get binary image
    _, thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)

    # Optional: Use morphological operations to clean the binary image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    cleaned_frame = cv2.morphologyEx(thresh_frame, cv2.MORPH_CLOSE, kernel)

    # Step 3: Display the original and preprocessed frames
    cv2.imshow("Original Feed", frame)
    cv2.imshow("Grayscale", gray_frame)
    cv2.imshow("Thresholded Frame", cleaned_frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()
