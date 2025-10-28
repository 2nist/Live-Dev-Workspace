"""
Analysis and validation endpoints for arrangements.
"""
from arranger.models.arrangement import Arrangement
from arranger.utils.music_theory import get_borrowed_chords, get_cadence

def analyze_arrangement(arrangement: dict):
    """Analyze arrangement for theory features and provide feedback."""
    # Basic analysis
    arr = Arrangement(**arrangement)
    feedback = []
    # Check for borrowed chords
    for section in arr.sections:
        borrowed = [c.name for c in section.chords if c.name in get_borrowed_chords(arr.key, arr.time_signature)]
        if borrowed:
            feedback.append(f"Section {section.label} uses borrowed chords: {', '.join(borrowed)}")
    # Check for cadences
    for order_item in arr.order:
        if order_item.section_label.lower().startswith("cadence"):
            feedback.append(f"Order item {order_item.section_label} may be a cadence.")
    return {"feedback": feedback}

# FastAPI router (optional, for when FastAPI is available)
try:
    from fastapi import APIRouter, Body
    router = APIRouter()
    
    @router.post("/theory/analyze_arrangement")
    def analyze_arrangement_endpoint(arrangement: dict = Body(...)):
        return analyze_arrangement(arrangement)
except ImportError:
    # FastAPI not available, OSC-only mode
    router = None
