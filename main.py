import pygame
import Adafruit_BBIO.GPIO as GPIO
import time
import openai

# Initialize Pygame Mixer
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024) 

openai.api_key = "REMOVED_API_KEY_FOR_SECURITY_REASONS"

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

PROMPT_MESSAGE = ("Create a Python script that converts recorded musical events into MIDI files using the 'mido' library. The script needs to accommodate two types of musical instruments: piano and guitar. The data for this script will be provided in a list of tuples, where each tuple represents a musical event. Each tuple contains three elements: the instrument type ('piano' or 'guitar'), the musical note (such as 'C', 'D', 'E' for piano, and specific notes like 'E', 'A', 'D', 'G', 'B', 'E' for guitar," 

"reflecting typical tuning), and the time interval in seconds since the previous note was played. The MIDI note numbers should be mapped such that for piano, Middle C (C4) is MIDI number 60, and for guitar, the low E (E2) is MIDI number 40. The script should ensure that each note is played after the specified delay relative to the previous note, replicating the timing as it was originally recorded."

"Additionally, the script should include functionality to save the generated MIDI file in the current directory under the name 'recording.mid'. Please also include a function to preload sounds for quick playback access during execution. The script should handle creating the MIDI file, adding events based on the provided list, saving the completed MIDI file, and provide error handling for common issues such as invalid note entries or unsupported instrument types."

"Example data format for events: events = [('piano', 'C', 0.5), ('guitar', 'E', 1.0), ('piano', 'G', 0.5)]"

"Please ensure the script is fully functional with the above specifications, including the actual events data provided here to demonstrate the expected input and output behavior.")

LLM_MODEL = "gpt-4-turbo"

# Current instrument
current_instrument = 'piano'
menu_options = ['Recording', 'Playback', 'Generate MIDI']
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
    elif app_state == 'midi':
        # Optionally handle stopping midi generating here if it's not automatically managed
        stop_generate_midi()

def execute_selected_option():
    global current_menu_index, app_state
    selected_option = menu_options[current_menu_index]
    if selected_option == 'Recording':
        start_recording()
    elif selected_option == 'Playback':
        start_playback()
    elif selected_option == 'Generate MIDI':
        start_generate_midi()

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

def start_generate_midi():
    global app_state, events
    app_state = 'midi'
    generate_midi(events)

def generate_midi(events):
    global app_state
    message = PROMPT_MESSAGE + str(events)
    print("communicating with openai API")
    response = openai.Completion.create(engine=LLM_MODEL, prompt=message)
    response_text = response.choices[0].text  # assuming this is your API response
    print("response received, running exec on generated script")
    filename = 'llm_midi.py'
    
    with open(filename, 'w') as file:
        file.write(response_text)
    with open(filename, 'r') as file:
        script_content = file.read()
        
    exec(script_content)
    print("midi file generation complete")
    app_state = 'normal'

    
def stop_generate_midi():
    global app_state
    app_state = 'normal'

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
    #print(note_name, app_state)
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
                              bouncetime=500)
setup_gpio()

# Menu/Recording button setup
menu_recording_pin = 'P8_17'
GPIO.setup(menu_recording_pin, GPIO.IN)
# Unified callback function for menu control and recording
GPIO.add_event_detect(menu_recording_pin, GPIO.RISING, callback=lambda channel: menu_control(), bouncetime=500)

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
                              bouncetime=500)

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
GPIO.add_event_detect(instrument_pin, GPIO.RISING, callback=lambda x: switch_instrument(), bouncetime=500)


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
    