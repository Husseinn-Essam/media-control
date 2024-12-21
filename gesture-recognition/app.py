from flask import Flask, Response, jsonify, request
import cv2
import threading
from flask_cors import CORS
import base64

from opencvExp import gesture_recognition_loop
app = Flask(__name__)
CORS(app)

## Params
current_camera = 0
color_mode = "HSV"
bounding_box_ratio = 0.25

gesture_mappings = {
    "oneFinger": "unmapped",
    "twoFinger": "unmapped",
    "threeFinger": "unmapped",
    "fourFinger": "unmapped",
    "fiveFinger": "unmapped",
    "rockOn": "unmapped",
    "fist": "unmapped",
}

@app.route('/recognize_gesture', methods=['POST'])
def recognize_gesture():
    """Process the current frame for gesture recognition."""
    try:
    
        # Assuming gesture_recognition_loop returns a tuple of (gesture, motion_detected, direction)
        gesture_recognition_loop(debug=True, frame=None, current_camera=current_camera, color_mode=color_mode, increased_ratio=bounding_box_ratio)

           
    except Exception as e:
        print(f"Error processing gesture: {e}")
        return jsonify({"error": "Internal server error"}), 500

       
@app.route('/update-settings', methods=['POST'])
def update_system_settings():
    """Update the system settings based on the request."""
    global current_camera, color_mode, bounding_box_ratio
    try:
        data = request.get_json()  # Parse the incoming JSON request
        
        # Validate incoming data (add more validation as needed)
        if 'camera' in data:
            current_camera = data['camera']
        if 'color_mode' in data:
            color_mode = data['color_mode']
        if 'bounded_ratio' in data:
            bounding_box_ratio = data['bounded_ratio']
        
        # Log the updated settings (this can be customized further)
        print(f"Updated settings: Camera: {current_camera}, Color Mode: {color_mode}, Bounded Ratio: {bounding_box_ratio}")
        
        return jsonify({"message": "Settings updated successfully", "settings": {
            "camera": current_camera,
            "color_mode": color_mode,
            "bounded_ratio": bounding_box_ratio
        }})
    except Exception as e:
        print(f"Error updating settings: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/settings', methods=['GET'])
def get_system_settings():
    """Retrieve the current system settings."""
    try:
        return jsonify({
            "camera": current_camera,
            "color_mode": color_mode,
            "bounded_ratio": bounding_box_ratio
        })
    except Exception as e:
        print(f"Error retrieving settings: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
@app.route('/update-gesture-mappings', methods=['POST'])
def update_gesture_mappings():
    """Update the gesture mappings based on the request."""
    global gesture_mappings
    try:
        if request.content_type != 'application/json':
            return jsonify({"error": "Unsupported Media Type: Content-Type must be application/json"}), 415

        data = request.get_json()  # Parse the incoming JSON request
        
        # Validate incoming data (add more validation as needed)
        for gesture in gesture_mappings.keys():
            if gesture in data:
                gesture_mappings[gesture] = data[gesture]
        
        # Log the updated gesture mappings (this can be customized further)
        print(f"Updated gesture mappings: {gesture_mappings}")
        
        return jsonify({"message": "Gesture mappings updated successfully", "gesture_mappings": gesture_mappings})
    except Exception as e:
        print(f"Error updating gesture mappings: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/gesture-mappings', methods=['GET'])
def get_gesture_mappings():
    """Retrieve the current gesture mappings."""
    try:
        return jsonify(gesture_mappings)
    except Exception as e:
        print(f"Error retrieving gesture mappings: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
@app.route('/')
def index():
    return "API is running. Endpoints: /video_feed, /recognize_gesture"

if __name__ == '__main__':
   
    app.run(host='0.0.0.0', port=5000) 
