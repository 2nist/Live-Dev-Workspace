"""
Data models for the Data Browser module.
Manages projects, songs, and musical database structures.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Set
from datetime import datetime
from enum import Enum
import json


class ProjectStatus(Enum):
    """Status of a music project."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class SongSource(Enum):
    """Source of the song data."""
    FILE_UPLOAD = "file_upload"
    YOUTUBE = "youtube"
    STREAMING = "streaming"
    IMPORTED = "imported"
    USER_CREATION = "user_creation"


@dataclass
class Tag:
    """Tag for categorizing songs and projects."""
    id: int
    name: str
    color: str = "#808080"  # Hex color
    description: str = ""
    usage_count: int = 0


@dataclass
class SongRecord:
    """Complete record of a song in the database."""
    id: str  # Unique identifier
    
    # Basic info
    title: str
    artist: str
    album: str = ""
    year: Optional[int] = None
    duration_seconds: float = 0.0
    
    # Source information
    source: SongSource = SongSource.FILE_UPLOAD
    source_url: str = ""  # YouTube URL, file path, etc.
    original_file_path: str = ""
    
    # Musical analysis
    tempo: float = 120.0
    key_signature: str = "C"
    time_signature: str = "4/4"
    genre: str = ""
    mood: str = ""
    energy_level: float = 0.5  # 0.0 to 1.0
    
    # Analysis metadata
    analysis_id: Optional[str] = None  # Links to AnalysisData
    analysis_date: Optional[datetime] = None
    analysis_quality: float = 0.0  # Overall analysis confidence
    has_stems: bool = False
    has_midi: bool = False
    has_lyrics: bool = False
    
    # Categorization
    tags: Set[str] = field(default_factory=set)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    # Usage tracking
    created_date: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    play_count: int = 0
    reference_count: int = 0  # How often used as reference
    
    # User notes
    notes: str = ""
    rating: int = 0  # 1-5 stars
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, SongSource):
                data[key] = value.value
            elif isinstance(value, set):
                data[key] = list(value)
            else:
                data[key] = value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SongRecord':
        """Create from dictionary."""
        # Handle datetime fields
        if 'created_date' in data and isinstance(data['created_date'], str):
            data['created_date'] = datetime.fromisoformat(data['created_date'])
        if 'last_accessed' in data and isinstance(data['last_accessed'], str):
            data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        if 'analysis_date' in data and isinstance(data['analysis_date'], str):
            data['analysis_date'] = datetime.fromisoformat(data['analysis_date'])
        
        # Handle enum fields
        if 'source' in data and isinstance(data['source'], str):
            data['source'] = SongSource(data['source'])
        
        # Handle set fields
        if 'tags' in data and isinstance(data['tags'], list):
            data['tags'] = set(data['tags'])
        
        return cls(**data)


@dataclass
class ProjectRecord:
    """Music project containing multiple songs and arrangements."""
    id: str  # Unique identifier
    
    # Basic info
    name: str
    description: str = ""
    status: ProjectStatus = ProjectStatus.DRAFT
    
    # Content
    songs: List[str] = field(default_factory=list)  # Song IDs
    arrangements: List[str] = field(default_factory=list)  # Arrangement IDs
    reference_tracks: List[str] = field(default_factory=list)  # Reference song IDs
    
    # Project settings
    default_tempo: float = 120.0
    default_key: str = "C"
    default_time_signature: str = "4/4"
    project_structure: Dict[str, Any] = field(default_factory=dict)
    
    # Categorization
    genre: str = ""
    tags: Set[str] = field(default_factory=set)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    modified_date: datetime = field(default_factory=datetime.now)
    last_opened: datetime = field(default_factory=datetime.now)
    
    # Collaboration
    owner: str = "user"
    collaborators: List[str] = field(default_factory=list)
    
    # Files and exports
    live_set_path: str = ""  # Path to Ableton Live set
    export_paths: Dict[str, str] = field(default_factory=dict)  # Export formats
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, ProjectStatus):
                data[key] = value.value
            elif isinstance(value, set):
                data[key] = list(value)
            else:
                data[key] = value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectRecord':
        """Create from dictionary."""
        # Handle datetime fields
        datetime_fields = ['created_date', 'modified_date', 'last_opened']
        for field in datetime_fields:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])
        
        # Handle enum fields
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = ProjectStatus(data['status'])
        
        # Handle set fields
        if 'tags' in data and isinstance(data['tags'], list):
            data['tags'] = set(data['tags'])
        
        return cls(**data)


