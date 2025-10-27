#!/usr/bin/env python3
"""
Advanced example: OSC listener for real-time events
"""

from live_dev import LiveConnection
import time


def on_beat(beat_number):
    """Callback for beat events."""
    print(f"♪ Beat: {beat_number}")


def on_tempo_change(tempo):
    """Callback for tempo changes."""
    print(f"⚡ Tempo changed: {tempo} BPM")


def main():
    """Listen to Live events in real-time."""
    
    print("=== OSC Event Listener Example ===\n")
    
    live = LiveConnection(scan_on_init=True)
    
    # Start listening for beat events
    print("Starting beat listener...")
    live.send_osc("/live/song/start_listen/beat")
    live.start_listening("/live/song/get/beat", on_beat)
    
    # Start listening for tempo changes
    print("Starting tempo listener...")
    live.send_osc("/live/song/start_listen/tempo")
    live.start_listening("/live/song/get/tempo", on_tempo_change)
    
    print("\nListening for events... (Press Ctrl+C to stop)")
    print("Try changing tempo or playing the song in Live\n")
    
    try:
        # Keep script running
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\nStopping listeners...")
        live.send_osc("/live/song/stop_listen/beat")
        live.send_osc("/live/song/stop_listen/tempo")
        live.stop_listening()
        print("✓ Done!")


if __name__ == "__main__":
    main()
