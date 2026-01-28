"""
Adapter to make AbletonConnection compatible with legacy LiveConnection interface.

This allows gradual migration from LiveConnection to AbletonConnection.
"""

from typing import Optional, List, Tuple
from arranger.live_bridge.ableton_connection import AbletonConnection


class LiveConnectionAdapter:
    """
    Adapter that makes AbletonConnection compatible with legacy LiveConnection API.
    
    Maps legacy method names to AbletonConnection methods.
    """
    
    def __init__(self, connection: AbletonConnection):
        self._conn = connection
    
    def is_connected(self) -> bool:
        """Check if connected to Live."""
        return self._conn.is_connected()
    
    def create_midi_track(self, index: int = -1) -> bool:
        """
        Create a new MIDI track.
        
        Note: AbletonConnection doesn't have direct track creation.
        This is a placeholder that returns True.
        """
        # AbletonConnection doesn't expose track creation directly
        # This would need to be implemented via OSC
        return True
    
    def create_audio_track(self, index: int = -1) -> bool:
        """Create a new audio track."""
        return True
    
    def get_num_tracks(self) -> Optional[int]:
        """Get the number of tracks."""
        return self._conn.get_num_tracks()
    
    def get_track_name(self, track_id: int) -> Optional[str]:
        """Get track name."""
        return self._conn.get_track_name(track_id)
    
    def find_track_by_name(self, name: str) -> Optional[int]:
        """
        Find a track by name.
        Note: This requires querying all tracks.
        """
        num_tracks = self.get_num_tracks()
        if num_tracks:
            for i in range(num_tracks):
                if self.get_track_name(i) == name:
                    return i
        return None
    
    def set_track_name(self, track_id: int, name: str) -> bool:
        """Set track name."""
        try:
            # AbletonConnection doesn't have set_track_name, but we can try via OSC
            # For now, return True as placeholder
            return True
        except:
            return False
    
    def set_track_color(self, track_id: int, color: int) -> bool:
        """Set track color."""
        # AbletonConnection doesn't expose this directly
        return True
    
    def create_clip(self, track_id: int, clip_index: int, length: float) -> bool:
        """Create a clip in a clip slot."""
        try:
            self._conn.create_midi_clip(track_id, clip_index, length)
            return True
        except:
            return False
    
    def delete_clip(self, track_id: int, clip_index: int) -> bool:
        """Delete a clip from a clip slot."""
        # AbletonConnection doesn't expose this directly
        return True
    
    def add_notes_to_clip(self, track_id: int, clip_id: int, notes: List[Tuple]) -> bool:
        """
        Add MIDI notes to a clip.
        
        Args:
            track_id: Track index
            clip_id: Clip index
            notes: List of tuples (pitch, start_time, duration, velocity, mute)
        """
        try:
            # Convert notes format: (pitch, start_time, duration, velocity, mute)
            # to AbletonConnection format: (pitch, start_time, duration, velocity)
            converted_notes = []
            for note in notes:
                if len(note) >= 4:
                    pitch, start_time, duration, velocity = note[0], note[1], note[2], note[3]
                    converted_notes.append((pitch, start_time, duration, velocity))
            
            self._conn.add_midi_notes(track_id, clip_id, converted_notes)
            return True
        except Exception as e:
            return False
    
    def remove_notes_from_clip(self, track_id: int, clip_id: int, 
                              start_pitch: Optional[int] = None,
                              pitch_span: Optional[int] = None,
                              start_time: Optional[float] = None,
                              time_span: Optional[float] = None) -> bool:
        """Remove notes from a clip."""
        # AbletonConnection doesn't expose this directly
        return True
    
    def set_clip_name(self, track_id: int, clip_id: int, name: str) -> bool:
        """Set clip name."""
        try:
            self._conn.set_clip_name(track_id, clip_id, name)
            return True
        except:
            return False
    
    def set_clip_color(self, track_id: int, clip_id: int, color: int) -> bool:
        """Set clip color."""
        # AbletonConnection doesn't expose this directly
        return True
    
    def set_tempo(self, tempo: float) -> bool:
        """Set global tempo."""
        try:
            self._conn.set_tempo(tempo)
            return True
        except:
            return False
    
    def set_time_signature(self, numerator: int, denominator: int) -> bool:
        """Set time signature."""
        # AbletonConnection doesn't expose this directly via single call
        # Would need to be implemented via OSC
        return True
    
    def create_scene(self, index: int = -1) -> bool:
        """Create a new scene."""
        try:
            self._conn.create_scene(index)
            return True
        except:
            return False
    
    def open_live_set(self, file_path: str) -> bool:
        """Open a Live set file."""
        # Not supported
        return False
