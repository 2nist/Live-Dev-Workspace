#!/usr/bin/env python3
"""
MIDI generation example: Create MIDI clips programmatically
"""

from live_dev import LiveConnection, M4LDeviceHelper, create_scale
import random


def main():
    """Create MIDI patterns in Live."""
    
    live = LiveConnection(scan_on_init=True)
    helper = M4LDeviceHelper(live)
    
    print("=== MIDI Generation Example ===\n")
    
    # Create a simple melody
    print("Creating melody on track 0, clip 0...")
    root_note = 60  # C4
    scale = create_scale(root_note, "minor")
    
    # Generate random melody from scale
    melody = [random.choice(scale) for _ in range(16)]
    helper.create_note_sequence(
        track_index=0,
        clip_index=0,
        pitches=melody,
        duration=0.25,  # 16th notes
        velocity=100
    )
    
    # Create a drum pattern
    print("Creating drum pattern on track 1, clip 0...")
    drum_pattern = [
        (36, [0, 4, 8, 12]),           # Kick on quarter notes
        (38, [4, 12]),                 # Snare on 2 and 4
        (42, list(range(16))),         # Hi-hat on every 16th
    ]
    
    helper.create_drum_pattern(
        track_index=1,
        clip_index=0,
        pattern=drum_pattern,
        step_duration=0.25
    )
    
    print("\n✓ MIDI clips created!")
    print("Tip: Fire the clips in Live to hear them")


if __name__ == "__main__":
    main()
