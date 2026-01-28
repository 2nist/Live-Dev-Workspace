# MIR Datasets to Ableton Live Integration Guide

## Executive Summary

This guide provides a comprehensive path to efficiently utilize ChoCo MIR datasets in Ableton Live through JAMS/JSON conversion and OSC controls. The integration bridges the gap between music information retrieval research data and live music production.

## Repository Analysis

### ChoCo Repository (`choco-main`)
- **Purpose**: Large-scale chord corpus with 20K+ timed chord annotations
- **Formats**: JAMS files (JSON Annotated Music Specification)
- **Content**: 
  - Chord progressions in Harte notation (e.g., "C:maj7", "F:min/5")
  - Temporal annotations (time, duration, confidence)
  - Metadata (title, artist, genre, composers, performers)
  - Multiple partitions: Billboard, Jazz Corpus, Real Book, iReal Pro, etc.
- **Key Files**:
  - `choco/jams_utils.py`: JAMS file manipulation utilities
  - `choco/jams_score.py`: Score-based JAMS handling
  - `choco/converters/`: Format conversion tools

### Live Dev Repository (`Live_Dev`)
- **Purpose**: Ableton Live development and control infrastructure
- **Components**:
  - **AbletonOSC**: OSC interface to Live Object Model (ports 11000/11001)
  - **Python Integration**: High-level Python API for Live control
  - **Max for Live Tools**: Device development support
- **Key Capabilities**:
  - Real-time OSC control of Live
  - MIDI clip creation and manipulation
  - Track/device parameter control
  - Beat/event listening

## Integration Architecture

```
┌─────────────────┐
│  ChoCo JAMS     │
│  Dataset Files  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  JAMS Parser    │  ← Extract chord progressions, timing, metadata
│  (jams library) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  JSON Converter │  ← Convert to lightweight JSON format
│  (Custom)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Chord Processor│  ← Convert Harte notation to MIDI notes
│  (music21/py)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  OSC Controller │  ← Send commands to Ableton Live
│  (AbletonOSC)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ableton Live   │  ← Create clips, trigger playback
│  (via OSC)      │
└─────────────────┘
```

## Implementation Path

### Phase 1: JAMS to JSON Conversion

**Goal**: Convert JAMS files to a lightweight JSON format for easier processing

**Implementation**:
1. Parse JAMS files using the `jams` library
2. Extract chord annotations with timing information
3. Convert to simplified JSON structure
4. Include metadata for filtering/searching

**JSON Structure**:
```json
{
  "metadata": {
    "title": "Song Title",
    "artist": "Artist Name",
    "genre": "jazz",
    "duration": 180.5,
    "dataset": "real-book"
  },
  "chords": [
    {
      "time": 0.0,
      "duration": 2.0,
      "chord": "C:maj7",
      "confidence": 1.0
    },
    {
      "time": 2.0,
      "duration": 2.0,
      "chord": "F:maj7",
      "confidence": 1.0
    }
  ],
  "key": "C major",
  "time_signature": "4/4"
}
```

### Phase 2: Chord to MIDI Conversion

**Goal**: Convert Harte chord notation to MIDI notes for Ableton Live

**Implementation**:
1. Parse Harte notation (e.g., "C:maj7", "F:min/5")
2. Generate MIDI note arrays for each chord
3. Map to Ableton Live's MIDI clip format
4. Handle inversions and voicings

**Chord Processing**:
- Use `music21` or custom parser for Harte notation
- Generate chord voicings (root position, inversions, extensions)
- Map to MIDI note numbers (0-127)
- Consider voice leading between chords

### Phase 3: OSC Integration

**Goal**: Send chord progressions to Ableton Live via OSC

**Implementation**:
1. Connect to AbletonOSC (port 11000)
2. Create MIDI tracks and clips
3. Send MIDI notes via `/live/clip/add/notes`
4. Trigger clips and control playback

**OSC Commands**:
- `/live/clip/create_clip`: Create new MIDI clip
- `/live/clip/add/notes`: Add MIDI notes to clip
- `/live/clip/fire`: Trigger clip playback
- `/live/song/set/tempo`: Set tempo
- `/live/track/set/name`: Name tracks

### Phase 4: Advanced Features

**Goal**: Add intelligent features for music production

