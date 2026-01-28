"""
Arrangement builder - creates tracks, clips, and applies sections to Ableton Live.
"""
from typing import List, Dict, Optional
import logging
import sys
import os
# Add python/src to path
workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
python_src = os.path.join(workspace_root, "python", "src")
if python_src not in sys.path:
    sys.path.insert(0, python_src)

from arranger.live_bridge.ableton_connection import AbletonConnection
from arranger.utils.live_adapter import LiveConnectionAdapter
from arranger.utils.adapters import SectionAdapter, ChordAdapter
from arranger.services.arrangement_service import ArrangementService
from ableton_arranger.core.chord import midi_notes_from_chord
import ableton_arranger.config as config


logger = logging.getLogger(__name__)


class ArrangementBuilder:
    """
    Builds arrangement in Ableton Live from sections.
    
    Legacy wrapper around ArrangementService for backward compatibility.
    """
    
    def __init__(self, connection):
        """
        Initialize arrangement builder.
        
        Args:
            connection: AbletonConnection or LiveConnectionAdapter instance
        """
        # Extract AbletonConnection if wrapped
        if isinstance(connection, AbletonConnection):
            self._connection = connection
        elif hasattr(connection, '_conn'):
            self._connection = connection._conn
        else:
            # Create mock connection
            self._connection = AbletonConnection(mock=True)
        
        # Use unified ArrangementService
        self.service = ArrangementService(self._connection)
        
        # Keep legacy interface
        self.conn = LiveConnectionAdapter(self._connection)
        self.role_tracks: Dict[str, int] = {}  # Cache track IDs by role name
        self.track_counter = 0  # Track creation counter
    
    def ensure_role_tracks(self) -> bool:
        """
        Ensure all role tracks exist.
        Creates tracks if they don't exist, or finds existing ones.
        
        Returns:
            True if all tracks are ready
        """
        if not self.conn.is_connected():
            logger.error("Not connected to Ableton Live")
            return False
        
        # For now, we'll create tracks sequentially
        # In a real implementation, we'd query existing tracks first
        for role in config.ROLES:
            role_name = role["name"]
            
            # Check if we already have this track cached
            if role_name in self.role_tracks:
                continue
            
            # Create new MIDI track
            if self.conn.create_midi_track(-1):  # -1 = append to end
                track_id = self.track_counter
                self.role_tracks[role_name] = track_id
                
                # Set track name
                self.conn.set_track_name(track_id, role_name)
                
                # Set track color (convert REAPER format if needed)
                color = role.get("color", 0x808080)
                self.conn.set_track_color(track_id, color)
                
                self.track_counter += 1
                logger.info(f"Created track '{role_name}' at index {track_id}")
            else:
                logger.error(f"Failed to create track '{role_name}'")
                return False
        
        return True
    
    def build_arrangement(self, sections: List) -> bool:
        """
        Build the complete arrangement from sections.
        
        Args:
            sections: List of SectionAdapter or Section objects
            
        Returns:
            True if successful
        """
        if not sections:
            logger.warning("No sections to build")
            return False
        
        # Extract Pydantic sections from adapters
        pydantic_sections = []
        for s in sections:
            if isinstance(s, SectionAdapter):
                pydantic_sections.append(s._section)
            else:
                # Try to convert legacy section
                try:
                    from arranger.utils.adapters import legacy_section_to_pydantic
                    pydantic_sections.append(legacy_section_to_pydantic(s))
                except:
                    logger.warning(f"Could not convert section: {s}")
                    continue
        
        # Use unified service
        return self.service.build_from_sections(
            pydantic_sections,
            title="Arrangement",
            bpm=120.0,
            key="C"
        )
    
    def build_arrangement_legacy(self, sections: List) -> bool:
        """
        Legacy build method (kept for compatibility).
        
        Args:
            sections: List of Section objects
            
        Returns:
            True if successful
        """
        if not sections:
            logger.warning("No sections to build")
            return False
        
        if not self.ensure_role_tracks():
            return False
        
        # Calculate cumulative time positions
        current_time = 0.0
        default_tempo = 120.0  # Default if no tempo specified
        
        for section_idx, section in enumerate(sections):
            logger.info(f"Building section {section_idx + 1}: {section.name}")
            
            # Set tempo if specified
            if section.tempo and section.tempo > 0:
                self.conn.set_tempo(section.tempo)
                default_tempo = section.tempo
            
            # Set time signature if different from default
            if section.timesig_num != 4 or section.timesig_denom != 4:
                self.conn.set_time_signature(section.timesig_num, section.timesig_denom)
            
            # Calculate section length
            section_length = section.length_seconds(default_tempo)
            
            # Create clips for each role track
            for role in config.ROLES:
                role_name = role["name"]
                track_id = self.role_tracks.get(role_name)
                
                if track_id is None:
                    logger.warning(f"Track '{role_name}' not found, skipping")
                    continue
                
                # Create clip in session view (clip slot index = section index)
                # Note: Arrangement view clips may require different approach
                clip_index = section_idx
                bars = section.bars
                beats_per_bar = section.timesig_num * (4.0 / section.timesig_denom)
                clip_length = bars * beats_per_bar
                
                # Create or reuse clip
                self.conn.create_clip(track_id, clip_index, clip_length)
                
                # Set clip name
                self.conn.set_clip_name(track_id, clip_index, section.name)
                
                # Set clip color based on section
                section_color = section.get_color()
                self.conn.set_clip_color(track_id, clip_index, section_color)
                
                # If this is the Chords track, add chord notes
                if role_name == "Chords" and section.chords:
                    # Handle both adapter and legacy chord formats
                    self._apply_chords_to_clip(track_id, clip_index, section)
            
            current_time += section_length
        
        logger.info(f"Arrangement built: {len(sections)} sections")
        return True
    
    def _apply_chords_to_clip(self, track_id: int, clip_id: int, section: Section):
        """
        Apply chord progression to a clip as MIDI notes.
        
        Args:
            track_id: Track index
            clip_id: Clip index
            section: Section with chords
        """
        if not section.chords:
            return
        
        notes = []
        bars = section.bars
        beats_per_bar = section.timesig_num * (4.0 / section.timesig_denom)
        total_beats = bars * beats_per_bar
        
        for chord_data in section.chords:
            # Handle ChordAdapter, legacy Chord, or dict
            if isinstance(chord_data, ChordAdapter):
                # Use adapter's underlying chord for MIDI generation
                chord = chord_data._chord
                # Need to convert to legacy format for midi_notes_from_chord
                # Create a minimal legacy chord object
                class LegacyChord:
                    def __init__(self, root, type_idx, start_beat, duration_beats, inversion, bass_note, octave):
                        self.root = root
                        self.type_idx = type_idx
                        self.start_beat = start_beat
                        self.duration_beats = duration_beats
                        self.inversion = inversion
                        self.bass_note = bass_note
                        self.octave = octave
                
                legacy_chord = LegacyChord(
                    root=chord_data.root,
                    type_idx=chord_data.type_idx,
                    start_beat=chord_data.start_beat,
                    duration_beats=chord_data.duration_beats,
                    inversion=chord_data.inversion,
                    bass_note=chord_data.bass_note,
                    octave=chord_data.octave
                )
                chord = legacy_chord
            elif isinstance(chord_data, dict):
                # Try legacy format first
                try:
                    from ableton_arranger.core.chord import Chord as LegacyChord
                    chord = LegacyChord.from_dict(chord_data)
                except:
                    continue
            else:
                # Assume it's already a legacy Chord
                chord = chord_data
                if not hasattr(chord, 'root'):
                    continue
            
            # Validate timing
            if chord.start_beat < 0 or chord.start_beat >= total_beats:
                logger.warning(f"Chord at beat {chord.start_beat} is out of range")
                continue
            
            # Get MIDI notes for this chord
            midi_notes = midi_notes_from_chord(chord)
            
            if not midi_notes:
                logger.warning(f"No MIDI notes generated for chord")
                continue
            
            # Add notes to clip
            # Each note: (pitch, start_time, duration, velocity, mute)
            for pitch in midi_notes:
                start_time = chord.start_beat
                duration = min(chord.duration_beats, total_beats - start_time)
                velocity = 100  # Default velocity
                mute = False
                
                notes.append((pitch, start_time, duration, velocity, mute))
        
        if notes:
            self.conn.add_notes_to_clip(track_id, clip_id, notes)
            logger.info(f"Added {len(notes)} notes to clip")
