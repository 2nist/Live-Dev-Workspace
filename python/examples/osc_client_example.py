"""
Example: OSC client for arranger system.

This script demonstrates how to interact with the arranger OSC server
to get theory guidance, create scenes, and schedule playback.
"""

from pythonosc import udp_client
import time


def main():
    # Connect to arranger OSC server
    client = udp_client.SimpleUDPClient("127.0.0.1", 12000)
    
    print("Arranger OSC Client Example")
    print("=" * 50)
    
    # 1. Get theory guidance for a key/mode
    print("\n1. Requesting theory guidance for C major, chord I...")
    client.send_message("/theory/guidance", ["C", "major", "I"])
    time.sleep(0.1)
    
    # 2. Get common progressions
    print("\n2. Requesting common progressions in C major...")
    client.send_message("/theory/progressions", ["C", "major"])
    time.sleep(0.1)
    
    # 3. Get cadences
    print("\n3. Requesting all cadence types...")
    client.send_message("/theory/cadences", [])
    time.sleep(0.1)
    
    # 4. Create a scene in Live
    print("\n4. Creating a scene 'Verse1' with clips...")
    client.send_message("/live/create_scene", ["Verse1", "drums", "bass", "keys"])
    time.sleep(0.1)
    
    # 5. Create chord clips
    print("\n5. Creating chord clips...")
    client.send_message("/live/create_chord_clip", ["Cmaj7", 4, 1])
    time.sleep(0.05)
    client.send_message("/live/create_chord_clip", ["Dm7", 4, 2])
    time.sleep(0.05)
    client.send_message("/live/create_chord_clip", ["G7", 4, 3])
    time.sleep(0.1)
    
    # 6. Schedule playback order
    print("\n6. Scheduling playback order...")
    order = ["Intro", "Verse1", "Chorus", "Verse2", "Chorus", "Bridge", "Chorus"]
    client.send_message("/live/schedule_playback", order)
    time.sleep(0.1)
    
    # 7. Get live theory suggestions
    print("\n7. Requesting live theory suggestions...")
    live_state = {"key": "C", "mode": "major", "tempo": 120, "section": "chorus"}
    client.send_message("/live/theory_suggestions", [live_state])
    time.sleep(0.1)
    
    # 8. Analyze arrangement
    print("\n8. Analyzing arrangement...")
    arrangement = {
        "key": "C",
        "mode": "major",
        "sections": [
            {"label": "V1", "type": "verse", "bars": 8},
            {"label": "C", "type": "chorus", "bars": 8}
        ]
    }
    client.send_message("/theory/analyze_arrangement", [arrangement])
    time.sleep(0.1)
    
    print("\n" + "=" * 50)
    print("Example completed. Check server output for replies.")
    print("\nTo start the server, run:")
    print("  python -c 'from arranger.live_bridge.osc_server import ArrangerOSCServer; server = ArrangerOSCServer(); server.serve_forever()'")


if __name__ == "__main__":
    main()
