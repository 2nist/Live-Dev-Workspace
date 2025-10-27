"""
Music Theory Guidance Utilities

Provides reference functions for chord progressions, cadences, modal interchange, substitutions, and diatonic/modal harmony.
All functions are for user guidance only, not enforced rules.
"""

from typing import List, Dict

# --- Progression Theory ---
COMMON_PROGRESSIONS = {
    "major": [
        ["I", "IV", "V"],
        ["ii", "V", "I"],
        ["I", "vi", "IV", "V"],
        ["I", "V", "vi", "IV"],
        ["I", "IV", "vi", "V"],
    ],
    "minor": [
        ["i", "iv", "V"],
        ["i", "VI", "III", "VII"],
        ["i", "ii°", "V", "i"],
    ],
    "modal": {
        "dorian": [["i", "IV", "v"], ["i", "bVII", "IV", "i"]],
        "mixolydian": [["I", "bVII", "IV"], ["I", "IV", "bVII", "I"]],
        # ...other modes
    },
}

# --- Cadences ---
CADENCES = {
    "authentic": ["V", "I"],
    "plagal": ["IV", "I"],
    "deceptive": ["V", "vi"],
    "half": ["IV", "V"],
}

# --- Borrowed Chords / Modal Interchange ---
BORROWED_CHORDS = {
    "major": ["bIII", "bVI", "bVII"],
    "minor": ["IV", "V", "I"],
}

# --- Substitutions ---
SUBSTITUTIONS = {
    "tritone": lambda chord: ["bII7"] if chord.endswith("7") else [],
    "diatonic": lambda chord: ["iii", "vi"] if chord == "I" else [],
    "chromatic": lambda chord: ["bVI", "bII"] if chord == "V" else [],
}

# --- Diatonic & Modal Harmony ---
DIATONIC_DEGREES = {
    "major": ["I", "ii", "iii", "IV", "V", "vi", "vii°"],
    "minor": ["i", "ii°", "III", "iv", "V", "VI", "VII"],
}

MODAL_DEGREES = {
    "dorian": ["i", "ii", "bIII", "IV", "v", "vi°", "bVII"],
    "mixolydian": ["I", "ii", "iii°", "IV", "v", "vi", "bVII"],
    # ...other modes
}

# --- Utility Functions ---
def get_common_progressions(key: str, mode: str = "major") -> List[List[str]]:
    """Return common progressions for the given key and mode."""
    if mode in COMMON_PROGRESSIONS:
        return COMMON_PROGRESSIONS[mode]
    return COMMON_PROGRESSIONS["modal"].get(mode, [])

def get_cadence(cadence_type: str) -> List[str]:
    """Return chord sequence for a given cadence type."""
    return CADENCES.get(cadence_type, [])

def get_borrowed_chords(key: str, mode: str = "major") -> List[str]:
    """Return list of borrowed chords for the key/mode."""
    return BORROWED_CHORDS.get(mode, [])

def get_substitutions(chord: str, type_: str = "tritone") -> List[str]:
    """Suggest possible substitutions for a chord."""
    func = SUBSTITUTIONS.get(type_)
    return func(chord) if func else []

def get_diatonic_degrees(mode: str = "major") -> List[str]:
    """Return diatonic scale degrees for a mode."""
    return DIATONIC_DEGREES.get(mode, [])

def get_modal_degrees(mode: str) -> List[str]:
    """Return modal scale degrees for a mode."""
    return MODAL_DEGREES.get(mode, [])

# --- Registration Functions (for user extension) ---
def add_progression(mode: str, progression: List[str]):
    """Add a custom progression to the library."""
    if mode not in COMMON_PROGRESSIONS:
        COMMON_PROGRESSIONS[mode] = []
    COMMON_PROGRESSIONS[mode].append(progression)

def add_cadence(name: str, chords: List[str]):
    """Add a custom cadence type."""
    CADENCES[name] = chords

def add_borrowed_chord(mode: str, chord: str):
    """Add a borrowed chord to the library."""
    if mode not in BORROWED_CHORDS:
        BORROWED_CHORDS[mode] = []
    if chord not in BORROWED_CHORDS[mode]:
        BORROWED_CHORDS[mode].append(chord)

def add_substitution(type_: str, func):
    """Add a custom substitution function."""
    SUBSTITUTIONS[type_] = func

def add_diatonic_degree(mode: str, degree: str):
    """Add a diatonic degree to the library."""
    if mode not in DIATONIC_DEGREES:
        DIATONIC_DEGREES[mode] = []
    if degree not in DIATONIC_DEGREES[mode]:
        DIATONIC_DEGREES[mode].append(degree)

def add_modal_degree(mode: str, degree: str):
    """Add a modal degree to the library."""
    if mode not in MODAL_DEGREES:
        MODAL_DEGREES[mode] = []
    if degree not in MODAL_DEGREES[mode]:
        MODAL_DEGREES[mode].append(degree)

# --- Guidance API ---
def get_theory_guidance(context: Dict) -> Dict:
    """
    Given an arrangement or section context, return theory suggestions.
    Example: Suggest cadences, substitutions, borrowed chords, progressions.
    """
    # This is a stub for future expansion
    return {
        "progressions": get_common_progressions(context.get("key", "C"), context.get("mode", "major")),
        "cadences": {k: get_cadence(k) for k in CADENCES},
        "borrowed_chords": get_borrowed_chords(context.get("key", "C"), context.get("mode", "major")),
        "substitutions": get_substitutions(context.get("chord", "V7")),
        "diatonic_degrees": get_diatonic_degrees(context.get("mode", "major")),
        "modal_degrees": get_modal_degrees(context.get("mode", "major")),
    }
