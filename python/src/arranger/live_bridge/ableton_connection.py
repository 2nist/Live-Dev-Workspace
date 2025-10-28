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
    
    def __init__(self, hostname="127.0.0.1", port=11000, client_port=11001, mock=False, auto_reconnect=True):
        """
        Initialize Ableton Live connection.
        
        Args:
            hostname: Ableton OSC server address
            port: Ableton OSC server port (default 11000)
            client_port: Local client port for replies (default 11001)
            mock: Use mock mode (no actual connection)
            auto_reconnect: Automatically reconnect on connection loss
        """
        self.hostname = hostname
        self.port = port
        self.client_port = client_port
        self.mock = mock or not ABLETONOSC_AVAILABLE
        self.auto_reconnect = auto_reconnect
        self.connected = False
        self.client = None
        
        # Mock state for testing
        self._mock_state = {
            "tempo": 120.0,
            "time_signature": (4, 4),
            "playing": False,
            "scenes": [],
            "tracks": []
        }
        
        if not self.mock:
            self._connect()
        else:
            logger.info("Using mock mode for Ableton connection")
    
    def _connect(self):
        """Internal method to establish connection."""
        try:
            self.client = AbletonOSCClient(self.hostname, self.port, self.client_port)
            # Test connection
            result = self.client.query("/live/test", timeout=2.0)
            if result and result[0] == "ok":
                self.connected = True
                logger.info(f"Connected to Ableton Live via OSC at {self.hostname}:{self.port}")
            else:
                logger.warning("AbletonOSC test failed")
                self.connected = False
                if not self.auto_reconnect:
                    self.mock = True
        except Exception as e:
            logger.warning(f"Could not connect to Ableton Live: {e}")
            self.connected = False
            if not self.auto_reconnect:
                self.mock = True
    
    def reconnect(self) -> bool:
        """Attempt to reconnect to Ableton Live."""
        if self.mock and not ABLETONOSC_AVAILABLE:
            logger.warning("Cannot reconnect: AbletonOSC not available")
            return False
        
        logger.info("Attempting to reconnect to Ableton Live...")
        self.mock = False
        self._connect()
        return self.connected
    
    def health_check(self) -> Dict[str, any]:
        """Check connection health and Live status."""
        health = {
            "connected": self.is_connected(),
            "mock_mode": self.mock,
            "hostname": self.hostname,
            "port": self.port
        }
        
        if self.is_connected():
            try:
                health["tempo"] = self.get_tempo()
                health["num_tracks"] = self.get_num_tracks()
                health["num_scenes"] = self.get_num_scenes()
                health["status"] = "healthy"
            except Exception as e:
                health["status"] = "degraded"
                health["error"] = str(e)
        else:
            health["status"] = "disconnected"
        
        return health
    
    def is_connected(self) -> bool:
        """Check if connected to Live."""
        return self.connected and not self.mock
    
    # Song/Transport methods
    
    def get_tempo(self) -> float:
        """Get current song tempo."""
        if self.mock:
            return self._mock_state["tempo"]
        try:
            result = self.client.query("/live/song/get/tempo")
            return float(result[0])
        except Exception as e:
            logger.error(f"Failed to get tempo: {e}")
            if self.auto_reconnect:
                self.reconnect()
            return 120.0
    
    def set_tempo(self, tempo: float):
        """Set song tempo."""
        if self.mock:
            self._mock_state["tempo"] = tempo
            logger.debug(f"Mock: set tempo to {tempo}")
            return
        try:
            self.client.send_message("/live/song/set/tempo", [tempo])
        except Exception as e:
            logger.error(f"Failed to set tempo: {e}")
            if self.auto_reconnect:
                self.reconnect()
    
    def get_time_signature(self) -> Tuple[int, int]:
        """Get current time signature."""
        if self.mock:
            return self._mock_state["time_signature"]
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
            self._mock_state["playing"] = True
            logger.debug("Mock: play")
            return
        try:
            self.client.send_message("/live/song/start_playing", [])
        except Exception as e:
            logger.error(f"Failed to start playback: {e}")
    
    def stop(self):
        """Stop playback."""
        if self.mock:
            self._mock_state["playing"] = False
            logger.debug("Mock: stop")
            return
        try:
            self.client.send_message("/live/song/stop_playing", [])
        except Exception as e:
            logger.error(f"Failed to stop playback: {e}")
    
    def is_playing(self) -> bool:
        """Check if transport is playing."""
        if self.mock:
            return self._mock_state["playing"]
        try:
            result = self.client.query("/live/song/get/is_playing")
            return bool(result[0])
        except Exception as e:
            logger.error(f"Failed to check playing status: {e}")
            return False
    
    # Scene methods
    
    def get_num_scenes(self) -> int:
        """Get number of scenes in Live set."""
        if self.mock:
            return len(self._mock_state["scenes"])
        try:
            result = self.client.query("/live/song/get/num_scenes")
            return int(result[0])
        except Exception as e:
            logger.error(f"Failed to get num scenes: {e}")
            return 0
    
    def get_scene_names(self) -> List[str]:
        """Get names of all scenes."""
        if self.mock:
            return [s["name"] for s in self._mock_state["scenes"]]
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
            if index == -1:
                index = len(self._mock_state["scenes"])
            self._mock_state["scenes"].insert(index, {"name": f"Scene {index}", "clips": []})
            logger.debug(f"Mock: create scene at index {index}")
            return index
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
            if 0 <= scene_index < len(self._mock_state["scenes"]):
                self._mock_state["scenes"][scene_index]["name"] = name
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
            return len(self._mock_state["tracks"])
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
    
    # Track parameter methods
    
    def set_track_volume(self, track_index: int, volume: float):
        """Set track volume (0.0 to 1.0)."""
        if self.mock:
            logger.debug(f"Mock: set track {track_index} volume to {volume}")
            return
        try:
            self.client.send_message("/live/track/set/volume", [track_index, volume])
        except Exception as e:
            logger.error(f"Failed to set track volume: {e}")
    
    def get_track_volume(self, track_index: int) -> float:
        """Get track volume (0.0 to 1.0)."""
        if self.mock:
            return 0.85
        try:
            result = self.client.query("/live/track/get/volume", [track_index])
            return float(result[0])
        except Exception as e:
            logger.error(f"Failed to get track volume: {e}")
            return 0.85
    
    def set_track_pan(self, track_index: int, pan: float):
        """Set track pan (-1.0 to 1.0)."""
        if self.mock:
            logger.debug(f"Mock: set track {track_index} pan to {pan}")
            return
        try:
            self.client.send_message("/live/track/set/panning", [track_index, pan])
        except Exception as e:
            logger.error(f"Failed to set track pan: {e}")
    
    def set_track_mute(self, track_index: int, mute: bool):
        """Mute or unmute a track."""
        if self.mock:
            logger.debug(f"Mock: {'mute' if mute else 'unmute'} track {track_index}")
            return
        try:
            self.client.send_message("/live/track/set/mute", [track_index, int(mute)])
        except Exception as e:
            logger.error(f"Failed to set track mute: {e}")
    
    def set_track_solo(self, track_index: int, solo: bool):
        """Solo or unsolo a track."""
        if self.mock:
            logger.debug(f"Mock: {'solo' if solo else 'unsolo'} track {track_index}")
            return
        try:
            self.client.send_message("/live/track/set/solo", [track_index, int(solo)])
        except Exception as e:
            logger.error(f"Failed to set track solo: {e}")
    
    def set_track_arm(self, track_index: int, arm: bool):
        """Arm or unarm a track for recording."""
        if self.mock:
            logger.debug(f"Mock: {'arm' if arm else 'unarm'} track {track_index}")
            return
        try:
            self.client.send_message("/live/track/set/arm", [track_index, int(arm)])
        except Exception as e:
            logger.error(f"Failed to set track arm: {e}")
    
    # Clip looping and manipulation
    
    def set_clip_loop(self, track_index: int, scene_index: int, loop: bool):
        """Enable or disable clip looping."""
        if self.mock:
            logger.debug(f"Mock: set clip loop to {loop}")
            return
        try:
            self.client.send_message("/live/clip/set/looping", [track_index, scene_index, int(loop)])
        except Exception as e:
            logger.error(f"Failed to set clip loop: {e}")
    
    def set_clip_loop_length(self, track_index: int, scene_index: int, length: float):
        """Set clip loop length in bars."""
        if self.mock:
            logger.debug(f"Mock: set clip loop length to {length}")
            return
        try:
            self.client.send_message("/live/clip/set/loop_end", [track_index, scene_index, length])
        except Exception as e:
            logger.error(f"Failed to set clip loop length: {e}")
    
    def get_clip_length(self, track_index: int, scene_index: int) -> float:
        """Get clip length in bars."""
        if self.mock:
            return 4.0
        try:
            result = self.client.query("/live/clip/get/length", [track_index, scene_index])
            return float(result[0])
        except Exception as e:
            logger.error(f"Failed to get clip length: {e}")
            return 4.0
    
    def duplicate_scene(self, scene_index: int) -> int:
        """Duplicate a scene."""
        if self.mock:
            logger.debug(f"Mock: duplicate scene {scene_index}")
            return scene_index + 1
        try:
            self.client.send_message("/live/scene/duplicate", [scene_index])
            return scene_index + 1
        except Exception as e:
            logger.error(f"Failed to duplicate scene: {e}")
            return -1
    
    def delete_scene(self, scene_index: int):
        """Delete a scene."""
        if self.mock:
            if 0 <= scene_index < len(self._mock_state["scenes"]):
                del self._mock_state["scenes"][scene_index]
            logger.debug(f"Mock: delete scene {scene_index}")
            return
        try:
            self.client.send_message("/live/scene/delete", [scene_index])
        except Exception as e:
            logger.error(f"Failed to delete scene: {e}")
    
    def close(self):
        """Close the connection."""
        if not self.mock and hasattr(self, 'client') and self.client:
            try:
                self.client.stop()
                self.connected = False
                logger.info("Closed Ableton OSC connection")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
