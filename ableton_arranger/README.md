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

1. Start Ableton Live with AbletonOSC.amxd loaded
2. Run the application:
```bash
python ableton_arranger/main.py
```

3. Use the interface:
   - **Left Panel**: Manage sections (add, delete, edit)
   - **Right Panel**: Chord editor (coming soon)
   - **Rebuild Button**: Creates tracks and clips in Ableton Live based on your sections

## Project Structure

```
ableton_arranger/
├── main.py                 # Entry point
├── config.py              # Role tracks, presets, constants
├── requirements.txt       # Dependencies
├── core/
│   ├── section.py         # Section dataclass
│   ├── chord.py           # Chord theory and types
│   ├── connection.py      # OSC connection to Live
│   ├── arrangement_builder.py  # Build arrangement
│   └── persistence.py     # JSON save/load
├── gui/
│   ├── main_window.py     # Main window with splitter
│   ├── section_panel.py   # Section management UI
│   └── chord_panel.py     # Chord editor (stub)
└── data/
    └── sections.json      # Saved sections
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
- ⏳ Phase 4: Chord Editor - Planned

## Notes

- The application connects to AbletonOSC on `localhost:11000` by default
- Sections are auto-saved to `data/sections.json` on close
- Track colors use REAPER format (0xBBGGRR) - may need conversion for Ableton
- Arrangement clips are created in session view - manual arrangement may be needed

## License

Port of REAPER script - see original script for license information.
