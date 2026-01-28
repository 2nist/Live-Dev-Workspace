# Quick Commands Reference

## Navigate to Correct Directory

The scripts are in the `examples` subdirectory. Use these commands:

```bash
# Navigate to examples directory
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/python/examples

# Then run the analysis
python3 choco_metadata_analysis.py \
    --jams-dir /Users/Matthew/Choco/choco-main/partitions \
    --output coverage_report.txt
```

## Or Use Full Path

```bash
# From anywhere
python3 /Users/Matthew/Live_Dev/Live-Dev-Workspace/python/examples/choco_metadata_analysis.py \
    --jams-dir /Users/Matthew/Choco/choco-main/partitions \
    --output coverage_report.txt
```

## Quick Test (Sample)

For faster initial analysis, use a sample:

```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/python/examples

python3 choco_metadata_analysis.py \
    --jams-dir /Users/Matthew/Choco/choco-main/partitions \
    --sample 100 \
    --output quick_report.txt
```

## All Available Scripts

```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/python/examples

# Metadata analysis
python3 choco_metadata_analysis.py --help

# Enhancement pipeline
python3 choco_enhancement_pipeline.py --help

# Search example
python3 choco_search_example.py --help

# Quick start
python3 choco_quick_start.py
```

## Common Issues

### "File not found"
Make sure you're in the correct directory:
```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/python/examples
```

### "Module not found"
Install dependencies:
```bash
pip3 install jams music21 rapidfuzz
```

### "JAMS files not found"
Check the path:
```bash
ls /Users/Matthew/Choco/choco-main/partitions/*.jams | head -5
```
