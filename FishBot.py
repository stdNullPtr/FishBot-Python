import pyautogui
import pygetwindow as gw
import time
import keyboard
import sounddevice as sd
import numpy as np

FISHING_CAST_DURATION_SECONDS = 15
BOBBER_IMAGE_PATH = "bobber.png"
LOUDNESS_THRESHOLD = 0.8
FISH_FOUND_SPLASH = False
BOBBER_FOUND = False

def sound_callback(indata, frames, time, status):
    """ Callback function for capturing audio data. """
    volume_norm = np.linalg.norm(indata) * 100
    print(f"Sound level: '{volume_norm}'")
    if BOBBER_FOUND and volume_norm > LOUDNESS_THRESHOLD:
        print("Bobber splash! Right-clicking.")
        global FISH_FOUND_SPLASH
        FISH_FOUND_SPLASH = True
        pyautogui.rightClick()
        raise sd.CallbackAbort  # Stop listening

def ensure_window_in_focus(window_title):
    """ Wait for the user to bring a window with the given title into focus. Exit loop if 'DEL' key is pressed. """
    print(f"Waiting for window '{window_title}' to be in focus. Press 'DEL' key to stop the process.")
    while True:
        try:
            window = gw.getWindowsWithTitle(window_title)[0]
            if window.isActive:
                print(f"Window '{window_title}' is now in focus.")
                return True
        except IndexError:
            pass  # Do nothing if the window is not found

        print(f"Waiting for game window '{window_title}' to be in focus...")
        
        # sleep for a total of 5 seconds, while checking if the exit key is being pressed every 0.25 seconds
        for _ in range(20):
            if keyboard.is_pressed('delete'):
                print("Exit key pressed. Stopping the process.")
                return False
            time.sleep(0.25)

def fishing_loop():
    start_time = time.time()
    with sd.InputStream(callback=sound_callback):
        while time.time() - start_time < FISHING_CAST_DURATION_SECONDS:
            global FISH_FOUND_SPLASH
            global BOBBER_FOUND
            if FISH_FOUND_SPLASH == True:
                time.sleep(1) # wait a bit after catch for a reset
                FISH_FOUND_SPLASH = False
                BOBBER_FOUND = False
                return
            if not BOBBER_FOUND:
                try:
                    found_location = pyautogui.locateOnScreen(BOBBER_IMAGE_PATH, confidence=0.6) # Adjust confidence as needed
                    if found_location:
                        print(f"Bobber found at {found_location}")
                        center_point = pyautogui.center(found_location)
                        pyautogui.moveTo(center_point.x, center_point.y, duration=1, tween=pyautogui.easeInOutQuad)
                        BOBBER_FOUND = True
                except Exception as e:
                    print(f"Can't find bobber! {e}")

            # sleep for a total of 0.25 (save cpu usage) seconds, while checking if the exit key is being pressed
            for _ in range(5):
                if keyboard.is_pressed('delete'):
                    print("Exit key pressed. Exiting fishing loop.")
                    return
                time.sleep(0.05)

def main_loop(window_title):
    while True:
        try:
            window_focused = gw.getWindowsWithTitle(window_title)[0].isActive
        except IndexError:
            window_focused = False
        if not window_focused:
            ensure_window_in_focus(window_title)

        print("Main loop.")
        pyautogui.press('1')
        print(f"Pressed '1'. Fishing for {FISHING_CAST_DURATION_SECONDS} seconds at most...")
        
        fishing_loop()

        # sleep for a total of 2 seconds (save cpu usage and wait for loot and old bobber to dissappear) seconds, while checking if the exit key is being pressed
        for _ in range(8):
            if keyboard.is_pressed('delete'):
                print("Exit key pressed. Exiting main loop.")
                return
            time.sleep(0.25)

window_title = "World of Warcraft"
main_loop(window_title)