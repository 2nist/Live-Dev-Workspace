"""
OSC connection to Ableton Live via AbletonOSC.
Wraps python-osc client for sending commands to Live.
"""
from typing import Optional, List, Tuple
from pythonosc.udp_client import UDPClient
import logging


logger = logging.getLogger(__name__)


class LiveConnection:
    """Manages OSC connection to Ableton Live."""
    
    def __init__(self, host: str = 'localhost', port: int = 11000):
        """
        Initialize OSC client connection.
        
        Args:
            host: AbletonOSC server host (default: localhost)
            port: AbletonOSC server port (default: 11000)
        """
        self.host = host
        self.port = port
        self.client: Optional[UDPClient] = None
        self.connected = False
        
        try:
            self.client = UDPClient(host, port)
            self.connected = True
            logger.info(f"Connected to AbletonOSC at {host}:{port}")
        except Exception as e:
            logger.error(f"Failed to connect to AbletonOSC: {e}")
            self.connected = False
    
    def _send(self, address: str, *args):
        """Send OSC message to Live."""
        if not self.connected or not self.client:
            logger.warning(f"Cannot send OSC message: not connected")
            return False
        
        try:
            self.client.send_message(address, args)
            return True
        except Exception as e:
            logger.error(f"Error sending OSC message to {address}: {e}")
            return False
    
    def create_midi_track(self, index: int = -1) -> bool:
        """
        Create a new MIDI track.
        
        Args:
            index: Track index (-1 = end of list)
            
        Returns:
            True if successful
        """
        return self._send("/live/song/create_midi_track", index)
    
    def create_audio_track(self, index: int = -1) -> bool:
        """Create a new audio track."""
        return self._send("/live/song/create_audio_track", index)
    
    def get_num_tracks(self) -> Optional[int]:
        """
        Get the number of tracks in the set.
        Note: This requires a response handler, which is complex with python-osc.
        For now, we'll assume tracks are created successfully.
        """
        # TODO: Implement response handling if needed
        return None
    
    def get_track_name(self, track_id: int) -> Optional[str]:
        """Get track name. Requires response handling."""
        # TODO: Implement if needed
        return None
    
    def find_track_by_name(self, name: str) -> Optional[int]:
        """
        Find a track by name.
        Note: This requires querying all tracks, which needs response handling.
        For now, we'll track names in the ArrangementBuilder.
        """
        # TODO: Implement with response handling
        return None
    
    def set_track_name(self, track_id: int, name: str) -> bool:
        """Set track name."""
        return self._send("/live/track/set/name", track_id, name)
    
    def set_track_color(self, track_id: int, color: int) -> bool:
        """
        Set track color.
        
        Args:
            track_id: Track index
            color: Color value (format may need conversion from REAPER's 0xBBGGRR)
        """
        return self._send("/live/track/set/color", track_id, color)
    
    def create_clip(self, track_id: int, clip_index: int, length: float) -> bool:
        """
        Create a clip in a clip slot.
        
        Args:
            track_id: Track index
            clip_index: Clip slot index
            length: Clip length in beats
        """
        return self._send("/live/clip_slot/create_clip", track_id, clip_index, length)
    
    def delete_clip(self, track_id: int, clip_index: int) -> bool:
        """Delete a clip from a clip slot."""
        return self._send("/live/clip_slot/delete_clip", track_id, clip_index)
    
    def add_notes_to_clip(self, track_id: int, clip_id: int, notes: List[Tuple]) -> bool:
        """
        Add MIDI notes to a clip.
        
        Args:
            track_id: Track index
            clip_id: Clip index
            notes: List of tuples (pitch, start_time, duration, velocity, mute)
                   Each note is: (int, float, float, int, bool)
        """
        # OSC message format: /live/clip/add/notes track_id clip_id pitch start_time duration velocity mute ...
        # Flatten the notes list
        args = [track_id, clip_id]
        for note in notes:
            pitch, start_time, duration, velocity, mute = note
            args.extend([pitch, start_time, duration, velocity, 1 if mute else 0])
        
        return self._send("/live/clip/add/notes", *args)
    
    def remove_notes_from_clip(self, track_id: int, clip_id: int, 
                              start_pitch: Optional[int] = None,
                              pitch_span: Optional[int] = None,
                              start_time: Optional[float] = None,
                              time_span: Optional[float] = None) -> bool:
        """Remove notes from a clip."""
        args = []
        if start_pitch is not None:
            args.append(start_pitch)
        if pitch_span is not None:
            args.append(pitch_span)
        if start_time is not None:
            args.append(start_time)
        if time_span is not None:
            args.append(time_span)
        
        return self._send("/live/clip/remove/notes", *args)
    
    def set_clip_name(self, track_id: int, clip_id: int, name: str) -> bool:
        """Set clip name."""
        return self._send("/live/clip/set/name", track_id, clip_id, name)
    
    def set_clip_color(self, track_id: int, clip_id: int, color: int) -> bool:
        """Set clip color."""
        return self._send("/live/clip/set/color", track_id, clip_id, color)
    
    def set_tempo(self, tempo: float) -> bool:
        """Set global tempo."""
        return self._send("/live/song/set/tempo", tempo)
    
    def set_time_signature(self, numerator: int, denominator: int) -> bool:
        """Set time signature."""
        result1 = self._send("/live/song/set/signature_numerator", numerator)
        result2 = self._send("/live/song/set/signature_denominator", denominator)
        return result1 and result2
    
    def create_scene(self, index: int = -1) -> bool:
        """Create a new scene."""
        return self._send("/live/song/create_scene", index)
    
    def is_connected(self) -> bool:
        """Check if connected to Live."""
        return self.connected
    
    def open_live_set(self, file_path: str) -> bool:
        """
        Open a Live set file.
        Note: AbletonOSC doesn't have a direct "open set" command.
        This would need to be done via Live's file system or manual user action.
        For now, return True as placeholder.
        
        Args:
            file_path: Path to .als file
            
        Returns:
            True if successful (placeholder)
        """
        # TODO: Implement Live set opening via OSC or file system
        logger.info(f"Would open Live set: {file_path}")
        return True
