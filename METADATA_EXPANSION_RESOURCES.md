# Metadata Expansion Resources for ChoCo Dataset

## Overview

This document identifies resources and methods to expand metadata coverage in the ChoCo dataset, particularly for missing artist and song title information.

## Current Coverage Analysis

First, analyze your dataset to see what's missing:

```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/python/examples
python3 choco_metadata_analysis.py \
    --jams-dir /Users/Matthew/Choco/choco-main/partitions \
    --output metadata_report.txt
```

## Resources for Metadata Expansion

### 1. MusicBrainz (Primary Resource) ⭐

**Best for**: Artist names, song titles, release information, identifiers

**Coverage**: 
- 2+ million artists
- 30+ million recordings
- Comprehensive metadata

**API**: 
- REST API: `https://musicbrainz.org/ws/2/`
- Rate limit: 1 request/second (free)
- Python library: `musicbrainzngs`

**What it provides**:
- Artist names (with aliases)
- Song titles (with alternative titles)
- Release information
- ISRC codes
- Relationships between artists
- Genre tags

**Usage Example**:
```python
import musicbrainzngs

musicbrainzngs.set_useragent("ChoCo-Enhancer", "1.0", "your@email.com")

# Search by ISRC or recording ID
result = musicbrainzngs.get_recording_by_id("recording_id")
# Returns: artist, title, release, etc.
```

**Limitations**:
- Requires identifiers (MBID, ISRC) for best results
- Rate limited
- Some entries may be incomplete

### 2. Discogs API

**Best for**: Release information, artist names, genres, years

**Coverage**:
- 15+ million releases
- Comprehensive artist database
- Genre classifications

**API**:
- REST API: `https://api.discogs.com/`
- Rate limit: 60 requests/minute (free tier)
- Requires OAuth for some endpoints

**What it provides**:
- Artist names and aliases
- Release titles and years
- Track listings
- Genre and style tags
- Label information

**Usage**:
```python
import discogs_client

client = discogs_client.Client('ChoCo-Enhancer/1.0', user_token='your_token')
results = client.search('artist', type='artist')
```

### 3. Spotify Web API

**Best for**: Popular songs, modern releases, popularity metrics

**Coverage**:
- 100+ million tracks
- Good for popular music
- Less comprehensive for classical/jazz

**API**:
- REST API: `https://api.spotify.com/v1/`
- Requires OAuth authentication
- Rate limit: Varies by endpoint

**What it provides**:
- Artist names
- Track titles
- Album information
- Popularity scores
- Audio features

**Usage**:
```python
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
results = sp.search(q='artist:coltrane track:giant steps', type='track')
```

### 4. Last.fm API

**Best for**: Tags, similar artists, user-generated metadata

**Coverage**:
- Large user-generated database
- Tags and genres
- Similarity data

**API**:
- REST API: `http://ws.audioscrobbler.com/2.0/`
- Rate limit: None (but be respectful)
- Requires API key

**What it provides**:
- Artist names
- Track titles
- Tags and genres
- Similar artists
- User play counts

### 5. AcousticBrainz

**Best for**: Audio features, but limited metadata

**Coverage**:
- Audio analysis data
- Limited to MusicBrainz-linked recordings

**API**:
- REST API: `https://acousticbrainz.org/api/v1/`
- No rate limit specified

### 6. Wikipedia/Wikidata

**Best for**: Historical information, composer data, classical music

**Coverage**:
- Comprehensive for notable works
- Good for classical compositions
- Structured data via Wikidata

**API**:
- Wikipedia API: `https://en.wikipedia.org/api/rest_v1/`
- Wikidata SPARQL: `https://query.wikidata.org/sparql`

**What it provides**:
- Composer information
- Work titles
- Historical context
- Relationships

### 7. AllMusic

**Best for**: Genre classifications, reviews (scraping required)

**Coverage**:
- Comprehensive genre database
- Artist biographies
- Album reviews

**Note**: No official API, would require web scraping (check ToS)

### 8. The Real Book / iReal Pro Data

**Best for**: Jazz standards (already in ChoCo)

**Coverage**:
- Jazz standard titles
- Composer information
- Already partially in dataset

## Implementation Strategy

### Phase 1: Use Existing Identifiers

Many files may have identifiers but missing display names:

