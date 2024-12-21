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

@app.route('/recognize_gesture', methods=['POST'])
def recognize_gesture():
    """Process the current frame for gesture recognition."""
    try:
    
        gesture_recognition_loop(debug=True, frame=None, current_camera=current_camera, color_mode=color_mode, increased_ratio=bounding_box_ratio)

           
    except Exception as e:
        print(f"Error processing gesture: {e}")
        return jsonify({"error": "Internal server error"}), 500

       
@app.route('/update-settings', methods=['POST'])
def update_system_settings():
    """Update the system settings based on the request."""
    global current_camera, color_mode, bounding_box_ratio
    try:
        data = request.get_json() 
        
        if 'camera' in data:
            current_camera = data['camera']
        if 'color_mode' in data:
            color_mode = data['color_mode']
        if 'bounded_ratio' in data:
            bounding_box_ratio = data['bounded_ratio']
        
        print(f"Updated settings: Camera: {current_camera}, Color Mode: {color_mode}, Bounded Ratio: {bounding_box_ratio}")
        
        return jsonify({"message": "Settings updated successfully"}), 200
    except Exception as e:
        print(f"Error updating settings: {e}")
        return jsonify({"error": "Internal server error"}), 500
       
@app.route('/')
def index():
    return "API is running. Endpoints: /video_feed, /recognize_gesture"

if __name__ == '__main__':
   
    app.run(host='0.0.0.0', port=5000) 
