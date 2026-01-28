# ChoCo Partitions Overview

**Location**: `/Users/Matthew/Choco/choco-main/partitions`

## Dataset Partitions

The ChoCo dataset is organized into multiple partitions, each containing JAMS files from different sources.

### Major Partitions

1. **Real Book** - Jazz standards from The Real Book
2. **iReal Pro** - iReal Pro playlists
3. **Billboard** - Billboard chart songs
4. **Isophonics** - Pop/rock songs
5. **Weimar** - Weimar Jazz Database
6. **RWC-Pop** - RWC Popular Music Database
7. **Chordify** - Chordify annotations
8. **JAAH** - Jazz Audio-Aligned Harmony
9. **And more...**

## Check Partition Sizes

```bash
for dir in /Users/Matthew/Choco/choco-main/partitions/*/; do 
    name=$(basename "$dir")
    count=$(find "$dir" -name "*.jams" -type f 2>/dev/null | wc -l)
    echo "$name: $count files"
done | sort -t: -k2 -nr
```

## Processing Status

Check which partitions have been processed:

```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/python/examples

# See processing status by partition
for dir in /Users/Matthew/Choco/choco-main/partitions/*/; do
    name=$(basename "$dir")
    total=$(find "$dir" -name "*.jams" -type f 2>/dev/null | wc -l)
    processed=$(find ./choco_enhanced/json_intermediate -path "*$name*" -name "*.json" 2>/dev/null | wc -l)
    if [ "$total" -gt 0 ]; then
        percent=$((processed * 100 / total))
        echo "$name: $processed/$total ($percent%)"
    fi
done
```

## Process Specific Partition

To process just one partition:

```bash
python3 choco_enhancement_pipeline.py \
    --jams-dir /Users/Matthew/Choco/choco-main/partitions/isophonics \
    --output-dir ./choco_enhanced_isophonics
```

## Partition Characteristics

Different partitions have different characteristics:

- **Real Book**: High metadata coverage, jazz standards
- **iReal Pro**: Good chord annotations, various genres
- **Billboard**: Popular music, good metadata
- **Weimar**: Jazz database, may have unknown namespaces
- **Isophonics**: Pop/rock, good coverage

Each partition is processed independently and results are organized in the output directory.
