"""
Arrangement builder - creates tracks, clips, and applies sections to Ableton Live.
"""
from typing import List, Dict, Optional
import logging
from ableton_arranger.core.connection import LiveConnection
from ableton_arranger.core.section import Section
from ableton_arranger.core.chord import Chord, midi_notes_from_chord
import ableton_arranger.config as config


logger = logging.getLogger(__name__)


class ArrangementBuilder:
    """Builds arrangement in Ableton Live from sections."""
    
    def __init__(self, connection: LiveConnection):
        """
        Initialize arrangement builder.
        
        Args:
            connection: LiveConnection instance
        """
        self.conn = connection
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
    
    def build_arrangement(self, sections: List[Section]) -> bool:
        """
        Build the complete arrangement from sections.
        
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
            # Convert dict to Chord if needed
            if isinstance(chord_data, dict):
                chord = Chord.from_dict(chord_data)
            elif isinstance(chord_data, Chord):
                chord = chord_data
            else:
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
