#!/usr/bin/env python3
"""
Quick start script - Test your Live Dev Integration setup
"""

import sys


def check_imports():
    """Check if all required modules can be imported."""
    print("=== Checking Dependencies ===\n")
    
    modules = [
        ("live", "pylive"),
        ("pythonosc", "python-osc"),
        ("colorama", "colorama"),
    ]
    
    missing = []
    for module, package in modules:
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("\n✓ All dependencies installed")
    return True


def check_live_dev():
    """Check if live_dev package is available."""
    print("\n=== Checking Live Dev Package ===\n")
    
    try:
        import live_dev
        print(f"✓ live_dev package (version {live_dev.__version__})")
        return True
    except ImportError as e:
        print(f"✗ live_dev package not found: {e}")
        print("\nInstall with: pip install -e .")
        return False


def test_connection():
    """Test connection to Ableton Live."""
    print("\n=== Testing Live Connection ===\n")
    
    try:
        from live_dev import LiveConnection
        
        print("Attempting to connect to Ableton Live...")
        with LiveConnection() as live:
            success = live.test_connection()
            
            if success:
                print(f"✓ Connected successfully")
                print(f"  Tempo: {live.get_tempo()} BPM")
                
                tracks = live.get_tracks()
                if tracks:
                    print(f"  Tracks: {len(tracks)}")
                else:
                    print("  No tracks found (Live Set may be empty)")
                
                return True
            else:
                print("✗ Connection test failed")
                return False
                
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nMake sure:")
        print("  1. Ableton Live is running")
        print("  2. AbletonOSC is installed and enabled in Preferences")
        print("  3. Ports 11000 and 11001 are not blocked")
        return False


def show_next_steps():
    """Show next steps for the user."""
    print("\n=== Next Steps ===\n")
    print("1. Explore the examples:")
    print("   cd examples")
    print("   python3 01_basic_connection.py")
    print("")
    print("2. Read the documentation:")
    print("   - README.md for API overview")
    print("   - examples/README.md for detailed examples")
    print("")
    print("3. Start building your Max for Live device!")
    print("")


def main():
    """Run all checks."""
    print("\n" + "="*50)
    print(" Live Dev Integration - Quick Start")
    print("="*50 + "\n")
    
    checks = [
        ("Dependencies", check_imports),
        ("Package", check_live_dev),
    ]
    
    all_passed = True
    for name, check_func in checks:
        if not check_func():
            all_passed = False
            break
    
    if not all_passed:
        print("\n" + "="*50)
        print("⚠️  Setup incomplete - please fix the errors above")
        print("="*50)
        sys.exit(1)
    
    # Test connection (optional)
    print("\nBasic checks passed! Testing Live connection...\n")
    connection_ok = test_connection()
    
    print("\n" + "="*50)
    if connection_ok:
        print("✓ All checks passed - Setup complete!")
    else:
        print("⚠️  Setup OK, but Live connection failed")
        print("   (This is normal if Live is not running)")
    print("="*50)
    
    show_next_steps()


if __name__ == "__main__":
    main()
