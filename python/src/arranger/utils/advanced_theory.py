"""
Advanced theory models: scales, microtonal, voicing, and voice leading utilities.
"""
from typing import List, Dict
import math

# --- Non-Western Scales ---
NON_WESTERN_SCALES = {
    "hirajoshi": [0, 2, 3, 7, 8],
    "pelog": [0, 1, 3, 7, 8],
    "maqam rast": [0, 2, 4, 5, 7, 9, 11],
    # ...add more
}

def get_non_western_scale(name: str, root: int = 0) -> List[int]:
    """Return MIDI note numbers for a non-Western scale."""
    intervals = NON_WESTERN_SCALES.get(name)
    if not intervals:
        return []
    return [(root + i) % 12 for i in intervals]

# --- Microtonal Support ---
def get_microtonal_notes(root: int, divisions: int = 24) -> List[float]:
    """Return microtonal note frequencies for a given root and division."""
    return [root + (i / divisions) * 12 for i in range(divisions)]

# --- Custom Tuning Systems ---
def get_custom_tuning(notes: List[float]) -> List[float]:
    """Return custom tuning note frequencies."""
    return notes

# --- Chord Voicing & Voice Leading ---
def suggest_voicings(chord: str, style: str = "close") -> List[int]:
    """Suggest MIDI voicings for a chord and style."""
    # Stub: integrate with Chord model
    if style == "close":
        return [0, 4, 7]
    elif style == "open":
        return [0, 7, 12]
    return [0, 4, 7]

def suggest_voice_leading(chord1: List[int], chord2: List[int]) -> List[int]:
    """Suggest voice leading between two chords (minimize movement)."""
    # Stub: simple nearest note mapping
    return [min(chord2, key=lambda n: abs(n - c)) for c in chord1]
