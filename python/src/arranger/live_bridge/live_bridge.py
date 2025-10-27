"""
Live bridge: scene management, clip creation, playback scheduling.
"""
from typing import List, Dict, Optional
import logging
from arranger.live_bridge.ableton_connection import AbletonConnection

logger = logging.getLogger(__name__)

class SceneManager:
    """Manage Ableton Live scenes."""
    
    def __init__(self, connection: Optional[AbletonConnection] = None):
        self.connection = connection or AbletonConnection(mock=True)
        self.scenes = []  # Local cache for mock mode
    
    def create_scene(self, name: str, clips: List[Dict]) -> int:
        """Create a new scene in Ableton Live."""
        logger.info(f"Creating scene '{name}' with {len(clips)} clips")
        
        if self.connection.is_connected():
            # Create scene in Live
            scene_index = self.connection.create_scene(-1)
            self.connection.set_scene_name(scene_index, name)
            return scene_index
        else:
            # Mock mode: cache locally
            self.scenes.append({"name": name, "clips": clips})
            return len(self.scenes) - 1
    
    def list_scenes(self) -> List[str]:
        """List all scenes in the current Live set."""
        if self.connection.is_connected():
            return self.connection.get_scene_names()
        else:
            # Mock mode: return cached scenes
            return [s["name"] for s in self.scenes]
    
    def trigger_scene(self, scene_index: int):
        """Trigger a scene to start playback."""
        logger.info(f"Triggering scene {scene_index}")
        if self.connection.is_connected():
            self.connection.trigger_scene(scene_index)
        else:
            logger.debug(f"Mock: trigger scene {scene_index}")


class ChordClipFactory:
    """Create MIDI clips for chords."""
    
    def __init__(self, connection: Optional[AbletonConnection] = None):
        self.connection = connection or AbletonConnection(mock=True)
    
    def create_chord_clip(self, chord: str, length: int, track: int) -> Dict:
        """Create a MIDI clip for a chord."""
        from arranger.models.chord import Chord
        
        logger.info(f"Creating chord clip for '{chord}' on track {track}, length {length}")
        
        # Parse chord and generate MIDI notes
        try:
            chord_obj = Chord.from_name(chord)
            midi_notes = chord_obj.to_midi_notes()
            logger.debug(f"Generated MIDI notes: {midi_notes}")
            
            if self.connection.is_connected():
                # Get current number of scenes to create clip in new scene
                num_scenes = self.connection.get_num_scenes()
                scene_index = num_scenes  # Create in new scene
                
                # Create MIDI clip
                self.connection.create_midi_clip(track, scene_index, length)
                
                # Add notes (full length, quarter note duration)
                notes = []
                for pitch in midi_notes:
                    # Note: (pitch, start_time, duration, velocity)
                    notes.append((pitch, 0.0, float(length), 100))
                
                self.connection.add_midi_notes(track, scene_index, notes)
                self.connection.set_clip_name(track, scene_index, f"{chord}")
                
                return {
                    "track": track,
                    "scene": scene_index,
                    "notes": midi_notes,
                    "length": length,
                    "connected": True
                }
            else:
                # Mock mode: just return the MIDI notes
                return {"track": track, "notes": midi_notes, "length": length, "connected": False}
                
        except Exception as e:
            logger.error(f"Failed to create chord clip: {e}")
            raise

class PlaybackScheduler:
    """Schedule playback of scenes and sections."""
    
    def __init__(self, connection: Optional[AbletonConnection] = None):
        self.connection = connection or AbletonConnection(mock=True)
        self.scheduled_order = []
        self.scene_mapping = {}  # Maps section labels to scene indices
    
    def schedule_playback(self, order: List[str]) -> Dict:
        """Schedule playback of scenes/sections in order."""
        logger.info(f"Scheduling playback order: {order}")
        self.scheduled_order = order
        
        # Map section labels to scene indices if connected
        if self.connection.is_connected():
            scene_names = self.connection.get_scene_names()
            for label in order:
                # Find matching scene by name
                try:
                    idx = scene_names.index(label)
                    self.scene_mapping[label] = idx
                except ValueError:
                    logger.warning(f"Scene '{label}' not found in Live set")
        
        return {"order": order, "status": "scheduled", "connected": self.connection.is_connected()}
    
    def get_current_order(self) -> List[str]:
        """Get the current playback order."""
        return self.scheduled_order
    
    def trigger_next(self) -> Optional[str]:
        """Trigger the next scene in the scheduled order."""
        if not self.scheduled_order:
            return None
        
        next_label = self.scheduled_order.pop(0)
        
        if self.connection.is_connected() and next_label in self.scene_mapping:
            scene_index = self.scene_mapping[next_label]
            self.connection.trigger_scene(scene_index)
            logger.info(f"Triggered scene '{next_label}' (index {scene_index})")
        else:
            logger.debug(f"Mock: trigger scene '{next_label}'")
        
        return next_label
