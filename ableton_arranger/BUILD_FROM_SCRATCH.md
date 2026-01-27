# Building Arrangements From Scratch

Yes! You can build complete arrangements from scratch without importing any MP3 files. This guide shows you how.

## Quick Start: Build From Scratch

### Option 1: Basic 2-Panel Application (Recommended for Manual Building)

```bash
python ableton_arranger/main.py
```

This gives you:
- **Left Panel**: Section management
- **Right Panel**: Chord editor with lyrics support

### Option 2: Integrated 4-Panel Application

```bash
python ableton_arranger/main_integrated.py
```

This includes everything plus:
- Audio analyzer (if you want to analyze later)
- Data browser (for managing your library)

## Complete Workflow: Building From Scratch

### Step 1: Add Sections

1. In the **Sections** panel (left), click **Add**
2. A new section appears in the table
3. Edit the section properties:
   - **Name**: Double-click to rename (e.g., "Intro", "Verse 1", "Chorus")
   - **Bars**: Use spinbox to set length (e.g., 4, 8, 16 bars)
   - **Time Sig**: Select from dropdown (4/4, 3/4, 6/8, etc.)
   - **Tempo**: Set tempo for this section (optional, uses global tempo if not set)

4. Repeat to add all sections (Intro, Verse, Chorus, Bridge, Outro, etc.)

**Tip**: Use section presets by selecting common names like "Intro", "Verse", "Chorus" - they get automatic color coding!

### Step 2: Add Chord Progressions

1. **Select a section** by clicking on it in the Sections panel
2. The **Chord** panel (right) now shows that section's timeline
3. **Add chords** using one of these methods:

   **Method A: Diatonic Palette (Easiest)**
   - Set the **Key** and **Scale** at the top (e.g., Key: C, Scale: Ionian)
   - Click the diatonic chord buttons (I, ii, iii, IV, V, vi, vii°)
   - Chords are automatically appended to the progression

   **Method B: Timeline Double-Click**
   - Double-click anywhere on the timeline to add a chord at that position
   - The first diatonic chord is added by default
   - Then edit it using the chord editor

   **Method C: Progression Presets**
   - Scroll down to "Progression Presets"
   - Click a preset (e.g., "I-V-vi-IV", "ii-V-I")
   - The progression is automatically added

4. **Edit chords**:
   - Click a chord on the timeline to select it
   - Use the "Selected Chord" editor to change:
     - Root note
     - Chord type (major, minor, 7th, etc.)
     - Inversion
     - Start beat and duration
     - Bass note (for slash chords)
     - Octave

5. **Move/Resize chords**:
   - Drag a chord horizontally to move it
   - Drag the edges to resize duration
   - Use the timeline to visualize the progression

6. **Repeat for each section**: Select each section and add its chord progression

### Step 3: Add Lyrics (Optional)

1. With a section selected, scroll down in the **Chord** panel
2. Find the **"Lyrics (Optional)"** section
3. Type or paste lyrics into the text box
4. Lyrics are automatically saved with the section

**Note**: Lyrics are stored per-section. You can add different lyrics for each section (Verse 1, Chorus, etc.)

### Step 4: Build Arrangement in Ableton Live

1. **Ensure Ableton Live is running** with AbletonOSC.amxd loaded
2. Click **Rebuild** in the Sections panel
3. The application will:
   - Create role tracks (Drums, Bass, Chords, Melody, etc.)
   - Create clips for each section
   - Apply chord progressions as MIDI notes to the "Chords" track
   - Set tempo and time signatures
   - Color-code clips based on section types

4. Your arrangement is now in Ableton Live!

## Example: Building a Simple Song

### Structure:
1. **Intro** - 4 bars, 4/4, 120 BPM
   - Chords: C major (4 bars)
   - Lyrics: (none)

2. **Verse 1** - 8 bars, 4/4, 120 BPM
   - Chords: C - Am - F - G (2 bars each)
   - Lyrics: "This is the first verse..."

3. **Chorus** - 8 bars, 4/4, 120 BPM
   - Chords: F - C - Am - G (2 bars each)
   - Lyrics: "This is the chorus..."

4. **Verse 2** - 8 bars, 4/4, 120 BPM
   - Chords: C - Am - F - G (2 bars each)
   - Lyrics: "This is the second verse..."

5. **Chorus** - 8 bars, 4/4, 120 BPM
   - Chords: F - C - Am - G (2 bars each)
   - Lyrics: "This is the chorus..."

6. **Outro** - 4 bars, 4/4, 120 BPM
   - Chords: C major (4 bars)
   - Lyrics: (none)

**Total**: 40 bars, ~2 minutes at 120 BPM

## Tips for Building From Scratch

### Section Management
- Use descriptive names: "Intro", "Verse 1", "Chorus", "Bridge", "Outro"
- Set appropriate bar lengths (4, 8, 16 bars are common)
- Use section presets for automatic color coding

### Chord Progressions
- Start with diatonic chords in your key
- Use the progression presets for common patterns
- Experiment with chord substitutions (available in "Substitutions & Theory")
- Try secondary dominants for more interesting progressions
- Use inversions to create smoother voice leading

### Lyrics
- Add lyrics section by section
- You can copy/paste from external text editors
- Lyrics are saved with the section data
- Each section can have its own lyrics

### Time Signatures
- Most songs use 4/4, but you can use 3/4, 6/8, etc.
- Each section can have its own time signature
- The timeline automatically adjusts

### Tempo Changes
- Set tempo per-section for tempo changes
- Leave tempo empty to use global tempo
- Useful for builds, breakdowns, tempo shifts

## Saving Your Work

- Sections are **auto-saved** when you:
  - Add/edit/delete sections
  - Modify chord progressions
  - Change lyrics
  - Close the application

- Manual save: Use **File → Save Sections** (Ctrl+S)

- Load: Use **File → Load Sections** (Ctrl+O)

## Advanced Features

### Chord Substitutions
- Select a chord in the timeline
- Expand "Substitutions & Theory" section
- See available substitutions:
  - Tritone substitutions
  - Relative major/minor
  - Parallel major/minor
  - Secondary dominants
  - Borrowed chords
- Click to apply substitutions

### Progression Analysis
- The progression display shows your current chord progression
- Use it to verify your chord changes
- Helps with voice leading and harmonic analysis

## Comparison: From Scratch vs. From Analysis

| Feature | From Scratch | From Analysis |
|---------|-------------|---------------|
| **Sections** | Manual creation | Auto-detected |
| **Chords** | Manual entry | Auto-detected |
| **Lyrics** | Manual entry | Auto-transcribed |
| **Tempo** | Manual setting | Auto-detected |
| **Time Sig** | Manual setting | Auto-detected |
| **Control** | Full control | Based on source |
| **Speed** | Slower | Faster |
| **Accuracy** | Perfect | Depends on source |

## When to Build From Scratch

✅ **Use when:**
- You want full creative control
- You're composing original music
- You want specific chord progressions
- You need precise timing
- You're working with lyrics you've written
- You want to experiment with different structures

✅ **Use analysis when:**
- You're remixing or covering existing songs
- You want to learn from existing arrangements
- You need quick structure detection
- You're working with reference tracks

## Next Steps

- Read `QUICKSTART.md` for general usage
- Read `INTEGRATION_GUIDE.md` for advanced integration
- Check `README.md` for feature overview

Happy arranging! 🎵
