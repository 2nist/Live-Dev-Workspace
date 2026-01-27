# Lyrics Integration - Manual vs. Whisper Analysis

## Overview

Lyrics are fully integrated into the Ableton Arranger workflow, whether you add them manually or get them from Whisper transcription.

## Two Ways to Add Lyrics

### 1. Manual Entry (Build From Scratch)

**Location**: Chord Panel → "Lyrics (Optional)" section

**How it works**:
1. Select a section in the Sections panel
2. Scroll down in the Chord panel
3. Find the "Lyrics (Optional)" text box
4. Type or paste lyrics
5. Lyrics are automatically saved with the section

**Features**:
- Per-section lyrics (each section can have its own lyrics)
- Auto-saved when you change sections or close the app
- Stored in the same JSON file as sections
- Editable at any time

### 2. Whisper Transcription (From Audio Analysis)

**Location**: Analyzer Panel → "Full Analysis" or "Detect Structure"

**How it works**:
1. Analyze an audio file with lyrics transcription enabled
2. Whisper transcribes the entire audio file
3. Lyrics are automatically extracted and assigned to sections based on timing
4. Lyrics appear in the same "Lyrics (Optional)" editor in the Chord panel

**Features**:
- Automatic transcription from audio
- Word-level timing (words are matched to sections by time)
- Full text available for reference
- Can be edited after transcription

## How Lyrics Are Integrated

### Data Flow

```
Audio File
    ↓
Whisper Transcription
    ↓
AnalysisData.lyrics (with word timing)
    ↓
Extract words for each section (by time range)
    ↓
Section.lyrics (per-section text)
    ↓
Chord Panel Lyrics Editor (displays and allows editing)
```

### Integration Points

1. **Analysis → Sections** (`integrated_main_window.py`):
   - When analysis completes, lyrics are extracted from `AnalysisData.lyrics.words`
   - Words are matched to sections based on their timing (`start_time`)
   - Each section gets lyrics that fall within its time range
   - Lyrics are stored in `section.lyrics`

2. **Section → UI** (`chord_panel.py`):
   - When a section is selected, `set_selected_section()` loads `section.lyrics`
   - Lyrics are displayed in the "Lyrics (Optional)" text editor
   - User can edit them manually
   - Changes are saved back to `section.lyrics`

3. **Persistence** (`section.py`, `persistence.py`):
   - Lyrics are included in `Section.to_dict()`
   - Saved to JSON with sections
   - Loaded from JSON when app starts

## Example: Lyrics from Analysis

### Input (Audio File)
- Song: "Hello World" by Test Artist
- Duration: 120 seconds
- Sections detected:
  - Intro: 0-8s
  - Verse 1: 8-32s
  - Chorus: 32-56s
  - Verse 2: 56-80s
  - Chorus: 80-104s
  - Outro: 104-120s

### Whisper Transcription
```
Full text: "Hello world, this is a test song. Hello world, singing along. 
           Hello world, this is the chorus. Hello world, one more time."
Words with timing:
  - "Hello" (0.0-0.5s)
  - "world" (0.5-1.0s)
  - "this" (8.0-8.3s)
  - "is" (8.3-8.5s)
  ...
```

### Result (Assigned to Sections)
- **Intro** (0-8s): "Hello world"
- **Verse 1** (8-32s): "this is a test song. Hello world, singing along."
- **Chorus** (32-56s): "Hello world, this is the chorus."
- **Verse 2** (56-80s): "Hello world, one more time."
- **Chorus** (80-104s): (repeated)
- **Outro** (104-120s): (none)

## Display in UI

### Analyzer Panel Results
After analysis completes, the results show:
```
✓ Lyrics transcribed (45 words)
  Hello world, this is a test song...
```

### Chord Panel Lyrics Editor
When you select a section:
- The lyrics editor shows the lyrics for that section
- You can edit them if needed
- Changes are saved automatically

## Editing Lyrics

### After Analysis
1. Analysis completes with transcribed lyrics
2. Select a section in Sections panel
3. Lyrics appear in Chord panel's lyrics editor
4. Edit as needed
5. Changes are saved to `section.lyrics`

### Manual Entry
1. Select a section
2. Type lyrics in the editor
3. Auto-saved when you change sections

## Technical Details

### LyricsData Structure
```python
@dataclass
class LyricsData:
    full_text: str  # Complete transcription
    words: List[Dict]  # [{"word": "hello", "start": 1.5, "end": 1.8}]
    language: str
    confidence: float
```

### Section.lyrics
```python
@dataclass
class Section:
    ...
    lyrics: Optional[str] = None  # Per-section lyrics text
```

### Extraction Logic
```python
# Extract words that fall within section time range
for word_info in analysis_data.lyrics.words:
    word_start = word_info.get("start", 0.0)
    if (word_start >= section_data.start_time and 
        word_start < section_data.end_time):
        section_lyrics_words.append(word_info.get("word", ""))

section.lyrics = " ".join(section_lyrics_words)
```

## Configuration

### Enable Lyrics Transcription
```python
config = AnalysisConfig()
config.enable_lyrics_transcription = True
config.whisper_model = "base"  # or "small", "medium", "large"
```

### Whisper Models
- **tiny**: Fastest, least accurate
- **base**: Good balance (default)
- **small**: Better accuracy
- **medium**: High accuracy
- **large**: Best accuracy, slowest

## Best Practices

### For Manual Entry
- Add lyrics section by section
- Use line breaks for verse structure
- Copy/paste from external editors
- Review before building arrangement

### For Whisper Transcription
- Use "base" or "small" model for speed
- Use "medium" or "large" for accuracy
- Review and edit transcribed lyrics
- Check word timing matches sections

### Hybrid Approach
1. Use Whisper for initial transcription
2. Review and edit in the lyrics editor
3. Add missing sections manually
4. Refine timing and wording

## Troubleshooting

### Lyrics Not Appearing After Analysis
- Check that `enable_lyrics_transcription = True` in config
- Verify Whisper is installed: `pip install openai-whisper`
- Check console logs for transcription errors
- Ensure audio file has vocals/lyrics

### Lyrics Not Matching Sections
- Word timing may not align with section boundaries
- Edit manually to correct
- Use full text as reference
- Adjust section timing if needed

### Lyrics Editor Not Showing
- Ensure a section is selected
- Scroll down in Chord panel
- Check that section has lyrics assigned
- Try refreshing the panel

## Summary

✅ **Manual Lyrics**: Fully integrated, per-section, editable
✅ **Whisper Lyrics**: Automatically transcribed and assigned to sections
✅ **Display**: Same editor for both manual and transcribed lyrics
✅ **Editing**: Can edit transcribed lyrics just like manual ones
✅ **Persistence**: Saved with sections in JSON

Both methods are fully integrated and use the same UI and storage system!
