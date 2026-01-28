# Ableton Arranger - Integration Guide

Complete guide for using the integrated 4-panel application.

## Architecture Overview

The integrated application combines four main modules:

1. **Sections Panel** - Section management (left top)
2. **Chords Panel** - Chord progression editor (left bottom)
3. **Analyzer Panel** - Audio analysis (right top)
4. **Data Browser Panel** - Song library and projects (right bottom)

## Package Structure

```
ableton_arranger/
├── main_integrated.py          # Integrated application entry point
├── main.py                      # Original 2-panel entry point
├── core/                        # Core arrangement functionality
│   ├── section.py
│   ├── chord.py
│   ├── connection.py
│   ├── arrangement_builder.py
│   └── persistence.py
├── gui/                         # GUI components
│   ├── main_window.py          # Original 2-panel window
│   ├── integrated_main_window.py  # 4-panel integrated window
│   ├── section_panel.py
│   ├── chord_panel.py
│   ├── chord_timeline.py
│   └── analyzer_panel.py
├── analyzer/                    # Audio analysis module
│   ├── audio_analyzer.py       # Main analyzer coordinator
│   ├── structure_detector.py   # SONOTELLER.AI + fallback
│   ├── stem_processor.py       # Stem separation
│   ├── chord_detector.py       # Chord detection
│   └── lyrics_transcriber.py   # Whisper transcription
├── data/                        # Data browser module
│   ├── models.py               # Data models
│   ├── database.py             # SQLite database manager
│   ├── project_manager.py      # Project lifecycle
│   └── browser_ui.py          # Browser UI components
└── shared/                      # Shared data models
    └── data_models.py          # Inter-module communication
```

## Running the Integrated Application

```bash
python ableton_arranger/main_integrated.py
```

## Complete Workflow

### 1. Analyze an Audio File

1. Click "Browse..." in the Analyzer panel
2. Select an MP3/WAV file
3. Click "Full Analysis" or "Detect Structure"
4. Wait for analysis to complete
5. Results show: sections, chords, lyrics, stems

### 2. Apply Analysis to Arrangement

1. After analysis completes, click "Apply to Arrangement"
2. Sections are automatically created in the Sections panel
3. Chords are added to each section
4. Select a section to edit its chords in the Chord panel

### 3. Edit Sections and Chords

1. Use Sections panel to add/edit/delete sections
2. Select a section to edit its chord progression
3. Use Chord panel timeline to:
   - Click chords to select
   - Drag to move
   - Drag edges to resize
   - Double-click to add
4. Use diatonic palette to quickly add chords
5. Edit selected chords with the editor controls

### 4. Build Arrangement in Ableton Live

1. Click "Rebuild" in Sections panel
2. Application creates tracks and clips in Live
3. Chord progressions are applied as MIDI notes

### 5. Manage Song Library

1. Use Data Browser panel to:
   - Search songs by title, artist, genre
   - Filter by tempo, key, analysis status
   - View analysis results
   - Create projects
2. Click "Analyze" on a song to analyze it
3. Analysis results are saved to database

## Module Integration Points

### Analyzer → Sections/Chords

- `AnalysisData` → `Section` objects via `to_arrangement_section()`
- `ChordData` → `Chord` objects via `to_chord_object()`
- Automatic timing conversion (seconds → beats)

### Analyzer → Database

- `AnalysisData` stored as JSON in database
- Song metadata extracted and stored
- Analysis flags (has_stems, has_midi, has_lyrics) updated

### Database → Analyzer

- Songs can be analyzed from browser
- Analysis results linked to songs
- Projects can reference analyzed songs

### Sections/Chords → Live

- `ArrangementBuilder` creates tracks and clips
- Chord progressions converted to MIDI notes
- Section colors and names applied

## Configuration

### Analysis Configuration

```python
from ableton_arranger.shared.data_models import AnalysisConfig

config = AnalysisConfig()
config.sonoteller_api_key = "your_api_key"  # For structure detection
config.enable_stem_separation = True
config.enable_chord_detection = True
config.enable_lyrics_transcription = True
config.whisper_model = "base"  # or "small", "medium", "large"
```

### Browser Configuration

```python
from ableton_arranger.data.models import BrowserConfig

config = BrowserConfig()
config.database_path = "data/songs.db"
config.auto_analyze_imports = True
config.backup_enabled = True
```

## Error Handling

The application includes comprehensive error handling:

- **Connection Errors**: Graceful degradation if Ableton Live not connected
- **Analysis Errors**: User-friendly error messages with details
- **Database Errors**: Transaction rollback and error logging
- **File Errors**: Validation and clear error messages

## Performance Optimization

### For Large Song Libraries

1. **Database Indexing**: Automatic indexes on common search fields
2. **Pagination**: Search results limited to 50 by default
3. **Caching**: Analysis results cached to avoid re-analysis
4. **Background Processing**: Analysis runs in separate thread

### Recommended Settings

```python
# For large libraries (>1000 songs)
config.default_search_limit = 100
config.cache_analysis_data = True
config.preload_thumbnails = False  # Disable for performance
```

## Testing

Run integration tests:

```bash
python -m pytest ableton_arranger/tests/test_integration.py
```

Or use unittest:

```bash
python -m unittest ableton_arranger.tests.test_integration
```

## M4L Conversion Notes

All modules are designed for Max for Live device conversion:

- Simple request/response patterns
- JSON serialization for data transfer
- Modular architecture (each panel = separate device)
- OSC-compatible communication

## Troubleshooting

### Analysis Fails

- Check audio file format (MP3, WAV supported)
- Verify librosa/whisper installation
- Check API keys if using SONOTELLER.AI
- Review logs for detailed error messages

### Database Errors

- Check database file permissions
- Verify SQLite3 is available
- Check disk space
- Review database backup settings

### Live Connection Issues

- Ensure Ableton Live is running
- Verify AbletonOSC.amxd is loaded
- Check port 11000 is not blocked
- Review firewall settings

## Next Steps

1. **Stem Separation**: Implement Ableton Live 12.3 native integration
2. **MIDI Export**: Export chord progressions as MIDI files
3. **Project Templates**: Pre-configured project structures
4. **Batch Processing**: Analyze multiple files at once
5. **Cloud Sync**: Sync projects and songs across devices
