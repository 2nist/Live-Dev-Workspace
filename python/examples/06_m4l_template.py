#!/usr/bin/env python3
"""
Max for Live device template generator

This script demonstrates how to set up a complete environment
for a Max for Live device with Python control.
"""

from live_dev import LiveConnection, M4LDeviceHelper


def create_performance_controller():
    """Create a basic performance controller setup."""
    
    print("=== M4L Performance Controller Setup ===\n")
    
    live = LiveConnection(scan_on_init=False)
    helper = M4LDeviceHelper(live)
    
    # Create track structure
    print("Creating track structure...")
    helper.setup_basic_scene(num_midi_tracks=4, num_audio_tracks=2)
    
    # Name the tracks
    tracks = live.get_tracks()
    track_names = ["Lead", "Bass", "Drums", "FX", "Audio 1", "Audio 2"]
    
    for i, name in enumerate(track_names):
        if i < len(tracks):
            live.send_osc("/live/track/set/name", i, name)
    
    print(f"Created {len(track_names)} tracks")
    
    # Create clips in first scene
    print("\nCreating initial clips...")
    for i in range(min(4, len(tracks))):
        live.send_osc("/live/clip_slot/create_clip", i, 0, 8.0)
    
    # Set colors for tracks
    colors = [12, 8, 4, 60]  # Different colors for each MIDI track
    for i, color in enumerate(colors):
        live.send_osc("/live/track/set/color_index", i, color)
    
    # Export track info
    print("\n=== Track Summary ===")
    for i in range(min(6, len(tracks))):
        info = helper.export_track_info(i)
        print(f"\nTrack {i}: {info.get('name', 'Unknown')}")
        print(f"  Devices: {info.get('num_devices', 0)}")
        print(f"  Clips: {info.get('num_clips', 0)}")
    
    print("\n✓ M4L controller setup complete!")
    print("\nNext steps:")
    print("  1. Add devices to your tracks in Live")
    print("  2. Use examples 03 and 04 to populate clips")
    print("  3. Create your Max for Live device to control this setup")


def create_generative_setup():
    """Create a setup for generative music."""
    
    print("=== Generative Music Setup ===\n")
    
    live = LiveConnection(scan_on_init=True)
    helper = M4LDeviceHelper(live)
    
    # This would create a more complex setup for generative music
    # For example: multiple MIDI tracks with different instruments,
    # randomized clips, etc.
    
    print("Creating generative music environment...")
    
    # Create MIDI tracks for different roles
    for i in range(4):
        live.create_midi_track()
    
    live.scan()
    
    print(f"✓ Created {len(live.get_tracks())} tracks for generative setup")
    print("\nReady for generative algorithms!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "generative":
        create_generative_setup()
    else:
        create_performance_controller()
