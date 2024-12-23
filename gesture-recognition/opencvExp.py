import cv2
import numpy as np
import math
from segmenterFunc import segmenter
from customAlgos import convexity_defects, angle_between_points, get_palm_center, is_rock_on, detect_pointing_direction, calcSolidity, filterDefects
from motionFunc import motion_add_point_to_buffer, motion_handle_buffer_reset, motion_track_points
from systemActions import perform_action
# debug related stuff
# current_camera = 0 # default webcam
pause = False
quit = False

# Initialize webcam

def toggle_camera():
    # Using the global variables
    global cap, g_current_camera
    # Release the current camera
    cap.release()
    
    # Switch between cameras
    if g_current_camera == 0:
        g_current_camera = 1
    else:
        g_current_camera = 0

    # Reinitialize the capture with the new camera
    cap = cv2.VideoCapture(g_current_camera)

def toggle_pause():
    global pause
    if pause:
        pause = False
        print('System resumed')
    else:
        pause = True
        print('System paused')

def handle_key():
    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        global quit
        quit = True
    # Switch camera if 's' pressed
    elif cv2.waitKey(1) & 0xFF == ord('s'):
        toggle_camera()
    elif cv2.waitKey(1) & 0xFF == ord('p'):
        toggle_pause()

cap = cv2.VideoCapture(0)
g_current_camera = 0
def gesture_recognition_loop(gesture_mappings,direction_mappings,motion_mappings,debug=True,frame=None,current_camera=0,color_mode="HSV",increased_ratio=0.25, safe_to_run = False):
    if not safe_to_run:
        print("opencvExp: Autolaunch prevented!")
        print("opencvExp: Please set safe_to_run to True to run the gesture recognition loop.")
        return
    
    global cap, g_current_camera
    
    g_current_camera = current_camera
    cap = cv2.VideoCapture(g_current_camera)
    print(gesture_mappings)
    while True:
        # Capture the frame twice a second

        handle_key()
        
        if quit:
            print("Quitting...")
            break
        if pause:
            continue
     
        cv2.waitKey(50)
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame. Exiting...")
            break
        frame = cv2.flip(frame, 1)
    
        # Draw the ROI rectangle
        # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Apply image filtering and gesture recognition
        # roi, thresh, contours = imageFiltering(frame)
        frame = cv2.GaussianBlur(frame, (5, 5), 0)
        results = segmenter(frame,color_mode,increased_ratio)

        # At start we may not have a hand in the frame
        if len(results) == 2:
            thresh, roi  = results
            full_frame_segmented = None 
            capturedFrame = np.zeros_like(frame)  
        else:
            thresh, roi,capturedFrame ,full_frame_segmented = results
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find the contours of the thresholded hand in the context of the full frame
        # Since I need the actual locations as well for my motion tracking
        # - Karim
        countoursFull , _ = cv2.findContours(full_frame_segmented, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        drawing = np.zeros(roi.shape, np.uint8)
        drawing2 = np.zeros(roi.shape, np.uint8)

        # Initialize gesture and motion variables
        gesture = "UNKNOWN"
        motion_detected = "UNKNOWN"
        direction = "UNKNOWN"
        motion_last_detected = "UNKNOWN"
        try:

            contour = max(contours, key=lambda c: cv2.contourArea(c), default=0)
            contourFull = max(countoursFull, key=lambda c: cv2.contourArea(c), default=0)

            palmCenter = get_palm_center(contour)
            palmCenterFull = get_palm_center(contourFull)

            # Add the centroid point of the hand (cx,cy) to a history 
            motion_add_point_to_buffer((palmCenterFull[0], palmCenterFull[1]))

            cv2.circle(drawing, palmCenter, 5, (0, 0, 255), -1)
            cv2.circle(full_frame_segmented, palmCenterFull, 5, (0, 0, 255), -1)

            hull = cv2.convexHull(contour)
            cv2.drawContours(drawing, [contour], -1, (0, 255, 0), 1)
            cv2.drawContours(drawing2, [contourFull], -1, (0, 255, 0), 1)
            cv2.drawContours(drawing, [hull], -1, (0, 0, 255), 1)
    
            hull_indices = cv2.convexHull(contour, returnPoints=False).flatten()

            defects = convexity_defects(contour[:, 0, :], hull_indices)
            
            
            # Filter defects with approximately 90 degrees
            filtered_defects, count_defects = filterDefects( defects, contour)
            
            # Draw filtered convexity defects
            for defect in filtered_defects:
                start_idx, end_idx, far_idx, depth = defect
                start = tuple(contour[start_idx][0])
                end = tuple(contour[end_idx][0])
                far = tuple(contour[far_idx][0])
                cv2.line(drawing, start, end, (255, 0, 0), 1)  # Blue line for defect
                cv2.circle(drawing, far, 5, (0, 255, 255), -1)  # Yellow circle for defect point
            
            palm_center = get_palm_center(contour)
            cv2.circle(drawing, palmCenter, 5, (0, 0, 255), -1)
            direction = detect_pointing_direction(frame, contour)       
            solidity = calcSolidity(contour)
            
            if is_rock_on(contour,drawing,palm_center[0],palm_center[1], count_defects)==True and direction!="oneFingerLeft" and direction!="oneFingerRight" and solidity<=0.6:
                gesture = "rockOn"
            elif count_defects == 0:
                if solidity > 0.6:  # Fist: High solidity (compact shape)
                    gesture = "fist"
                else:  # hand with one finger pointing
                    gesture = "oneFinger"
                    # check direction
                    direction = detect_pointing_direction(frame, contour)
                    cv2.putText(frame, f"Direction: {direction}", (10, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            elif count_defects == 1:
                gesture = "twoFinger"
            elif count_defects == 2:
                gesture = "threeFinger"
            elif count_defects == 3:
                gesture = "fourFinger"
            elif count_defects == 4:
                gesture = "fiveFinger"
            else:
                gesture = "UNKNOWN"
            
            motion_detected = motion_track_points()
            if motion_detected != None:
                motion_last_detected = motion_detected
            
            # perform_action(gesture,gesture_mappings,direction_mappings,motion_mappings,direction,motion_detected)
            
            cv2.putText(frame, f"Gesture: {gesture}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Detected Motion: {motion_detected}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.putText(frame, f"Last Detected Motion: {motion_last_detected}", (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        except Exception as e:
            print(f"Error processing frame: {e}")
            pass
        # debug mode shows different types for frames
        if (debug == True):
            # display the frames
            cv2.imshow("ROI", cv2.resize(roi, (300, 400)))
            cv2.imshow("Threshold", cv2.resize(thresh, (300, 400)))
            cv2.imshow("Drawing", cv2.resize(drawing, (300, 400)))
            cv2.imshow("capturedFrame", capturedFrame)
            if full_frame_segmented is not None and np.any(full_frame_segmented):
                cv2.imshow("full_frame_segmented", full_frame_segmented)
            cv2.imshow("Frame", frame)
        
        # motion_handle_roi_buffer_reset()
      

    cap.release()
    cv2.destroyAllWindows()


gesture_recognition_loop(debug=True,gesture_mappings={
    "ONE": "unmapped",
    "TWO": "mute",
    "THREE": "volume_up",
    "FOUR": "volume_down",
    "FIVE": "play_pause",
    "ROCK ON": "mute",
    "FIST": "unmapped",

} ,direction_mappings=None,motion_mappings=None)
