import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Set up hands detection with MediaPipe
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Open webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to RGB and HSV
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Process frame for hand landmarks
    results = hands.process(rgb_frame)

    # Create a blank binary image for the segmented hand
    binary_hand = np.zeros(frame.shape[:2], dtype=np.uint8)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Convert landmarks to pixel coordinates
            h, w, _ = frame.shape
            landmark_points = [(int(landmark.x * w), int(landmark.y * h)) for landmark in hand_landmarks.landmark]

            # Calculate the bounding box of the hand
            x_min = max(0, min(pt[0] for pt in landmark_points))
            y_min = max(0, min(pt[1] for pt in landmark_points))
            x_max = min(w, max(pt[0] for pt in landmark_points))
            y_max = min(h, max(pt[1] for pt in landmark_points))

            # Extract ROI from the original frame and HSV frame
            roi_hsv = hsv_frame[y_min:y_max, x_min:x_max]

            # Skin color range in HSV (adjust as needed)
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)

            # Skin mask based on HSV range
            skin_mask = cv2.inRange(roi_hsv, lower_skin, upper_skin)

            # Create a blank mask for the hand
            roi_hand_mask = np.zeros((y_max - y_min, x_max - x_min), dtype=np.uint8)

            # Create a convex hull around the landmarks localized to the ROI
            localized_landmarks = [(pt[0] - x_min, pt[1] - y_min) for pt in landmark_points]
            hull = cv2.convexHull(np.array(localized_landmarks, dtype=np.int32))
            cv2.fillConvexPoly(roi_hand_mask, hull, 255)

            # Combine hand landmark mask with skin mask in the ROI
            combined_mask = cv2.bitwise_and(skin_mask, roi_hand_mask)

            # Place the segmented hand mask back into the full binary hand mask
            binary_hand[y_min:y_max, x_min:x_max] = combined_mask

            # Draw landmarks and bounding box on the frame (optional)
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Display the original frame
    cv2.imshow("Original Frame", frame)

    # Display the binary hand segmentation in a separate window
    cv2.imshow("Segmented Hand (Binary)", binary_hand)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
