"""
Configuration constants for Ableton Arranger.
Ports all constants from the REAPER Lua script.
"""

# Role definitions (Earth tone color palette)
# Colors are in REAPER format (0xBBGGRR), will need conversion for Ableton
ROLES = [
    {"name": "Drums", "color": 0x5C4033FF},    # Dark Brown (coffee)
    {"name": "Bass", "color": 0x8B4513FF},     # Saddle Brown
    {"name": "Chords", "color": 0x228B22FF, "fx": ["Scaler 3", "Scaler 2"]},  # Forest Green
    {"name": "Melody", "color": 0xD2691EFF},   # Chocolate/Burnt Orange
    {"name": "Sequencer", "color": 0x40E0D0FF, "fx": ["apc64_step_sequencer"]}, # Turquoise
    {"name": "FX", "color": 0x6B8E23FF},       # Olive Drab
    {"name": "In1", "color": 0xCD853FFF},      # Peru/Tan
    {"name": "In2", "color": 0x2F4F4FFF},      # Dark Slate Grey (muted teal)
]

# Musical theory data
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Chord color wheel (based on circle of fifths - chordcolors.com style)
# Index by chromatic note: C=0, C#=1, D=2, etc.
NOTE_COLORS = {
    0: 0xE53935FF,   # C  = Red
    1: 0x1E88E5FF,   # C# = Blue
    2: 0xFB8C00FF,   # D  = Orange
    3: 0x8E24AAFF,   # D# = Purple
    4: 0xFDD835FF,   # E  = Yellow
    5: 0xD81B60FF,   # F  = Magenta/Pink
    6: 0x00ACC1FF,   # F# = Cyan/Teal
    7: 0xFF7043FF,   # G  = Orange-Red
    8: 0x5E35B1FF,   # G# = Blue-Purple
    9: 0xC0CA33FF,   # A  = Yellow-Green
    10: 0x7B1FA2FF,  # A# = Deep Purple
    11: 0x43A047FF,  # B  = Green
}

def get_chord_color(root: int) -> int:
    """Get color for a chord based on its root note."""
    return NOTE_COLORS.get(root % 12, 0x808080FF)

