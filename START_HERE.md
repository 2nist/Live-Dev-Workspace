# Start Here: ChoCo Implementation

## Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/python
pip3 install jams music21 rapidfuzz
# Or if using a virtual environment:
# pip install -r requirements_choco.txt
```

### Step 2: Run Implementation Test

```bash
python3 implement_choco.py
```

This will:
- ✅ Check dependencies
- ✅ Find your ChoCo dataset
- ✅ Run a test conversion
- ✅ Verify everything works

### Step 3: Process Your Dataset

```bash
cd examples

# Full pipeline
python choco_enhancement_pipeline.py \
    --jams-dir /Users/Matthew/Choco/choco-main/partitions \
    --output-dir ./choco_enhanced
```

## What Happens

1. **JAMS → JSON**: Converts all JAMS files to lightweight JSON
2. **Enhancement**: Normalizes names, creates unique IDs
3. **Indexes**: Builds searchable artist/song indexes
4. **Duplicates**: Finds duplicate songs across datasets
5. **Statistics**: Generates dataset insights

## Output

After processing, you'll have:

```
choco_enhanced/
├── json_intermediate/     # Converted JSON files
├── json_enhanced/         # Enhanced JSON files (use these!)
└── indexes/
    ├── artist_index.json  # Fast artist lookup
    ├── song_index.json    # Fast song lookup
    ├── duplicates.json    # Duplicate groups
    └── statistics.json    # Dataset stats
```

## Next Steps

### Search the Dataset

```bash
python choco_search_example.py \
    --enhanced-dir ./choco_enhanced/json_enhanced \
    --search-artist "miles davis"
```

### Send to Ableton Live

```python
from choco_integration import ChocoLiveBridge

bridge = ChocoLiveBridge("./choco_enhanced/json_enhanced")
bridge.connect()
bridge.load_song("path/to/song.json")
bridge.send_to_live(track_index=0, clip_index=0)
```

## Troubleshooting

### "Module not found"
```bash
pip install jams music21 rapidfuzz
```

### "JAMS files not found"
Check the path:
```bash
ls /Users/Matthew/Choco/choco-main/partitions/*.jams
```

### "Import error"
Make sure you're in the right directory:
```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/python
```

## Full Documentation

- **Integration Guide**: `MIR_TO_ABLETON_INTEGRATION_GUIDE.md`
- **Enhancement Guide**: `METADATA_ENHANCEMENT_GUIDE.md`
- **Examples**: `python/examples/README_CHOCO.md`

## Ready?

Run the test first:
```bash
python implement_choco.py
```

Then proceed with the full pipeline when ready!
