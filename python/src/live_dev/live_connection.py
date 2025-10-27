"""
LiveConnection: Unified interface for Ableton Live OSC communication

This module provides a simplified, unified API that wraps both pylive
and AbletonOSC functionality for easier Max for Live device development.
"""

import live
from pythonosc import udp_client, osc_server, dispatcher
import threading
import time
from typing import Optional, Callable, Any, Dict, List
from .utils import logger


class LiveConnection:
    """
    Unified connection manager for Ableton Live.
    
    Combines pylive's high-level API with AbletonOSC's OSC capabilities
    for comprehensive Live control.
    """
    
    def __init__(
        self,
        host: str = "127.0.0.1",
        osc_send_port: int = 11000,
        osc_receive_port: int = 11001,
        scan_on_init: bool = False
    ):
        """
        Initialize connection to Ableton Live.
        
        Args:
            host: IP address of Live instance (default: localhost)
            osc_send_port: Port to send OSC messages to AbletonOSC (default: 11000)
            osc_receive_port: Port to receive OSC replies (default: 11001)
            scan_on_init: Whether to scan the Live Set on initialization
        """
        self.host = host
        self.osc_send_port = osc_send_port
        self.osc_receive_port = osc_receive_port
        
        # Initialize pylive Set
        logger.info(f"Connecting to Ableton Live at {host}...")
        self.set = live.Set(host=host, port=osc_send_port)
        
        if scan_on_init:
            logger.info("Scanning Live Set...")
            self.set.scan()
        
        # Initialize OSC client for direct AbletonOSC communication
        self.osc_client = udp_client.SimpleUDPClient(host, osc_send_port)
        
        # Setup OSC server for receiving messages
        self._dispatcher = dispatcher.Dispatcher()
        self._osc_server = None
        self._server_thread = None
        self._callbacks: Dict[str, List[Callable]] = {}
        
        logger.info("✓ Connection established")
    
    def start_listening(self, address: str, callback: Callable):
        """
        Start listening for OSC messages on a specific address.
        
        Args:
            address: OSC address pattern to listen for
            callback: Function to call when message is received
        """
        if address not in self._callbacks:
            self._callbacks[address] = []
        self._callbacks[address].append(callback)
        
        # Map the address to the dispatcher
        self._dispatcher.map(address, self._handle_osc_message)
        
        # Start server if not already running
        if self._osc_server is None:
            self._start_osc_server()
        
        logger.info(f"Started listening on {address}")
    
    def stop_listening(self, address: Optional[str] = None):
        """
        Stop listening for OSC messages.
        
        Args:
            address: Specific address to stop listening to, or None to stop all
        """
        if address:
            if address in self._callbacks:
                del self._callbacks[address]
                self._dispatcher.unmap(address, self._handle_osc_message)
                logger.info(f"Stopped listening on {address}")
        else:
            self._callbacks.clear()
            if self._osc_server:
                self._osc_server.shutdown()
                self._osc_server = None
            logger.info("Stopped all listening")
    
    def _start_osc_server(self):
        """Start the OSC server in a background thread."""
        from pythonosc import osc_server as server
        
        self._osc_server = server.ThreadingOSCUDPServer(
            (self.host, self.osc_receive_port),
            self._dispatcher
        )
        self._server_thread = threading.Thread(
            target=self._osc_server.serve_forever,
            daemon=True
        )
        self._server_thread.start()
        logger.info(f"OSC server listening on port {self.osc_receive_port}")
    
    def _handle_osc_message(self, address: str, *args):
        """Internal handler for incoming OSC messages."""
        if address in self._callbacks:
            for callback in self._callbacks[address]:
                try:
                    callback(*args)
                except Exception as e:
                    logger.error(f"Error in callback for {address}: {e}")
    
    def send_osc(self, address: str, *args):
        """
        Send a raw OSC message to AbletonOSC.
        
        Args:
            address: OSC address path
            *args: Values to send
        """
        self.osc_client.send_message(address, args)
    
    def test_connection(self) -> bool:
        """
        Test the connection to Ableton Live.
        
        Returns:
            True if connection is successful
        """
        try:
            self.send_osc("/live/test")
            time.sleep(0.1)
            logger.info("✓ Connection test successful")
            return True
        except Exception as e:
            logger.error(f"✗ Connection test failed: {e}")
            return False
    
    # Convenience methods for common operations
    
    def get_tempo(self) -> float:
        """Get current song tempo."""
        return self.set.tempo
    
    def set_tempo(self, tempo: float):
        """Set song tempo."""
        self.set.tempo = tempo
    
    def get_tracks(self) -> List:
        """Get list of all tracks."""
        if not self.set.tracks:
            self.set.scan()
        return self.set.tracks
    
    def get_track(self, index: int):
        """Get a specific track by index."""
        tracks = self.get_tracks()
        if 0 <= index < len(tracks):
            return tracks[index]
        return None
    
    def play(self):
        """Start playback."""
        self.send_osc("/live/song/start_playing")
    
    def stop(self):
        """Stop playback."""
        self.send_osc("/live/song/stop_playing")
    
    def stop_all_clips(self):
        """Stop all playing clips."""
        self.send_osc("/live/song/stop_all_clips")
    
    def get_track_names(self) -> List[str]:
        """Get names of all tracks."""
        return [track.name for track in self.get_tracks()]
    
    def fire_clip(self, track_index: int, clip_index: int):
        """
        Fire a clip at the specified track and clip index.
        
        Args:
            track_index: Index of the track
            clip_index: Index of the clip slot
        """
        self.send_osc("/live/clip/fire", track_index, clip_index)
    
    def stop_clip(self, track_index: int, clip_index: int):
        """
        Stop a clip at the specified track and clip index.
        
        Args:
            track_index: Index of the track
            clip_index: Index of the clip slot
        """
        self.send_osc("/live/clip/stop", track_index, clip_index)
    
    def create_midi_track(self, index: int = -1):
        """
        Create a new MIDI track.
        
        Args:
            index: Position to insert track (-1 for end)
        """
        self.send_osc("/live/song/create_midi_track", index)
    
    def create_audio_track(self, index: int = -1):
        """
        Create a new audio track.
        
        Args:
            index: Position to insert track (-1 for end)
        """
        self.send_osc("/live/song/create_audio_track", index)
    
    def scan(self):
        """Rescan the Live Set to refresh track/clip information."""
        self.set.scan()
        logger.info("Live Set scanned")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup."""
        self.stop_listening()
    
    def __repr__(self):
        """String representation."""
        num_tracks = len(self.set.tracks) if self.set.tracks else "unknown"
        return f"<LiveConnection: {num_tracks} tracks, tempo={self.set.tempo}>"
