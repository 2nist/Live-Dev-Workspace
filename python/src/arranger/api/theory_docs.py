"""
Theory documentation API endpoints.
"""
from fastapi import APIRouter
from arranger.utils.music_theory import COMMON_PROGRESSIONS, CADENCES, BORROWED_CHORDS, SUBSTITUTIONS

router = APIRouter()

@router.get("/theory/docs/progressions")
def docs_progressions():
    """Get documentation and examples for progressions."""
    return {"progressions": COMMON_PROGRESSIONS, "examples": ["I-IV-V", "ii-V-I"]}

@router.get("/theory/docs/cadences")
def docs_cadences():
    """Get documentation and examples for cadences."""
    return {"cadences": CADENCES, "examples": ["V-I", "IV-I"]}

@router.get("/theory/docs/borrowed_chords")
def docs_borrowed_chords():
    """Get documentation and examples for borrowed chords."""
    return {"borrowed_chords": BORROWED_CHORDS, "examples": ["bVI in major", "IV in minor"]}

@router.get("/theory/docs/substitutions")
def docs_substitutions():
    """Get documentation and examples for substitutions."""
    return {"substitutions": list(SUBSTITUTIONS.keys()), "examples": ["tritone for V7", "diatonic for I"]}
