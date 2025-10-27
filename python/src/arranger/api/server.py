"""
FastAPI backend for music theory guidance API.

Exposes endpoints for progressions, cadences, substitutions, borrowed chords, and concept addition.
"""

from fastapi import FastAPI, Body
from arranger.api import theory

app = FastAPI(title="Arranger Music Theory API", description="Reference and guidance endpoints for progressions, cadences, substitutions, and more.")

@app.post("/theory/guidance")
def theory_guidance(context: dict = Body(...)):
    """Get theory guidance for a given context (key, mode, chord)."""
    return theory.api_get_theory_guidance(context)

@app.get("/theory/progressions")
def get_progressions(key: str = "C", mode: str = "major"):
    """Get progression suggestions for key/mode."""
    return theory.api_get_progressions(key, mode)

@app.get("/theory/cadences")
def get_cadences():
    """Get all cadence types."""
    return theory.api_get_cadences()

@app.get("/theory/borrowed_chords")
def get_borrowed_chords(key: str = "C", mode: str = "major"):
    """Get borrowed chords for key/mode."""
    return theory.api_get_borrowed_chords(key, mode)

@app.get("/theory/substitutions")
def get_substitutions(chord: str = "V7", type_: str = "tritone"):
    """Get chord substitutions."""
    return theory.api_get_substitutions(chord, type_)

# --- Concept Addition Endpoints ---
@app.post("/theory/add_progression")
def add_progression(mode: str = Body(...), progression: list = Body(...)):
    """Add a custom progression."""
    return theory.api_add_progression(mode, progression)

@app.post("/theory/add_cadence")
def add_cadence(name: str = Body(...), chords: list = Body(...)):
    """Add a custom cadence."""
    return theory.api_add_cadence(name, chords)

@app.post("/theory/add_borrowed_chord")
def add_borrowed_chord(mode: str = Body(...), chord: str = Body(...)):
    """Add a borrowed chord."""
    return theory.api_add_borrowed_chord(mode, chord)

@app.post("/theory/add_diatonic_degree")
def add_diatonic_degree(mode: str = Body(...), degree: str = Body(...)):
    """Add a diatonic degree."""
    return theory.api_add_diatonic_degree(mode, degree)

@app.post("/theory/add_modal_degree")
def add_modal_degree(mode: str = Body(...), degree: str = Body(...)):
    """Add a modal degree."""
    return theory.api_add_modal_degree(mode, degree)

# To run: `uvicorn arranger.api.server:app --reload`
# OpenAPI docs: http://localhost:8000/docs
