# ChoCo Dataset Processing Status

**Dataset Location**: `/Users/Matthew/Choco/choco-main/partitions`

## Current Status

### Pipeline Progress
- **Total JAMS files**: 106,918
- **Converted to JSON**: Check with `./check_pipeline.sh`
- **Enhanced**: Check with `./check_pipeline.sh`
- **Status**: Running in background

### Quick Check Commands

```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/python/examples

# Check pipeline status
./check_pipeline.sh

# Count converted files
find ./choco_enhanced/json_intermediate -name "*.json" | wc -l

# Count enhanced files  
find ./choco_enhanced/json_enhanced -name "*.json" | wc -l

# View recent progress
tail -20 pipeline.log
```

## Dataset Structure

The ChoCo dataset contains multiple partitions:

```
/Users/Matthew/Choco/choco-main/partitions/
├── isophonics/          # Pop/rock songs
├── billboard/           # Billboard charts
├── real-book/           # Jazz standards
├── ireal-pro/           # iReal Pro playlists
├── weimar/              # Weimar Jazz Database
├── rwc-pop/             # RWC Pop database
├── chordify/            # Chordify annotations
├── jaah/                # Jazz Audio-Aligned Harmony
└── ... (more partitions)
```

## Processing Output

All processed files are saved to:
```
./choco_enhanced/
├── json_intermediate/    # Raw JSON conversion
├── json_enhanced/        # Enhanced with normalized names
└── indexes/              # Search indexes and statistics
```

## Next Steps

1. **Wait for completion** - Pipeline processes all files automatically
2. **Use enhanced files** - Once complete, use files in `json_enhanced/`
3. **Search dataset** - Use `choco_search_example.py` to find songs
4. **Send to Ableton** - Use `ChocoLiveBridge` to send chord progressions

## Estimated Completion

With 106,918 files:
- **Conversion**: ~2-4 hours
- **Enhancement**: ~30-60 minutes  
- **Indexes**: ~1-2 hours
- **Duplicates**: ~2-4 hours
- **Total**: ~6-12 hours

Monitor progress with `./check_pipeline.sh`
