import pyautogui
import time
last_action_time = 0
action_cooldown = 1.5 

def perform_action(gesture, gesture_mappings, direction_mappings, motion_mappings, direction=None, movement=None):
    global last_action_time
    current_time = time.time()
    

    try:
        # Handle motions first if present, as it takes precedence
        if movement:
            movement_action = motion_mappings.get(movement, "unmapped")
            print(f"Movement: {movement}")
            print(f"Movement Action: {movement_action}")

            if movement_action == "fullscreen":
                pyautogui.press('f')
            elif movement_action == "close":
                pyautogui.hotkey('ctrl', 'q')
            elif movement_action == "changeAudioDevice":
                pyautogui.hotkey('shift', 'a')
            elif movement_action == "showTime":
                pyautogui.press('t')

            last_action_time = current_time
            return 
        
        # cooldown
        if current_time - last_action_time < action_cooldown:
            return  
        
        # Handle gestures if there is no motion
        action = gesture_mappings.get(gesture, "unmapped")
        if direction and gesture == "oneFinger":
            action = direction_mappings.get(direction, "unmapped")
            print(f"Direction: {direction}")
            print(f"Action: {action}")

        if action == "mute":
            pyautogui.press("volumemute")
        elif action == "volume_up":
            pyautogui.press("volumeup")
        elif action == "volume_down":
            pyautogui.press("volumedown")
        elif action == "play_pause":
            pyautogui.press("playpause")
        elif action == "next":
            pyautogui.press('n')
        elif action == "previous":
            pyautogui.press('p')
        elif action == "fast_forward":
            pyautogui.hotkey('ctrl', 'right')
        elif action == "rewind":
            pyautogui.hotkey('ctrl', 'left')
        elif action == "speed_up":
            pyautogui.press('=')
        elif action == "speed_down":
            pyautogui.press('-')

        last_action_time = current_time

    except Exception as e:
        print(f"Error performing action: {e}")
