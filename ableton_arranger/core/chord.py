"""
Chord theory, types, and progression functions.
Ports all chord-related functionality from the REAPER script.
"""
from dataclasses import dataclass
from typing import Optional, List, Tuple
import ableton_arranger.config as config


@dataclass
class Chord:
    """Represents a chord with root, type, timing, and voicing."""
    root: int  # 0-11 (C=0, C#=1, etc.)
    type_idx: int = 1  # Index into CHORD_TYPES
    start_beat: float = 0.0
    duration_beats: float = 4.0
    inversion: int = 0
    bass_note: Optional[int] = None  # 0-11, for slash chords
    octave: int = 4
    
    def to_dict(self) -> dict:
        """Convert chord to dictionary for JSON serialization."""
        return {
            "root": self.root,
            "type_idx": self.type_idx,
            "start_beat": self.start_beat,
            "duration_beats": self.duration_beats,
            "inversion": self.inversion,
            "bass_note": self.bass_note,
            "octave": self.octave
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create chord from dictionary."""
        return cls(
            root=data.get("root", 0),
            type_idx=data.get("type_idx", 1),
            start_beat=data.get("start_beat", 0.0),
            duration_beats=data.get("duration_beats", 4.0),
            inversion=data.get("inversion", 0),
            bass_note=data.get("bass_note"),
            octave=data.get("octave", 4)
        )


def get_scale_notes(root: int, scale_type: str) -> List[int]:
    """Get the scale notes for a given root and scale type."""
    intervals = config.SCALE_INTERVALS.get(scale_type, config.SCALE_INTERVALS["ionian"])
    return [(root + interval) % 12 for interval in intervals]


def get_diatonic_chords(root: int, scale_type: str) -> List[dict]:
    """
    Get diatonic chords for a given key and scale type.
    
    Returns:
        List of dicts with root, type_idx, and degree
    """
    scale_notes = get_scale_notes(root, scale_type)
    
    # Mode chord types (1=maj, 2=min, 3=dim, etc.)
    mode_chord_types = {
        "ionian": [1, 2, 2, 1, 1, 2, 8],      # I, ii, iii, IV, V, vi, vii°
        "dorian": [2, 2, 1, 1, 2, 8, 1],       # i, ii, bIII, IV, v, vi°, bVII
        "phrygian": [2, 1, 1, 2, 8, 1, 2],    # i, bII, bIII, iv, v°, bVI, bvii
        "lydian": [1, 1, 2, 8, 1, 2, 2],       # I, II, iii, #iv°, V, vi, vii
        "mixolydian": [1, 2, 8, 1, 2, 2, 1],  # I, ii, iii°, IV, v, vi, bVII
        "aeolian": [2, 8, 1, 2, 2, 1, 1],     # i, ii°, bIII, iv, v, bVI, bVII
        "locrian": [8, 1, 2, 2, 1, 1, 2]      # i°, bII, biii, iv, bV, bVI, bvii
    }
    
    types = mode_chord_types.get(scale_type, mode_chord_types["ionian"])
    diatonic = []
    
    for i, note in enumerate(scale_notes):
        chord_type_idx = types[i] if i < len(types) else 1
        diatonic.append({
            "root": note,
            "type_idx": chord_type_idx,
            "degree": i + 1
        })
    
    return diatonic


def get_chord_name(root: int, type_idx: int, inversion: int = 0, bass_note: Optional[int] = None) -> str:
    """Get the display name for a chord."""
    root_name = config.NOTE_NAMES[root]
    chord_type = config.CHORD_TYPES[type_idx - 1] if 1 <= type_idx <= len(config.CHORD_TYPES) else config.CHORD_TYPES[0]
    display = chord_type["display"]
    if display == "":
        display = "maj"
    
    name = root_name + display
    
    # Add bass note notation if slash chord
    if bass_note is not None and bass_note != root:
        name = name + "/" + config.NOTE_NAMES[bass_note]
    elif inversion > 0:
        # Show inversion as slash chord with bass note
        intervals = chord_type["intervals"]
        if inversion < len(intervals):
            bass_interval = intervals[inversion]
            bass = (root + bass_interval) % 12
            name = name + "/" + config.NOTE_NAMES[bass]
    
    return name


def get_chord_full_name(chord: Chord) -> str:
    """Get full chord name with all details."""
    return get_chord_name(chord.root, chord.type_idx, chord.inversion, chord.bass_note)


def midi_notes_from_chord(chord: Chord) -> List[int]:
    """
    Generate MIDI note numbers for a chord with inversion and octave.
    
    Returns:
        List of MIDI note numbers (0-127)
    """
    chord_type = config.CHORD_TYPES[chord.type_idx - 1] if 1 <= chord.type_idx <= len(config.CHORD_TYPES) else config.CHORD_TYPES[0]
    octave = chord.octave
    base = octave * 12
    intervals = chord_type["intervals"]
    notes = []
    
    # Get all notes first (with MIDI range validation)
    for interval in intervals:
        note = base + chord.root + interval
        if 0 <= note <= 127:
            notes.append(note)
    
    # Apply inversion (move lower notes up an octave)
    inversion = chord.inversion
    for i in range(inversion):
        if len(notes) > 0:
            new_note = notes[0] + 12
            if new_note <= 127:
                notes[0] = new_note
                notes.sort()
            else:
                break  # Can't invert further without exceeding MIDI range
    
    # Override bass note if specified
    if chord.bass_note is not None:
        bass = (octave - 1) * 12 + chord.bass_note
        if 0 <= bass <= 127:
            # Remove any existing note with same pitch class
            notes = [n for n in notes if n % 12 != chord.bass_note]
            notes.insert(0, bass)
    
    return sorted(notes)


def get_tritone_sub(chord: Chord) -> Optional[Chord]:
    """Get tritone substitution (replace V7 with bII7)."""
    chord_type = config.CHORD_TYPES[chord.type_idx - 1] if 1 <= chord.type_idx <= len(config.CHORD_TYPES) else None
    if not chord_type:
        return None
    
    # Tritone sub works best on dominant 7th chords
    if chord_type["category"] == "7th" or chord_type["name"] == "7":
        tritone_root = (chord.root + 6) % 12
        return Chord(
            root=tritone_root,
            type_idx=chord.type_idx,
            start_beat=chord.start_beat,
            duration_beats=chord.duration_beats,
            inversion=0,
            octave=chord.octave,
            bass_note=None
        )
    return None


def get_relative_sub(chord: Chord) -> Optional[Chord]:
    """Get relative major/minor substitution."""
    chord_type = config.CHORD_TYPES[chord.type_idx - 1] if 1 <= chord.type_idx <= len(config.CHORD_TYPES) else None
    if not chord_type:
        return None
    
    new_root = None
    new_type = None
    
    if chord_type["name"] == "maj" or chord_type["name"] == "maj7":
        # Major -> relative minor (down 3 semitones)
        new_root = (chord.root - 3) % 12
        new_type = 6 if chord_type["name"] == "maj7" else 2  # m7 or min
    elif chord_type["name"] == "min" or chord_type["name"] == "m7":
        # Minor -> relative major (up 3 semitones)
        new_root = (chord.root + 3) % 12
        new_type = 8 if chord_type["name"] == "m7" else 1  # maj7 or maj
    else:
        return None
    
    if new_root is None or new_type is None:
        return None
    
    return Chord(
        root=new_root,
        type_idx=new_type,
        start_beat=chord.start_beat,
        duration_beats=chord.duration_beats,
        inversion=0,
        octave=chord.octave
    )


def get_parallel_sub(chord: Chord) -> Optional[Chord]:
    """Get parallel major/minor substitution."""
    chord_type = config.CHORD_TYPES[chord.type_idx - 1] if 1 <= chord.type_idx <= len(config.CHORD_TYPES) else None
    if not chord_type:
        return None
    
    new_type = None
    if chord_type["name"] == "maj":
        new_type = 2  # min
    elif chord_type["name"] == "min":
        new_type = 1  # maj
    elif chord_type["name"] == "maj7":
        new_type = 6  # m7
    elif chord_type["name"] == "m7":
        new_type = 8  # maj7
    else:
        return None
    
    return Chord(
        root=chord.root,
        type_idx=new_type,
        start_beat=chord.start_beat,
        duration_beats=chord.duration_beats,
        inversion=0,
        octave=chord.octave
    )


def get_secondary_dominant(target_root: int, key_root: int) -> Chord:
    """Get secondary dominant (V of the target chord)."""
    # Secondary dominant is a perfect 5th above the target
    sec_dom_root = (target_root + 7) % 12
    return Chord(
        root=sec_dom_root,
        type_idx=9,  # Dominant 7
        inversion=0,
        octave=4
    )


def get_all_secondary_dominants(key_root: int, scale_type: str) -> List[dict]:
    """Get all available secondary dominants for current key."""
    scale_notes = get_scale_notes(key_root, scale_type)
    sec_doms = []
    
    # V/ii, V/iii, V/IV, V/V, V/vi (not V/I or V/vii°)
    targets = [2, 3, 4, 5, 6]
    target_names = ["V/ii", "V/iii", "V/IV", "V/V", "V/vi"]
    
    for i, degree in enumerate(targets):
        if degree <= len(scale_notes):
            target_note = scale_notes[degree - 1]
            sec_dom = get_secondary_dominant(target_note, key_root)
            sec_dom_dict = {
                "root": sec_dom.root,
                "type_idx": sec_dom.type_idx,
                "name": target_names[i],
                "resolves_to": degree
            }
            sec_doms.append(sec_dom_dict)
    
    return sec_doms


def get_borrowed_chords(key_root: int, scale_type: str) -> List[dict]:
    """Get borrowed chords from parallel mode."""
    borrowed = []
    
    # Common borrowed chords from parallel minor (for major keys)
    if scale_type == "ionian":
        # bVII (Mixolydian/natural minor)
        borrowed.append({
            "root": (key_root + 10) % 12,
            "type_idx": 1,
            "name": "bVII",
            "source": "mixolydian"
        })
        # bVI (natural minor)
        borrowed.append({
            "root": (key_root + 8) % 12,
            "type_idx": 1,
            "name": "bVI",
            "source": "aeolian"
        })
        # bIII (natural minor)
        borrowed.append({
            "root": (key_root + 3) % 12,
            "type_idx": 1,
            "name": "bIII",
            "source": "aeolian"
        })
        # iv (minor iv)
        borrowed.append({
            "root": (key_root + 5) % 12,
            "type_idx": 2,
            "name": "iv",
            "source": "aeolian"
        })
        # #IV dim (lydian)
        borrowed.append({
            "root": (key_root + 6) % 12,
            "type_idx": 3,
            "name": "#iv°",
            "source": "lydian"
        })
    elif scale_type == "aeolian":
        # Borrowed from parallel major
        # IV (instead of iv)
        borrowed.append({
            "root": (key_root + 5) % 12,
            "type_idx": 1,
            "name": "IV",
            "source": "ionian"
        })
        # I (picardy third)
        borrowed.append({
            "root": key_root,
            "type_idx": 1,
            "name": "I",
            "source": "ionian"
        })
    
    return borrowed


def get_chord_substitutions(chord: Chord) -> List[Chord]:
    """Get all available chord substitution options."""
    subs = []
    
    tritone = get_tritone_sub(chord)
    if tritone:
        subs.append(tritone)
    
    relative = get_relative_sub(chord)
    if relative:
        subs.append(relative)
    
    parallel = get_parallel_sub(chord)
    if parallel:
        subs.append(parallel)
    
    return subs
