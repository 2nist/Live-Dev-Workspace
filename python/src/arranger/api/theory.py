"""
API endpoints for music theory guidance (stub).

These endpoints provide reference suggestions for progressions, cadences, substitutions, and modal interchange.
"""

from arranger.utils.music_theory import (
    get_common_progressions,
    get_cadence,
    get_borrowed_chords,
    get_substitutions,
    get_diatonic_degrees,
    get_modal_degrees,
    get_theory_guidance,
    add_progression,
    add_cadence,
    add_borrowed_chord,
    add_substitution,
    add_diatonic_degree,
    add_modal_degree,
)

# Example stub functions for OSC API integration

# --- API Endpoints for Adding Concepts ---
def api_add_progression(mode: str, progression: list):
    """API: Add a custom progression."""
    add_progression(mode, progression)
    return {"status": "ok", "added": progression, "mode": mode}

def api_add_cadence(name: str, chords: list):
    """API: Add a custom cadence."""
    add_cadence(name, chords)
    return {"status": "ok", "added": chords, "name": name}

def api_add_borrowed_chord(mode: str, chord: str):
    """API: Add a borrowed chord."""
    add_borrowed_chord(mode, chord)
    return {"status": "ok", "added": chord, "mode": mode}

def api_add_substitution(type_: str, func):
    """API: Add a custom substitution function."""
    add_substitution(type_, func)
    return {"status": "ok", "type": type_}

def api_add_diatonic_degree(mode: str, degree: str):
    """API: Add a diatonic degree."""
    add_diatonic_degree(mode, degree)
    return {"status": "ok", "added": degree, "mode": mode}

def api_add_modal_degree(mode: str, degree: str):
    """API: Add a modal degree."""
    add_modal_degree(mode, degree)
    return {"status": "ok", "added": degree, "mode": mode}

def api_get_progressions(key: str, mode: str = "major"):
    """API: Get progression suggestions."""
    return get_common_progressions(key, mode)

def api_get_cadences():
    """API: Get all cadence types."""
    return {k: get_cadence(k) for k in ["authentic", "plagal", "deceptive", "half"]}

def api_get_borrowed_chords(key: str, mode: str = "major"):
    """API: Get borrowed chords for key/mode."""
    return get_borrowed_chords(key, mode)

def api_get_substitutions(chord: str, type_: str = "tritone"):
    """API: Get chord substitutions."""
    return get_substitutions(chord, type_)

def api_get_theory_guidance(context: dict):
    """API: Get all theory guidance for a context (arrangement/section)."""
    return get_theory_guidance(context)
