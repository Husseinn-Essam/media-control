import json
from flask import Flask, Response, jsonify, request
import cv2
import threading
from flask_cors import CORS
import base64

from opencvExp import gesture_recognition_loop
app = Flask(__name__)
CORS(app)

## Params
SETTINGS_FILE = 'settings.json'
GESTURE_MAPPINGS_FILE = 'gesture_mappings.json'

def load_json_file(file_path, default_data):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return default_data

def save_json_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Load settings and gesture mappings
settings = load_json_file(SETTINGS_FILE, {
    "camera": 0,
    "color_mode": "HSV",
    "bounded_ratio": 0.25
})

mappings = load_json_file(GESTURE_MAPPINGS_FILE, {
    "gestureMappings": {
        "oneFinger": "unmapped",
        "twoFinger": "unmapped",
        "threeFinger": "unmapped",
        "fourFinger": "unmapped",
        "fiveFinger": "unmapped",
        "rockOn": "unmapped",
        "fist": "unmapped",
    },
    "directionMappings": {
        "oneFingerUp": "unmapped",
        "oneFingerDown": "unmapped",
        "oneFingerLeft": "unmapped",
        "oneFingerRight": "unmapped",
    },
    "motionMappings": {
        "UP": "unmapped",
        "DOWN": "unmapped",
        "LEFT": "unmapped",
        "RIGHT": "unmapped",
    }
})

gesture_mappings = {"gestureMappings": mappings.get("gestureMappings", {})}
direction_mappings = {"directionMappings": mappings.get("directionMappings", {})}
motion_mappings = {"motionMappings": mappings.get("motionMappings", {})}

@app.route('/recognize_gesture', methods=['POST'])
def recognize_gesture():
    """Process the current frame for gesture recognition."""
    try:
        print(gesture_mappings)
        gesture_recognition_loop(debug=True, frame=None, current_camera=settings["camera"], color_mode=settings["color_mode"], increased_ratio=settings["bounded_ratio"],gesture_mappings=gesture_mappings['gestureMappings'],direction_mappings=direction_mappings['directionMappings'],motion_mappings=motion_mappings['motionMappings'])
    except Exception as e:
        print(f"Error processing gesture: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/update-settings', methods=['POST'])
def update_system_settings():
    """Update the system settings based on the request."""
    global settings
    try:
        if request.content_type != 'application/json':
            return jsonify({"error": "Unsupported Media Type: Content-Type must be application/json"}), 415

        data = request.get_json()  
        
        if 'camera' in data:
            settings["camera"] = data['camera']
        if 'color_mode' in data:
            settings["color_mode"] = data['color_mode']
        if 'bounded_ratio' in data:
            settings["bounded_ratio"] = data['bounded_ratio']

        # print(f"Updated settings: Camera: {settings["camera"]}, Color Mode: {settings["color_mode"]}, Bounded Ratio: {settings["bounded_ratio"]}")

        
        # Save the updated settings to the configuration file
        save_json_file(SETTINGS_FILE, settings)
        
        return jsonify({"message": "Settings updated successfully", "settings": settings})
    except Exception as e:
        print(f"Error updating settings: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/settings', methods=['GET'])
def get_system_settings():
    """Retrieve the current system settings."""
    try:
        return jsonify(settings)
    except Exception as e:
        print(f"Error retrieving settings: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/update-gesture-mappings', methods=['POST'])
def update_gesture_mappings():
    """Update the gesture mappings based on the request."""
    global gesture_mappings, direction_mappings, motion_mappings
    try:
        if request.content_type != 'application/json':
            return jsonify({"error": "Unsupported Media Type: Content-Type must be application/json"}), 415

        data = request.get_json()  
        
        if 'gestureMappings' in data:
            gesture_mappings['gestureMappings'] = data['gestureMappings']
        if 'directionMappings' in data:
            direction_mappings['directionMappings'] = data['directionMappings']
        if 'motionMappings' in data:
            motion_mappings['motionMappings'] = data['motionMappings']
        
        print(f"Updated gesture mappings: {gesture_mappings}")
        print(f"Updated direction mappings: {direction_mappings}")
        print(f"Updated motion mappings: {motion_mappings}")

        # Save the updated mappings to the configuration file
        save_json_file(GESTURE_MAPPINGS_FILE, {
            "gestureMappings": gesture_mappings['gestureMappings'],
            "directionMappings": direction_mappings['directionMappings'],
            "motionMappings": motion_mappings['motionMappings']
        })
        
        return jsonify({
            "message": "Gesture mappings updated successfully",
            "gesture_mappings": gesture_mappings,
            "direction_mappings": direction_mappings,
            "motion_mappings": motion_mappings
        })
    except Exception as e:
        print(f"Error updating gesture mappings: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/gesture-mappings', methods=['GET'])
def get_gesture_mappings():
    """Retrieve the current gesture mappings."""
    try:
        return jsonify({
            "gestureMappings": gesture_mappings['gestureMappings'],
            "directionMappings": direction_mappings['directionMappings'],
            "motionMappings": motion_mappings['motionMappings']
        })
    except Exception as e:
        print(f"Error retrieving gesture mappings: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/')
def index():
    return "API is running. Endpoints: /video_feed, /recognize_gesture, /update-settings, /settings, /update-gesture-mappings, /gesture-mappings"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
