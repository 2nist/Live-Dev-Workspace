#!/usr/bin/env python3
"""
Quick Start Example for ChoCo Integration

A simple example showing the basic workflow:
1. Convert a single JAMS file
2. Enhance its metadata
3. Search for similar songs
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "src"))

from choco_integration import (
    jams_to_json,
    MetadataEnhancer,
    harte_to_midi_notes,
)


def main():
    print("="*60)
    print("ChoCo Integration Quick Start")
    print("="*60)
    print()
    
    # Example: Convert a single JAMS file
    print("Step 1: Convert JAMS to JSON")
    print("-" * 60)
    
    # You would replace this with an actual JAMS file path
    jams_file = input("Enter path to a JAMS file (or press Enter to skip): ").strip()
    
    if jams_file and Path(jams_file).exists():
        json_data = jams_to_json(jams_file, "example_song.json")
        print(f"✓ Converted: {jams_file}")
        print(f"  Title: {json_data.get('metadata', {}).get('title', 'N/A')}")
        print(f"  Artist: {json_data.get('metadata', {}).get('artist', 'N/A')}")
        print(f"  Chords: {len(json_data.get('chords', []))}")
    else:
        print("Skipping JAMS conversion (no file provided)")
        # Load example JSON if available
        if Path("example_song.json").exists():
            with open("example_song.json", 'r') as f:
                json_data = json.load(f)
        else:
            print("No example file found. Please provide a JAMS file.")
            return
    
    print()
    
    # Step 2: Enhance metadata
    print("Step 2: Enhance Metadata")
    print("-" * 60)
    
    enhancer = MetadataEnhancer()
    enhanced = enhancer.enhance_metadata(json_data)
    
    metadata = enhanced.get('metadata', {})
    print(f"✓ Enhanced metadata:")
    print(f"  Original title: {metadata.get('title_original', metadata.get('title', 'N/A'))}")
    print(f"  Normalized title: {metadata.get('title_normalized', 'N/A')}")
    print(f"  Original artist: {metadata.get('artist_original', metadata.get('artist', 'N/A'))}")
    print(f"  Normalized artist: {metadata.get('artist_normalized', 'N/A')}")
    print(f"  Unique ID: {metadata.get('unique_id', 'N/A')}")
    
    print()
    
    # Step 3: Convert chords to MIDI
    print("Step 3: Convert Chords to MIDI Notes")
    print("-" * 60)
    
    chords = enhanced.get('chords', [])
    if chords:
        print(f"Converting first 5 chords to MIDI notes:")
        for i, chord_data in enumerate(chords[:5], 1):
            chord_str = chord_data.get('chord', '')
            midi_notes = harte_to_midi_notes(chord_str)
            print(f"  {i}. {chord_str} -> MIDI notes: {midi_notes}")
    else:
        print("No chords found in this file")
    
    print()
    
    # Step 4: Show search terms
    print("Step 4: Search Terms")
    print("-" * 60)
    print(f"Search terms: {metadata.get('search_terms', 'N/A')}")
    
    print()
    print("="*60)
    print("Quick start complete!")
    print("="*60)
    print()
    print("Next steps:")
    print("  1. Run the full pipeline: python choco_enhancement_pipeline.py")
    print("  2. Search the dataset: python choco_search_example.py")
    print("  3. Send to Ableton Live: see integration examples")


if __name__ == "__main__":
    main()
