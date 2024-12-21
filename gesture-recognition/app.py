from flask import Flask, Response, jsonify, request
import cv2
import threading
from flask_cors import CORS
import base64

from opencvExp import gesture_recognition_loop
app = Flask(__name__)
CORS(app)


current_camera = 0
cap = cv2.VideoCapture(current_camera)

# Shared variable for the current frame
current_frame = None

# Lock for thread-safe frame access
frame_lock = threading.Lock()

def capture_frames():
    """Continuously capture frames from the webcam."""
    global current_frame
    cv2.waitKey(100)
    while True:
        success, frame = cap.read()
        if success:
            with frame_lock:
                #flip the frame so that it is not mirrored
                current_frame = cv2.flip(frame, 1)

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
    try:
        with frame_lock:
            if current_frame is None:
                return jsonify({"error": "No frame available"}), 400
            
            # Assuming gesture_recognition_loop returns a tuple of (gesture, motion_detected, direction)
            gesture, motion_detected, motion_last_detected, direction= gesture_recognition_loop(debug=False, api=True, frame=current_frame)

            # Construct the response only if debug is False
            result = {}
            if gesture:
                result = {
                    "gesture": gesture,
                    "motion_detected": motion_detected,
                    "motion_last_detected": motion_last_detected,
                    "direction": direction,
                
                }
            return jsonify(result)
    except Exception as e:
        print(f"Error processing gesture: {e}")
        return jsonify({"error": "Internal server error"}), 500

       
@app.route('/')
def index():
    return "API is running. Endpoints: /video_feed, /recognize_gesture"

if __name__ == '__main__':
   
    app.run(host='0.0.0.0', port=5000) 