# Scale intervals
SCALE_INTERVALS = {
    "ionian": [0, 2, 4, 5, 7, 9, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "aeolian": [0, 2, 3, 5, 7, 8, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10]
}

SCALE_ORDER = ["ionian", "dorian", "phrygian", "lydian", "mixolydian", "aeolian", "locrian"]

# Comprehensive chord types with intervals
CHORD_TYPES = [
    # Basic triads
    {"name": "maj", "intervals": [0, 4, 7], "display": "", "category": "triad"},
    {"name": "min", "intervals": [0, 3, 7], "display": "m", "category": "triad"},
    {"name": "dim", "intervals": [0, 3, 6], "display": "°", "category": "triad"},
    {"name": "aug", "intervals": [0, 4, 8], "display": "+", "category": "triad"},
    
    # Suspended chords
    {"name": "sus2", "intervals": [0, 2, 7], "display": "sus2", "category": "sus"},
    {"name": "sus4", "intervals": [0, 5, 7], "display": "sus4", "category": "sus"},
    {"name": "7sus4", "intervals": [0, 5, 7, 10], "display": "7sus4", "category": "sus"},
    
    # Seventh chords
    {"name": "maj7", "intervals": [0, 4, 7, 11], "display": "maj7", "category": "7th"},
    {"name": "7", "intervals": [0, 4, 7, 10], "display": "7", "category": "7th"},
    {"name": "m7", "intervals": [0, 3, 7, 10], "display": "m7", "category": "7th"},
    {"name": "m/maj7", "intervals": [0, 3, 7, 11], "display": "m(maj7)", "category": "7th"},
    {"name": "dim7", "intervals": [0, 3, 6, 9], "display": "°7", "category": "7th"},
    {"name": "m7b5", "intervals": [0, 3, 6, 10], "display": "ø7", "category": "7th"},
    {"name": "aug7", "intervals": [0, 4, 8, 10], "display": "+7", "category": "7th"},
    
    # Extended chords (9th, 11th, 13th)
    {"name": "9", "intervals": [0, 4, 7, 10, 14], "display": "9", "category": "ext"},
    {"name": "maj9", "intervals": [0, 4, 7, 11, 14], "display": "maj9", "category": "ext"},
    {"name": "m9", "intervals": [0, 3, 7, 10, 14], "display": "m9", "category": "ext"},
    {"name": "11", "intervals": [0, 4, 7, 10, 14, 17], "display": "11", "category": "ext"},
    {"name": "m11", "intervals": [0, 3, 7, 10, 14, 17], "display": "m11", "category": "ext"},
    {"name": "13", "intervals": [0, 4, 7, 10, 14, 21], "display": "13", "category": "ext"},
    {"name": "maj13", "intervals": [0, 4, 7, 11, 14, 21], "display": "maj13", "category": "ext"},
    
    # Add chords
    {"name": "add9", "intervals": [0, 4, 7, 14], "display": "add9", "category": "add"},
    {"name": "madd9", "intervals": [0, 3, 7, 14], "display": "m(add9)", "category": "add"},
    {"name": "add11", "intervals": [0, 4, 7, 17], "display": "add11", "category": "add"},
    {"name": "6", "intervals": [0, 4, 7, 9], "display": "6", "category": "add"},
    {"name": "m6", "intervals": [0, 3, 7, 9], "display": "m6", "category": "add"},
    {"name": "6/9", "intervals": [0, 4, 7, 9, 14], "display": "6/9", "category": "add"},
    
    # Altered chords (for jazz/tension)
    {"name": "7#9", "intervals": [0, 4, 7, 10, 15], "display": "7#9", "category": "alt"},
    {"name": "7b9", "intervals": [0, 4, 7, 10, 13], "display": "7b9", "category": "alt"},
    {"name": "7#5", "intervals": [0, 4, 8, 10], "display": "7#5", "category": "alt"},
    {"name": "7b5", "intervals": [0, 4, 6, 10], "display": "7b5", "category": "alt"},
    {"name": "7alt", "intervals": [0, 4, 8, 10, 13], "display": "7alt", "category": "alt"},
    
    # Power chord
    {"name": "5", "intervals": [0, 7], "display": "5", "category": "power"},
]

# Chord type categories for UI grouping
CHORD_CATEGORIES = [
    {"id": "triad", "name": "Triads"},
    {"id": "sus", "name": "Suspended"},
    {"id": "7th", "name": "7th Chords"},
    {"id": "ext", "name": "Extended"},
    {"id": "add", "name": "Add/6th"},
    {"id": "alt", "name": "Altered"},
    {"id": "power", "name": "Power"},
]

# Inversion names
INVERSION_NAMES = ["Root", "1st Inv", "2nd Inv", "3rd Inv"]

# Function categories for chord progression theory
FUNCTION_CATEGORIES = {
    "tonic": [1, 6],      # I, vi (stability/resolution)
    "subdominant": [2, 4], # ii, IV (motion away from tonic)
    "dominant": [5, 7],    # V, vii° (tension, wants to resolve)
}

# Common progression patterns (from 2nist theory)
PROGRESSION_PRESETS = [
    {"name": "I-IV-V-I (Basic)", "degrees": [1, 4, 5, 1]},
    {"name": "I-V-vi-IV (Pop)", "degrees": [1, 5, 6, 4]},
    {"name": "ii-V-I (Jazz)", "degrees": [2, 5, 1]},
    {"name": "I-vi-IV-V (50s)", "degrees": [1, 6, 4, 5]},
    {"name": "vi-IV-I-V (Axis)", "degrees": [6, 4, 1, 5]},
    {"name": "I-IV-vi-V", "degrees": [1, 4, 6, 5]},
    {"name": "I-ii-V-I", "degrees": [1, 2, 5, 1]},
    {"name": "I-iii-IV-V", "degrees": [1, 3, 4, 5]},
    {"name": "IV-V-iii-vi (Royal Road)", "degrees": [4, 5, 3, 6]},
    {"name": "i-VII-VI-VII (Andalusian)", "degrees": [1, 7, 6, 7]},
    {"name": "I-V-vi-iii-IV-I-IV-V (Canon)", "degrees": [1, 5, 6, 3, 4, 1, 4, 5]},
]

# Common section name presets
SECTION_PRESETS = ["Intro", "Verse", "PreChorus", "Chorus", "Bridge", "Refrain", "Hook", "Break", "Outro", "Custom"]

# Section colors (monochromatic scheme: white for Verse, black for Chorus, greys for others)
# Colors are in REAPER native format (0xBBGGRR)
SECTION_COLORS = {
    "Intro": 0xB0B0B0,      # Light grey
    "Verse": 0xFFFFFF,       # White
    "PreChorus": 0x909090,  # Medium grey
    "Chorus": 0x303030,     # Near black
    "Bridge": 0x707070,     # Dark grey
    "Refrain": 0x404040,    # Darker grey
    "Hook": 0x505050,       # Dark grey
    "Break": 0xA0A0A0,      # Light grey
    "Outro": 0xC0C0C0,      # Very light grey
    "Custom": 0x808080,     # Medium grey (default)
}

def get_section_color(name: str) -> int:
    """Get color for a section based on its name."""
    # Try exact match first
    if name in SECTION_COLORS:
        return SECTION_COLORS[name]
    # Try case-insensitive partial match
    name_lower = name.lower()
    for preset, color in SECTION_COLORS.items():
        if preset.lower() in name_lower or name_lower in preset.lower():
            return color
    # Default grey
    return 0x808080

# Time signature presets
TIME_SIG_PRESETS = [
    {"num": 4, "denom": 4, "display": "4/4"},
    {"num": 3, "denom": 4, "display": "3/4"},
    {"num": 6, "denom": 8, "display": "6/8"},
    {"num": 2, "denom": 4, "display": "2/4"},
    {"num": 5, "denom": 4, "display": "5/4"},
    {"num": 7, "denom": 8, "display": "7/8"},
    {"num": 12, "denom": 8, "display": "12/8"},
]
