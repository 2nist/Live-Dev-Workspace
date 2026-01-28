# Running the Enhancement Pipeline

## Current Status

The pipeline is running but encountering some files with unknown namespaces (like `chord_weimar`). The converter has been updated to handle these gracefully.

## Quick Start

```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/python/examples

# Run on full dataset (will take time for 106K+ files)
/Users/Matthew/.pyenv/versions/3.8.19/bin/python3 choco_enhancement_pipeline.py \
    --jams-dir /Users/Matthew/Choco/choco-main/partitions \
    --output-dir ./choco_enhanced
```

## Run on Specific Dataset First (Recommended)

Test on a smaller dataset first:

```bash
# Test on isophonics (smaller dataset)
/Users/Matthew/.pyenv/versions/3.8.19/bin/python3 choco_enhancement_pipeline.py \
    --jams-dir /Users/Matthew/Choco/choco-main/partitions/isophonics \
    --output-dir ./choco_enhanced_isophonics
```

## Background Processing

For the full dataset, run in background:

```bash
nohup /Users/Matthew/.pyenv/versions/3.8.19/bin/python3 choco_enhancement_pipeline.py \
    --jams-dir /Users/Matthew/Choco/choco-main/partitions \
    --output-dir ./choco_enhanced \
    > pipeline.log 2>&1 &

echo "Pipeline running in background. Monitor with: tail -f pipeline.log"
```

## Check Progress

```bash
# Check if still running
ps aux | grep choco_enhancement_pipeline

# Check output directory
ls -lh ./choco_enhanced/json_intermediate/ | wc -l
ls -lh ./choco_enhanced/json_enhanced/ | wc -l

# Check logs
tail -f pipeline.log
```

## Expected Output

After completion, you'll have:

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

## Note on Errors

Some files may have errors due to:
- Unknown namespaces (like `chord_weimar`) - now handled gracefully
- Missing metadata - expected, will be reported in statistics
- Corrupted files - will be skipped with error logged

The pipeline will continue processing even if some files fail.