```python
# If file has MusicBrainz ID but missing title/artist
mbid = jam.file_metadata.identifiers.get("MB")
if mbid:
    # Lookup via MusicBrainz API
    recording = musicbrainzngs.get_recording_by_id(mbid)
    # Fill in missing metadata
```

### Phase 2: Match by Audio Features

For files with audio but missing metadata:

```python
# Use audio fingerprinting (e.g., AcoustID)
import acoustid

# Match audio to MusicBrainz
fingerprint = acoustid.fingerprint_file("audio.wav")
results = acoustid.lookup(api_key, fingerprint)
# Returns MusicBrainz recording IDs
```

### Phase 3: Fuzzy Matching

Match by partial information:

```python
# If you have partial title or artist
from choco_integration import MetadataEnhancer

enhancer = MetadataEnhancer()
normalized = enhancer.normalize_name(partial_name)

# Search MusicBrainz
results = musicbrainzngs.search_recordings(
    recording=normalized,
    limit=10
)
# Match by similarity
```

### Phase 4: Dataset-Specific Lookups

Different datasets may have different metadata sources:

- **Real Book**: Use Real Book database
- **iReal Pro**: Use iReal Pro playlist data
- **Billboard**: Use Billboard charts database
- **Classical**: Use IMSLP, Grove Music Online

## Recommended Tools

### Python Libraries

```bash
pip install musicbrainzngs discogs-client spotipy lastfm-python
```

### Tools Created

1. **Metadata Enhancer** (`metadata_enhancer.py`)
   - Normalizes names
   - Creates unique IDs
   - Already implemented

2. **Metadata Expander** (to be created)
   - Fetches missing metadata from APIs
   - Matches by identifiers
   - Fuzzy matching fallback

## Implementation Plan

### Step 1: Analyze Coverage

```bash
python3 choco_metadata_analysis.py \
    --jams-dir /path/to/choco \
    --output coverage_report.txt \
    --json coverage_data.json
```

### Step 2: Prioritize by Dataset

Focus on datasets with:
- High identifier coverage (easier to expand)
- Large number of missing titles/artists
- Most useful for your use case

### Step 3: Implement Expander

Create `metadata_expander.py` that:
1. Reads JAMS files
2. Checks for identifiers
3. Queries MusicBrainz/Discogs APIs
4. Fills in missing metadata
5. Saves enhanced files

### Step 4: Batch Process

```python
from choco_integration import MetadataExpander

expander = MetadataExpander()
expander.expand_metadata(
    jams_directory="/path/to/choco",
    output_directory="/path/to/enhanced",
    use_musicbrainz=True,
    use_discogs=True,
)
```

## Estimated Coverage Improvement

Based on typical MIR datasets:

- **With Identifiers**: 60-80% can be expanded
- **With Audio Fingerprinting**: +10-20%
- **With Fuzzy Matching**: +5-10%
- **Total Potential**: 75-90% coverage achievable

## Cost Considerations

### Free Tiers

- **MusicBrainz**: Free, 1 req/sec
- **Discogs**: Free, 60 req/min
- **Last.fm**: Free with API key
- **Wikipedia**: Free, no limits

### Paid Options

- **Spotify**: Free tier available
- **Discogs Pro**: $20/month for higher limits
- **MusicBrainz**: Donation-based

## Next Steps

1. **Run Analysis**: Determine current coverage
2. **Identify Gaps**: See which datasets need most help
3. **Implement Expander**: Create metadata expansion tool
4. **Batch Process**: Expand metadata for all files
5. **Validate**: Verify expanded metadata quality

## Example: Quick Expansion

```python
# For files with MusicBrainz IDs
import musicbrainzngs
import jams

jam = jams.load("song.jams")
mbid = jam.file_metadata.identifiers.get("MB")

if mbid and not jam.file_metadata.title:
    recording = musicbrainzngs.get_recording_by_id(mbid)
    jam.file_metadata.title = recording["title"]
    jam.file_metadata.artist = recording["artist-credit"][0]["name"]
    jam.save("song_enhanced.jams")
```

## Conclusion

With the right tools and APIs, you can significantly expand metadata coverage:
- **MusicBrainz** is the best starting point
- **Identifiers** make expansion much easier
- **Fuzzy matching** can help with partial data
- **Batch processing** makes it scalable

The analysis script will show you exactly what's missing and help prioritize expansion efforts.
