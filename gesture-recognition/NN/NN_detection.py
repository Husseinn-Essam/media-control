import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands()

# Initialize webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # Check if hands are detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Logic for gesture detection (e.g., pointing, open/closed hand)
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.append([lm.x, lm.y, lm.z])

            # Gesture detection based on landmarks (example: open vs. closed hand)
            thumb_x, thumb_y = landmarks[4][0], landmarks[4][1]
            index_x, index_y = landmarks[8][0], landmarks[8][1]
            middle_x, middle_y = landmarks[12][0], landmarks[12][1]

            # Example: Check if thumb and index finger are separated (open hand)
            if abs(thumb_x - index_x) > 0.05 and abs(thumb_y - index_y) > 0.05:
                cv2.putText(frame, "Open Hand", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Example: Check if thumb and index finger are close together (closed hand)
            elif abs(thumb_x - index_x) < 0.1 and abs(thumb_y - index_y) < 0.1:
                cv2.putText(frame, "Closed Hand", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Display frame
    cv2.imshow("Hand Tracking", frame)

    # Break on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
