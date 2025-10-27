"""Live integration endpoints for real-time theory suggestions."""
from arranger.api import theory
from arranger.utils import advanced_theory

def live_theory_suggestions(live_state: dict):
    """Suggest theory ideas based on current Live set state."""
    # Example: live_state = {"key": "C", "mode": "major", "tempo": 120, "section": "chorus"}
    guidance = theory.api_get_theory_guidance(live_state)
    # Add advanced suggestions
    voicings = advanced_theory.suggest_voicings("Cmaj7")
    return {"guidance": guidance, "voicings": voicings}

# FastAPI router (optional, for when FastAPI is available)
try:
    from fastapi import APIRouter, Body
    router = APIRouter()
    
    @router.post("/live/theory_suggestions")
    def live_theory_suggestions_endpoint(live_state: dict = Body(...)):
        return live_theory_suggestions(live_state)
except ImportError:
    # FastAPI not available, OSC-only mode
    router = None

# OSC/WebSocket push notifications would be implemented in the server runtime.
