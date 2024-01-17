import sounddevice as sd
import numpy as np
from pynput.keyboard import Controller, Key, Listener
from ewmh import EWMH
import time
import subprocess

def baseline_v2():
    # Visual ASCII Art for Welcome Message
    welcome_message = """
    \033[91m __                                      _             
    (_   _  ._ _   _  _|_ |_  o ._   _     _|_ o  _ |_     
    __) (_) | | | (/_  |_ | | | | | (_|     |  | _> | | \/ 
                                     _| __              /  
    \033[0m
    """

    print("\n\n Welcome to ")
    print(welcome_message)
    print("Let's get started...\n\n\n")  
    time.sleep(3)

    # Ask for the target key
    target_key = input("What is your \033[91mCAST and INTERACT\033[0m keybind? Press the key you want to use: ")

    # Ask for the sound threshold
    threshold = float(input("\033[91mEnter the sound threshold (a numerical value from 1 to 10, e.g., 10):\033[0m "))

    # Show a list of all possible sound devices
    devices = sd.query_devices()
    print("List of available sound devices:")
    for i, device in enumerate(devices):
        print(f"Index {i}: {device['name']}")

    # Ask for the audio input device index
    device_index = int(input("\033[91mEnter the desired audio input device index:\033[0m "))

    # Set the audio device and start the listener
    device = devices[device_index]['index']

    ewmh = EWMH()

    # Get a list of all windows
    windows = subprocess.check_output(['xdotool', 'search', '--onlyvisible', '--name', '']).decode('utf-8').split()

    # Show a list of active windows
    print("\033[91mPlease choose your current World of Warcraft window:\033[0m \n")
    non_empty_windows = [(i, window_id) for i, window_id in enumerate(windows) if subprocess.check_output(['xdotool', 'getwindowname', window_id]).decode('utf-8').strip()]
    for i, window_id in non_empty_windows:
        window_name = subprocess.check_output(['xdotool', 'getwindowname', window_id]).decode('utf-8').strip()
        print(f"Index {i}: {window_name}")

    # Ask for the user's current World of Warcraft window
    wow_index = int(input("\033[91mEnter the index:\033[0m "))

    # Validate the input index
    if 0 <= wow_index < len(windows):
        wow_window_id = windows[wow_index]
        wow_window_name = subprocess.check_output(['xdotool', 'getwindowname', wow_window_id]).decode('utf-8').strip()
        print(f"Selected World of Warcraft window: \033[91m{wow_window_name}\033[0m")
        subprocess.run(['xdotool', 'windowactivate', wow_window_id])
    else:
        print("Invalid index. Exiting.")
        exit()

    # Create a keyboard controller
    keyboard_controller = Controller()
    paused = False  # Flag to track the pause state

    def toggle_pause():
        global paused
        paused = not paused
        print(f"Script {'Paused' if paused else 'Resumed'}")

    # Function to handle key presses
    def on_press(key):
        if key == Key.num_lock:
            toggle_pause()

    # Listener to detect key presses
    listener = Listener(on_press=on_press)
    listener.start()

    print("\033[91mStarting...\033[0m ")
    time.sleep(3)
    keyboard_controller.press(target_key)
    time.sleep(1)
    keyboard_controller.release(target_key)
    print("Listening to sound... ")

    # Function to recast the target key
    def recast_target_key(counter):
        keyboard_controller.press(target_key)
        print(f"Casting... ")
        time.sleep(1)
        keyboard_controller.release(target_key)

    def on_audio(indata, frames, audio_time, status):
        global paused
        if paused:
            return

        volume_norm = np.linalg.norm(indata) * 10    
        if volume_norm > threshold:        
            # Simulate key press
            keyboard_controller.press(target_key)        
            time.sleep(1)  # Adjust the sleep duration if needed
            keyboard_controller.release(target_key)
            
            # Counter for "Gotcha..."
            counter = on_audio.counter if hasattr(on_audio, 'counter') else 1
            print(f"Gotcha... \033[91m{counter}\033[0m")
            on_audio.counter = counter + 1
            
            # Recast the target key
            recast_target_key(counter)

    with sd.InputStream(callback=on_audio, channels=2, device=device):
        try:
            while True:
                time.sleep(1)  # Sleep for 1 second
        except KeyboardInterrupt:
            print("Interrupted by user")

