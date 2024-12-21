import pyautogui
import time

last_action_time = 0
action_cooldown = 1
def perform_action(gesture,gesture_mappings):
    global last_action_time
    current_time = time.time()
    if current_time - last_action_time < action_cooldown:
        print("Action on cooldown")
        return 

    try:
        print(gesture)
        action = gesture_mappings.get(gesture, "unmapped")
        print(action)
        if action == "mute":
            pyautogui.press("volumemute")
        elif action == "volume_up":
            pyautogui.press("volumeup")
        elif action == "volume_down":
            pyautogui.press("volumedown")
        elif action == "play_pause":
            pyautogui.press("playpause")
        last_action_time = current_time

    except Exception as e:
        print(f"Error performing action: {e}")
        return
