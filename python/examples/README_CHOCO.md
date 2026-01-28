# ChoCo Integration Examples

Examples for using ChoCo MIR datasets with Ableton Live.

## Setup

1. Install dependencies:
```bash
pip install -r ../requirements_choco.txt
```

2. Make sure you have the ChoCo dataset available:
   - JAMS files from the ChoCo repository
   - Or already converted JSON files

## Examples

### 1. Complete Enhancement Pipeline

Run the full enhancement pipeline to convert JAMS to JSON, enhance metadata, build indexes, and find duplicates:

```bash
# Full pipeline from JAMS files
python choco_enhancement_pipeline.py \
    --jams-dir /path/to/choco/partitions \
    --output-dir ./choco_enhanced

# Skip JAMS conversion (already have JSON)
python choco_enhancement_pipeline.py \
    --json-dir ./json_files \
    --output-dir ./choco_enhanced \
    --skip-convert

# Only enhance metadata (skip indexes/duplicates)
python choco_enhancement_pipeline.py \
    --json-dir ./json_files \
    --output-dir ./choco_enhanced \
    --only-enhance
```

**Output Structure**:
```
choco_enhanced/
├── json_intermediate/     # Converted JSON files
├── json_enhanced/         # Enhanced JSON files
└── indexes/
    ├── artist_index.json
    ├── song_index.json
    ├── duplicates.json
    └── statistics.json
```

### 2. Search and Explore

Search the enhanced dataset:

```bash
# Search for an artist
python choco_search_example.py \
    --enhanced-dir ./choco_enhanced/json_enhanced \
    --search-artist "miles davis"

# Search for a song
python choco_search_example.py \
    --enhanced-dir ./choco_enhanced/json_enhanced \
    --search-song "autumn leaves"

# Filter by genre
python choco_search_example.py \
    --enhanced-dir ./choco_enhanced/json_enhanced \
    --filter-genre jazz

# Show duplicate songs
python choco_search_example.py \
    --enhanced-dir ./choco_enhanced/json_enhanced \
    --show-duplicates
```

### 3. Send to Ableton Live

See `choco_integration_example.py` (to be created) for examples of sending chord progressions to Ableton Live.

## Workflow

### Recommended Workflow

1. **Convert and Enhance**:
   ```bash
   python choco_enhancement_pipeline.py \
       --jams-dir /path/to/choco \
       --output-dir ./choco_enhanced
   ```

2. **Explore Dataset**:
   ```bash
   # See what artists are available
   python choco_search_example.py \
       --enhanced-dir ./choco_enhanced/json_enhanced \
       --filter-genre jazz \
       --limit 20
   ```

3. **Find Specific Songs**:
   ```bash
   python choco_search_example.py \
       --enhanced-dir ./choco_enhanced/json_enhanced \
       --search-song "blue note"
   ```

4. **Send to Live** (see integration examples):
   ```python
   from choco_integration import ChocoLiveBridge
   
   bridge = ChocoLiveBridge("./choco_enhanced/json_enhanced")
   bridge.connect()
   
   # Load and send a song
   bridge.load_song("path/to/song.json")
   bridge.send_to_live(track_index=0, clip_index=0)
   ```

## Troubleshooting

### Import Errors

If you get import errors, make sure you're running from the examples directory and the parent directory is in the Python path:

```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/python/examples
python choco_enhancement_pipeline.py ...
```

Or install the package in development mode:

```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/python
pip install -e .
```

### Missing Dependencies

Install all dependencies:

```bash
pip install jams music21 rapidfuzz
```

### JAMS Files Not Found

Make sure the path to JAMS files is correct. The ChoCo dataset structure is typically:

```
choco-main/
└── partitions/
    ├── randochoco/
    │   └── choco_expanded/
    │       ├── jazz/
    │       ├── pop/
    │       └── classical/
    └── ...
```

Use the full path to the `partitions` directory or specific subdirectory.

## Performance Tips

1. **Large Datasets**: The enhancement pipeline can take time for large datasets (20K+ files). Consider:
   - Running on a subset first
   - Using `--only-enhance` to skip duplicate detection initially
   - Processing in batches

2. **Memory Usage**: Building indexes loads all files into memory. For very large datasets:
   - Process in chunks
   - Use streaming for statistics

3. **Duplicate Detection**: This is the slowest step. You can:
   - Skip it initially with `--only-enhance`
   - Lower the similarity threshold for faster processing
   - Process specific genres/datasets separately

## Next Steps

After enhancement, you can:

1. **Use in Ableton Live**: Send chord progressions to Live via OSC
2. **Build Applications**: Use the indexes for search interfaces
3. **Analyze Patterns**: Study chord progressions across genres
4. **Create Datasets**: Filter and export specific subsets

See the main integration guide for more details: `MIR_TO_ABLETON_INTEGRATION_GUIDE.md`
