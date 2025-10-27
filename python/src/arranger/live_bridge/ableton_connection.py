"""
AbletonOSC connection wrapper for Live bridge integration.

Provides a simplified interface to AbletonOSC for scene/clip management and transport control.
"""
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import sys

logger = logging.getLogger(__name__)

# Add AbletonOSC client to path
ABLETON_OSC_PATH = Path(__file__).parent.parent.parent.parent.parent / "AbletonOSC-master"
if ABLETON_OSC_PATH.exists():
    sys.path.insert(0, str(ABLETON_OSC_PATH))
    
try:
    from client.client import AbletonOSCClient, TICK_DURATION
    ABLETONOSC_AVAILABLE = True
except ImportError:
    logger.warning("AbletonOSC client not available. Live integration will use mock mode.")
    ABLETONOSC_AVAILABLE = False
    TICK_DURATION = 0.15


class AbletonConnection:
    """Wrapper for AbletonOSC client with arranger-specific methods."""
    
    def __init__(self, hostname="127.0.0.1", port=11000, client_port=11001, mock=False):
        """
        Initialize Ableton Live connection.
        
        Args:
            hostname: Ableton OSC server address
            port: Ableton OSC server port (default 11000)
            client_port: Local client port for replies (default 11001)
            mock: Use mock mode (no actual connection)
        """
        self.mock = mock or not ABLETONOSC_AVAILABLE
        self.connected = False
        
        if not self.mock:
            try:
                self.client = AbletonOSCClient(hostname, port, client_port)
                # Test connection
                result = self.client.query("/live/test", timeout=1.0)
                if result and result[0] == "ok":
                    self.connected = True
                    logger.info(f"Connected to Ableton Live via OSC at {hostname}:{port}")
                else:
                    logger.warning("AbletonOSC test failed, using mock mode")
                    self.mock = True
            except Exception as e:
                logger.warning(f"Could not connect to Ableton Live: {e}. Using mock mode.")
                self.mock = True
        else:
            logger.info("Using mock mode for Ableton connection")
    
    def is_connected(self) -> bool:
        """Check if connected to Live."""
        return self.connected and not self.mock
    
    # Song/Transport methods
    
    def get_tempo(self) -> float:
        """Get current song tempo."""
        if self.mock:
            return 120.0
        try:
            result = self.client.query("/live/song/get/tempo")
            return float(result[0])
        except Exception as e:
            logger.error(f"Failed to get tempo: {e}")
            return 120.0
    
    def set_tempo(self, tempo: float):
        """Set song tempo."""
        if self.mock:
            logger.debug(f"Mock: set tempo to {tempo}")
            return
        try:
            self.client.send_message("/live/song/set/tempo", [tempo])
        except Exception as e:
            logger.error(f"Failed to set tempo: {e}")
    
    def get_time_signature(self) -> Tuple[int, int]:
        """Get current time signature."""
        if self.mock:
            return (4, 4)
        try:
            num = self.client.query("/live/song/get/signature_numerator")[0]
            denom = self.client.query("/live/song/get/signature_denominator")[0]
            return (int(num), int(denom))
        except Exception as e:
            logger.error(f"Failed to get time signature: {e}")
            return (4, 4)
    
    def play(self):
        """Start playback."""
        if self.mock:
            logger.debug("Mock: play")
            return
        try:
            self.client.send_message("/live/song/start_playing", [])
        except Exception as e:
            logger.error(f"Failed to start playback: {e}")
    
    def stop(self):
        """Stop playback."""
        if self.mock:
            logger.debug("Mock: stop")
            return
        try:
            self.client.send_message("/live/song/stop_playing", [])
        except Exception as e:
            logger.error(f"Failed to stop playback: {e}")
    
    # Scene methods
    
    def get_num_scenes(self) -> int:
        """Get number of scenes in Live set."""
        if self.mock:
            return 0
        try:
            result = self.client.query("/live/song/get/num_scenes")
            return int(result[0])
        except Exception as e:
            logger.error(f"Failed to get num scenes: {e}")
            return 0
    
    def get_scene_names(self) -> List[str]:
        """Get names of all scenes."""
        if self.mock:
            return []
        try:
            num_scenes = self.get_num_scenes()
            names = []
            for i in range(num_scenes):
                result = self.client.query("/live/scene/get/name", [i])
                names.append(result[0])
            return names
        except Exception as e:
            logger.error(f"Failed to get scene names: {e}")
            return []
    
    def create_scene(self, index: int = -1) -> int:
        """
        Create a new scene at the specified index.
        
        Args:
            index: Scene index (-1 for end)
        
        Returns:
            Index of created scene
        """
        if self.mock:
            logger.debug(f"Mock: create scene at index {index}")
            return 0
        try:
            num_scenes = self.get_num_scenes()
            if index == -1:
                index = num_scenes
            self.client.send_message("/live/song/create_scene", [index])
            return index
        except Exception as e:
            logger.error(f"Failed to create scene: {e}")
            return -1
    
    def set_scene_name(self, scene_index: int, name: str):
        """Set the name of a scene."""
        if self.mock:
            logger.debug(f"Mock: set scene {scene_index} name to '{name}'")
            return
        try:
            self.client.send_message("/live/scene/set/name", [scene_index, name])
        except Exception as e:
            logger.error(f"Failed to set scene name: {e}")
    
    def trigger_scene(self, scene_index: int):
        """Trigger (fire) a scene."""
        if self.mock:
            logger.debug(f"Mock: trigger scene {scene_index}")
            return
        try:
            self.client.send_message("/live/scene/fire", [scene_index])
        except Exception as e:
            logger.error(f"Failed to trigger scene: {e}")
    
    # Track methods
    
    def get_num_tracks(self) -> int:
        """Get number of tracks in Live set."""
        if self.mock:
            return 0
        try:
            result = self.client.query("/live/song/get/num_tracks")
            return int(result[0])
        except Exception as e:
            logger.error(f"Failed to get num tracks: {e}")
            return 0
    
    def get_track_name(self, track_index: int) -> str:
        """Get name of a track."""
        if self.mock:
            return f"Track {track_index}"
        try:
            result = self.client.query("/live/track/get/name", [track_index])
            return result[0]
        except Exception as e:
            logger.error(f"Failed to get track name: {e}")
            return f"Track {track_index}"
    
    # Clip methods
    
    def create_midi_clip(self, track_index: int, scene_index: int, length: float = 4.0):
        """
        Create a MIDI clip in a track/scene slot.
        
        Args:
            track_index: Track index
            scene_index: Scene index (clip slot)
            length: Clip length in bars
        """
        if self.mock:
            logger.debug(f"Mock: create MIDI clip at track {track_index}, scene {scene_index}, length {length}")
            return
        try:
            # Create clip slot
            self.client.send_message("/live/clip_slot/create_clip", [track_index, scene_index, length])
        except Exception as e:
            logger.error(f"Failed to create MIDI clip: {e}")
    
    def add_midi_notes(self, track_index: int, scene_index: int, notes: List[Tuple[int, float, float, int]]):
        """
        Add MIDI notes to a clip.
        
        Args:
            track_index: Track index
            scene_index: Scene/clip index
            notes: List of (pitch, start_time, duration, velocity) tuples
        """
        if self.mock:
            logger.debug(f"Mock: add {len(notes)} MIDI notes to track {track_index}, clip {scene_index}")
            return
        try:
            for pitch, start_time, duration, velocity in notes:
                self.client.send_message("/live/clip/add/notes", 
                                        [track_index, scene_index, pitch, start_time, duration, velocity])
        except Exception as e:
            logger.error(f"Failed to add MIDI notes: {e}")
    
    def set_clip_name(self, track_index: int, scene_index: int, name: str):
        """Set the name of a clip."""
        if self.mock:
            logger.debug(f"Mock: set clip name to '{name}'")
            return
        try:
            self.client.send_message("/live/clip/set/name", [track_index, scene_index, name])
        except Exception as e:
            logger.error(f"Failed to set clip name: {e}")
    
    def trigger_clip(self, track_index: int, scene_index: int):
        """Trigger (fire) a clip."""
        if self.mock:
            logger.debug(f"Mock: trigger clip at track {track_index}, scene {scene_index}")
            return
        try:
            self.client.send_message("/live/clip/fire", [track_index, scene_index])
        except Exception as e:
            logger.error(f"Failed to trigger clip: {e}")
    
    def close(self):
        """Close the connection."""
        if not self.mock and hasattr(self, 'client'):
            try:
                self.client.stop()
                self.connected = False
                logger.info("Closed Ableton OSC connection")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