**Features**:
- **Chord Progression Analysis**: Analyze common progressions
- **Voice Leading**: Optimize chord voicings for smooth transitions
- **Rhythm Generation**: Add rhythmic patterns to chords
- **Scale Constraints**: Ensure notes fit within key/scale
- **Real-time Control**: Live manipulation of chord progressions

## Code Examples

### Example 1: JAMS to JSON Converter

```python
import jams
import json
from pathlib import Path

def jams_to_json(jams_path, output_path=None):
    """
    Convert a JAMS file to simplified JSON format.
    
    Args:
        jams_path: Path to JAMS file
        output_path: Optional output JSON path
    """
    jam = jams.load(jams_path, strict=False)
    
    # Extract metadata
    metadata = {
        "title": jam.file_metadata.title or "",
        "artist": jam.file_metadata.artist or "",
        "duration": jam.file_metadata.duration or 0.0,
        "genre": jam.sandbox.get("genre", ""),
        "dataset": jam.sandbox.get("dataset", ""),
    }
    
    # Extract chord annotations
    chord_ann = jam.search(namespace="chord_harte")
    if not chord_ann:
        chord_ann = jam.search(namespace="chord")
    
    chords = []
    if chord_ann:
        for obs in chord_ann[0].data:
            chords.append({
                "time": float(obs.time),
                "duration": float(obs.duration),
                "chord": str(obs.value),
                "confidence": float(obs.confidence)
            })
    
    # Extract key information
    key_ann = jam.search(namespace="key_mode")
    key = ""
    if key_ann:
        # Get most common key
        keys = [obs.value for obs in key_ann[0].data]
        if keys:
            key = keys[0]
    
    result = {
        "metadata": metadata,
        "chords": chords,
        "key": key
    }
    
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
    
    return result
```

### Example 2: Chord to MIDI Converter

```python
def harte_to_midi_notes(chord_str, root_octave=4):
    """
    Convert Harte notation to MIDI note numbers.
    
    Args:
        chord_str: Harte chord string (e.g., "C:maj7", "F:min/5")
        root_octave: Octave for root note (default 4 = middle C)
    
    Returns:
        List of MIDI note numbers
    """
    # Parse Harte notation
    # Format: [ROOT][:QUALITY][/BASS]
    # Example: "C:maj7" -> C major 7th
    # Example: "F:min/5" -> F minor with 5th in bass
    
    # Note mapping
    note_map = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
        'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
    }
    
    # Parse root and quality
    if ':' in chord_str:
        root_str, quality = chord_str.split(':', 1)
    else:
        root_str, quality = chord_str, 'maj'
    
    # Handle bass note
    if '/' in quality:
        quality, bass = quality.split('/', 1)
    else:
        bass = None
    
    # Get root MIDI note
    root_note = note_map.get(root_str, 0)
    root_midi = root_octave * 12 + root_note
    
    # Define intervals for chord qualities
    intervals = {
        'maj': [0, 4, 7],
        'min': [0, 3, 7],
        'dim': [0, 3, 6],
        'aug': [0, 4, 8],
        'maj7': [0, 4, 7, 11],
        'min7': [0, 3, 7, 10],
        'dom7': [0, 4, 7, 10],
        'dim7': [0, 3, 6, 9],
        'maj6': [0, 4, 7, 9],
        'min6': [0, 3, 7, 9],
    }
    
    # Get intervals for quality
    chord_intervals = intervals.get(quality, intervals['maj'])
    
    # Generate MIDI notes
    notes = [root_midi + interval for interval in chord_intervals]
    
    # Handle inversions/bass notes
    if bass:
        # Simple bass note handling
        bass_note = note_map.get(bass, 0)
        bass_midi = (root_octave - 1) * 12 + bass_note
        notes = [bass_midi] + [n for n in notes if n != bass_midi]
    
    return sorted(set(notes))  # Remove duplicates and sort
```

### Example 3: Send Chords to Ableton Live

