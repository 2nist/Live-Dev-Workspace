"""
Metadata Expander for ChoCo Datasets

Expands missing metadata by querying external APIs:
- MusicBrainz (primary)
- Discogs (secondary)
- Spotify (for popular music)
"""

import logging
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import API clients
try:
    import musicbrainzngs
    MUSICBRAINZ_AVAILABLE = True
except ImportError:
    MUSICBRAINZ_AVAILABLE = False
    logger.warning("musicbrainzngs not available. Install with: pip install musicbrainzngs")

try:
    import discogs_client
    DISCOGS_AVAILABLE = True
except ImportError:
    DISCOGS_AVAILABLE = False
    logger.warning("discogs_client not available. Install with: pip install discogs-client")

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    SPOTIFY_AVAILABLE = True
except ImportError:
    SPOTIFY_AVAILABLE = False
    logger.warning("spotipy not available. Install with: pip install spotipy")


class MetadataExpander:
    """
    Expands missing metadata by querying external APIs.
    """
    
    def __init__(
        self,
        musicbrainz_useragent: str = "ChoCo-Expander/1.0",
        musicbrainz_email: str = "",
        discogs_token: Optional[str] = None,
        spotify_client_id: Optional[str] = None,
        spotify_client_secret: Optional[str] = None,
        rate_limit_delay: float = 1.0,
    ):
        """
        Initialize metadata expander.
        
        Args:
            musicbrainz_useragent: User agent for MusicBrainz API
            musicbrainz_email: Email for MusicBrainz API (required)
            discogs_token: Discogs API token (optional)
            spotify_client_id: Spotify client ID (optional)
            spotify_client_secret: Spotify client secret (optional)
            rate_limit_delay: Delay between API requests (seconds)
        """
        self.rate_limit_delay = rate_limit_delay
        self.stats = {
            "musicbrainz_queries": 0,
            "discogs_queries": 0,
            "spotify_queries": 0,
            "successful_expansions": 0,
            "failed_expansions": 0,
        }
        
        # Initialize MusicBrainz
        if MUSICBRAINZ_AVAILABLE:
            musicbrainzngs.set_useragent(musicbrainz_useragent, "1.0", musicbrainz_email)
            self.musicbrainz = musicbrainzngs
        else:
            self.musicbrainz = None
        
        # Initialize Discogs
        if DISCOGS_AVAILABLE and discogs_token:
            self.discogs = discogs_client.Client("ChoCo-Expander/1.0", user_token=discogs_token)
        else:
            self.discogs = None
        
        # Initialize Spotify
        if SPOTIFY_AVAILABLE and spotify_client_id and spotify_client_secret:
            client_credentials = SpotifyClientCredentials(
                client_id=spotify_client_id,
                client_secret=spotify_client_secret
            )
            self.spotify = spotipy.Spotify(client_credentials_manager=client_credentials)
        else:
            self.spotify = None
    
    def _rate_limit(self):
        """Apply rate limiting."""
        time.sleep(self.rate_limit_delay)
    
    def expand_from_musicbrainz(
        self,
        metadata: Dict[str, Any],
        mbid: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Expand metadata using MusicBrainz API.
        
        Args:
            metadata: Current metadata dictionary
            mbid: MusicBrainz recording ID (if available)
        
        Returns:
            Updated metadata dictionary
        """
        if not self.musicbrainz:
            return metadata
        
        expanded = metadata.copy()
        
        try:
            # Get MBID from identifiers if not provided
            if not mbid:
                identifiers = metadata.get("identifiers", {})
                mbid = identifiers.get("MB") or identifiers.get("musicbrainz")
            
            if mbid:
                self._rate_limit()
                self.stats["musicbrainz_queries"] += 1
                
                try:
                    recording = self.musicbrainz.get_recording_by_id(
                        mbid,
                        includes=["artists", "releases"]
                    )
                    
                    # Fill in missing title
                    if not expanded.get("title") and recording.get("title"):
                        expanded["title"] = recording["title"]
                    
                    # Fill in missing artist
                    if not expanded.get("artist") and recording.get("artist-credit"):
                        artist_credit = recording["artist-credit"]
                        if isinstance(artist_credit, list) and len(artist_credit) > 0:
                            expanded["artist"] = artist_credit[0].get("name", "")
                        elif isinstance(artist_credit, dict):
                            expanded["artist"] = artist_credit.get("name", "")
                    
                    # Fill in release if available
                    if not expanded.get("release") and recording.get("releases"):
                        releases = recording["releases"]
                        if releases and len(releases) > 0:
                            expanded["release"] = releases[0].get("title", "")
                    
                    self.stats["successful_expansions"] += 1
                    
                except Exception as e:
                    logger.warning(f"MusicBrainz lookup failed for {mbid}: {e}")
                    self.stats["failed_expansions"] += 1
            
            # Try search if no MBID but have partial info
            elif expanded.get("title") or expanded.get("artist"):
                self._rate_limit()
                self.stats["musicbrainz_queries"] += 1
                
                try:
                    query = ""
                    if expanded.get("title"):
                        query = f'recording:"{expanded["title"]}"'
                    if expanded.get("artist"):
                        if query:
                            query += f' AND artist:"{expanded["artist"]}"'
                        else:
                            query = f'artist:"{expanded["artist"]}"'
                    
                    if query:
                        results = self.musicbrainz.search_recordings(query, limit=1)
                        
                        if results.get("recording-list") and len(results["recording-list"]) > 0:
                            recording = results["recording-list"][0]
                            
                            # Fill missing fields
                            if not expanded.get("title") and recording.get("title"):
                                expanded["title"] = recording["title"]
                            
                            if not expanded.get("artist"):
                                artist_credit = recording.get("artist-credit", {})
                                if isinstance(artist_credit, list) and len(artist_credit) > 0:
                                    expanded["artist"] = artist_credit[0].get("name", "")
                            
                            # Add MBID to identifiers
                            if recording.get("id"):
                                if "identifiers" not in expanded:
                                    expanded["identifiers"] = {}
                                expanded["identifiers"]["MB"] = recording["id"]
                            
                            self.stats["successful_expansions"] += 1
                
                except Exception as e:
                    logger.warning(f"MusicBrainz search failed: {e}")
                    self.stats["failed_expansions"] += 1
        
        except Exception as e:
            logger.error(f"Error in MusicBrainz expansion: {e}")
        
        return expanded
    
    def expand_from_discogs(
        self,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Expand metadata using Discogs API.
        
        Args:
            metadata: Current metadata dictionary
        
        Returns:
            Updated metadata dictionary
        """
        if not self.discogs:
            return metadata
        
        expanded = metadata.copy()
        
        try:
            # Search by artist and title if available
            search_query = ""
            if expanded.get("artist"):
                search_query = expanded["artist"]
            if expanded.get("title"):
                if search_query:
                    search_query += f" {expanded['title']}"
                else:
                    search_query = expanded["title"]
            
            if search_query:
                self._rate_limit()
                self.stats["discogs_queries"] += 1
                
                try:
                    results = self.discogs.search(search_query, type='release')
                    
                    if results and len(results) > 0:
                        release = results[0]
                        
                        # Fill in missing release info
                        if not expanded.get("release") and release.title:
                            expanded["release"] = release.title
                        
                        # Fill in missing artist
                        if not expanded.get("artist") and release.artists:
                            expanded["artist"] = release.artists[0].name
                        
                        # Fill in genre
                        if not expanded.get("genre") and release.genres:
                            expanded["genre"] = ", ".join(release.genres)
                        
                        self.stats["successful_expansions"] += 1
                
                except Exception as e:
                    logger.warning(f"Discogs search failed: {e}")
                    self.stats["failed_expansions"] += 1
        
        except Exception as e:
            logger.error(f"Error in Discogs expansion: {e}")
        
        return expanded
    
    def expand_from_spotify(
        self,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Expand metadata using Spotify API.
        
        Args:
            metadata: Current metadata dictionary
        
        Returns:
            Updated metadata dictionary
        """
        if not self.spotify:
            return metadata
        
        expanded = metadata.copy()
        
        try:
            # Build search query
            query_parts = []
            if expanded.get("artist"):
                query_parts.append(f'artist:"{expanded["artist"]}"')
            if expanded.get("title"):
                query_parts.append(f'track:"{expanded["title"]}"')
            
            if query_parts:
                query = " ".join(query_parts)
                self._rate_limit()
                self.stats["spotify_queries"] += 1
                
                try:
                    results = self.spotify.search(q=query, type='track', limit=1)
                    
                    if results.get("tracks", {}).get("items"):
                        track = results["tracks"]["items"][0]
                        
                        # Fill in missing title
                        if not expanded.get("title") and track.get("name"):
                            expanded["title"] = track["name"]
                        
                        # Fill in missing artist
                        if not expanded.get("artist") and track.get("artists"):
                            expanded["artist"] = track["artists"][0]["name"]
                        
                        # Fill in album/release
                        if not expanded.get("release") and track.get("album", {}).get("name"):
                            expanded["release"] = track["album"]["name"]
                        
                        self.stats["successful_expansions"] += 1
                
                except Exception as e:
                    logger.warning(f"Spotify search failed: {e}")
                    self.stats["failed_expansions"] += 1
        
        except Exception as e:
            logger.error(f"Error in Spotify expansion: {e}")
        
        return expanded
    
    def expand_metadata(
        self,
        metadata: Dict[str, Any],
        use_musicbrainz: bool = True,
        use_discogs: bool = False,
        use_spotify: bool = False,
        priority_order: List[str] = ["musicbrainz", "discogs", "spotify"],
    ) -> Dict[str, Any]:
        """
        Expand metadata using available APIs in priority order.
        
        Args:
            metadata: Current metadata dictionary
            use_musicbrainz: Use MusicBrainz API
            use_discogs: Use Discogs API
            use_spotify: Use Spotify API
            priority_order: Order to try APIs
        
        Returns:
            Expanded metadata dictionary
        """
        expanded = metadata.copy()
        
        # Check what's missing
        needs_title = not expanded.get("title")
        needs_artist = not expanded.get("artist")
        
        if not (needs_title or needs_artist):
            # Nothing to expand
            return expanded
        
        # Try APIs in priority order
        for api in priority_order:
            if api == "musicbrainz" and use_musicbrainz:
                expanded = self.expand_from_musicbrainz(expanded)
                # Stop if we got what we need
                if not (needs_title and not expanded.get("title") or 
                        needs_artist and not expanded.get("artist")):
                    break
            
            elif api == "discogs" and use_discogs:
                expanded = self.expand_from_discogs(expanded)
                if not (needs_title and not expanded.get("title") or 
                        needs_artist and not expanded.get("artist")):
                    break
            
            elif api == "spotify" and use_spotify:
                expanded = self.expand_from_spotify(expanded)
                if not (needs_title and not expanded.get("title") or 
                        needs_artist and not expanded.get("artist")):
                    break
        
        return expanded
    
    def get_stats(self) -> Dict[str, int]:
        """Get expansion statistics."""
        return self.stats.copy()


def expand_json_metadata(
    json_path: str,
    output_path: Optional[str] = None,
    use_musicbrainz: bool = True,
    use_discogs: bool = False,
    use_spotify: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Expand metadata for a single JSON file.
    
    Args:
        json_path: Path to JSON file
        output_path: Optional output path
        use_musicbrainz: Use MusicBrainz API
        use_discogs: Use Discogs API
        use_spotify: Use Spotify API
        **kwargs: Additional arguments for MetadataExpander
    
    Returns:
        Expanded JSON data
    """
    import json
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    expander = MetadataExpander(**kwargs)
    
    # Expand metadata
    metadata = data.get("metadata", {})
    expanded_metadata = expander.expand_metadata(
        metadata,
        use_musicbrainz=use_musicbrainz,
        use_discogs=use_discogs,
        use_spotify=use_spotify,
    )
    
    data["metadata"] = expanded_metadata
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    return data
