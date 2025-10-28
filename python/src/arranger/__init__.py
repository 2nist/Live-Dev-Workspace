"""
Song Arrangement System for Ableton Live

A modular, production-ready system for creating and managing
song arrangements with sections, chords, and playback sequencing.
"""

__version__ = "0.1.0"
__author__ = "Live-Dev-Workspace Team"

from .models.section import Section, SectionType
from .models.chord import Chord, ChordQuality
from .models.arrangement import Arrangement, OrderItem

__all__ = [
    "Section",
    "SectionType",
    "Chord",
    "ChordQuality",
    "Arrangement",
    "OrderItem",
]
