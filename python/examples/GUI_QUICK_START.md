# ChoCo to Ableton Live GUI - Quick Start

## Launch the GUI

```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/python/examples
python3 choco_ableton_gui_pyqt5.py
```

## Features

### 1. Load Dataset
- **Auto-loads**: Automatically loads `./choco_enhanced/json_enhanced/` if it exists
- **Manual load**: Click "Browse" to select a different directory
- **Click "Load"** to build/load indexes

### 2. Search & Browse
- **Search box**: Type to filter by artist or song title
- **Results list**: Click any song to view details
- **Real-time filtering**: Results update as you type

### 3. View Song Details
- **Information panel**: Shows title, artist, genre, duration
- **Chord list**: Displays first 10 chords with timing
- **Full chord count**: Shows total number of chords

### 4. Send to Ableton Live

**Before sending:**
1. **Test Connection**: Click "Test Connection" to verify Ableton Live is running
   - Make sure AbletonOSC is enabled in Live Preferences
   - You should see "Ableton Live: Connected" in green

2. **Configure**:
   - **Track**: Select which track in Live (0 = first track)
   - **Clip**: Select which clip slot (0 = first slot)
   - **Voicing**: Choose chord voicing style
     - `close`: Compact voicing (one octave)
     - `open`: Spread across octaves
     - `spread`: Wide spacing

3. **Preview**: Click "Preview Chords" to see MIDI note conversion

4. **Send**: Click "Send to Ableton Live"
   - Creates a MIDI clip in the specified track/clip
   - Adds all chord notes
   - Ready to play in Live!

## Requirements

- **Ableton Live** running with **AbletonOSC** enabled
- **Enhanced JSON files** in `./choco_enhanced/json_enhanced/`
- **PyQt5** installed (already done)

## Troubleshooting

### "Ableton Live: Not Connected"
- Make sure Ableton Live is running
- Enable AbletonOSC in Preferences > Link/Tempo/MIDI
- Click "Test Connection" again

### "No songs found"
- Make sure you've loaded the enhanced directory
- Check that `./choco_enhanced/json_enhanced/` exists
- Try clicking "Load" again

### "Failed to send"
- Check Ableton Live is running
- Verify track/clip numbers are valid
- Make sure the selected song has chords

## Tips

- **Search is case-insensitive**: "coltrane" finds "Coltrane"
- **Multiple results**: Songs may appear multiple times if they have different artists
- **Preview first**: Always preview chords before sending to verify conversion
- **Track management**: Use different tracks for different songs to keep them organized

## Keyboard Shortcuts

- **Enter**: Send to Live (when song selected)
- **Escape**: Close preview windows
- **Ctrl+F**: Focus search box

Enjoy browsing and inserting your ChoCo dataset into Ableton Live!
