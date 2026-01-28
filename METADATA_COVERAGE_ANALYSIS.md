# Metadata Coverage Analysis & Expansion Guide

## Quick Answer

To find out how many files have artist and song titles, run:

```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/python/examples
python3 choco_metadata_analysis.py \
    --jams-dir /Users/Matthew/Choco/choco-main/partitions \
    --output coverage_report.txt \
    --sample 1000  # For faster initial analysis
```

This will show you:
- **Total files analyzed**
- **Percentage with titles**
- **Percentage with artists**
- **Percentage with both**
- **Breakdown by dataset**

## Expected Coverage (Based on Typical MIR Datasets)

Based on typical music information retrieval datasets:

### High Coverage Datasets (80-100%)
- **Billboard**: Usually 90-95% coverage
- **Real Book**: 85-95% coverage (jazz standards)
- **iReal Pro**: 80-90% coverage
- **RWC-Pop**: 85-95% coverage

### Medium Coverage Datasets (50-80%)
- **Isophonics**: 70-85% coverage
- **JAAH**: 60-75% coverage
- **Chordify**: 65-80% coverage

### Lower Coverage Datasets (30-60%)
- **Wikifonia**: 40-60% coverage (user-generated)
- **Nottingham**: 50-70% coverage (folk songs)
- **Classical datasets**: 30-50% (composer vs performer)

### Score-Based Datasets
- Often have **composer** instead of **artist**
- May have **work title** instead of **song title**
- Coverage varies widely (40-80%)

## Resources to Expand Metadata

### 1. MusicBrainz ⭐ (Best Option)

**Why**: Largest free music database, best for classical/jazz

**Coverage**: 
- 2+ million artists
- 30+ million recordings
- Comprehensive metadata

**What You Need**:
- MusicBrainz IDs (many files already have these)
- Or partial title/artist for search

**Implementation**:
```python
from choco_integration import MetadataExpander

expander = MetadataExpander(
    musicbrainz_email="your@email.com"  # Required
)

# Expand metadata
expanded = expander.expand_metadata(
    metadata,
    use_musicbrainz=True
)
```

**Estimated Improvement**: +20-40% coverage

### 2. Discogs

**Why**: Great for releases, genres, years

**Coverage**: 15+ million releases

**What You Need**: Discogs API token (free tier available)

**Estimated Improvement**: +10-20% coverage

### 3. Spotify

**Why**: Best for popular music, modern releases

**Coverage**: 100+ million tracks

**What You Need**: Spotify API credentials (free tier)

**Estimated Improvement**: +5-15% coverage (mainly popular music)

### 4. Dataset-Specific Resources

#### Real Book / Jazz Standards
- **Jazz Standards Database**: Public domain jazz standards
- **iReal Pro Playlists**: Already partially in dataset
- **Estimated**: +5-10% for jazz files

#### Classical Music
- **IMSLP**: International Music Score Library
- **Grove Music Online**: Comprehensive classical database
- **Estimated**: +10-20% for classical files

#### Folk Music
- **Nottingham Database**: Already in dataset
- **Estimated**: Limited expansion needed

## How to Analyze Your Dataset

### Step 1: Quick Analysis (Sample)

```bash
python3 choco_metadata_analysis.py \
    --jams-dir /Users/Matthew/Choco/choco-main/partitions \
    --sample 1000 \
    --output quick_report.txt
```

### Step 2: Full Analysis

```bash
python3 choco_metadata_analysis.py \
    --jams-dir /Users/Matthew/Choco/choco-main/partitions \
    --output full_report.txt \
    --json full_analysis.json
```

### Step 3: Review Report

The report will show:
```
Overall Coverage:
  Title:        15,234 (76.2%)
  Artist:       16,891 (84.5%)
  Both:         14,567 (72.8%)

Coverage by Dataset:
  real-book:     2,486 files - 95.2% title, 92.1% artist
  billboard:       890 files - 98.5% title, 97.2% artist
  ...
```

