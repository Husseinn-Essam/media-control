from flask import Flask, Response, jsonify, request
import cv2
import threading

app = Flask(__name__)

cap = cv2.VideoCapture(0)

# Shared variable for the current frame
current_frame = None

# Lock for thread-safe frame access
frame_lock = threading.Lock()

def capture_frames():
    """Continuously capture frames from the webcam."""
    global current_frame
    while True:
        success, frame = cap.read()
        if success:
            with frame_lock:
                current_frame = frame

# Start the frame capture in a separate thread
capture_thread = threading.Thread(target=capture_frames, daemon=True)
capture_thread.start()

@app.route('/video_feed')
def video_feed():
    """MJPEG stream endpoint for the frontend."""
    def generate_frames():
        while True:
            with frame_lock:
                if current_frame is None:
                    continue
                _, buffer = cv2.imencode('.jpg', current_frame)
                frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/recognize_gesture', methods=['POST'])
def recognize_gesture():
    """Process the current frame for gesture recognition."""
    with frame_lock:
        if current_frame is None:
            return jsonify({"error": "No frame available"}), 400
        
        gray_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
        _, thresh_frame = cv2.threshold(blurred_frame, 50, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        num_contours = len(contours)

        gesture_detected = "Unknown"
        if num_contours > 0:
            gesture_detected = "Hand Detected"

        return jsonify({
            "gesture": gesture_detected,
            "contours": num_contours
        })

@app.route('/')
def index():
    return "API is running. Endpoints: /video_feed, /recognize_gesture"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
