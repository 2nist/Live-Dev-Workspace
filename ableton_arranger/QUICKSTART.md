# Quick Start Guide - Integrated Ableton Arranger

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install AbletonOSC in Ableton Live:**
   - Download from: https://github.com/ideoforms/AbletonOSC
   - Copy `AbletonOSC.amxd` to your Live set
   - Enable it in your Live set

3. **Optional: Install analysis dependencies:**
```bash
# For stem separation (choose one)
pip install spleeter  # or
pip install demucs    # Better quality

# For lyrics transcription
pip install openai-whisper

# For audio analysis
pip install librosa
```

## Running the Application

### Option 1: Basic 2-Panel Application
```bash
python ableton_arranger/main.py
```
- Sections panel (left)
- Chord editor (right)

### Option 2: Integrated 4-Panel Application (Recommended)
```bash
python ableton_arranger/main_integrated.py
```
- Sections | Chords | Analyzer | Data Browser

## Quick Workflow

### Option A: Build From Scratch (No MP3 Required)

1. **Add Sections** in the Sections panel (top left)
2. **Add Chords** to each section using the Chord panel (bottom left)
3. **Add Lyrics** (optional) in the Lyrics editor in the Chord panel
4. **Build Arrangement** by clicking "Rebuild" in the Sections panel

See `BUILD_FROM_SCRATCH.md` for detailed instructions.

### Option B: Analyze an Audio File

1. Open the **Analyzer** panel (top right)
2. Click **Browse...** and select an MP3/WAV file
3. Click **Full Analysis** or **Detect Structure**
4. Wait for analysis to complete (progress bar shows status)
5. Click **Apply to Arrangement** when done

### 2. Edit Sections and Chords

1. Sections appear in the **Sections** panel (top left)
2. Click a section to select it
3. Edit chord progressions in the **Chord** panel (bottom left):
   - Use timeline to drag/move/resize chords
   - Use diatonic palette to add chords
   - Edit selected chord properties

### 3. Build Arrangement in Ableton Live

1. Ensure Ableton Live is running with AbletonOSC.amxd loaded
2. Click **Rebuild** in the Sections panel
3. Tracks and clips are created in Live
4. Chord progressions are applied as MIDI notes

### 4. Manage Your Library

1. Use **Data Browser** panel (bottom right) to:
   - Search songs by title, artist, genre
   - Filter by tempo, key, analysis status
   - Create and manage projects
   - View analysis history

## Configuration

### Analysis Settings

Edit `AnalysisConfig` in code or via UI:
- `sonoteller_api_key` - For structure detection (optional, has fallback)
- `enable_stem_separation` - Enable/disable stem separation
- `enable_chord_detection` - Enable/disable chord detection
- `enable_lyrics_transcription` - Enable/disable lyrics
- `whisper_model` - Whisper model size ("tiny", "base", "small", "medium", "large")

### Database Settings

Edit `BrowserConfig`:
- `database_path` - Path to SQLite database
- `auto_analyze_imports` - Auto-analyze imported songs
- `backup_enabled` - Enable automatic backups

## Troubleshooting

### "Not connected to Ableton Live"
- Ensure Ableton Live is running
- Verify AbletonOSC.amxd is loaded
- Check port 11000 is accessible

### Analysis fails
- Check audio file format (MP3, WAV supported)
- Verify required libraries installed (librosa, whisper, etc.)
- Check file permissions
- Review console logs for detailed errors

### Import errors
- Ensure you're running from workspace root
- Check Python path includes workspace root
- Verify all dependencies installed

## Example: Complete Workflow

```python
# 1. Analyze a song
# (Use Analyzer panel UI)

# 2. Analysis automatically creates sections
# Sections appear in Sections panel

# 3. Edit chord progressions
# Select section → Edit in Chord panel

# 4. Build arrangement
# Click "Rebuild" → Arrangement created in Live

# 5. Save to library
# Analysis automatically saved to database
```

## Performance Tips

- **Large Libraries**: Use pagination (default 50 results)
- **Fast Analysis**: Use "Detect Structure" instead of "Full Analysis"
- **Batch Processing**: Analyze multiple files sequentially
- **Database**: Regular backups recommended for large libraries

## Next Steps

- Read `INTEGRATION_GUIDE.md` for detailed integration patterns
- Check `IMPLEMENTATION_SUMMARY.md` for architecture details
- Run tests: `python -m unittest ableton_arranger.tests.test_integration`
