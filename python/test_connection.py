#!/usr/bin/env python3
"""
Test script for Ableton Live connection.
Tests both mock and live modes.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from arranger.live_bridge.ableton_connection import AbletonConnection
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mock_mode():
    """Test connection in mock mode."""
    print("\n" + "="*60)
    print("TESTING MOCK MODE")
    print("="*60)
    
    conn = AbletonConnection(mock=True)
    
    # Test connection status
    print(f"Connected: {conn.is_connected()}")
    print(f"Mock mode: {conn.mock}")
    
    # Test health check
    health = conn.health_check()
    print(f"\nHealth Check: {health}")
    
    # Test transport
    print(f"\nTempo: {conn.get_tempo()} BPM")
    print(f"Time Signature: {conn.get_time_signature()}")
    print(f"Playing: {conn.is_playing()}")
    
    # Test tempo change
    conn.set_tempo(128.0)
    print(f"New Tempo: {conn.get_tempo()} BPM")
    
    # Test scenes
    print(f"\nNumber of scenes: {conn.get_num_scenes()}")
    scene_idx = conn.create_scene(-1)
    print(f"Created scene at index: {scene_idx}")
    conn.set_scene_name(scene_idx, "Test Scene")
    print(f"Scene names: {conn.get_scene_names()}")
    
    # Test tracks
    print(f"\nNumber of tracks: {conn.get_num_tracks()}")
    
    # Test playback
    conn.play()
    print(f"Playing: {conn.is_playing()}")
    conn.stop()
    print(f"Playing: {conn.is_playing()}")
    
    conn.close()
    print("\n✅ Mock mode tests passed!")

def test_live_mode():
    """Test connection to actual Ableton Live."""
    print("\n" + "="*60)
    print("TESTING LIVE MODE")
    print("="*60)
    print("Make sure Ableton Live is running with AbletonOSC installed!")
    print("Press Enter to continue (or Ctrl+C to skip)...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nSkipping Live mode tests")
        return
    
    conn = AbletonConnection(mock=False, auto_reconnect=True)
    
    # Test connection status
    print(f"\nConnected: {conn.is_connected()}")
    print(f"Mock mode: {conn.mock}")
    
    if not conn.is_connected():
        print("\n⚠️  Not connected to Live. Make sure:")
        print("   1. Ableton Live is running")
        print("   2. AbletonOSC remote script is installed and selected")
        print("   3. Live shows 'AbletonOSC: Listening on port 11000'")
        return
    
    # Test health check
    health = conn.health_check()
    print(f"\nHealth Check:")
    for key, value in health.items():
        print(f"  {key}: {value}")
    
    # Test transport
    print(f"\n--- Transport Control ---")
    print(f"Tempo: {conn.get_tempo()} BPM")
    print(f"Time Signature: {conn.get_time_signature()}")
    print(f"Playing: {conn.is_playing()}")
    
    # Test scenes and tracks
    print(f"\n--- Live Set Info ---")
    print(f"Number of tracks: {conn.get_num_tracks()}")
    print(f"Number of scenes: {conn.get_num_scenes()}")
    
    scene_names = conn.get_scene_names()
    print(f"Scenes: {scene_names[:5]}..." if len(scene_names) > 5 else f"Scenes: {scene_names}")
    
    # Test track info
    num_tracks = conn.get_num_tracks()
    if num_tracks > 0:
        print(f"\n--- Track 0 Info ---")
        print(f"Name: {conn.get_track_name(0)}")
        print(f"Volume: {conn.get_track_volume(0)}")
    
    # Test scene creation (optional)
    print("\n--- Scene Management ---")
    response = input("Create a test scene? (y/n): ")
    if response.lower() == 'y':
        scene_idx = conn.create_scene(-1)
        conn.set_scene_name(scene_idx, "Arranger Test Scene")
        print(f"✅ Created scene '{conn.get_scene_names()[scene_idx]}' at index {scene_idx}")
        
        # Optionally delete it
        response = input("Delete the test scene? (y/n): ")
        if response.lower() == 'y':
            conn.delete_scene(scene_idx)
            print("✅ Deleted test scene")
    
    conn.close()
    print("\n✅ Live mode tests completed!")

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("ABLETON LIVE CONNECTION TEST SUITE")
    print("="*60)
    
    try:
        # Always test mock mode
        test_mock_mode()
        
        # Optionally test live mode
        test_live_mode()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
