"""
ChoCo MIR Dataset Integration for Ableton Live

This module provides tools to convert ChoCo JAMS files to JSON format
and send chord progressions to Ableton Live via OSC.
"""

__version__ = "1.0.0"

from .jams_converter import jams_to_json, batch_convert_jams_to_json, search_json_files
from .chord_converter import harte_to_midi_notes, chord_to_voicing, chord_progression_to_midi
from .live_integration import send_chord_progression_to_live, ChocoLiveBridge
from .metadata_enhancer import MetadataEnhancer, enhance_json_metadata
from .metadata_expander import MetadataExpander, expand_json_metadata

__all__ = [
    "jams_to_json",
    "batch_convert_jams_to_json",
    "search_json_files",
    "harte_to_midi_notes",
    "chord_to_voicing",
    "chord_progression_to_midi",
    "send_chord_progression_to_live",
    "ChocoLiveBridge",
    "MetadataEnhancer",
    "enhance_json_metadata",
    "MetadataExpander",
    "expand_json_metadata",
]
