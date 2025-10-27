"""
Example: Creating an arrangement in Ableton Live

This example demonstrates how to:
1. Connect to Ableton Live via AbletonOSC
2. Create scenes with chord clips
3. Build a complete song arrangement
4. Schedule and trigger playback

Requirements:
- Ableton Live running with AbletonOSC remote script installed
- AbletonOSC listening on port 11000
"""

from arranger.live_bridge.ableton_connection import AbletonConnection
from arranger.live_bridge.live_bridge import SceneManager, ChordClipFactory, PlaybackScheduler
from arranger.models.arrangement import Arrangement
from arranger.models.section import Section, SectionType
from arranger.models.chord import Chord
import time


def create_song_arrangement():
    """Create a complete song arrangement in Ableton Live."""
    
    print("=" * 60)
    print("Arranger System - Live Integration Example")
    print("=" * 60)
    
    # Connect to Ableton Live
    print("\n1. Connecting to Ableton Live...")
    ableton = AbletonConnection(hostname="127.0.0.1", port=11000, mock=False)
    
    if ableton.is_connected():
        print("   ✓ Connected to Ableton Live")
        tempo = ableton.get_tempo()
        time_sig = ableton.get_time_signature()
        print(f"   Current tempo: {tempo} BPM")
        print(f"   Time signature: {time_sig[0]}/{time_sig[1]}")
    else:
        print("   ✗ Running in mock mode (Live not connected)")
        print("   To connect: Start Live with AbletonOSC remote script")
    
    # Initialize Live bridge components
    scene_mgr = SceneManager(ableton)
    clip_factory = ChordClipFactory(ableton)
    scheduler = PlaybackScheduler(ableton)
    
    # Define song structure
    print("\n2. Creating song arrangement...")
    
    # Intro: C - Am - F - G
    print("   Creating Intro...")
    intro_idx = scene_mgr.create_scene("Intro", [])
    if ableton.is_connected():
        clip_factory.create_chord_clip("C", 4, 0)
        clip_factory.create_chord_clip("Am", 4, 1)
        clip_factory.create_chord_clip("F", 4, 2)
        clip_factory.create_chord_clip("G", 4, 3)
    
    time.sleep(0.2)
    
    # Verse: C - G - Am - F
    print("   Creating Verse...")
    verse_idx = scene_mgr.create_scene("Verse", [])
    if ableton.is_connected():
        clip_factory.create_chord_clip("C", 4, 0)
        clip_factory.create_chord_clip("G", 4, 1)
        clip_factory.create_chord_clip("Am", 4, 2)
        clip_factory.create_chord_clip("F", 4, 3)
    
    time.sleep(0.2)
    
    # Chorus: F - G - C - Am
    print("   Creating Chorus...")
    chorus_idx = scene_mgr.create_scene("Chorus", [])
    if ableton.is_connected():
        clip_factory.create_chord_clip("F", 4, 0)
        clip_factory.create_chord_clip("G", 4, 1)
        clip_factory.create_chord_clip("C", 4, 2)
        clip_factory.create_chord_clip("Am", 4, 3)
    
    time.sleep(0.2)
    
    # Bridge: Dm - Em - F - G
    print("   Creating Bridge...")
    bridge_idx = scene_mgr.create_scene("Bridge", [])
    if ableton.is_connected():
        clip_factory.create_chord_clip("Dm", 4, 0)
        clip_factory.create_chord_clip("Em", 4, 1)
        clip_factory.create_chord_clip("F", 4, 2)
        clip_factory.create_chord_clip("G", 4, 3)
    
    time.sleep(0.2)
    
    # List all created scenes
    print("\n3. Scenes created in Live:")
    scenes = scene_mgr.list_scenes()
    for i, name in enumerate(scenes):
        print(f"   {i}: {name}")
    
    # Schedule playback order
    print("\n4. Scheduling playback order...")
    playback_order = [
        "Intro",
        "Verse", "Chorus",
        "Verse", "Chorus",
        "Bridge",
        "Chorus", "Chorus"
    ]
    
    result = scheduler.schedule_playback(playback_order)
    print(f"   Scheduled: {', '.join(playback_order)}")
    print(f"   Status: {result['status']}")
    print(f"   Connected: {result['connected']}")
    
    # Demonstrate scene triggering
    if ableton.is_connected():
        print("\n5. Triggering first scene...")
        next_scene = scheduler.trigger_next()
        print(f"   Triggered: {next_scene}")
        print("\n   Use scheduler.trigger_next() to play through the arrangement")
    else:
        print("\n5. Mock mode: Scene triggering simulated")
    
    # Demonstrate tempo/transport control
    print("\n6. Transport controls available:")
    print(f"   ableton.play() - Start playback")
    print(f"   ableton.stop() - Stop playback")
    print(f"   ableton.set_tempo(tempo) - Set tempo")
    print(f"   scene_mgr.trigger_scene(index) - Trigger specific scene")
    
    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)
    
    # Clean up
    ableton.close()


def create_chord_progression_example():
    """Example: Create a scene with a specific chord progression."""
    
    print("\n" + "=" * 60)
    print("Chord Progression Example")
    print("=" * 60)
    
    ableton = AbletonConnection(mock=False)
    clip_factory = ChordClipFactory(ableton)
    
    # ii-V-I progression in C major
    progression = ["Dm7", "G7", "Cmaj7"]
    
    print("\nCreating ii-V-I progression:")
    for i, chord in enumerate(progression):
        print(f"   {i+1}. {chord}")
        result = clip_factory.create_chord_clip(chord, 4, i)
        if result.get("connected"):
            print(f"      Created in Live at track {i}")
        else:
            print(f"      Mock: {len(result['notes'])} notes")
    
    ableton.close()


def query_live_state_example():
    """Example: Query current Live set state."""
    
    print("\n" + "=" * 60)
    print("Query Live State Example")
    print("=" * 60)
    
    ableton = AbletonConnection(mock=False)
    
    if ableton.is_connected():
        print("\nCurrent Live Set Info:")
        print(f"   Tempo: {ableton.get_tempo()} BPM")
        print(f"   Time Signature: {ableton.get_time_signature()}")
        print(f"   Num Tracks: {ableton.get_num_tracks()}")
        print(f"   Num Scenes: {ableton.get_num_scenes()}")
        
        # List tracks
        num_tracks = ableton.get_num_tracks()
        if num_tracks > 0:
            print(f"\n   Tracks:")
            for i in range(min(num_tracks, 8)):  # Limit to 8
                name = ableton.get_track_name(i)
                print(f"      {i}: {name}")
        
        # List scenes
        scene_names = ableton.get_scene_names()
        if scene_names:
            print(f"\n   Scenes:")
            for i, name in enumerate(scene_names[:8]):  # Limit to 8
                print(f"      {i}: {name}")
    else:
        print("\nNot connected to Live (mock mode)")
    
    ableton.close()


if __name__ == "__main__":
    # Run main example
    create_song_arrangement()
    
    # Uncomment to run other examples:
    # create_chord_progression_example()
    # query_live_state_example()
