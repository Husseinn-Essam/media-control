import tensorflow as tf
import numpy as np
import cv2
import os
import mediapipe as mp

def translate_number_to_string(number):
    mapping = {
        9: "FIVE",
        13: "FIVE",
        10: "TWO",
        6: "ONE",
        4: "FIST",
        7: "One Finger Left",
        2: "One Finger Right",
        1: "One Finger Up",
        3: "One Finger Down",
        30: "One Finger Down",
        12: "ROCK ON"
    }
    return mapping.get(number, "unknown")

# Set GPU configuration (optional, for memory growth)
physical_devices = tf.config.experimental.list_physical_devices("GPU")
if physical_devices:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)

# Load the .h5 model
filepath = os.path.join(os.path.dirname(__file__), "model_detection_3/modelgood.h5")
print("Model path:", filepath)

# Load the model
model = tf.keras.models.load_model(filepath, compile=False)

# Compile the model to avoid the reduction error
model.compile(
    optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
)

# Set up MediaPipe Hands for landmark detection.
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5
)

# Capture webcam frames
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to RGB (MediaPipe requires RGB format)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame to detect hand landmarks
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Extract 21 hand landmarks (x, y) for each landmark
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.append([lm.x, lm.y])  # Extract x, y coordinates

            # Convert the landmarks to a numpy array and reshape it to (1, 21, 2)
            input_landmarks = np.array(landmarks).reshape(1, 21, 2)

            # Use GPU for inference
            with tf.device("/GPU:0"):  # Specify GPU:0 for inference
                predictions = model.predict(input_landmarks)

            predicted_class = np.argmax(predictions, axis=1)

            # Display predictions on the frame
            print(f"Predicted Class: {predicted_class}")
            text = f"Predicted Class: {predicted_class[0]}"
            
            gesture_text = translate_number_to_string(predicted_class[0])
            cv2.putText(
                frame,
                gesture_text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                frame,
                text,
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

            # Draw the hand landmarks on the frame
            for landmark in hand_landmarks.landmark:
                # Draw hand connections
                mp.solutions.drawing_utils.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_utils.DrawingSpec(
                        color=(0, 255, 0), thickness=2, circle_radius=2
                    ),
                    mp.solutions.drawing_utils.DrawingSpec(
                        color=(255, 0, 0), thickness=2
                    ),
                )

    # Show the frame
    cv2.imshow("Frame", frame)

    # Exit loop on 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
