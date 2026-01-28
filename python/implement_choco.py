#!/usr/bin/env python3
"""
ChoCo Implementation Starter Script

This script helps you get started with the ChoCo integration.
It will guide you through the setup and run a test implementation.
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    missing = []
    
    try:
        import jams
        print("  ✓ jams")
    except ImportError:
        missing.append("jams")
        print("  ✗ jams (missing)")
    
    try:
        import music21
        print("  ✓ music21")
    except ImportError:
        print("  ⚠ music21 (optional)")
    
    try:
        from rapidfuzz import fuzz
        print("  ✓ rapidfuzz")
    except ImportError:
        print("  ⚠ rapidfuzz (optional, but recommended)")
    
    if missing:
        print(f"\nMissing required dependencies: {', '.join(missing)}")
        print("Install with: pip install jams")
        return False
    
    return True

def check_paths():
    """Check if ChoCo dataset paths exist."""
    print("\nChecking ChoCo dataset paths...")
    
    possible_paths = [
        "/Users/Matthew/Choco/choco-main/partitions",
        "/Users/Matthew/Choco/choco-main",
        "./choco-main/partitions",
        "../Choco/choco-main/partitions",
    ]
    
    found_paths = []
    for path in possible_paths:
        if Path(path).exists():
            jams_files = list(Path(path).rglob("*.jams"))
            if jams_files:
                found_paths.append((path, len(jams_files)))
                print(f"  ✓ {path} ({len(jams_files)} JAMS files)")
            else:
                print(f"  ⚠ {path} (exists but no JAMS files)")
        else:
            print(f"  ✗ {path} (not found)")
    
    return found_paths

def create_test_implementation():
    """Create a test implementation with a small subset."""
    print("\n" + "="*60)
    print("Creating Test Implementation")
    print("="*60)
    
    # Add src to path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        from choco_integration import (
            jams_to_json,
            MetadataEnhancer,
            harte_to_midi_notes,
        )
        print("✓ Successfully imported choco_integration modules")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Make sure you're in the correct directory")
        return False
    
    # Find a test JAMS file
    test_paths = [
        "/Users/Matthew/Choco/choco-main/partitions",
        "./choco-main/partitions",
    ]
    
    test_jams = None
    for base_path in test_paths:
        if Path(base_path).exists():
            jams_files = list(Path(base_path).rglob("*.jams"))
            if jams_files:
                test_jams = jams_files[0]
                break
    
    if not test_jams:
        print("\n⚠ No JAMS files found for testing")
        print("Creating a mock example instead...")
        return create_mock_example()
    
    print(f"\nUsing test file: {test_jams.name}")
    
    try:
        # Step 1: Convert to JSON
        print("\n1. Converting JAMS to JSON...")
        output_json = Path(__file__).parent / "test_output" / "test_song.json"
        output_json.parent.mkdir(exist_ok=True)
        
        json_data = jams_to_json(str(test_jams), str(output_json))
        print(f"   ✓ Converted: {output_json}")
        
        metadata = json_data.get('metadata', {})
        print(f"   Title: {metadata.get('title', 'N/A')}")
        print(f"   Artist: {metadata.get('artist', 'N/A')}")
        print(f"   Chords: {len(json_data.get('chords', []))}")
        
        # Step 2: Enhance metadata
        print("\n2. Enhancing metadata...")
        enhancer = MetadataEnhancer()
        enhanced = enhancer.enhance_metadata(json_data)
        
        enhanced_meta = enhanced.get('metadata', {})
        print(f"   ✓ Enhanced")
        print(f"   Normalized title: {enhanced_meta.get('title_normalized', 'N/A')}")
        print(f"   Normalized artist: {enhanced_meta.get('artist_normalized', 'N/A')}")
        print(f"   Unique ID: {enhanced_meta.get('unique_id', 'N/A')}")
        
        # Step 3: Test chord conversion
        print("\n3. Testing chord to MIDI conversion...")
        chords = enhanced.get('chords', [])
        if chords:
            for i, chord_data in enumerate(chords[:3], 1):
                chord_str = chord_data.get('chord', '')
                if chord_str and chord_str != 'N':
                    midi_notes = harte_to_midi_notes(chord_str)
                    print(f"   {i}. {chord_str} → MIDI: {midi_notes}")
        
        # Save enhanced version
        enhanced_json = output_json.parent / "test_song_enhanced.json"
        import json
        with open(enhanced_json, 'w') as f:
            json.dump(enhanced, f, indent=2)
        print(f"\n   ✓ Saved enhanced version: {enhanced_json}")
        
        print("\n" + "="*60)
        print("✓ Test Implementation Successful!")
        print("="*60)
        print(f"\nOutput files:")
        print(f"  - {output_json}")
        print(f"  - {enhanced_json}")
        print(f"\nNext steps:")
        print(f"  1. Run full pipeline: python examples/choco_enhancement_pipeline.py")
        print(f"  2. Search dataset: python examples/choco_search_example.py")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error during implementation: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_mock_example():
    """Create a mock example when no JAMS files are available."""
    print("\nCreating mock example...")
    
    mock_data = {
        "metadata": {
            "title": "Autumn Leaves",
            "artist": "The Bill Evans Trio",
            "genre": "jazz",
            "duration": 180.5
        },
        "chords": [
            {"time": 0.0, "duration": 4.0, "chord": "C:min", "confidence": 1.0},
            {"time": 4.0, "duration": 4.0, "chord": "F:min", "confidence": 1.0},
            {"time": 8.0, "duration": 4.0, "chord": "Bb:maj", "confidence": 1.0},
            {"time": 12.0, "duration": 4.0, "chord": "Eb:maj", "confidence": 1.0},
        ]
    }
    
    # Add src to path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        from choco_integration import MetadataEnhancer, harte_to_midi_notes
        
        enhancer = MetadataEnhancer()
        enhanced = enhancer.enhance_metadata(mock_data)
        
        output_dir = Path(__file__).parent / "test_output"
        output_dir.mkdir(exist_ok=True)
        
        import json
        output_file = output_dir / "mock_example_enhanced.json"
        with open(output_file, 'w') as f:
            json.dump(enhanced, f, indent=2)
        
        print(f"✓ Created mock example: {output_file}")
        print(f"\nEnhanced metadata:")
        meta = enhanced.get('metadata', {})
        print(f"  Unique ID: {meta.get('unique_id')}")
        print(f"  Normalized: {meta.get('title_normalized')} - {meta.get('artist_normalized')}")
        
        print(f"\nChord to MIDI examples:")
        for chord_data in enhanced.get('chords', [])[:3]:
            chord = chord_data.get('chord', '')
            midi = harte_to_midi_notes(chord)
            print(f"  {chord} → {midi}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("ChoCo Integration Implementation Starter")
    print("="*60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install missing dependencies first:")
        print("  pip install jams music21 rapidfuzz")
        return
    
    # Check paths
    found_paths = check_paths()
    
    # Run test implementation
    success = create_test_implementation()
    
    if success:
        print("\n" + "="*60)
        print("Ready to proceed with full implementation!")
        print("="*60)
        print("\nTo process your full dataset:")
        print("  cd examples")
        print("  python choco_enhancement_pipeline.py \\")
        print("      --jams-dir /path/to/choco/partitions \\")
        print("      --output-dir ./choco_enhanced")
        print()
        if found_paths:
            print("Or use one of the found paths:")
            for path, count in found_paths[:1]:
                print(f"  python choco_enhancement_pipeline.py \\")
                print(f"      --jams-dir {path} \\")
                print(f"      --output-dir ./choco_enhanced")
    else:
        print("\n" + "="*60)
        print("Implementation test had issues")
        print("="*60)
        print("\nTroubleshooting:")
        print("  1. Make sure dependencies are installed")
        print("  2. Check that ChoCo dataset path is correct")
        print("  3. Verify file permissions")

if __name__ == "__main__":
    main()
