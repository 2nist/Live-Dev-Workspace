# Ableton Arranger

Section-based arrangement helper for Ableton Live. Port of REAPER Lua script to Python with PyQt5 GUI and AbletonOSC communication.

## Features

- **Section Management**: Add, edit, and delete arrangement sections with name, bars, tempo, and time signature
- **Section Presets**: Pre-defined section types (Intro, Verse, Chorus, etc.) with color coding
- **Role Tracks**: Automatic creation of role-based tracks (Drums, Bass, Chords, Melody, etc.)
- **Arrangement Building**: Build complete arrangements in Ableton Live with tracks, clips, and MIDI notes
- **Chord Editor**: (Phase 1: Stub) Placeholder for future chord progression editor

## Requirements

- Python 3.7+
- PyQt5 >= 5.15.0
- python-osc >= 1.8.0
- Ableton Live 11+ with AbletonOSC.amxd installed

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install AbletonOSC in Ableton Live:
   - Download [AbletonOSC](https://github.com/ideoforms/AbletonOSC)
   - Copy `AbletonOSC.amxd` to your Live set or Max for Live devices folder
   - Enable it in your Live set

## Usage

### Basic Application (2-panel)

1. Start Ableton Live with AbletonOSC.amxd loaded
2. Run the basic application:
```bash
python ableton_arranger/main.py
```

3. Use the interface:
   - **Left Panel**: Manage sections (add, delete, edit)
   - **Right Panel**: Chord editor with interactive timeline
   - **Rebuild Button**: Creates tracks and clips in Ableton Live

### Integrated Application (4-panel)

For the complete integrated system with audio analysis and data browser:

```bash
python ableton_arranger/main_integrated.py
```

Features:
   - **Top Left**: Section management
   - **Bottom Left**: Chord progression editor
   - **Top Right**: Audio analyzer (MP3 → sections/chords)
   - **Bottom Right**: Song library and project browser

## Project Structure

```
ableton_arranger/
├── main.py                      # Basic 2-panel entry point
├── main_integrated.py          # Integrated 4-panel entry point
├── config.py                   # Role tracks, presets, constants
├── requirements.txt            # Dependencies
├── core/                       # Core arrangement functionality
│   ├── section.py             # Section dataclass
│   ├── chord.py               # Chord theory and types
│   ├── connection.py          # OSC connection to Live
│   ├── arrangement_builder.py # Build arrangement
│   └── persistence.py         # JSON save/load
├── gui/                        # GUI components
│   ├── main_window.py         # Basic 2-panel window
│   ├── integrated_main_window.py  # 4-panel integrated window
│   ├── section_panel.py       # Section management UI
│   ├── chord_panel.py         # Chord editor
│   ├── chord_timeline.py      # Interactive timeline widget
│   └── analyzer_panel.py      # Audio analyzer panel
├── analyzer/                   # Audio analysis module
│   ├── audio_analyzer.py      # Main analyzer coordinator
│   ├── structure_detector.py  # SONOTELLER.AI + fallback
│   ├── stem_processor.py      # Stem separation
│   ├── chord_detector.py      # Chord detection
│   └── lyrics_transcriber.py  # Whisper transcription
├── data/                       # Data browser module
│   ├── models.py              # Data models
│   ├── database.py           # SQLite database manager
│   ├── project_manager.py    # Project lifecycle
│   └── browser_ui.py         # Browser UI components
├── shared/                      # Shared data models
│   └── data_models.py        # Inter-module communication
├── tests/                      # Test suite
│   └── test_integration.py   # Integration tests
└── data/                       # Runtime data
    └── sections.json         # Saved sections
```

## Key Differences from REAPER Version

1. **GUI**: PyQt5 instead of ReaImGui
2. **Communication**: AbletonOSC (OSC protocol) instead of REAPER API
3. **Data Format**: JSON instead of Lua file
4. **Arrangement Clips**: Currently creates session view clips (arrangement view support may be added later)

## Development Status

- ✅ Phase 1: Core Infrastructure - Complete
- ✅ Phase 2: GUI Foundation - Complete
- ✅ Phase 3: Arrangement Building - Complete
- ✅ Phase 4: Chord Editor - Complete
- ✅ Phase 5: Audio Analyzer Integration - Complete
- ✅ Phase 6: Data Browser Integration - Complete
- ✅ Phase 7: Integrated 4-Panel Application - Complete

## Notes

- The application connects to AbletonOSC on `localhost:11000` by default
- Sections are auto-saved to `data/sections.json` on close
- Track colors use REAPER format (0xBBGGRR) - may need conversion for Ableton
- Arrangement clips are created in session view - manual arrangement may be needed

## License

Port of REAPER script - see original script for license information.
