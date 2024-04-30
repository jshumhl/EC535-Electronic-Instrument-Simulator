import pygame
import Adafruit_BBIO.GPIO as GPIO
import time

# Initialize Pygame Mixer
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024) 

# Instruments definition
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


# Function to set up GPIO pins and callbacks for the current instrument
def setup_notes():
    global notes
    notes = instruments[current_instrument]
    for note_name, note_info in notes.items():
        GPIO.setup(note_info['pin'], GPIO.IN)
        GPIO.remove_event_detect(note_info['pin'])  # Remove previous event detection
        GPIO.add_event_detect(note_info['pin'], GPIO.RISING,
                              callback=lambda channel, sound=pygame.mixer.Sound(note_info['file']), note_name=note_name: (sound.play(), print(f"{current_instrument} Note pressed: {note_name}")),
                              bouncetime=300)

setup_notes()  # Initial setup for piano

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


def play_note(note):
    sound_file = instruments[current_instrument][note]
    sound = pygame.mixer.Sound(sound_file)
    sound.play()
    if recording:
        record_event(note)
        
# Setup recording button
recording_pin = 'P8_17'
GPIO.setup(recording_pin, GPIO.IN)
last_press_time = None
recording = False
events = []

def record_event(channel):
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

GPIO.add_event_detect(recording_pin, GPIO.BOTH, callback=record_event, bouncetime=300)

def playback_events(events):
    start_time = time.time()
    for instrument, note, event_time in events:
        # Wait for the right time to play the note
        while time.time() - start_time < event_time:
            time.sleep(0.01)  # Sleep a short time to allow for timely playback
        # Play the note from the correct instrument
        sound_file = instruments[instrument][note]
        sound = pygame.mixer.Sound(sound_file)
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