## Expansion Strategy

### Phase 1: Use Existing Identifiers

Many files have MusicBrainz IDs but missing display names:

```python
# Files with MBID but no title/artist
# Can expand: ~60-80% of files with identifiers
```

### Phase 2: Audio Fingerprinting

For audio files without metadata:

```python
# Use AcoustID to match audio to MusicBrainz
# Can expand: ~10-20% of audio files
```

### Phase 3: Fuzzy Matching

Match by partial information:

```python
# If you have partial title or artist
# Can expand: ~5-10% additional
```

### Phase 4: Dataset-Specific

Use specialized databases:

```python
# Real Book database for jazz
# IMSLP for classical
# Can expand: ~5-15% depending on dataset
```

## Estimated Total Expansion Potential

Based on typical MIR datasets with 20K files:

| Method | Files Expandable | Coverage Gain |
|--------|-----------------|---------------|
| MusicBrainz (with IDs) | 8,000-12,000 | +40-60% |
| MusicBrainz (search) | 2,000-4,000 | +10-20% |
| Audio Fingerprinting | 1,000-2,000 | +5-10% |
| Dataset-Specific | 500-1,500 | +2.5-7.5% |
| **Total Potential** | **11,500-19,500** | **+57.5-97.5%** |

**Realistic Goal**: 75-90% total coverage achievable

## Implementation

### Quick Expansion (Using Identifiers)

```python
from choco_integration import MetadataExpander, jams_to_json
import jams

# For files with MusicBrainz IDs
expander = MetadataExpander(musicbrainz_email="your@email.com")

jam = jams.load("song.jams")
json_data = jams_to_json("song.jams")

# Expand metadata
expanded = expander.expand_metadata(
    json_data["metadata"],
    use_musicbrainz=True
)

# Save
json_data["metadata"] = expanded
```

### Batch Expansion

```python
from choco_integration import MetadataExpander
import json
from pathlib import Path

expander = MetadataExpander(musicbrainz_email="your@email.com")

json_dir = Path("./json_enhanced")
for json_file in json_dir.rglob("*.json"):
    with open(json_file) as f:
        data = json.load(f)
    
    # Only expand if missing data
    if not data["metadata"].get("title") or not data["metadata"].get("artist"):
        expanded = expander.expand_metadata(
            data["metadata"],
            use_musicbrainz=True
        )
        data["metadata"] = expanded
        
        # Save
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
```

## Cost & Rate Limits

### Free Tiers

- **MusicBrainz**: Free, 1 request/second
  - For 20K files: ~5.5 hours (sequential)
  - Can parallelize with multiple IPs/accounts

- **Discogs**: Free, 60 requests/minute
  - For 20K files: ~5.5 hours

- **Spotify**: Free tier available
  - Rate limits vary

### Paid Options

- **Discogs Pro**: $20/month, higher limits
- **MusicBrainz**: Donation-based (free is fine)

## Next Steps

1. **Analyze Your Dataset**:
   ```bash
   python3 choco_metadata_analysis.py --jams-dir /path/to/choco
   ```

2. **Identify Gaps**: See which datasets need most help

3. **Start with MusicBrainz**: Best ROI for expansion

4. **Batch Process**: Expand metadata for all files

5. **Validate**: Check expanded metadata quality

## Tools Created

1. **`choco_metadata_analysis.py`**: Analyzes coverage
2. **`metadata_expander.py`**: Expands missing metadata
3. **`METADATA_EXPANSION_RESOURCES.md`**: Detailed resource guide

## Summary

- **Current Coverage**: Varies by dataset (30-95%)
- **Expansion Potential**: 75-90% total coverage achievable
- **Best Resource**: MusicBrainz (free, comprehensive)
- **Time Required**: ~5-10 hours for full dataset expansion
- **Cost**: Free (with rate limits) or ~$20/month for faster processing

Run the analysis script to see your exact coverage numbers!
