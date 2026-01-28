"""
Chord to MIDI Converter

Converts Harte chord notation to MIDI note numbers for Ableton Live.
"""

import logging
import re
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


# Note name to semitone mapping
NOTE_MAP = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}

# Chord quality to interval mapping (in semitones)
CHORD_INTERVALS = {
    # Triads
    'maj': [0, 4, 7],
    'min': [0, 3, 7],
    'dim': [0, 3, 6],
    'aug': [0, 4, 8],
    'sus2': [0, 2, 7],
    'sus4': [0, 5, 7],
    
    # Seventh chords
    'maj7': [0, 4, 7, 11],
    'min7': [0, 3, 7, 10],
    'dom7': [0, 4, 7, 10],
    'dim7': [0, 3, 6, 9],
    'hdim7': [0, 3, 6, 10],  # Half-diminished
    'aug7': [0, 4, 8, 10],
    'maj6': [0, 4, 7, 9],
    'min6': [0, 3, 7, 9],
    
    # Extended chords
    'maj9': [0, 4, 7, 11, 14],
    'min9': [0, 3, 7, 10, 14],
    'dom9': [0, 4, 7, 10, 14],
    'maj11': [0, 4, 7, 11, 14, 17],
    'min11': [0, 3, 7, 10, 14, 17],
    'dom11': [0, 4, 7, 10, 14, 17],
    'maj13': [0, 4, 7, 11, 14, 17, 21],
    'min13': [0, 3, 7, 10, 14, 17, 21],
    'dom13': [0, 4, 7, 10, 14, 17, 21],
    
    # Add chords
    'add9': [0, 4, 7, 14],
    'add11': [0, 4, 7, 17],
    'add13': [0, 4, 7, 21],
    
    # Default (major triad)
    '': [0, 4, 7],
}


def parse_harte_chord(chord_str: str) -> Tuple[str, str, Optional[str], Optional[str]]:
    """
    Parse Harte notation chord string.
    
    Format: [ROOT][:QUALITY][/BASS][(EXTENSIONS)]
    Examples:
        "C" -> C major
        "C:min" -> C minor
        "C:maj7" -> C major 7th
        "F:min/5" -> F minor with 5th in bass
        "C:maj7(9)" -> C major 7th add 9
    
    Args:
        chord_str: Harte chord notation string
    
    Returns:
        Tuple of (root, quality, bass, extension)
    """
    if not chord_str or chord_str == 'N':  # No chord
        return ('', '', None, None)
    
    # Handle slash chords (bass note)
    if '/' in chord_str:
        chord_part, bass = chord_str.split('/', 1)
    else:
        chord_part, bass = chord_str, None
    
    # Handle extensions in parentheses
    extension_match = re.search(r'\((\d+)\)', chord_part)
    if extension_match:
        extension = extension_match.group(1)
        chord_part = re.sub(r'\(\d+\)', '', chord_part)
    else:
        extension = None
    
    # Parse root and quality
    if ':' in chord_part:
        root_str, quality = chord_part.split(':', 1)
    else:
        # Default to major if no quality specified
        root_str, quality = chord_part, 'maj'
    
    return (root_str.strip(), quality.strip(), bass, extension)


