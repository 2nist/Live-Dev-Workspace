"""
M4L Device Helper: Utilities for Max for Live device development

This module provides helper functions and classes specifically designed
for creating Max for Live devices with Python control.
"""

from typing import List, Dict, Optional, Any, Tuple
import random
from .live_connection import LiveConnection
from .utils import logger


class M4LDeviceHelper:
    """
    Helper class for Max for Live device development.
    
    Provides common patterns and utilities for M4L device creation.
    """
    
    def __init__(self, connection: Optional[LiveConnection] = None):
        """
        Initialize M4L device helper.
        
        Args:
            connection: Existing LiveConnection or None to create new
        """
        self.connection = connection or LiveConnection(scan_on_init=True)
    
    def get_track_clips(self, track_index: int) -> List:
        """
        Get all clips on a track.
        
        Args:
            track_index: Index of the track
            
        Returns:
            List of clip objects (None for empty slots)
        """
        track = self.connection.get_track(track_index)
        if track:
            return track.clips
        return []
    
    def get_clip_info(self, track_index: int, clip_index: int) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive information about a clip.
        
        Args:
            track_index: Index of the track
            clip_index: Index of the clip
            
        Returns:
            Dictionary with clip information or None if clip doesn't exist
        """
        clips = self.get_track_clips(track_index)
        if 0 <= clip_index < len(clips) and clips[clip_index] is not None:
            clip = clips[clip_index]
            return {
                "name": clip.name,
                "length": clip.length,
                "color": getattr(clip, "color", None),
                "is_playing": getattr(clip, "is_playing", False),
                "is_recording": getattr(clip, "is_recording", False),
            }
        return None
    
    def randomize_device_parameters(
        self,
        track_index: int,
        device_index: int = 0,
        exclude_params: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Randomize parameters of a device (useful for generative music).
        
        Args:
            track_index: Index of the track
            device_index: Index of the device on the track
            exclude_params: List of parameter names to exclude from randomization
            
        Returns:
            Dictionary of parameter names and new values
        """
        track = self.connection.get_track(track_index)
        if not track or not track.devices:
            logger.warning(f"No device found at track {track_index}, device {device_index}")
            return {}
        
        if device_index >= len(track.devices):
            logger.warning(f"Device index {device_index} out of range")
            return {}
        
        device = track.devices[device_index]
        exclude_params = exclude_params or []
        randomized = {}
        
        for param in device.parameters:
            if param.name not in exclude_params:
                try:
                    new_value = random.uniform(param.min, param.max)
                    param.value = new_value
                    randomized[param.name] = new_value
                except Exception as e:
                    logger.error(f"Error randomizing {param.name}: {e}")
        
        logger.info(f"Randomized {len(randomized)} parameters on {device.name}")
        return randomized
    
    def create_note_sequence(
        self,
        track_index: int,
        clip_index: int,
        pitches: List[int],
        duration: float = 1.0,
        velocity: int = 100,
        start_time: float = 0.0
    ):
        """
        Create a sequence of MIDI notes in a clip.
        
        Args:
            track_index: Index of the track
            clip_index: Index of the clip
            pitches: List of MIDI pitch values (0-127)
            duration: Duration of each note in beats
            velocity: MIDI velocity (0-127)
            start_time: Starting time in beats
        """
        # Remove existing notes
        self.connection.send_osc("/live/clip/remove/notes", track_index, clip_index)
        
        # Add new notes
        time = start_time
        for pitch in pitches:
            self.connection.send_osc(
                "/live/clip/add/notes",
                track_index,
                clip_index,
                pitch,
                time,
                duration,
                velocity,
                False  # mute
            )
            time += duration
        
        logger.info(f"Created {len(pitches)} note sequence in clip [{track_index}, {clip_index}]")
    
    def create_drum_pattern(
        self,
        track_index: int,
        clip_index: int,
        pattern: List[Tuple[int, List[int]]],
        step_duration: float = 0.25
    ):
        """
        Create a drum pattern using a simplified notation.
        
        Args:
            track_index: Index of the track
            clip_index: Index of the clip
            pattern: List of (pitch, steps) where steps are beat positions
            step_duration: Duration of each step in beats
            
        Example:
            pattern = [
                (36, [0, 4, 8, 12]),  # Kick on beats 1, 2, 3, 4
                (38, [4, 12]),         # Snare on beats 2, 4
                (42, [0, 2, 4, 6, 8, 10, 12, 14])  # Hi-hat on 8ths
            ]
        """
        # Remove existing notes
        self.connection.send_osc("/live/clip/remove/notes", track_index, clip_index)
        
        # Add drum hits
        for pitch, steps in pattern:
            for step in steps:
                time = step * step_duration
                self.connection.send_osc(
                    "/live/clip/add/notes",
                    track_index,
                    clip_index,
                    pitch,
                    time,
                    step_duration,
                    100,  # velocity
                    False  # mute
                )
        
        logger.info(f"Created drum pattern with {len(pattern)} voices")
    
    def get_device_parameters(
        self, 
        track_index: int, 
        device_index: int = 0
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get all parameters of a device with their current values and ranges.
        
        Args:
            track_index: Index of the track
            device_index: Index of the device
            
        Returns:
            Dictionary mapping parameter names to their info
        """
        track = self.connection.get_track(track_index)
        if not track or not track.devices:
            return {}
        
        if device_index >= len(track.devices):
            return {}
        
        device = track.devices[device_index]
        params = {}
        
        for param in device.parameters:
            params[param.name] = {
                "value": param.value,
                "min": param.min,
                "max": param.max,
                "default": getattr(param, "default", None)
            }
        
        return params
    
    def modulate_parameter(
        self,
        track_index: int,
        device_index: int,
        param_name: str,
        values: List[float],
        interval: float = 0.5
    ):
        """
        Modulate a parameter over time (for creating LFO-like effects).
        
        Args:
            track_index: Index of the track
            device_index: Index of the device
            param_name: Name of the parameter to modulate
            values: List of values to cycle through
            interval: Time between value changes in seconds
            
        Note: This is a synchronous example. For real-time use, 
        implement with threading or async.
        """
        import time
        
        track = self.connection.get_track(track_index)
        if not track or not track.devices:
            logger.warning("Track or device not found")
            return
        
        device = track.devices[device_index]
        param = None
        
        for p in device.parameters:
            if p.name == param_name:
                param = p
                break
        
        if not param:
            logger.warning(f"Parameter '{param_name}' not found")
            return
        
        logger.info(f"Modulating {param_name} with {len(values)} values")
        for value in values:
            param.value = value
            time.sleep(interval)
    
    def copy_clip_to_slots(
        self,
        source_track: int,
        source_clip: int,
        target_tracks: List[int]
    ):
        """
        Copy a clip to multiple track slots (useful for creating variations).
        
        Args:
            source_track: Source track index
            source_clip: Source clip index
            target_tracks: List of target track indices
        """
        for target_track in target_tracks:
            self.connection.send_osc(
                "/live/clip_slot/duplicate_clip_to",
                source_track,
                source_clip,
                target_track,
                source_clip
            )
            logger.info(f"Copied clip to track {target_track}")
    
    def setup_basic_scene(
        self,
        num_midi_tracks: int = 4,
        num_audio_tracks: int = 2
    ):
        """
        Set up a basic scene with MIDI and audio tracks.
        
        Args:
            num_midi_tracks: Number of MIDI tracks to create
            num_audio_tracks: Number of audio tracks to create
        """
        logger.info(f"Creating {num_midi_tracks} MIDI and {num_audio_tracks} audio tracks...")
        
        for _ in range(num_midi_tracks):
            self.connection.create_midi_track()
        
        for _ in range(num_audio_tracks):
            self.connection.create_audio_track()
        
        # Rescan to get new tracks
        self.connection.scan()
        logger.info("✓ Scene setup complete")
    
    def export_track_info(self, track_index: int) -> Dict[str, Any]:
        """
        Export comprehensive information about a track.
        
        Args:
            track_index: Index of the track
            
        Returns:
            Dictionary with track information
        """
        track = self.connection.get_track(track_index)
        if not track:
            return {}
        
        return {
            "name": track.name,
            "volume": track.volume if hasattr(track, "volume") else None,
            "pan": track.pan if hasattr(track, "pan") else None,
            "mute": track.mute if hasattr(track, "mute") else None,
            "solo": track.solo if hasattr(track, "solo") else None,
            "num_clips": len(track.clips) if track.clips else 0,
            "num_devices": len(track.devices) if track.devices else 0,
            "devices": [d.name for d in track.devices] if track.devices else [],
            "clips": [
                {"name": c.name, "length": c.length} if c else None 
                for c in (track.clips or [])
            ]
        }
