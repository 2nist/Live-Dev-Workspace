"""
Unified Arrangement Service.

Combines ArrangementBuilder, SceneManager, and ChordClipFactory functionality
into a single service for building arrangements in Ableton Live.
"""

from typing import List, Dict, Optional
import logging
from arranger.live_bridge.ableton_connection import AbletonConnection
from arranger.live_bridge.live_bridge import SceneManager, ChordClipFactory, PlaybackScheduler
from arranger.models.arrangement import Arrangement
from arranger.models.section import Section
from arranger.models.chord import Chord

logger = logging.getLogger(__name__)


class ArrangementService:
    """
    Unified service for building and managing arrangements in Ableton Live.
    
    Combines scene management, clip creation, and arrangement building.
    """
    
    def __init__(self, connection: Optional[AbletonConnection] = None):
        """
        Initialize arrangement service.
        
        Args:
            connection: AbletonConnection instance (creates mock if None)
        """
        if connection is None:
            connection = AbletonConnection(mock=True)
        
        self.connection = connection
        self.scene_manager = SceneManager(connection)
        self.clip_factory = ChordClipFactory(connection)
        self.playback_scheduler = PlaybackScheduler(connection)
        
        self.role_tracks: Dict[str, int] = {}  # Cache track IDs by role name
        self.track_counter = 0
    
    def build_arrangement(self, arrangement: Arrangement, 
                         role_tracks: Optional[Dict[str, int]] = None) -> bool:
        """
        Build complete arrangement in Ableton Live.
        
        Args:
            arrangement: Arrangement instance
            role_tracks: Optional mapping of role names to track indices
            
        Returns:
            True if successful
        """
        if not arrangement.sections:
            logger.warning("No sections to build")
            return False
        
        if not self.connection.is_connected():
            logger.warning("Not connected to Ableton Live - using mock mode")
        
        # Set global tempo
        self.connection.set_tempo(arrangement.bpm)
        
        # Ensure role tracks exist
        if role_tracks:
            self.role_tracks = role_tracks
        else:
            self._ensure_role_tracks()
        
        # Build sections as scenes
        scene_mapping = {}  # Maps section labels to scene indices
        
        for section_idx, section in enumerate(arrangement.sections):
            # Create scene for this section
            scene_index = self.scene_manager.create_scene(section.label, [])
            scene_mapping[section.label] = scene_index
            
            # Set scene name
            self.connection.set_scene_name(scene_index, section.label)
            
            # Set tempo if section has override
            if section.tempo_override:
                # Note: Tempo is global in Live, so we can't set per-section
                # This would need tempo automation or separate Live sets
                pass
            
            # Create clips for each role track
            for role_name, track_id in self.role_tracks.items():
                # Calculate clip length
                beats_per_bar = section.time_signature[0] * (4.0 / section.time_signature[1])
                clip_length = section.bars * beats_per_bar
                
                # Create MIDI clip
                self.connection.create_midi_clip(track_id, scene_index, clip_length)
                self.connection.set_clip_name(track_id, scene_index, f"{section.label} - {role_name}")
                
                # If this is the Chords track, add chord notes
                if role_name == "Chords" and section.chords:
                    self._add_chords_to_clip(track_id, scene_index, section, clip_length)
        
        # Build playback order
        if arrangement.order:
            order_labels = []
            for order_item in arrangement.order:
                for _ in range(order_item.repeat):
                    order_labels.append(order_item.section_label)
            
            self.playback_scheduler.schedule_playback(order_labels)
        
        logger.info(f"Built arrangement: {len(arrangement.sections)} sections")
        return True
    
    def build_from_sections(self, sections: List[Section], 
                           title: str = "Untitled",
                           bpm: float = 120.0,
                           key: str = "C") -> bool:
        """
        Build arrangement from list of sections (legacy compatibility).
        
        Args:
            sections: List of Section instances
            title: Arrangement title
            bpm: Tempo
            key: Key
            
        Returns:
            True if successful
        """
        # Convert sections to Arrangement
        from arranger.models.arrangement import Arrangement, OrderItem
        
        # Create order from sections
        order = [OrderItem(section_label=s.label) for s in sections]
        
        arrangement = Arrangement(
            title=title,
            bpm=bpm,
            key=key,
            sections=sections,
            order=order
        )
        
        return self.build_arrangement(arrangement)
    
    def _ensure_role_tracks(self):
        """Ensure role tracks exist (creates if needed)."""
        # Default role tracks
        roles = ["Drums", "Bass", "Chords", "Melody", "Pads"]
        
        for role in roles:
            if role not in self.role_tracks:
                # Create track (placeholder - would need OSC implementation)
                # For now, assign sequential track IDs
                self.role_tracks[role] = self.track_counter
                self.track_counter += 1
                logger.info(f"Assigned track {self.role_tracks[role]} to role '{role}'")
    
    def _add_chords_to_clip(self, track_id: int, scene_index: int, 
                            section: Section, clip_length: float):
        """
        Add chord notes to a MIDI clip.
        
        Args:
            track_id: Track index
            scene_index: Scene/clip index
            section: Section with chords
            clip_length: Clip length in beats
        """
        if not section.chords:
            return
        
        notes = []
        for chord in section.chords:
            # Get MIDI notes for chord
            midi_notes = chord.to_midi_notes(octave=4, style="close")
            
            # Calculate timing
            # Note: Pydantic Chord uses 'beats' field, but we need start_beat
            # This should be stored in metadata or calculated from position
            start_beat = 0.0  # Default - would need to track chord positions
            if hasattr(chord, 'metadata') and 'start_beat' in chord.metadata:
                start_beat = chord.metadata['start_beat']
            
            duration = float(chord.beats)
            
            # Add notes
            for pitch in midi_notes:
                notes.append((pitch, start_beat, duration, 100))
        
        if notes:
            self.connection.add_midi_notes(track_id, scene_index, notes)
            logger.info(f"Added {len(notes)} notes to clip")
    
    def get_scene_for_section(self, section_label: str) -> Optional[int]:
        """Get scene index for a section label."""
        # Would need to track this during build
        return None
    
    def trigger_section(self, section_label: str):
        """Trigger playback of a section."""
        scene_index = self.get_scene_for_section(section_label)
        if scene_index is not None:
            self.connection.trigger_scene(scene_index)
