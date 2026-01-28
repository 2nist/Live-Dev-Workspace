"""
Ableton Live Integration for ChoCo Chord Progressions

Sends chord progressions from JAMS/JSON to Ableton Live via OSC.
"""

import logging
from typing import Dict, List, Optional, Any

try:
    from live_dev import LiveConnection
except ImportError:
    LiveConnection = None
    logging.warning("live_dev not available. Install from Live_Dev repository.")

from .chord_converter import harte_to_midi_notes, chord_progression_to_midi

logger = logging.getLogger(__name__)


def send_chord_progression_to_live(
    json_data: Dict[str, Any],
    track_index: int = 0,
    clip_index: int = 0,
    live_connection: Optional[Any] = None,
    tempo: Optional[float] = None,
    voicing: str = "close",
    root_octave: int = 4,
    clear_existing: bool = True,
) -> Any:
    """
    Send chord progression from JSON to Ableton Live.
    
    Args:
        json_data: JSON data from jams_to_json()
        track_index: Target track in Live
        clip_index: Target clip slot
        live_connection: Existing LiveConnection instance (creates new if None)
        tempo: Override tempo (uses JSON tempo if available)
        voicing: Chord voicing style ("close", "open", "spread")
        root_octave: Root octave for chords
        clear_existing: Clear existing notes in clip
    
    Returns:
        LiveConnection instance
    """
    if LiveConnection is None:
        raise ImportError(
            "live_dev module required. Install from Live_Dev repository."
        )
    
    # Create or use existing connection
    if live_connection is None:
        live = LiveConnection(scan_on_init=True)
    else:
        live = live_connection
    
    # Get tempo
    if tempo is None:
        tempo = json_data.get('metadata', {}).get('tempo', 120.0)
    
    # Set tempo in Live
    try:
        live.set_tempo(tempo)
    except Exception as e:
        logger.warning(f"Could not set tempo: {e}")
    
    # Get chord data
    chords = json_data.get('chords', [])
    if not chords:
        logger.warning("No chords found in JSON data")
        return live
    
    # Calculate clip length (in beats)
    duration = json_data.get('metadata', {}).get('duration', 0.0)
    beats_per_sec = tempo / 60.0
    
    if duration > 0:
        # Duration is in seconds, convert to beats
        clip_length = duration * beats_per_sec
    else:
        # Estimate from last chord
        last_chord = chords[-1]
        clip_length = (last_chord['time'] + last_chord['duration']) * beats_per_sec
    
    # Ensure minimum clip length
    clip_length = max(clip_length, 4.0)  # At least 4 beats
    
    # Create or clear clip
    try:
        if clear_existing:
            # Delete existing clip if it exists
            try:
                live.send_message('/live/clip_slot/delete_clip', track_index, clip_index)
            except:
                pass  # Clip might not exist
        
        # Create new clip
        live.send_message(
            '/live/clip_slot/create_clip',
            track_index,
            clip_index,
            clip_length
        )
    except Exception as e:
        logger.warning(f"Could not create clip: {e}")
        return live
    
    # Add chords as MIDI notes
    note_count = 0
    for chord_data in chords:
        chord_str = chord_data.get('chord', '')
        if not chord_str or chord_str == 'N':
            continue
        
        time_sec = chord_data.get('time', 0.0)
        duration_sec = chord_data.get('duration', 2.0)
        
        # Convert to beats
        start_beat = time_sec * beats_per_sec
        duration_beat = duration_sec * beats_per_sec
        
        # Convert chord to MIDI notes
        midi_notes = harte_to_midi_notes(
            chord_str,
            root_octave=root_octave,
            voicing=voicing
        )
        
        if not midi_notes:
            continue
        
        # Add notes to clip
        for note in midi_notes:
            try:
                live.send_message(
                    '/live/clip/add/notes',
                    track_index,
                    clip_index,
                    note,           # pitch
                    start_beat,     # start_time (beats)
                    duration_beat,  # duration (beats)
                    100,            # velocity
                    0               # mute (0 = not muted)
                )
                note_count += 1
            except Exception as e:
                logger.warning(f"Error adding note {note}: {e}")
    
    logger.info(
        f"✓ Added {note_count} notes to track {track_index}, clip {clip_index}"
    )
    
    return live