def harte_to_midi_notes(
    chord_str: str,
    root_octave: int = 4,
    voicing: str = "root",
    max_notes: Optional[int] = None,
) -> List[int]:
    """
    Convert Harte notation to MIDI note numbers.
    
    Args:
        chord_str: Harte chord string (e.g., "C:maj7", "F:min/5")
        root_octave: Octave for root note (default 4 = middle C)
        voicing: Voicing style ("root", "close", "open", "spread")
        max_notes: Maximum number of notes to return (None = all)
    
    Returns:
        List of MIDI note numbers (0-127)
    """
    if not chord_str or chord_str == 'N':
        return []
    
    root_str, quality, bass, extension = parse_harte_chord(chord_str)
    
    if not root_str:
        return []
    
    # Get root MIDI note
    root_note = NOTE_MAP.get(root_str, 0)
    root_midi = root_octave * 12 + root_note
    
    # Get intervals for chord quality
    intervals = CHORD_INTERVALS.get(quality, CHORD_INTERVALS['maj'])
    
    # Add extension if specified
    if extension:
        ext_semitones = int(extension) - 1  # Convert scale degree to semitones
        # Adjust for octave
        while ext_semitones < intervals[-1]:
            ext_semitones += 12
        intervals = intervals + [ext_semitones]
    
    # Generate MIDI notes from intervals
    notes = [root_midi + interval for interval in intervals]
    
    # Apply voicing
    if voicing == "open":
        # Spread notes across octaves
        notes = apply_open_voicing(notes)
    elif voicing == "spread":
        # Even wider spread
        notes = apply_spread_voicing(notes)
    elif voicing == "close":
        # Keep in one octave (already done)
        pass
    
    # Handle bass note (inversion)
    if bass:
        bass_note = NOTE_MAP.get(bass, 0)
        bass_midi = (root_octave - 1) * 12 + bass_note
        
        # Remove bass note from chord if present
        notes = [n for n in notes if n % 12 != bass_note]
        
        # Add bass note at the beginning
        notes = [bass_midi] + notes
    
    # Limit number of notes
    if max_notes and len(notes) > max_notes:
        # Keep root and bass, then top notes
        if bass:
            notes = [notes[0]] + notes[-max_notes+1:]
        else:
            notes = notes[:max_notes]
    
    # Remove duplicates and sort
    notes = sorted(set(notes))
    
    # Ensure all notes are in valid MIDI range (0-127)
    notes = [max(0, min(127, n)) for n in notes]
    
    return notes


def apply_open_voicing(notes: List[int]) -> List[int]:
    """Apply open voicing (spread across octaves)."""
    if len(notes) <= 3:
        return notes
    
    # Keep root, move 3rd up an octave, keep 5th, move 7th up
    voiced = [notes[0]]  # Root
    
    for i, note in enumerate(notes[1:], 1):
        if i == 1:  # 3rd
            voiced.append(note + 12)
        elif i == 2:  # 5th
            voiced.append(note)
        else:  # Extensions
            voiced.append(note + 12)
    
    return voiced


def apply_spread_voicing(notes: List[int]) -> List[int]:
    """Apply spread voicing (wider spacing)."""
    if len(notes) <= 2:
        return notes
    
    voiced = [notes[0]]  # Root
    
    for i, note in enumerate(notes[1:], 1):
        # Alternate octaves
        octave_offset = 12 if i % 2 == 0 else 0
        voiced.append(note + octave_offset)
    
    return voiced


def chord_to_voicing(
    chord_str: str,
    voicing_type: str = "close",
    root_octave: int = 4,
) -> List[int]:
    """
    Convert chord to specific voicing.
    
    Args:
        chord_str: Harte chord notation
        voicing_type: "close", "open", "spread", or "root"
        root_octave: Root octave
    
    Returns:
        List of MIDI notes
    """
    return harte_to_midi_notes(chord_str, root_octave, voicing_type)


def get_chord_notes_in_key(
    chord_str: str,
    key: str = "C major",
    root_octave: int = 4,
) -> List[int]:
    """
    Get chord notes, ensuring they fit within the specified key.
    
    Args:
        chord_str: Harte chord notation
        key: Key signature (e.g., "C major", "A minor")
        root_octave: Root octave
    
    Returns:
        List of MIDI notes that fit in the key
    """
    # Get base chord notes
    notes = harte_to_midi_notes(chord_str, root_octave)
    
    # TODO: Implement key filtering
    # For now, return all notes
    return notes


def chord_progression_to_midi(
    chords: List[dict],
    tempo: float = 120.0,
    beats_per_chord: float = 2.0,
) -> List[Tuple[float, float, List[int]]]:
    """
    Convert a chord progression to MIDI note events.
    
    Args:
        chords: List of chord dicts with 'chord', 'time', 'duration'
        tempo: Tempo in BPM
        beats_per_chord: Default beats per chord if duration not in beats
    
    Returns:
        List of (start_beat, duration_beat, midi_notes) tuples
    """
    events = []
    beats_per_sec = tempo / 60.0
    
    for chord_data in chords:
        chord_str = chord_data.get('chord', '')
        time_sec = chord_data.get('time', 0.0)
        duration_sec = chord_data.get('duration', beats_per_chord / beats_per_sec)
        
        # Convert time to beats
        start_beat = time_sec * beats_per_sec
        duration_beat = duration_sec * beats_per_sec
        
        # Convert chord to MIDI notes
        midi_notes = harte_to_midi_notes(chord_str)
        
        if midi_notes:
            events.append((start_beat, duration_beat, midi_notes))
    
    return events

