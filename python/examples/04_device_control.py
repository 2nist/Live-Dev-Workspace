#!/usr/bin/env python3
"""
Device control example: Manipulate device parameters
"""

from live_dev import LiveConnection, M4LDeviceHelper
import time


def main():
    """Control device parameters."""
    
    live = LiveConnection(scan_on_init=True)
    helper = M4LDeviceHelper(live)
    
    print("=== Device Parameter Control ===\n")
    
    track_index = 0
    device_index = 0
    
    # Get device parameters
    print(f"Getting parameters for track {track_index}, device {device_index}...")
    params = helper.get_device_parameters(track_index, device_index)
    
    if not params:
        print("No device found! Please add a device to track 0 and try again.")
        return
    
    print(f"\nFound {len(params)} parameters:")
    for name, info in list(params.items())[:5]:  # Show first 5
        print(f"  {name}: {info['value']:.2f} (range: {info['min']:.2f} - {info['max']:.2f})")
    
    # Randomize parameters
    print("\nRandomizing device parameters...")
    randomized = helper.randomize_device_parameters(
        track_index,
        device_index,
        exclude_params=["Device On"]  # Don't turn device off!
    )
    
    print(f"Randomized {len(randomized)} parameters")
    
    print("\n✓ Done!")


if __name__ == "__main__":
    main()