class ChocoLiveBridge:
    """
    High-level bridge between ChoCo datasets and Ableton Live.
    
    Provides convenient methods for loading, searching, and sending
    chord progressions to Live.
    """
    
    def __init__(self, json_directory: str = None, live_connection: Any = None):
        """
        Initialize bridge.
        
        Args:
            json_directory: Directory containing JSON files
            live_connection: Existing LiveConnection instance
        """
        self.json_directory = json_directory
        self.live = live_connection
        self.current_song = None
    
    def connect(self):
        """Connect to Ableton Live."""
        if LiveConnection is None:
            raise ImportError("live_dev module required")
        
        if self.live is None:
            self.live = LiveConnection(scan_on_init=True)
        
        return self.live
    
    def load_song(self, json_path: str) -> Dict[str, Any]:
        """
        Load a song from JSON file.
        
        Args:
            json_path: Path to JSON file
        
        Returns:
            Song data dictionary
        """
        import json
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.current_song = data
        return data
    
    def search_songs(
        self,
        search_term: str = "",
        genre: Optional[str] = None,
        dataset: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search for songs in JSON directory.
        
        Args:
            search_term: Search in title/artist
            genre: Filter by genre
            dataset: Filter by dataset
            limit: Maximum results
        
        Returns:
            List of matching songs
        """
        from .jams_converter import search_json_files
        
        if not self.json_directory:
            raise ValueError("json_directory not set")
        
        results = search_json_files(
            self.json_directory,
            search_term=search_term,
            genre=genre,
            dataset=dataset,
        )
        
        return results[:limit]
    
    def send_to_live(
        self,
        song_data: Optional[Dict[str, Any]] = None,
        track_index: int = 0,
        clip_index: int = 0,
        **kwargs
    ) -> Any:
        """
        Send song to Ableton Live.
        
        Args:
            song_data: Song data (uses current_song if None)
            track_index: Target track
            clip_index: Target clip
            **kwargs: Additional arguments for send_chord_progression_to_live
        
        Returns:
            LiveConnection instance
        """
        if self.live is None:
            self.connect()
        
        if song_data is None:
            if self.current_song is None:
                raise ValueError("No song data provided")
            song_data = self.current_song
        
        return send_chord_progression_to_live(
            song_data,
            track_index=track_index,
            clip_index=clip_index,
            live_connection=self.live,
            **kwargs
        )
    
    def play_chord(
        self,
        chord_str: str,
        duration: float = 2.0,
        track_index: int = 0,
        clip_index: int = 0,
        root_octave: int = 4,
        voicing: str = "close",
    ):
        """
        Play a single chord in Live.
        
        Args:
            chord_str: Harte chord notation
            duration: Duration in beats
            track_index: Target track
            clip_index: Target clip
            root_octave: Root octave
            voicing: Voicing style
        """
        if self.live is None:
            self.connect()
        
        # Create temporary clip
        try:
            self.live.send_message(
                '/live/clip_slot/create_clip',
                track_index,
                clip_index,
                duration
            )
        except:
            pass
        
        # Get MIDI notes
        midi_notes = harte_to_midi_notes(
            chord_str,
            root_octave=root_octave,
            voicing=voicing
        )
        
        # Add notes
        for note in midi_notes:
            self.live.send_message(
                '/live/clip/add/notes',
                track_index,
                clip_index,
                note,
                0.0,      # start at beginning
                duration, # duration
                100,      # velocity
                0         # not muted
            )
        
        # Fire clip
        self.live.send_message('/live/clip/fire', track_index, clip_index)
    
    def create_chord_track(
        self,
        chords: List[str],
        track_name: str = "Chords",
        clip_length: float = 32.0,
        tempo: float = 120.0,
    ) -> int:
        """
        Create a new track with chord progression.
        
        Args:
            chords: List of Harte chord strings
            track_name: Name for the track
            clip_length: Length of clip in beats
            tempo: Tempo in BPM
        
        Returns:
            Track index
        """
        if self.live is None:
            self.connect()
        
        # Create MIDI track
        try:
            num_tracks = self.live.get_num_tracks()
            self.live.send_message('/live/song/create_midi_track', num_tracks)
            track_index = num_tracks
        except Exception as e:
            logger.warning(f"Could not create track: {e}")
            track_index = 0
        
        # Set track name
        try:
            self.live.send_message(
                '/live/track/set/name',
                track_index,
                track_name
            )
        except:
            pass
        
        # Set tempo
        try:
            self.live.set_tempo(tempo)
        except:
            pass
        
        # Create clip and add chords
        clip_index = 0
        beats_per_chord = clip_length / len(chords) if chords else 2.0
        
        try:
            self.live.send_message(
                '/live/clip_slot/create_clip',
                track_index,
                clip_index,
                clip_length
            )
        except:
            pass
        
        # Add chords
        for i, chord_str in enumerate(chords):
            if not chord_str or chord_str == 'N':
                continue
            
            start_beat = i * beats_per_chord
            midi_notes = harte_to_midi_notes(chord_str)
            
            for note in midi_notes:
                try:
                    self.live.send_message(
                        '/live/clip/add/notes',
                        track_index,
                        clip_index,
                        note,
                        start_beat,
                        beats_per_chord,
                        100,
                        0
                    )
                except:
                    pass
        
        return track_index

