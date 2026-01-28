#!/usr/bin/env python3
"""
Full Workflow Demo

Demonstrates the complete ChoCo to Ableton Live workflow:
1. Load JAMS file
2. Convert to JSON
3. Enhance metadata
4. Convert chords to MIDI
5. Show how to send to Ableton Live
"""

import sys
from pathlib import Path

# Add src to path
script_dir = Path(__file__).resolve().parent
parent_dir = script_dir.parent
src_dir = parent_dir / "src"
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(src_dir))

from choco_integration import (
    jams_to_json,
    MetadataEnhancer,
    harte_to_midi_notes,
    chord_progression_to_midi,
)

def main():
    print("="*70)
    print("ChoCo to Ableton Live - Full Workflow Demo")
    print("="*70)
    print()
    
    # Find a sample JAMS file
    sample_files = [
        "/Users/Matthew/Choco/choco-main/partitions/weimar/choco/jams/weimar_228.jams",
        "/Users/Matthew/Choco/choco-main/partitions/isophonics/choco/jams/isophonics_170.jams",
    ]
    
    sample_file = None
    for f in sample_files:
        if Path(f).exists():
            sample_file = f
            break
    
    if not sample_file:
        print("No sample JAMS files found. Using mock data...")
        demo_mock_data()
        return
    
    print(f"Using sample file: {Path(sample_file).name}")
    print()
    
    # Step 1: Convert JAMS to JSON
    print("Step 1: Converting JAMS to JSON...")
    print("-" * 70)
    json_data = jams_to_json(sample_file)
    
    metadata = json_data.get('metadata', {})
    chords = json_data.get('chords', [])
    
    print(f"✓ Converted")
    print(f"  Title: {metadata.get('title', 'N/A')}")
    print(f"  Artist: {metadata.get('artist', 'N/A')}")
    print(f"  Genre: {metadata.get('genre', 'N/A')}")
    print(f"  Chords: {len(chords)} chord annotations")
    print()
    
    # Step 2: Enhance metadata
    print("Step 2: Enhancing metadata...")
    print("-" * 70)
    enhancer = MetadataEnhancer()
    enhanced = enhancer.enhance_metadata(json_data)
    
    enhanced_meta = enhanced.get('metadata', {})
    print(f"✓ Enhanced")
    print(f"  Normalized title: {enhanced_meta.get('title_normalized', 'N/A')}")
    print(f"  Normalized artist: {enhanced_meta.get('artist_normalized', 'N/A')}")
    print(f"  Unique ID: {enhanced_meta.get('unique_id', 'N/A')}")
    print()
    
    # Step 3: Convert chords to MIDI
    print("Step 3: Converting chords to MIDI notes...")
    print("-" * 70)
    
    if chords:
        print("First 5 chords as MIDI:")
        for i, chord_data in enumerate(chords[:5], 1):
            chord_str = chord_data.get('chord', '')
            if chord_str and chord_str != 'N':
                midi_notes = harte_to_midi_notes(chord_str)
                time = chord_data.get('time', 0)
                duration = chord_data.get('duration', 0)
                print(f"  {i}. {chord_str:10} -> MIDI: {midi_notes:30} (time: {time:.1f}s, dur: {duration:.1f}s)")
    else:
        print("  No chords found in this file")
        # Try a different file or use mock
        print("  Using example chords for demonstration:")
        example_chords = ['C:maj7', 'F:min', 'G:dom7', 'A:min']
        for i, chord in enumerate(example_chords, 1):
            notes = harte_to_midi_notes(chord)
            print(f"  {i}. {chord:10} -> MIDI: {notes}")
    print()
    
    # Step 4: Show Ableton Live integration
    print("Step 4: Ableton Live Integration (Example)")
    print("-" * 70)
    print("To send to Ableton Live, you would use:")
    print()
    print("  from choco_integration import ChocoLiveBridge")
    print("  ")
    print("  bridge = ChocoLiveBridge('./choco_enhanced/json_enhanced')")
    print("  bridge.connect()")
    print("  bridge.load_song('path/to/song.json')")
    print("  bridge.send_to_live(track_index=0, clip_index=0)")
    print()
    print("Or use the OSC commands directly:")
    print("  /live/clip_slot/create_clip <track> <clip> <length>")
    print("  /live/clip/add/notes <track> <clip> <pitch> <start> <duration> <velocity> <mute>")
    print("  /live/clip/fire <track> <clip>")
    print()
    
    # Step 5: Show chord progression
    if chords:
        print("Step 5: Chord Progression Analysis")
        print("-" * 70)
        print(f"Total chord progression: {len(chords)} chords")
        
        # Group by unique chords
        unique_chords = {}
        for chord_data in chords:
            chord = chord_data.get('chord', '')
            if chord and chord != 'N':
                unique_chords[chord] = unique_chords.get(chord, 0) + 1
        
        print(f"Unique chords: {len(unique_chords)}")
        print("Most common chords:")
        sorted_chords = sorted(unique_chords.items(), key=lambda x: x[1], reverse=True)
        for chord, count in sorted_chords[:10]:
            print(f"  {chord:15} appears {count} times")
    
    print()
    print("="*70)
    print("Demo Complete!")
    print("="*70)
    print()
    print("Next steps:")
    print("  1. Wait for full pipeline to complete")
    print("  2. Use enhanced JSON files in ./choco_enhanced/json_enhanced")
    print("  3. Send chord progressions to Ableton Live")
    print("  4. Build your music application!")


def demo_mock_data():
    """Demo with mock data if no JAMS files available."""
    print("Using mock chord progression...")
    print()
    
    mock_chords = [
        {"time": 0.0, "duration": 2.0, "chord": "C:maj7", "confidence": 1.0},
        {"time": 2.0, "duration": 2.0, "chord": "F:min", "confidence": 1.0},
        {"time": 4.0, "duration": 2.0, "chord": "G:dom7", "confidence": 1.0},
        {"time": 6.0, "duration": 2.0, "chord": "A:min", "confidence": 1.0},
    ]
    
    print("Chord Progression:")
    for i, chord_data in enumerate(mock_chords, 1):
        chord = chord_data['chord']
        notes = harte_to_midi_notes(chord)
        print(f"  {i}. {chord:10} -> MIDI: {notes}")
    
    print()
    print("This progression can be sent to Ableton Live as MIDI notes!")


if __name__ == "__main__":
    main()