```python
from live_dev import LiveConnection
import time

def send_chord_progression_to_live(json_data, track_index=0, clip_index=0):
    """
    Send chord progression from JSON to Ableton Live.
    
    Args:
        json_data: JSON data from jams_to_json()
        track_index: Target track in Live
        clip_index: Target clip slot
    """
    live = LiveConnection(scan_on_init=True)
    
    # Set tempo if available
    if 'tempo' in json_data.get('metadata', {}):
        live.set_tempo(json_data['metadata']['tempo'])
    
    # Create clip
    clip_length = json_data['metadata'].get('duration', 32.0)  # Default 32 beats
    live.send_message('/live/clip_slot/create_clip', track_index, clip_index, clip_length)
    
    # Add chords as MIDI notes
    for chord_data in json_data['chords']:
        chord_str = chord_data['chord']
        start_time = chord_data['time']  # In seconds
        duration = chord_data['duration']  # In seconds
        
        # Convert to beats (assuming 120 BPM = 2 beats/sec)
        tempo = live.get_tempo()
        beats_per_sec = tempo / 60.0
        start_beat = start_time * beats_per_sec
        duration_beat = duration * beats_per_sec
        
        # Convert chord to MIDI notes
        midi_notes = harte_to_midi_notes(chord_str)
        
        # Add notes to clip
        for note in midi_notes:
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
    
    print(f"✓ Chord progression sent to track {track_index}, clip {clip_index}")
    return live
```

### Example 4: Batch Processing

```python
from pathlib import Path
import json

def batch_convert_jams_to_json(jams_directory, output_directory):
    """
    Convert all JAMS files in a directory to JSON.
    
    Args:
        jams_directory: Directory containing JAMS files
        output_directory: Directory for JSON output
    """
    jams_dir = Path(jams_directory)
    output_dir = Path(output_directory)
    output_dir.mkdir(exist_ok=True)
    
    jams_files = list(jams_dir.glob("*.jams"))
    print(f"Found {len(jams_files)} JAMS files")
    
    for jams_file in jams_files:
        try:
            json_data = jams_to_json(str(jams_file))
            output_path = output_dir / (jams_file.stem + ".json")
            
            with open(output_path, 'w') as f:
                json.dump(json_data, f, indent=2)
            
            print(f"✓ Converted: {jams_file.name}")
        except Exception as e:
            print(f"✗ Error converting {jams_file.name}: {e}")
    
    print(f"\n✓ Conversion complete: {len(jams_files)} files processed")
```

## Recommended Workflow

### Step 1: Setup Environment

```bash
# Install dependencies
pip install jams music21 pythonosc rapidfuzz

# Or use existing Live_Dev environment
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/python
pip install -r requirements.txt
```

### Step 2: Convert JAMS to JSON

```python
# Convert a single file
from jams_to_json import jams_to_json

jams_path = "/path/to/choco/partitions/real-book/choco/song.jams"
json_data = jams_to_json(jams_path, "song.json")

# Or batch convert
from batch_convert import batch_convert_jams_to_json

batch_convert_jams_to_json(
    "/path/to/choco/partitions/real-book/choco",
    "./json_output"
)
```

### Step 3: Enhance Metadata (Recommended)

```python
from choco_integration import MetadataEnhancer

# Enhance metadata for better searchability
enhancer = MetadataEnhancer()

# Enhance all JSON files
enhanced_files = enhancer.batch_enhance(
    "./json_output",
    "./json_enhanced",
    overwrite=False
)

# Build search indexes
artist_index = enhancer.build_artist_index("./json_enhanced")
song_index = enhancer.build_song_index("./json_enhanced")

# Find duplicates
import glob
json_files = glob.glob("./json_enhanced/**/*.json", recursive=True)
duplicates = enhancer.find_duplicates(json_files)

print(f"Enhanced {len(enhanced_files)} files")
print(f"Found {len(artist_index)} unique artists")
print(f"Found {len(duplicates)} duplicate groups")
```

**Benefits of Enhancement**:
- Normalized artist/song names for consistent searching
- Unique identifiers for reliable referencing
- Duplicate detection and grouping
- Fast search indexes
- See `METADATA_ENHANCEMENT_GUIDE.md` for details

### Step 4: Filter and Search

```python
from choco_integration import search_json_files, MetadataEnhancer

# Simple search (before enhancement)
jazz_songs = search_json_files("./json_output", genre="jazz")
print(f"Found {len(jazz_songs)} jazz songs")

# Enhanced search with fuzzy matching (after enhancement)
enhancer = MetadataEnhancer()
artist_index = enhancer.build_artist_index("./json_enhanced")

# Fuzzy search for artist
results = enhancer.search_artists("miles davis", artist_index, limit=10)
for artist, score, songs in results:
    print(f"{artist} ({score:.1%} match): {len(songs)} songs")
```

