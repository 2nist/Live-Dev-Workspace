"""
Hardware Bridge for Arranger System.

Connects music theory, chord progressions, and arrangements to hardware controllers.
"""
import logging
from typing import Dict, List, Optional, Callable
from ..models.chord import Chord
from ..models.section import Section
from ..models.arrangement import Arrangement
from .controller_manager import get_controller_manager, HardwareController

logger = logging.getLogger(__name__)


class PadMapping:
    """Defines how pads map to musical elements."""
    
    # Color schemes
    COLORS = {
        # Chord types
        "major": (0, 127, 0),  # Green
        "minor": (0, 0, 127),  # Blue
        "dominant": (127, 64, 0),  # Orange
        "diminished": (127, 0, 127),  # Purple
        "augmented": (127, 127, 0),  # Yellow
        
        # Scale degrees
        "tonic": (0, 127, 0),  # Green
        "subdominant": (64, 64, 127),  # Blue
        "dominant": (127, 64, 0),  # Orange
        
        # Section states
        "playing": (0, 127, 0),  # Green
        "stopped": (64, 64, 64),  # Gray
        "selected": (127, 127, 127),  # White
        "muted": (64, 0, 0),  # Dark red
        
        # UI states
        "active": (127, 127, 127),
        "inactive": (32, 32, 32),
        "highlight": (127, 127, 0),
    }


class ChordPadMode:
    """
    Maps controller pads to chord progression controls.
    
    Layout for 8x8 grid (Push/Launchpad):
    - Top 2 rows: Chord progression (16 chords max)
    - Next 4 rows: Chord variations/voicings
    - Bottom 2 rows: Transport and mode controls
    """
    
    def __init__(self, controller: HardwareController):
        self.controller = controller
        self.current_progression: List[Chord] = []
        self.selected_chord_index: Optional[int] = None
        
    def set_progression(self, chords: List[Chord]):
        """Display chord progression on pads."""
        self.current_progression = chords
        
        # Light up pads for each chord (top 2 rows = 16 pads)
        for i, chord in enumerate(chords[:16]):
            color = self._chord_to_color(chord)
            self.controller.set_pad_color(i, color)
            
        # Clear remaining pads in progression area
        for i in range(len(chords), 16):
            self.controller.set_pad_color(i, (0, 0, 0))
            
    def _chord_to_color(self, chord: Chord) -> tuple:
        """Map chord quality to LED color."""
        quality = chord.quality.lower()
        
        if "maj" in quality:
            return PadMapping.COLORS["major"]
        elif "min" in quality:
            return PadMapping.COLORS["minor"]
        elif "dom" in quality or "7" in quality:
            return PadMapping.COLORS["dominant"]
        elif "dim" in quality:
            return PadMapping.COLORS["diminished"]
        elif "aug" in quality:
            return PadMapping.COLORS["augmented"]
        else:
            return (64, 64, 64)  # Gray for unknown
            
    def highlight_playing_chord(self, chord_index: int):
        """Highlight the currently playing chord."""
        # Dim previous highlight
        if self.selected_chord_index is not None:
            chord = self.current_progression[self.selected_chord_index]
            color = self._chord_to_color(chord)
            self.controller.set_pad_color(self.selected_chord_index, color)
            
        # Bright highlight for current
        self.selected_chord_index = chord_index
        self.controller.set_pad_color(chord_index, PadMapping.COLORS["highlight"])
        
    def show_chord_variations(self, chord: Chord, start_pad: int = 16):
        """
        Display chord variations on pads.
        
        Shows different voicings, inversions, extensions in the variation area.
        """
        variations = [
            {"name": "Root", "offset": 0},
            {"name": "1st Inv", "offset": 1},
            {"name": "2nd Inv", "offset": 2},
            {"name": "Add9", "offset": 0},
            {"name": "Sus4", "offset": 0},
            {"name": "No5", "offset": 0},
        ]
        
        base_color = self._chord_to_color(chord)
        
        for i, var in enumerate(variations[:32]):  # 4 rows = 32 pads
            pad = start_pad + i
            # Slightly dim variations
            color = tuple(int(c * 0.7) for c in base_color)
            self.controller.set_pad_color(pad, color)


class SectionPadMode:
    """
    Maps controller pads to arrangement sections.
    
    Layout:
    - Each pad represents a section
    - Colors indicate section type (verse, chorus, etc.)
    - Brightness indicates playing state
    """
    
    def __init__(self, controller: HardwareController):
        self.controller = controller
        self.sections: List[Section] = []
        self.playing_section: Optional[int] = None
        
    def set_sections(self, sections: List[Section]):
        """Display arrangement sections on pads."""
        self.sections = sections
        
        for i, section in enumerate(sections[:64]):  # Max 64 sections
            color = self._section_to_color(section)
            self.controller.set_pad_color(i, color)
            
        # Clear unused pads
        for i in range(len(sections), 64):
            self.controller.set_pad_color(i, (0, 0, 0))
            
    def _section_to_color(self, section: Section) -> tuple:
        """Map section name to color."""
        name_lower = section.name.lower()
        
        color_map = {
            "intro": (64, 64, 127),  # Light blue
            "verse": (0, 127, 0),  # Green
            "chorus": (127, 0, 0),  # Red
            "bridge": (127, 64, 0),  # Orange
            "outro": (64, 64, 64),  # Gray
            "drop": (127, 0, 127),  # Purple
            "breakdown": (0, 127, 127),  # Cyan
        }
        
        for key, color in color_map.items():
            if key in name_lower:
                return color
                
        return (64, 64, 64)  # Default gray
        
    def set_playing_section(self, section_index: int):
        """Highlight currently playing section."""
        # Dim previous
        if self.playing_section is not None:
            section = self.sections[self.playing_section]
            color = self._section_to_color(section)
            self.controller.set_pad_color(self.playing_section, color)
            
        # Brighten current
        self.playing_section = section_index
        self.controller.set_pad_color(section_index, PadMapping.COLORS["playing"])