@dataclass
class SearchQuery:
    """Search query for songs and projects."""
    
    # Text search
    text: str = ""  # Search in title, artist, notes
    
    # Filters
    genres: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    artists: List[str] = field(default_factory=list)
    
    # Musical filters
    tempo_range: Optional[tuple] = None  # (min_bpm, max_bpm)
    key_signatures: List[str] = field(default_factory=list)
    time_signatures: List[str] = field(default_factory=list)
    energy_range: Optional[tuple] = None  # (min_energy, max_energy)
    
    # Analysis filters
    has_stems: Optional[bool] = None
    has_midi: Optional[bool] = None
    has_lyrics: Optional[bool] = None
    min_analysis_quality: float = 0.0
    
    # Date filters
    date_added_after: Optional[datetime] = None
    date_added_before: Optional[datetime] = None
    last_accessed_after: Optional[datetime] = None
    
    # Rating and usage
    min_rating: int = 0
    min_play_count: int = 0
    only_favorites: bool = False
    
    # Sorting
    sort_by: str = "last_accessed"  # title, artist, tempo, rating, date_added
    sort_order: str = "desc"  # asc, desc
    
    # Pagination
    limit: int = 50
    offset: int = 0
    
    def to_sql_conditions(self) -> tuple:
        """Convert to SQL WHERE conditions and parameters."""
        conditions = []
        params = []
        
        if self.text:
            conditions.append("(title LIKE ? OR artist LIKE ? OR notes LIKE ?)")
            search_term = f"%{self.text}%"
            params.extend([search_term, search_term, search_term])
        
        if self.genres:
            genre_placeholders = ",".join(["?" for _ in self.genres])
            conditions.append(f"genre IN ({genre_placeholders})")
            params.extend(self.genres)
        
        if self.tempo_range:
            conditions.append("tempo BETWEEN ? AND ?")
            params.extend(self.tempo_range)
        
        if self.energy_range:
            conditions.append("energy_level BETWEEN ? AND ?")
            params.extend(self.energy_range)
        
        if self.has_stems is not None:
            conditions.append("has_stems = ?")
            params.append(self.has_stems)
        
        if self.has_midi is not None:
            conditions.append("has_midi = ?")
            params.append(self.has_midi)
        
        if self.has_lyrics is not None:
            conditions.append("has_lyrics = ?")
            params.append(self.has_lyrics)
        
        if self.min_analysis_quality > 0:
            conditions.append("analysis_quality >= ?")
            params.append(self.min_analysis_quality)
        
        if self.min_rating > 0:
            conditions.append("rating >= ?")
            params.append(self.min_rating)
        
        if self.only_favorites:
            conditions.append("rating >= 4")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Add sorting
        order_clause = f"ORDER BY {self.sort_by} {self.sort_order.upper()}"
        
        # Add pagination
        limit_clause = f"LIMIT {self.limit} OFFSET {self.offset}"
        
        return where_clause, params, order_clause, limit_clause


@dataclass
class BrowserConfig:
    """Configuration for the data browser."""
    
    # Database settings
    database_path: str = "~/Music/ableton_arranger/songs.db"
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    
    # Search settings
    default_search_limit: int = 50
    enable_fuzzy_search: bool = True
    search_cache_size: int = 100
    
    # Import settings
    auto_analyze_imports: bool = True
    auto_tag_genres: bool = True
    duplicate_detection: bool = True
    
    # Display settings
    default_view_mode: str = "grid"  # grid, list, detail
    thumbnail_size: int = 150
    show_waveforms: bool = True
    
    # Performance
    cache_analysis_data: bool = True
    preload_thumbnails: bool = True
    max_concurrent_operations: int = 4


# Utility classes for advanced features
@dataclass
class SimilarityResult:
    """Result from similarity analysis between songs."""
    song1_id: str
    song2_id: str
    similarity_score: float  # 0.0 to 1.0
    similarity_type: str  # tempo, key, structure, mood, etc.
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlaylistRule:
    """Rule for generating automatic playlists."""
    id: str
    name: str
    query: SearchQuery
    max_songs: int = 25
    auto_update: bool = True
    created_date: datetime = field(default_factory=datetime.now)


@dataclass
class ImportJob:
    """Background import job for batch processing."""
    id: str
    status: str  # pending, processing, completed, failed
    source_type: str  # folder, youtube_playlist, spotify_playlist
    source_path: str
    total_items: int = 0
    processed_items: int = 0
    failed_items: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: str = ""
