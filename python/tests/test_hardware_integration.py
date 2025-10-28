"""
Test script for hardware controller integration.

Tests controller detection, connection, and basic functionality.
"""
import sys
import time
from arranger.hardware import get_controller_manager, get_hardware_bridge, PushController
from arranger.models.chord import Chord
from arranger.models.section import Section
from arranger.models.arrangement import Arrangement


def test_controller_detection():
    """Test auto-detection of hardware controllers."""
    print("\n=== Testing Controller Detection ===")
    
    manager = get_controller_manager()
    detected = manager.auto_detect_controllers()
    
    print(f"Detected {len(detected)} controllers:")
    for controller in detected:
        print(f"  - {controller['type']} on {controller['port']}")
    
    return len(detected) > 0


def test_manual_connection():
    """Test manual controller connection."""
    print("\n=== Testing Manual Connection ===")
    
    try:
        import mido
        
        # List available MIDI ports
        print("\nAvailable MIDI Input Ports:")
        in_ports = mido.get_input_names()
        for i, port in enumerate(in_ports):
            print(f"  {i}: {port}")
            
        print("\nAvailable MIDI Output Ports:")
        out_ports = mido.get_output_names()
        for i, port in enumerate(out_ports):
            print(f"  {i}: {port}")
        
        # Try to find Push or Launchpad
        push_port = None
        launchpad_port = None
        apc64_port = None
        apc_mini_port = None
        
        for port in in_ports:
            if 'push' in port.lower():
                push_port = port
                break
            elif 'launchpad' in port.lower():
                launchpad_port = port
                break
            elif 'apc64' in port.lower():
                apc64_port = port
                break
            elif 'apc mini' in port.lower():
                apc_mini_port = port
                break
        
        if apc64_port:
            print(f"\nConnecting to APC64 on {apc64_port}...")
            manager = get_controller_manager()
            from arranger.hardware.controller_manager import APCController
            controller = APCController(apc64_port, apc64_port, 'apc64')
            manager.add_controller('apc64', controller)
            print("✅ Connected to APC64")
            return True
        elif apc_mini_port:
            print(f"\nConnecting to APC mini mk2 on {apc_mini_port}...")
            manager = get_controller_manager()
            from arranger.hardware.controller_manager import APCController
            controller = APCController(apc_mini_port, apc_mini_port, 'apc_mini_mk2')
            manager.add_controller('apc_mini_mk2', controller)
            print("✅ Connected to APC mini mk2")
            return True
        elif push_port:
            print(f"\nConnecting to Push on {push_port}...")
            manager = get_controller_manager()
            controller = PushController(push_port, push_port, version=2)
            manager.add_controller('push', controller)
            print("✅ Connected to Push")
            return True
        elif launchpad_port:
            print(f"\nConnecting to Launchpad on {launchpad_port}...")
            # Add Launchpad connection code if needed
            print("⚠️ Launchpad detected but not connected in this test")
            return False
        else:
            print("❌ No APC64, APC mini mk2, Push, or Launchpad detected")
            return False
            
    except ImportError:
        print("❌ mido not installed. Run: pip install mido python-rtmidi")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def test_chord_display():
    """Test chord progression display on hardware."""
    print("\n=== Testing Chord Progression Display ===")
    
    try:
        bridge = get_hardware_bridge()
        bridge.initialize()
        bridge.set_mode('chord')
        
        # Create test progression
        progression = [
            Chord(root='C', quality='maj7', duration=4.0, octave=4),
            Chord(root='D', quality='m7', duration=4.0, octave=4),
            Chord(root='G', quality='7', duration=4.0, octave=4),
            Chord(root='C', quality='maj7', duration=4.0, octave=4)
        ]
        
        print("Displaying I-ii-V-I progression...")
        bridge.display_chord_progression(progression)
        
        # Highlight each chord
        print("Highlighting chords sequentially...")
        for i in range(len(progression)):
            bridge.highlight_playing_chord(i)
            print(f"  Highlighting chord {i}: {progression[i].root}{progression[i].quality}")
            time.sleep(1)
        
        print("✅ Chord display test complete")
        return True
        
    except Exception as e:
        print(f"❌ Chord display failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_section_display():
    """Test arrangement section display."""
    print("\n=== Testing Section Display ===")
    
    try:
        bridge = get_hardware_bridge()
        bridge.set_mode('section')
        
        # Create test arrangement
        sections = [
            Section(
                name='Intro',
                duration=8.0,
                chords=[
                    Chord(root='C', quality='maj7', duration=4.0, octave=4),
                    Chord(root='Am', quality='m7', duration=4.0, octave=4)
                ]
            ),
            Section(
                name='Verse',
                duration=16.0,
                chords=[
                    Chord(root='C', quality='maj7', duration=4.0, octave=4),
                    Chord(root='F', quality='maj7', duration=4.0, octave=4),
                    Chord(root='G', quality='7', duration=4.0, octave=4),
                    Chord(root='C', quality='maj7', duration=4.0, octave=4)
                ]
            ),
            Section(
                name='Chorus',
                duration=16.0,
                chords=[
                    Chord(root='F', quality='maj7', duration=4.0, octave=4),
                    Chord(root='G', quality='7', duration=4.0, octave=4),
                    Chord(root='C', quality='maj7', duration=4.0, octave=4)
                ]
            )
        ]
        
        arrangement = Arrangement(
            name='Test Song',
            tempo=120.0,
            time_signature='4/4',
            sections=sections
        )
        
        print("Displaying arrangement sections...")
        bridge.display_arrangement(arrangement)
        
        # Highlight each section
        print("Highlighting sections sequentially...")
        for i, section in enumerate(sections):
            bridge.highlight_playing_section(i)
            print(f"  Highlighting section {i}: {section.name}")
            time.sleep(1.5)
        
        print("✅ Section display test complete")
        return True
        
    except Exception as e:
        print(f"❌ Section display failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scale_display():
    """Test scale layout display."""
    print("\n=== Testing Scale Display ===")
    
    try:
        bridge = get_hardware_bridge()
        bridge.set_mode('scale')
        
        # Display C major scale
        root = 60  # Middle C
        major_scale = [0, 2, 4, 5, 7, 9, 11]  # Major scale intervals
        
        print("Displaying C Major scale...")
        bridge.display_scale(root, major_scale)
        
        time.sleep(2)
        
        # Display A minor scale
        root = 57  # A
        minor_scale = [0, 2, 3, 5, 7, 8, 10]  # Natural minor
        
        print("Displaying A Minor scale...")
        bridge.display_scale(root, minor_scale)
        
        print("✅ Scale display test complete")
        return True
        
    except Exception as e:
        print(f"❌ Scale display failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all hardware tests."""
    print("=" * 60)
    print("Hardware Controller Integration Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Detection
    results['detection'] = test_controller_detection()
    
    # Test 2: Manual connection
    results['connection'] = test_manual_connection()
    
    # Only run display tests if connected
    manager = get_controller_manager()
    controllers = manager.list_controllers()
    
    if any(c['connected'] for c in controllers):
        print("\n✅ Controller connected, running display tests...")
        
        # Test 3: Chord display
        results['chord_display'] = test_chord_display()
        
        # Test 4: Section display
        results['section_display'] = test_section_display()
        
        # Test 5: Scale display
        results['scale_display'] = test_scale_display()
        
        # Cleanup
        print("\n=== Cleaning up ===")
        active = manager.get_active_controller()
        if active:
            active.clear_all_pads()
            print("Cleared all pads")
    else:
        print("\n⚠️ No controller connected, skipping display tests")
        print("To test display features, connect a Push or Launchpad")
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20s}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