class ScalePadMode:
    """
    Maps controller pads to scale/keyboard layout.
    
    Displays scale notes with chromatic/in-scale highlighting.
    """
    
    def __init__(self, controller: HardwareController):
        self.controller = controller
        self.root_note = 60  # Middle C
        self.scale_notes = []
        
    def set_scale(self, root: int, scale_notes: List[int]):
        """
        Display scale on pads in keyboard layout.
        
        Args:
            root: MIDI root note
            scale_notes: List of scale degrees (0-11)
        """
        self.root_note = root
        self.scale_notes = scale_notes
        
        # Map pads to chromatic notes starting from root
        for pad in range(64):
            # Calculate MIDI note for this pad
            midi_note = root + (pad // 8) * 12 + (pad % 8)
            
            # Check if note is in scale
            degree = (midi_note - root) % 12
            
            if degree in scale_notes:
                # In scale - bright color based on degree
                if degree == 0:
                    color = PadMapping.COLORS["tonic"]  # Root
                elif degree == 7:
                    color = PadMapping.COLORS["dominant"]  # Fifth
                elif degree == 5:
                    color = PadMapping.COLORS["subdominant"]  # Fourth
                else:
                    color = (64, 64, 127)  # Other scale tones
            else:
                # Chromatic - dim
                color = (16, 16, 16)
                
            self.controller.set_pad_color(pad, color)


class ArrangerHardwareBridge:
    """
    Bridge between arranger system and hardware controllers.
    
    Provides high-level interface for displaying musical data on hardware.
    """
    
    def __init__(self):
        self.controller_manager = get_controller_manager()
        self.active_mode = "chord"  # chord, section, scale, custom
        
        # Mode handlers
        self.chord_mode: Optional[ChordPadMode] = None
        self.section_mode: Optional[SectionPadMode] = None
        self.scale_mode: Optional[ScalePadMode] = None
        
    def initialize(self):
        """Initialize hardware bridge and detect controllers."""
        detected = self.controller_manager.auto_detect_controllers()
        logger.info(f"Detected {len(detected)} hardware controllers")
        
        for controller_info in detected:
            logger.info(f"Found: {controller_info['type']} on {controller_info['port']}")
            
    def set_mode(self, mode: str):
        """Switch controller mode (chord/section/scale)."""
        self.active_mode = mode
        
        controller = self.controller_manager.get_active_controller()
        if not controller:
            logger.warning("No active controller")
            return
            
        # Clear pads when switching modes
        controller.clear_all_pads()
        
        # Initialize mode
        if mode == "chord":
            self.chord_mode = ChordPadMode(controller)
        elif mode == "section":
            self.section_mode = SectionPadMode(controller)
        elif mode == "scale":
            self.scale_mode = ScalePadMode(controller)
            
        logger.info(f"Switched to {mode} mode")
        
    def display_chord_progression(self, chords: List[Chord]):
        """Display chord progression on active controller."""
        if self.active_mode != "chord":
            self.set_mode("chord")
            
        if self.chord_mode:
            self.chord_mode.set_progression(chords)
            
    def display_arrangement(self, arrangement: Arrangement):
        """Display full arrangement sections on controller."""
        if self.active_mode != "section":
            self.set_mode("section")
            
        if self.section_mode:
            self.section_mode.set_sections(arrangement.sections)
            
    def highlight_playing_chord(self, chord_index: int):
        """Highlight currently playing chord in progression."""
        if self.chord_mode:
            self.chord_mode.highlight_playing_chord(chord_index)
            
    def highlight_playing_section(self, section_index: int):
        """Highlight currently playing section."""
        if self.section_mode:
            self.section_mode.set_playing_section(section_index)
            
    def display_scale(self, root: int, scale_notes: List[int]):
        """Display scale layout on controller."""
        if self.active_mode != "scale":
            self.set_mode("scale")
            
        if self.scale_mode:
            self.scale_mode.set_scale(root, scale_notes)


# Global instance
_hardware_bridge = None

def get_hardware_bridge() -> ArrangerHardwareBridge:
    """Get the global hardware bridge instance."""
    global _hardware_bridge
    if _hardware_bridge is None:
        _hardware_bridge = ArrangerHardwareBridge()
    return _hardware_bridge
