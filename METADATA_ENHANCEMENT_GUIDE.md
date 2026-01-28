# Metadata Enhancement Guide for ChoCo Datasets

## Overview

This guide addresses metadata enhancement needs for better artist and song identification in the ChoCo MIR datasets. The current JAMS files contain basic metadata, but several enhancements can significantly improve searchability and identification.

## Current Metadata Status

### What's Available

Based on the JAMS file structure, the following metadata is typically available:

1. **Basic Fields**:
   - `title`: Song title
   - `artist`: Artist name
   - `release`: Album/release name
   - `duration`: Track duration

2. **Sandbox Metadata**:
   - `genre`: Musical genre
   - `dataset`: Source dataset name
   - `type`: "audio" or "score"
   - `composers`: List of composers
   - `performers`: List of performers
   - `release_year`: Year of release
   - `track_number`: Track number in release

3. **Identifiers**:
   - MusicBrainz ID (MB)
   - ISRC codes
   - Other dataset-specific identifiers

### Common Issues

1. **Inconsistent Naming**:
   - "The Beatles" vs "Beatles"
   - "John Coltrane" vs "Coltrane, John"
   - Variations in punctuation and spacing

2. **Missing Metadata**:
   - Some files lack artist information
   - Titles may be incomplete or abbreviated
   - Missing identifiers for external lookup

3. **Duplicate Detection**:
   - Same song appears in multiple datasets
   - Different versions of same song
   - No canonical identification

## Enhancement Solutions

### 1. Name Normalization

**Problem**: Artist and song names vary across datasets.

**Solution**: Implement normalization that:
- Removes common prefixes ("The", "A", "An")
- Strips parenthetical information
- Normalizes whitespace
- Converts to lowercase for comparison
- Preserves original names

**Implementation**:
```python
from choco_integration import MetadataEnhancer

enhancer = MetadataEnhancer()
enhanced = enhancer.enhance_metadata(json_data)
```

**Result**:
```json
{
  "metadata": {
    "title": "Autumn Leaves",
    "title_normalized": "autumn leaves",
    "artist": "The Bill Evans Trio",
    "artist_normalized": "bill evans trio",
    "search_terms": "autumn leaves the bill evans trio autumn leaves bill evans trio"
  }
}
```

### 2. Identifier Resolution

**Problem**: Identifiers exist but aren't always used to enrich metadata.

**Solution**: Extract and normalize identifiers, with optional resolution:
- MusicBrainz IDs for artist/track lookup
- ISRC codes for release identification
- Dataset-specific identifiers

**Implementation**:
```python
enhanced = enhancer.enhance_metadata(
    json_data,
    resolve_identifiers=True  # Future: resolve via APIs
)
```

### 3. Duplicate Detection

**Problem**: Same songs appear multiple times with slight variations.

**Solution**: Fuzzy matching to identify duplicates:
- Compare normalized titles and artists
- Use similarity scoring (85%+ threshold)
- Group duplicates for canonical selection

**Implementation**:
```python
duplicates = enhancer.find_duplicates(
    json_files,
    similarity_threshold=0.85
)

# Result: {
#   "bill_evans_trio_autumn_leaves": [
#     "file1.json",
#     "file2.json",
#     "file3.json"
#   ]
# }
```

### 4. Search Indexes

**Problem**: Searching large datasets is slow.

**Solution**: Build searchable indexes:
- Artist index: all songs by each artist
- Song index: all versions of each song
- Fuzzy search support

**Implementation**:
```python
# Build indexes
artist_index = enhancer.build_artist_index("./json_output")
song_index = enhancer.build_song_index("./json_output")

# Search
results = enhancer.search_artists("coltrane", artist_index, limit=10)
# Returns: [("john coltrane", 0.95, [songs...]), ...]
```

### 5. Unique Identifiers

**Problem**: No reliable way to uniquely identify songs.

**Solution**: Generate unique IDs from normalized metadata:
- Format: `{artist_normalized}_{title_normalized}`
- Consistent across duplicates
- Enables deduplication

**Implementation**:
```python
# Automatically added during enhancement
{
  "metadata": {
    "unique_id": "bill_evans_trio_autumn_leaves"
  }
}
```

## Usage Workflow

### Step 1: Convert JAMS to JSON

```python
from choco_integration import batch_convert_jams_to_json

batch_convert_jams_to_json(
    "/path/to/choco/jams",
    "./json_output"
)
```

### Step 2: Enhance Metadata

```python
from choco_integration import MetadataEnhancer

enhancer = MetadataEnhancer()

# Enhance all files
enhanced_files = enhancer.batch_enhance(
    "./json_output",
    "./json_enhanced",
    overwrite=False
)
```

### Step 3: Build Search Indexes

```python
# Build indexes for fast searching
artist_index = enhancer.build_artist_index("./json_enhanced")
song_index = enhancer.build_song_index("./json_enhanced")

# Save indexes
import json
with open("artist_index.json", "w") as f:
    json.dump(artist_index, f, indent=2)
```

