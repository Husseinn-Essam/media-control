import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2

# Set up the GestureRecognizer object.
# Read the gesture recognizer model file, create base options with the model data,
# and then create a GestureRecognizer object using these options.
with open(
    r"D:\FALL_24_PROJECTS\media-control-gui\gesture-recognition\NN\model_detection_2\gesture_recognizer.task",
    "rb",
) as model_file:
    model_data = model_file.read()

base_options = python.BaseOptions(model_asset_buffer=model_data)
options = vision.GestureRecognizerOptions(base_options=base_options)
recognizer = vision.GestureRecognizer.create_from_options(options)

# Set up MediaPipe Hands for landmark detection.
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5
)

# STEP 2: Capture webcam frames and process them.
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to RGB (MediaPipe requires RGB format)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Create an Image object from the frame
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # Recognize gestures in the current frame
    recognition_result = recognizer.recognize(mp_image)

    # Detect hand landmarks
    results = hands.process(rgb_frame)

    # Overlay gesture recognition result
    if recognition_result.gestures:
        top_gesture = recognition_result.gestures[0][0]  # Top gesture prediction
        gesture_text = f"Gesture: {top_gesture.category_name}"

        cv2.putText(
            frame,  # Image/frame to draw on
            gesture_text,  # Text to display
            (50, 50),  # Position (x, y)
            cv2.FONT_HERSHEY_SIMPLEX,  # Font type
            1,  # Font scale
            (0, 255, 0),  # Color (BGR - Green)
            2,  # Thickness
            cv2.LINE_AA,  # Line type
        )
    else:
        cv2.putText(
            frame,
            "Gesture: None",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),  # Color (BGR - Red)
            2,
            cv2.LINE_AA,
        )

    # Overlay hand landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            for landmark in hand_landmarks.landmark:
                # Convert normalized coordinates to pixel values
                h, w, _ = frame.shape
                x, y = int(landmark.x * w), int(landmark.y * h)

                # Draw each landmark
                cv2.circle(
                    frame, (x, y), 5, (255, 0, 0), -1
                )  # Blue circle for each landmark

            # Draw hand connections
            mp.solutions.drawing_utils.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp.solutions.drawing_utils.DrawingSpec(
                    color=(0, 255, 0), thickness=2, circle_radius=2
                ),
                mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 0), thickness=2),
            )

    # Display the frame with overlaid landmarks and gesture text
    cv2.imshow("Gesture Recognition with Landmarks", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):  # Exit on 'q'
        break

cap.release()
cv2.destroyAllWindows()
