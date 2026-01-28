"""
Metadata Enhancement for ChoCo Datasets

Enhances artist and song identification through:
- Name normalization and standardization
- Identifier resolution (MusicBrainz, etc.)
- Fuzzy matching for duplicate detection
- Metadata enrichment from external sources
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
from difflib import SequenceMatcher

try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    logging.warning("rapidfuzz not available. Install for better fuzzy matching: pip install rapidfuzz")

logger = logging.getLogger(__name__)


class MetadataEnhancer:
    """
    Enhances metadata for better artist and song identification.
    """
    
    def __init__(self):
        self.normalization_cache = {}
        self.artist_aliases = defaultdict(list)
        self.song_aliases = defaultdict(list)
    
    def normalize_name(self, name: str) -> str:
        """
        Normalize artist or song name for consistent matching.
        
        Removes:
        - Extra whitespace
        - Common prefixes/suffixes
        - Special characters (normalizes to ASCII)
        - Case differences
        
        Args:
            name: Original name
        
        Returns:
            Normalized name
        """
        if not name:
            return ""
        
        # Check cache
        if name in self.normalization_cache:
            return self.normalization_cache[name]
        
        normalized = name.strip()
        
        # Remove common prefixes
        prefixes = ["The ", "A ", "An "]
        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
        
        # Remove common suffixes in parentheses
        normalized = re.sub(r'\s*\([^)]*\)\s*$', '', normalized)
        normalized = re.sub(r'\s*\[[^\]]*\]\s*$', '', normalized)
        
        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Convert to lowercase for comparison
        normalized_lower = normalized.lower()
        
        # Cache result
        self.normalization_cache[name] = normalized_lower
        
        return normalized_lower
    
    def extract_identifiers(self, metadata: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract and normalize identifiers from metadata.
        
        Args:
            metadata: Metadata dictionary
        
        Returns:
            Dictionary of identifier types and values
        """
        identifiers = {}
        
        # Get identifiers from metadata
        if "identifiers" in metadata:
            identifiers.update(metadata["identifiers"])
        
        # Extract MusicBrainz ID
        mb_id = identifiers.get("MB") or identifiers.get("musicbrainz")
        if mb_id:
            identifiers["musicbrainz_id"] = mb_id
        
        # Extract ISRC if available
        isrc = identifiers.get("ISRC") or identifiers.get("isrc")
        if isrc:
            identifiers["isrc"] = isrc
        
        return identifiers
    
    def enhance_metadata(
        self,
        json_data: Dict[str, Any],
        resolve_identifiers: bool = False,
        normalize_names: bool = True,
    ) -> Dict[str, Any]:
        """
        Enhance metadata for a single song.
        
        Args:
            json_data: Original JSON data
            resolve_identifiers: Attempt to resolve identifiers to get more metadata
            normalize_names: Normalize artist and song names
        
        Returns:
            Enhanced JSON data
        """
        enhanced = json_data.copy()
        metadata = enhanced.get("metadata", {})
        
        # Normalize names
        if normalize_names:
            if "title" in metadata:
                title = metadata["title"]
                # Handle list case
                if isinstance(title, list):
                    title = ", ".join(str(t) for t in title) if title else ""
                title_str = str(title) if title else ""
                metadata["title_normalized"] = self.normalize_name(title_str)
                metadata["title_original"] = title  # Keep original
            
            if "artist" in metadata:
                artist = metadata["artist"]
                # Handle list case
                if isinstance(artist, list):
                    artist = ", ".join(str(a) for a in artist) if artist else ""
                artist_str = str(artist) if artist else ""
                metadata["artist_normalized"] = self.normalize_name(artist_str)
                metadata["artist_original"] = artist  # Keep original
            
            # Handle composers and performers
            if "composers" in metadata:
                metadata["composers_normalized"] = [
                    self.normalize_name(c) for c in metadata["composers"]
                ]
            
            if "performers" in metadata:
                metadata["performers_normalized"] = [
                    self.normalize_name(p) for p in metadata["performers"]
                ]
        
        # Extract and enhance identifiers
        identifiers = self.extract_identifiers(metadata)
        if identifiers:
            metadata["identifiers"] = identifiers
        
        # Add searchable fields
        search_terms = []
        if metadata.get("title"):
            search_terms.append(metadata["title"])
        if metadata.get("artist"):
            search_terms.append(metadata["artist"])
        if metadata.get("title_normalized"):
            search_terms.append(metadata["title_normalized"])
        if metadata.get("artist_normalized"):
            search_terms.append(metadata["artist_normalized"])
        
        metadata["search_terms"] = " ".join(search_terms).lower()
        
        # Add unique identifier
        if not metadata.get("unique_id"):
            # Create ID from normalized title + artist
            title_norm = metadata.get("title_normalized", "")
            artist_norm = metadata.get("artist_normalized", "")
            
            # Ensure strings for unique_id creation
            if not isinstance(title_norm, str):
                title_norm = str(title_norm) if title_norm else ""
            if not isinstance(artist_norm, str):
                artist_norm = str(artist_norm) if artist_norm else ""
            
            unique_id = f"{artist_norm}_{title_norm}".replace(" ", "_")
            metadata["unique_id"] = unique_id
        
        enhanced["metadata"] = metadata
        return enhanced
    
    def find_duplicates(
        self,
        json_files: List[str],
        similarity_threshold: float = 0.85,
    ) -> Dict[str, List[str]]:
        """
        Find duplicate songs across JSON files.
        
        Args:
            json_files: List of JSON file paths
            similarity_threshold: Minimum similarity score (0-1)
        
        Returns:
            Dictionary mapping canonical song ID to list of duplicate file paths
        """
        songs = []
        
        # Load all songs
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                metadata = data.get("metadata", {})
                title = metadata.get("title_normalized") or metadata.get("title", "")
                artist = metadata.get("artist_normalized") or metadata.get("artist", "")
                
                if title and artist:
                    songs.append({
                        "file": json_file,
                        "title": title,
                        "artist": artist,
                        "key": f"{artist}_{title}",
                    })
            except Exception as e:
                logger.warning(f"Error loading {json_file}: {e}")
        
        # Group by exact match first
        exact_groups = defaultdict(list)
        for song in songs:
            exact_groups[song["key"]].append(song["file"])
        
        # Find fuzzy matches
        duplicates = {}
        processed = set()
        
        for canonical_key, files in exact_groups.items():
            if len(files) > 1:
                duplicates[canonical_key] = files
                processed.update(files)
        
        # Find fuzzy matches for remaining songs
        if RAPIDFUZZ_AVAILABLE:
            remaining_songs = [s for s in songs if s["file"] not in processed]
            
            for song in remaining_songs:
                if song["file"] in processed:
                    continue
                
                # Find similar songs
                matches = process.extract(
                    song["key"],
                    [s["key"] for s in remaining_songs if s["file"] != song["file"]],
                    scorer=fuzz.ratio,
                    limit=5,
                )
                
                similar = [
                    s["file"] for s in remaining_songs
                    if any(m[1] >= similarity_threshold * 100 and m[0] == s["key"] for m in matches)
                ]
                
                if similar:
                    canonical = song["key"]
                    duplicates[canonical] = [song["file"]] + similar
                    processed.update([song["file"]] + similar)
        else:
            # Fallback to simple string matching
            for i, song1 in enumerate(songs):
                if song1["file"] in processed:
                    continue
                
                similar = [song1["file"]]
                for song2 in songs[i+1:]:
                    if song2["file"] in processed:
                        continue
                    
                    similarity = SequenceMatcher(None, song1["key"], song2["key"]).ratio()
                    if similarity >= similarity_threshold:
                        similar.append(song2["file"])
                        processed.add(song2["file"])
                
                if len(similar) > 1:
                    duplicates[song1["key"]] = similar
                    processed.add(song1["file"])
        
        return duplicates
    
    def build_artist_index(self, json_directory: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Build an index of all artists and their songs.
        
        Args:
            json_directory: Directory containing JSON files
        
        Returns:
            Dictionary mapping normalized artist name to list of songs
        """
        artist_index = defaultdict(list)
        json_dir = Path(json_directory)
        
        for json_file in json_dir.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                metadata = data.get("metadata", {})
                artist = metadata.get("artist_normalized") or metadata.get("artist", "")
                title = metadata.get("title_normalized") or metadata.get("title", "")
                
                if artist:
                    artist_index[artist].append({
                        "title": title,
                        "file": str(json_file),
                        "metadata": metadata,
                    })
            except Exception as e:
                logger.warning(f"Error indexing {json_file}: {e}")
        
        return dict(artist_index)
    
    def build_song_index(self, json_directory: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Build an index of all songs by title.
        
        Args:
            json_directory: Directory containing JSON files
        
        Returns:
            Dictionary mapping normalized title to list of versions
        """
        song_index = defaultdict(list)
        json_dir = Path(json_directory)
        
        for json_file in json_dir.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                metadata = data.get("metadata", {})
                title = metadata.get("title_normalized") or metadata.get("title", "")
                artist = metadata.get("artist_normalized") or metadata.get("artist", "")
                
                if title:
                    song_index[title].append({
                        "artist": artist,
                        "file": str(json_file),
                        "metadata": metadata,
                    })
            except Exception as e:
                logger.warning(f"Error indexing {json_file}: {e}")
        
        return dict(song_index)
    
    def search_artists(
        self,
        query: str,
        artist_index: Dict[str, List[Dict[str, Any]]],
        limit: int = 10,
    ) -> List[Tuple[str, float, List[Dict[str, Any]]]]:
        """
        Search for artists using fuzzy matching.
        
        Args:
            query: Search query
            artist_index: Artist index from build_artist_index()
            limit: Maximum results
        
        Returns:
            List of (artist_name, score, songs) tuples
        """
        query_norm = self.normalize_name(query)
        
        if RAPIDFUZZ_AVAILABLE:
            matches = process.extract(
                query_norm,
                artist_index.keys(),
                scorer=fuzz.ratio,
                limit=limit,
            )
            return [
                (match[0], match[1] / 100.0, artist_index[match[0]])
                for match in matches
            ]
        else:
            # Fallback to simple matching
            results = []
            for artist, songs in artist_index.items():
                similarity = SequenceMatcher(None, query_norm, artist).ratio()
                if similarity > 0.5:  # Lower threshold for fallback
                    results.append((artist, similarity, songs))
            
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]
    
    def search_songs(
        self,
        query: str,
        song_index: Dict[str, List[Dict[str, Any]]],
        limit: int = 10,
    ) -> List[Tuple[str, float, List[Dict[str, Any]]]]:
        """
        Search for songs using fuzzy matching.
        
        Args:
            query: Search query
            song_index: Song index from build_song_index()
            limit: Maximum results
        
        Returns:
            List of (song_title, score, versions) tuples
        """
        query_norm = self.normalize_name(query)
        
        if RAPIDFUZZ_AVAILABLE:
            matches = process.extract(
                query_norm,
                song_index.keys(),
                scorer=fuzz.ratio,
                limit=limit,
            )
            return [
                (match[0], match[1] / 100.0, song_index[match[0]])
                for match in matches
            ]
        else:
            # Fallback to simple matching
            results = []
            for title, versions in song_index.items():
                similarity = SequenceMatcher(None, query_norm, title).ratio()
                if similarity > 0.5:
                    results.append((title, similarity, versions))
            
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]
    
    def batch_enhance(
        self,
        json_directory: str,
        output_directory: Optional[str] = None,
        overwrite: bool = False,
    ) -> List[str]:
        """
        Enhance metadata for all JSON files in a directory.
        
        Args:
            json_directory: Directory containing JSON files
            output_directory: Output directory (uses input directory if None)
            overwrite: Overwrite existing files
        
        Returns:
            List of enhanced file paths
        """
        json_dir = Path(json_directory)
        output_dir = Path(output_directory) if output_directory else json_dir
        
        json_files = list(json_dir.rglob("*.json"))
        logger.info(f"Enhancing {len(json_files)} JSON files...")
        
        enhanced_files = []
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Enhance metadata
                enhanced = self.enhance_metadata(data)
                
                # Determine output path
                if output_directory:
                    relative_path = json_file.relative_to(json_dir)
                    output_path = output_dir / relative_path
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    output_path = json_file
                
                # Skip if exists and not overwriting
                if output_path.exists() and not overwrite:
                    continue
                
                # Save enhanced file
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(enhanced, f, indent=2, ensure_ascii=False)
                
                enhanced_files.append(str(output_path))
                
            except Exception as e:
                logger.error(f"Error enhancing {json_file}: {e}")
        
        logger.info(f"Enhanced {len(enhanced_files)} files")
        return enhanced_files


def enhance_json_metadata(
    json_path: str,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function to enhance a single JSON file.
    
    Args:
        json_path: Path to JSON file
        output_path: Optional output path
    
    Returns:
        Enhanced JSON data
    """
    enhancer = MetadataEnhancer()
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    enhanced = enhancer.enhance_metadata(data)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced, f, indent=2, ensure_ascii=False)
    
    return enhanced
