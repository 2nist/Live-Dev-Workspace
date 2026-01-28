"""
Max for Live Integration Bridge.

Provides helpers and utilities for Max for Live device development.
"""

from typing import Dict, List, Optional, Any
from arranger.live_bridge.osc_server import ArrangerOSCServer


class M4LBridge:
    """
    Bridge for Max for Live device integration.
    
    Provides simplified API for common Max for Live operations.
    """
    
    def __init__(self, osc_server: Optional[ArrangerOSCServer] = None):
        """
        Initialize M4L bridge.
        
        Args:
            osc_server: Optional OSC server instance (creates new if None)
        """
        self.osc_server = osc_server
    
    def get_chord_suggestions(self, key: str, mode: str = "major") -> List[Dict]:
        """
        Get chord suggestions for Max for Live device.
        
        Args:
            key: Key name
            mode: Mode name
            
        Returns:
            List of chord dictionaries
        """
        from arranger.services.theory_service import TheoryService
        service = TheoryService()
        return service.get_diatonic_chords(key, mode)
    
    def get_progression_templates(self, key: str, mode: str = "major") -> List[List[str]]:
        """
        Get progression templates for Max for Live device.
        
        Args:
            key: Key name
            mode: Mode name
            
        Returns:
            List of progression lists
        """
        from arranger.services.theory_service import TheoryService
        service = TheoryService()
        return service.get_progressions(key, mode)
    
    def create_chord_midi(self, chord_name: str, octave: int = 4) -> List[int]:
        """
        Generate MIDI notes for a chord name.
        
        Args:
            chord_name: Chord name (e.g., "Cmaj7")
            octave: Base octave
            
        Returns:
            List of MIDI note numbers
        """
        from arranger.models.chord import Chord
        try:
            chord = Chord.from_name(chord_name, beats=4)
            return chord.to_midi_notes(octave=octave, style="close")
        except:
            return []
    
    def validate_chord(self, chord_name: str) -> bool:
        """
        Validate a chord name.
        
        Args:
            chord_name: Chord name to validate
            
        Returns:
            True if valid
        """
        from arranger.models.chord import Chord
        try:
            Chord.from_name(chord_name)
            return True
        except:
            return False


# OSC Message Reference for Max for Live
OSC_REFERENCE = {
    "theory": {
        "/theory/progressions": {
            "args": ["key (str)", "mode (str)"],
            "returns": "List of progressions",
            "example": "/theory/progressions C major"
        },
        "/theory/cadences": {
            "args": [],
            "returns": "Dictionary of cadence types",
            "example": "/theory/cadences"
        },
        "/theory/guidance": {
            "args": ["key (str)", "mode (str)", "chord (str)"],
            "returns": "Theory guidance dictionary",
            "example": "/theory/guidance C major Cmaj7"
        }
    },
    "live": {
        "/live/play": {
            "args": [],
            "returns": "Status",
            "example": "/live/play"
        },
        "/live/stop": {
            "args": [],
            "returns": "Status",
            "example": "/live/stop"
        },
        "/live/create_chord_clip": {
            "args": ["chord (str)", "length (float)", "track (int)"],
            "returns": "Status",
            "example": "/live/create_chord_clip Cmaj7 4.0 0"
        },
        "/live/trigger_scene": {
            "args": ["scene_index (int)"],
            "returns": "Status",
            "example": "/live/trigger_scene 0"
        }
    }
}