### Step 4: Send to Ableton Live

```python
# Load JSON and send to Live
with open("song.json") as f:
    song_data = json.load(f)

live = send_chord_progression_to_live(song_data, track_index=0, clip_index=0)

# Fire the clip
live.send_message('/live/clip/fire', 0, 0)
```

## Advanced Use Cases

### 1. Chord Progression Analysis

```python
def analyze_progression_patterns(json_directory):
    """Find common chord progressions across dataset."""
    from collections import Counter
    
    progressions = []
    json_dir = Path(json_directory)
    
    for json_file in json_dir.glob("*.json"):
        with open(json_file) as f:
            data = json.load(f)
            chords = [c['chord'] for c in data['chords']]
            # Extract 4-chord progressions
            for i in range(len(chords) - 3):
                progression = tuple(chords[i:i+4])
                progressions.append(progression)
    
    # Find most common
    common = Counter(progressions).most_common(10)
    return common
```

### 2. Real-time Chord Player

```python
def create_chord_player(live, track_index=0):
    """Create a real-time chord player that responds to OSC."""
    def play_chord(chord_str, duration=2.0):
        midi_notes = harte_to_midi_notes(chord_str)
        clip_index = 0
        
        # Clear existing notes
        live.send_message('/live/clip/remove/notes', track_index, clip_index)
        
        # Add new chord
        for note in midi_notes:
            live.send_message(
                '/live/clip/add/notes',
                track_index, clip_index,
                note, 0.0, duration, 100, 0
            )
        
        # Fire clip
        live.send_message('/live/clip/fire', track_index, clip_index)
    
    return play_chord
```

### 3. Dataset Browser Interface

Create a web interface to browse the dataset and send selections to Live:

```python
from flask import Flask, render_template, jsonify, request
from pathlib import Path
import json

app = Flask(__name__)
JSON_DIR = Path("./json_output")

@app.route('/')
def index():
    return render_template('browser.html')

@app.route('/api/songs')
def list_songs():
    songs = []
    for json_file in JSON_DIR.glob("*.json"):
        with open(json_file) as f:
            data = json.load(f)
            songs.append({
                'id': json_file.stem,
                'title': data['metadata'].get('title', ''),
                'artist': data['metadata'].get('artist', ''),
                'genre': data['metadata'].get('genre', ''),
                'chord_count': len(data['chords'])
            })
    return jsonify(songs)

@app.route('/api/send_to_live/<song_id>')
def send_to_live(song_id):
    json_file = JSON_DIR / f"{song_id}.json"
    with open(json_file) as f:
        data = json.load(f)
    
    live = send_chord_progression_to_live(data)
    return jsonify({'status': 'sent'})
```

## Performance Considerations

1. **Batch Processing**: Convert JAMS to JSON once, then work with JSON
2. **Caching**: Cache chord-to-MIDI conversions
3. **Lazy Loading**: Only load JAMS files when needed
4. **Indexing**: Create search indexes for metadata

## Next Steps

1. **Implement Core Converters**: Create `jams_to_json.py` and `chord_to_midi.py`
2. **Build Integration Layer**: Create `choco_to_live.py` module
3. **Add CLI Tools**: Command-line utilities for common tasks
4. **Create Examples**: Working examples for each use case
5. **Documentation**: API documentation and tutorials

## Resources

- **JAMS Documentation**: https://jams.readthedocs.io
- **AbletonOSC**: https://github.com/ideoforms/AbletonOSC
- **ChoCo Repository**: https://github.com/smashub/choco
- **Harte Notation**: https://ismir2005.ismir.net/proceedings/1080.pdf
- **Music21**: https://web.mit.edu/music21/

## Conclusion

This integration path provides a complete workflow from MIR datasets to Ableton Live, enabling:
- Efficient data processing through JSON conversion
- Flexible chord-to-MIDI conversion
- Real-time control via OSC
- Advanced music production features

The modular design allows for incremental implementation and customization based on specific needs.

