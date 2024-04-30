import pygame
import Adafruit_BBIO.GPIO as GPIO
import time

# Initialize Pygame Mixer
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024) 

# Instruments definition
beep = 'note/beep.mp3'

instruments = {
    'piano': {
        'C': {'pin': 'P8_7', 'file': 'note/piano/piano_c.mp3'},
        'D': {'pin': 'P8_8', 'file': 'note/piano/piano_d.mp3'},
        'E': {'pin': 'P8_9', 'file': 'note/piano/piano_e.mp3'},
        'F': {'pin': 'P8_10', 'file': 'note/piano/piano_f.mp3'},
        'G': {'pin': 'P8_11', 'file': 'note/piano/piano_g.mp3'},
        'A': {'pin': 'P8_12', 'file': 'note/piano/piano_a.mp3'},
        'B': {'pin': 'P8_14', 'file': 'note/piano/piano_b.mp3'}
    },
    'guitar': {
        'E': {'pin': 'P8_7', 'file': 'note/guitar/guitar_e.mp3'},
        'A': {'pin': 'P8_8', 'file': 'note/guitar/guitar_a.mp3'},
        'D': {'pin': 'P8_9', 'file': 'note/guitar/guitar_d.mp3'},
        'G': {'pin': 'P8_10', 'file': 'note/guitar/guitar_g.mp3'},
        'B': {'pin': 'P8_11', 'file': 'note/guitar/guitar_b.mp3'},
        'he': {'pin': 'P8_12', 'file': 'note/guitar/guitar_he.mp3'},
        'hE': {'pin': 'P8_14', 'file': 'note/guitar/guitar_he.mp3'}
    }
}

# Current instrument
current_instrument = 'piano'
menu_options = ['Recording', 'Playback']
current_menu_index = 0  # Tracks which menu option is selected
app_state = 'normal'  # Can be 'normal', 'menu', 'recording', 'playback'
def menu_control():
    global app_state, recording, last_press_time
    #print(app_state)
    if app_state == 'normal':
        # Open the menu to select an option
        app_state = 'menu'
        display_menu()
    elif app_state == 'menu':
        # Execute the selected option from the menu
        execute_selected_option()
    elif app_state == 'recording':
        # Stop recording if currently recording
        stop_recording()
    elif app_state == 'playback':
        # Optionally handle stopping playback here if it's not automatically managed
        stop_playback()

def execute_selected_option():
    global current_menu_index, app_state
    selected_option = menu_options[current_menu_index]
    if selected_option == 'Recording':
        start_recording()
    elif selected_option == 'Playback':
        start_playback()

def start_recording():
    global recording, app_state, events, last_press_time
    recording = True
    app_state = 'recording'
    events = []
    last_press_time = time.time()  # Initialize last_press_time at the start of recording   
    print("Recording started.")

def stop_recording():
    global recording, app_state
    recording = False
    app_state = 'normal'
    print("Recording stopped.")
    print("Recorded events:", events)

def start_playback():
    global app_state
    app_state = 'playback'
    sounds = preload_sounds(instruments)
    playback_events(events, sounds)

def stop_playback():
    global app_state
    app_state = 'normal'
    # If there are any specific actions to stop playback, add them here

def display_menu():
    global current_menu_index
    print("Menu:")
    for index, option in enumerate(menu_options):
        prefix = "[*]" if index == current_menu_index else "[ ]"
        print(f"{prefix} {option}")

def play_note(sound):
    #sound_file = instruments[current_instrument][note]
    #sound = pygame.mixer.Sound(note_info['file'])
    sound.play()
    #if recording:
        #record_event(note)

# Define note button functions to select menu options
def note_button_pressed(note_name, sound):
    global current_menu_index, app_state
    print(note_name, app_state)
    if app_state == 'menu':
        # Assume 'C' corresponds to the first menu option, etc.
        menu_index = 'CDEFGAB'.index(note_name)
        if menu_index < len(menu_options):
            current_menu_index = menu_index
            #print(current_menu_index)
            display_menu()  # Re-display the menu with the new selection highlighted
    else:
        # Normal operation
        play_note(sound)

