#!/usr/bin/env python3
"""
Clip control example: Fire clips and control playback
"""

from live_dev import LiveConnection
import time


def main():
    """Example of controlling clip playback."""
    
    with LiveConnection(scan_on_init=True) as live:
        
        print("=== Clip Control Example ===\n")
        
        # Start playback
        print("Starting playback...")
        live.play()
        time.sleep(1)
        
        # Fire first clip on first track
        print("Firing clip [0, 0]...")
        live.fire_clip(0, 0)
        time.sleep(4)
        
        # Fire second clip
        print("Firing clip [0, 1]...")
        live.fire_clip(0, 1)
        time.sleep(4)
        
        # Stop all clips
        print("Stopping all clips...")
        live.stop_all_clips()
        time.sleep(1)
        
        # Stop playback
        print("Stopping playback...")
        live.stop()
        
        print("\n✓ Done!")


if __name__ == "__main__":
    main()
