#!/usr/bin/env python3
"""
Basic example: Connect to Live and query basic information
"""

from live_dev import LiveConnection, configure_logging
import logging

# Enable debug logging
configure_logging(level=logging.INFO)


def main():
    """Basic connection and info retrieval example."""
    
    # Create connection to Live
    with LiveConnection(scan_on_init=True) as live:
        
        # Test connection
        print("\n=== Testing Connection ===")
        live.test_connection()
        
        # Get basic info
        print("\n=== Song Info ===")
        print(f"Tempo: {live.get_tempo()} BPM")
        
        # Get track information
        print("\n=== Track Info ===")
        tracks = live.get_tracks()
        print(f"Number of tracks: {len(tracks)}")
        
        for i, track in enumerate(tracks):
            print(f"\nTrack {i}: {track.name}")
            if track.clips:
                print(f"  Clips: {len(track.clips)}")
                for j, clip in enumerate(track.clips):
                    if clip:
                        print(f"    Clip {j}: {clip.name} ({clip.length} beats)")
            
            if track.devices:
                print(f"  Devices: {', '.join([d.name for d in track.devices])}")


if __name__ == "__main__":
    main()