def setup_gpio():
    for note_name, note_info in instruments[current_instrument].items():
        GPIO.setup(note_info['pin'], GPIO.IN)
        # Ensure the lambda captures 'note_name' correctly by using it as a default argument
        GPIO.add_event_detect(note_info['pin'], GPIO.RISING, 
                              callback=lambda channel, note_name=note_name: note_button_pressed(note_name), 
                              bouncetime=300)
setup_gpio()

# Menu/Recording button setup
# Menu/Recording button setup
menu_recording_pin = 'P8_17'
GPIO.setup(menu_recording_pin, GPIO.IN)
# Unified callback function for menu control and recording
GPIO.add_event_detect(menu_recording_pin, GPIO.RISING, callback=lambda channel: menu_control(), bouncetime=300)

def menu_or_record_control():
    global app_state
    if app_state == 'normal':
        app_state = 'menu'
        display_menu()
    elif app_state == 'menu':
        execute_selected_option()
    elif app_state == 'recording':
        record_event()

# Function to set up GPIO pins and callbacks for the current instrument
def setup_notes():
    global notes
    notes = instruments[current_instrument]
    for note_name, note_info in notes.items():
        GPIO.setup(note_info['pin'], GPIO.IN)
        GPIO.remove_event_detect(note_info['pin'])  # Remove previous event detection
        GPIO.add_event_detect(note_info['pin'], GPIO.RISING,
                callback=lambda channel, sound=pygame.mixer.Sound(note_info['file']), note_name=note_name: (note_button_pressed(note_name, sound), print(f"{current_instrument} Note pressed: {note_name}")),
                              bouncetime=300)

setup_notes()

# Function to switch instruments
def switch_instrument():
    global current_instrument
    order = ['piano', 'guitar']  # Order of instruments
    current_index = order.index(current_instrument)
    current_instrument = order[(current_index + 1) % len(order)]
    print("Switched to", current_instrument)
    setup_notes()  # Re-setup GPIOs for the new instrument

# Setup the switch button
instrument_pin = 'P8_18'
GPIO.setup(instrument_pin, GPIO.IN)
GPIO.add_event_detect(instrument_pin, GPIO.RISING, callback=lambda x: switch_instrument(), bouncetime=300)


def play_note(sound):
    sound.play()

        
# Setup recording button
recording_pin = 'P8_17'
GPIO.setup(recording_pin, GPIO.IN)
last_press_time = None
recording = False
events = []

def record_event(channel=None):
    global last_press_time, recording, events
    current_time = time.time()
    if not recording:
        recording = True
        events = []  # Clear previous events
        print("Recording started.")
    else:
        recording = False
        print("Recording stopped.")
        print("Recorded events:", events)
    last_press_time = current_time
    
def preload_sounds(instruments):
    sounds = {}
    for inst, notes in instruments.items():
        for note, info in notes.items():
            sound_file = info['file']
            sounds[(inst, note)] = pygame.mixer.Sound(sound_file)
    return sounds

def playback_events(events, sounds):
    for instrument, note, wait_time in events:
        time.sleep(wait_time)  # Wait for the time specified in the event
        sound = sounds[(instrument, note)]
        sound.play()

try:
    while True:
        # Check each note pin if it's pressed and record the event if recording is active
        if recording:
            for note_name, note_info in notes.items():
                if GPIO.input(note_info['pin']):
                    event_time = time.time() - last_press_time
                    # Record the current instrument along with the note and event time
                    events.append((current_instrument, note_name, event_time))
                    last_press_time = time.time()
        time.sleep(0.1)  # Check every 100ms
except KeyboardInterrupt:
    print("Program terminated by user")
finally:
    GPIO.cleanup()  # Clean up GPIO settings before exiting
    
    
#Could we include feature that parse an input audio signal and convert it into MIDI notes. Turn through an internal music sample and output as the sound of a different instrument. I think this is doable since the
