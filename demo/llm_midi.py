import mido
from mido import MidiFile, MidiTrack, Message

def note_to_midi(note, instrument='piano'):
    # Basic MIDI note numbers for middle C octave (C4) for piano
    piano_mappings = {
        'C': 60, 'D': 62, 'E': 64, 'F': 65, 'G': 67, 'A': 69, 'B': 71
    }

    # Guitar mappings - typically starting from E2 (low E on standard tuning)
    guitar_mappings = {
        'E': 40, 'F': 41, 'F#': 42, 'G': 43, 'G#': 44,
        'A': 45, 'A#': 46, 'B': 47,
        'C': 48, 'C#': 49, 'D': 50, 'D#': 51, 'E': 52,
        'F': 53, 'F#': 54, 'G': 55
    }

    if instrument == 'piano':
        return piano_mappings.get(note, 60)  # Default to Middle C
    elif instrument == 'guitar':
        return guitar_mappings.get(note, 40)  # Default to Low E

# Updated usage assuming instrument is provided
def create_midi(events):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))

    last_time = 0

    for instrument, note, event_time in events:
        note_number = note_to_midi(note, instrument)
        delta_time = int(event_time * mid.ticks_per_beat)
        
        track.append(Message('note_on', note=note_number, velocity=64, time=delta_time))
        track.append(Message('note_off', note=note_number, velocity=64, time=int(0.5 * mid.ticks_per_beat)))

    mid.save('output.mid')

# Example events with instrument specific notes
events = [('guitar', 'G', 8.271004915237427), ('guitar', 'B', 0.4026932716369629), ('guitar', 'G', 0.4025301933288574), ('guitar', 'D', 0.6040258407592773), ('guitar', 'A', 0.9053499698638916), ('guitar', 'D', 0.5031371116638184), ('guitar', 'G', 0.5030207633972168),  ('piano', 'D', 5.186044692993164), ('piano', 'E', 0.5032095909118652), ('piano', 'F', 0.6042444705963135), ('piano', 'E', 0.8054592609405518), ('piano', 'F', 0.6040089130401611), ('piano', 'G', 1.0066492557525635), ('piano', 'A', 0.6045632362365723), ('piano', 'G', 0.6040225028991699), ('piano', 'F', 0.5033879280090332), ('piano', 'E', 0.6042165756225586), ('piano', 'F', 0.5031616687774658), ('piano', 'G', 0.6037414073944092), ('piano', 'D', 1.0067956447601318), ('piano', 'G', 1.0071110725402832), ('piano', 'E', 0.5031237602233887), ('piano', 'C', 0.503305196762085)]
create_midi(events)