### Step 4: Find and Handle Duplicates

```python
import glob

json_files = glob.glob("./json_enhanced/**/*.json", recursive=True)
duplicates = enhancer.find_duplicates(json_files)

# Review duplicates
for canonical_id, files in duplicates.items():
    if len(files) > 1:
        print(f"{canonical_id}: {len(files)} versions")
        for f in files:
            print(f"  - {f}")
```

### Step 5: Search and Use

```python
# Search for artist
results = enhancer.search_artists("miles davis", artist_index)
for artist, score, songs in results:
    print(f"{artist} ({score:.2%} match): {len(songs)} songs")

# Search for song
results = enhancer.search_songs("autumn leaves", song_index)
for title, score, versions in results:
    print(f"{title} ({score:.2%} match): {len(versions)} versions")
```

## Advanced Enhancements

### 1. External API Integration

**Future Enhancement**: Resolve identifiers via APIs:
- MusicBrainz API for artist/track metadata
- Spotify API for popularity metrics
- Last.fm API for tags and similar artists

```python
# Future implementation
enhanced = enhancer.enhance_metadata(
    json_data,
    resolve_identifiers=True,
    use_musicbrainz=True,
    use_spotify=True
)
```

### 2. Genre Standardization

**Enhancement**: Normalize genre names across datasets:
- "Jazz" vs "jazz" vs "JAZZ"
- "Pop" vs "Popular" vs "Pop/Rock"
- Create genre taxonomy

### 3. Artist Alias Resolution

**Enhancement**: Handle artist aliases and variations:
- "Miles Davis" = "Miles Dewey Davis III"
- "The Beatles" = "Beatles"
- Group related artists

### 4. Year Normalization

**Enhancement**: Extract and normalize release years:
- Handle various formats
- Validate year ranges
- Fill missing years from identifiers

## Recommended Enhancements for Your Workflow

### Immediate (High Priority)

1. **Normalize Names**: Run `batch_enhance()` on all JSON files
2. **Build Indexes**: Create artist and song indexes for fast searching
3. **Find Duplicates**: Identify duplicate songs for deduplication

### Short-term (Medium Priority)

1. **Identifier Extraction**: Extract all available identifiers
2. **Search Functionality**: Implement fuzzy search for artists/songs
3. **Unique IDs**: Generate consistent unique identifiers

### Long-term (Low Priority)

1. **API Integration**: Resolve identifiers via external APIs
2. **Genre Taxonomy**: Standardize genre classifications
3. **Artist Aliases**: Build alias database

## Example: Complete Enhancement Pipeline

```python
from choco_integration import (
    batch_convert_jams_to_json,
    MetadataEnhancer
)
import json

# 1. Convert JAMS to JSON
print("Converting JAMS to JSON...")
batch_convert_jams_to_json(
    "/Users/Matthew/Choco/choco-main/partitions",
    "./json_output"
)

# 2. Enhance metadata
print("Enhancing metadata...")
enhancer = MetadataEnhancer()
enhanced_files = enhancer.batch_enhance(
    "./json_output",
    "./json_enhanced"
)

# 3. Build indexes
print("Building search indexes...")
artist_index = enhancer.build_artist_index("./json_enhanced")
song_index = enhancer.build_song_index("./json_enhanced")

# Save indexes
with open("artist_index.json", "w") as f:
    json.dump(artist_index, f, indent=2)

with open("song_index.json", "w") as f:
    json.dump(song_index, f, indent=2)

# 4. Find duplicates
print("Finding duplicates...")
import glob
json_files = glob.glob("./json_enhanced/**/*.json", recursive=True)
duplicates = enhancer.find_duplicates(json_files)

# Save duplicate report
with open("duplicates.json", "w") as f:
    json.dump(duplicates, f, indent=2)

print(f"Enhancement complete!")
print(f"  - Enhanced files: {len(enhanced_files)}")
print(f"  - Unique artists: {len(artist_index)}")
print(f"  - Unique songs: {len(song_index)}")
print(f"  - Duplicate groups: {len(duplicates)}")
```

## Benefits

1. **Better Search**: Normalized names enable accurate searching
2. **Duplicate Management**: Identify and handle duplicate songs
3. **Consistent IDs**: Unique identifiers for reliable referencing
4. **Fast Lookups**: Indexed data for quick access
5. **Future-Proof**: Extensible for API integration

## Dependencies

```bash
# Required
pip install jams

# Optional (for better fuzzy matching)
pip install rapidfuzz
```

## Conclusion

Metadata enhancement significantly improves the usability of ChoCo datasets for:
- Searching and filtering songs
- Identifying duplicates
- Building artist/song catalogs
- Integration with external services
- Better organization in Ableton Live

The enhancement process is designed to be:
- **Non-destructive**: Preserves original metadata
- **Incremental**: Can be run multiple times
- **Extensible**: Easy to add new enhancements
- **Fast**: Efficient for large datasets
