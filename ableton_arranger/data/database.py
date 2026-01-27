"""
Database manager for the Data Browser module.
Handles persistent storage of songs, projects, and analysis data.
"""
import sqlite3
import os
import logging
import json
import shutil
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path

from ableton_arranger.data.models import (
    SongRecord, ProjectRecord, Tag, SearchQuery, 
    BrowserConfig, SimilarityResult, ImportJob
)
from ableton_arranger.shared.data_models import AnalysisData


logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages SQLite database for songs, projects, and analysis data.
    Designed for M4L compatibility with simple operations.
    """
    
    def __init__(self, config: BrowserConfig):
        """
        Initialize database manager.
        
        Args:
            config: Browser configuration
        """
        self.config = config
        self.db_path = os.path.expanduser(config.database_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Set up backup if enabled
        if config.backup_enabled:
            self._schedule_backup()
    
    def _init_database(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Songs table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS songs (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    album TEXT DEFAULT '',
                    year INTEGER,
                    duration_seconds REAL DEFAULT 0.0,
                    source TEXT DEFAULT 'file_upload',
                    source_url TEXT DEFAULT '',
                    original_file_path TEXT DEFAULT '',
                    tempo REAL DEFAULT 120.0,
                    key_signature TEXT DEFAULT 'C',
                    time_signature TEXT DEFAULT '4/4',
                    genre TEXT DEFAULT '',
                    mood TEXT DEFAULT '',
                    energy_level REAL DEFAULT 0.5,
                    analysis_id TEXT,
                    analysis_date TEXT,
                    analysis_quality REAL DEFAULT 0.0,
                    has_stems BOOLEAN DEFAULT FALSE,
                    has_midi BOOLEAN DEFAULT FALSE,
                    has_lyrics BOOLEAN DEFAULT FALSE,
                    tags TEXT DEFAULT '[]',  -- JSON array
                    custom_fields TEXT DEFAULT '{}',  -- JSON object
                    created_date TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    play_count INTEGER DEFAULT 0,
                    reference_count INTEGER DEFAULT 0,
                    notes TEXT DEFAULT '',
                    rating INTEGER DEFAULT 0,
                    
                    FOREIGN KEY (analysis_id) REFERENCES analysis_data(id)
                )
            """)
            
            # Projects table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    status TEXT DEFAULT 'draft',
                    songs TEXT DEFAULT '[]',  -- JSON array of song IDs
                    arrangements TEXT DEFAULT '[]',  -- JSON array
                    reference_tracks TEXT DEFAULT '[]',  -- JSON array
                    default_tempo REAL DEFAULT 120.0,
                    default_key TEXT DEFAULT 'C',
                    default_time_signature TEXT DEFAULT '4/4',
                    project_structure TEXT DEFAULT '{}',  -- JSON object
                    genre TEXT DEFAULT '',
                    tags TEXT DEFAULT '[]',  -- JSON array
                    custom_fields TEXT DEFAULT '{}',  -- JSON object
                    created_date TEXT NOT NULL,
                    modified_date TEXT NOT NULL,
                    last_opened TEXT NOT NULL,
                    owner TEXT DEFAULT 'user',
                    collaborators TEXT DEFAULT '[]',  -- JSON array
                    live_set_path TEXT DEFAULT '',
                    export_paths TEXT DEFAULT '{}'  -- JSON object
                )
            """)
            
            # Tags table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT DEFAULT '#808080',
                    description TEXT DEFAULT '',
                    usage_count INTEGER DEFAULT 0
                )
            """)
            
            # Analysis data table (stores full AnalysisData JSON)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analysis_data (
                    id TEXT PRIMARY KEY,
                    song_id TEXT NOT NULL,
                    analysis_json TEXT NOT NULL,  -- Full AnalysisData as JSON
                    created_date TEXT NOT NULL,
                    file_size INTEGER DEFAULT 0,
                    
                    FOREIGN KEY (song_id) REFERENCES songs(id)
                )
            """)
            
            # Similarity relationships
            conn.execute("""
                CREATE TABLE IF NOT EXISTS similarities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    song1_id TEXT NOT NULL,
                    song2_id TEXT NOT NULL,
                    similarity_score REAL NOT NULL,
                    similarity_type TEXT NOT NULL,
                    details TEXT DEFAULT '{}',  -- JSON object
                    computed_date TEXT NOT NULL,
                    
                    FOREIGN KEY (song1_id) REFERENCES songs(id),
                    FOREIGN KEY (song2_id) REFERENCES songs(id),
                    UNIQUE(song1_id, song2_id, similarity_type)
                )
            """)
            
            # Import jobs for batch processing
            conn.execute("""
                CREATE TABLE IF NOT EXISTS import_jobs (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    total_items INTEGER DEFAULT 0,
                    processed_items INTEGER DEFAULT 0,
                    failed_items TEXT DEFAULT '[]',  -- JSON array
                    started_at TEXT,
                    completed_at TEXT,
                    error_message TEXT DEFAULT ''
                )
            """)
            
            # Create indexes for better search performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_songs_artist ON songs(artist)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_songs_genre ON songs(genre)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_songs_tempo ON songs(tempo)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_songs_key ON songs(key_signature)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_songs_rating ON songs(rating)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_songs_last_accessed ON songs(last_accessed)")
            
            conn.commit()
            
        logger.info(f"Database initialized: {self.db_path}")
    
    def add_song(self, song: SongRecord) -> bool:
        """
        Add a song to the database.
        
        Args:
            song: SongRecord to add
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                song_data = song.to_dict()
                
                # Convert complex fields to JSON
                song_data['tags'] = json.dumps(list(song_data['tags']))
                song_data['custom_fields'] = json.dumps(song_data['custom_fields'])
                
                # Convert datetime to ISO string
                for field in ['created_date', 'last_accessed', 'analysis_date']:
                    if field in song_data and song_data[field]:
                        if isinstance(song_data[field], datetime):
                            song_data[field] = song_data[field].isoformat()
                
                # Insert song
                placeholders = ', '.join(['?' for _ in song_data])
                fields = ', '.join(song_data.keys())
                
                conn.execute(
                    f"INSERT OR REPLACE INTO songs ({fields}) VALUES ({placeholders})",
                    list(song_data.values())
                )
                
                conn.commit()
                logger.info(f"Added song: {song.title} by {song.artist}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to add song: {e}")
            return False
    
    def get_song(self, song_id: str) -> Optional[SongRecord]:
        """Get a song by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
                row = cursor.fetchone()
                
                if row:
                    song_data = dict(row)
                    
                    # Convert JSON fields back
                    song_data['tags'] = set(json.loads(song_data['tags']))
                    song_data['custom_fields'] = json.loads(song_data['custom_fields'])
                    
                    # Convert datetime fields
                    for field in ['created_date', 'last_accessed', 'analysis_date']:
                        if song_data[field]:
                            song_data[field] = datetime.fromisoformat(song_data[field])
                    
                    return SongRecord.from_dict(song_data)
                
        except Exception as e:
            logger.error(f"Failed to get song {song_id}: {e}")
        
        return None
    
    def search_songs(self, query: SearchQuery) -> List[SongRecord]:
        """
        Search songs with filters.
        
        Args:
            query: Search query with filters
            
        Returns:
            List of matching songs
        """
        try:
            where_clause, params, order_clause, limit_clause = query.to_sql_conditions()
            
            sql = f"""
                SELECT * FROM songs 
                WHERE {where_clause}
                {order_clause}
                {limit_clause}
            """
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()
                
                songs = []
                for row in rows:
                    song_data = dict(row)
                    
                    # Convert JSON fields
                    song_data['tags'] = set(json.loads(song_data['tags']))
                    song_data['custom_fields'] = json.loads(song_data['custom_fields'])
                    
                    # Convert datetime fields
                    for field in ['created_date', 'last_accessed', 'analysis_date']:
                        if song_data[field]:
                            song_data[field] = datetime.fromisoformat(song_data[field])
                    
                    songs.append(SongRecord.from_dict(song_data))
                
                return songs
                
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def add_project(self, project: ProjectRecord) -> bool:
        """Add a project to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                project_data = project.to_dict()
                
                # Convert complex fields to JSON
                for field in ['songs', 'arrangements', 'reference_tracks', 'tags', 
                             'custom_fields', 'collaborators', 'export_paths']:
                    if field in project_data:
                        if field == 'tags':
                            project_data[field] = json.dumps(list(project_data[field]))
                        else:
                            project_data[field] = json.dumps(project_data[field])
                
                # Convert project_structure to JSON
                project_data['project_structure'] = json.dumps(project_data['project_structure'])
                
                # Convert datetime fields
                for field in ['created_date', 'modified_date', 'last_opened']:
                    if field in project_data and project_data[field]:
                        if isinstance(project_data[field], datetime):
                            project_data[field] = project_data[field].isoformat()
                
                placeholders = ', '.join(['?' for _ in project_data])
                fields = ', '.join(project_data.keys())
                
                conn.execute(
                    f"INSERT OR REPLACE INTO projects ({fields}) VALUES ({placeholders})",
                    list(project_data.values())
                )
                
                conn.commit()
                logger.info(f"Added project: {project.name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to add project: {e}")
            return False
    
    def store_analysis_data(self, song_id: str, analysis_data: AnalysisData) -> bool:
        """
        Store complete analysis data for a song.
        
        Args:
            song_id: Song ID to link analysis to
            analysis_data: Complete AnalysisData object
            
        Returns:
            True if successful
        """
        try:
            analysis_json = analysis_data.to_json()
            analysis_id = f"{song_id}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO analysis_data 
                    (id, song_id, analysis_json, created_date, file_size)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    analysis_id,
                    song_id,
                    analysis_json,
                    datetime.now().isoformat(),
                    len(analysis_json)
                ))
                
                # Update song record with analysis info
                conn.execute("""
                    UPDATE songs SET 
                    analysis_id = ?,
                    analysis_date = ?,
                    analysis_quality = ?,
                    has_stems = ?,
                    has_midi = ?,
                    has_lyrics = ?
                    WHERE id = ?
                """, (
                    analysis_id,
                    analysis_data.analysis_time,
                    0.8,  # Default quality score
                    bool(analysis_data.stems.vocals_path),
                    len(analysis_data.chords) > 0,
                    bool(analysis_data.lyrics.full_text.strip()),
                    song_id
                ))
                
                conn.commit()
                logger.info(f"Stored analysis data for song {song_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to store analysis data: {e}")
            return False
    
    def get_analysis_data(self, song_id: str) -> Optional[AnalysisData]:
        """Get analysis data for a song."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT analysis_json FROM analysis_data WHERE song_id = ? ORDER BY created_date DESC LIMIT 1",
                    (song_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    analysis_json = row[0]
                    return AnalysisData.from_json(analysis_json)
                
        except Exception as e:
            logger.error(f"Failed to get analysis data for {song_id}: {e}")
        
        return None
    
    def get_similar_songs(self, song_id: str, limit: int = 10) -> List[SimilarityResult]:
        """Get songs similar to the given song."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT song1_id, song2_id, similarity_score, similarity_type, details
                    FROM similarities 
                    WHERE song1_id = ? OR song2_id = ?
                    ORDER BY similarity_score DESC
                    LIMIT ?
                """, (song_id, song_id, limit))
                
                results = []
                for row in cursor.fetchall():
                    results.append(SimilarityResult(
                        song1_id=row['song1_id'],
                        song2_id=row['song2_id'],
                        similarity_score=row['similarity_score'],
                        similarity_type=row['similarity_type'],
                        details=json.loads(row['details'])
                    ))
                
                return results
                
        except Exception as e:
            logger.error(f"Failed to get similar songs: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                stats = {}
                
                # Count records
                cursor = conn.execute("SELECT COUNT(*) FROM songs")
                stats['total_songs'] = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM projects")
                stats['total_projects'] = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM analysis_data")
                stats['analyzed_songs'] = cursor.fetchone()[0]
                
                # Genre distribution
                cursor = conn.execute("""
                    SELECT genre, COUNT(*) as count 
                    FROM songs 
                    WHERE genre != '' 
                    GROUP BY genre 
                    ORDER BY count DESC 
                    LIMIT 10
                """)
                stats['top_genres'] = dict(cursor.fetchall())
                
                # Database file size
                stats['database_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
    
    def backup_database(self, backup_path: Optional[str] = None) -> bool:
        """Create database backup."""
        try:
            if not backup_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"{self.db_path}.backup_{timestamp}"
            
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False
    
    def _schedule_backup(self):
        """Schedule automatic backups (placeholder for implementation)."""
        # This could use threading.Timer or a proper scheduler
        # For now, just log that backup is configured
        logger.info(f"Automatic backup enabled every {self.config.backup_interval_hours} hours")
    
    def cleanup_old_data(self, days: int = 90):
        """Clean up old temporary data."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                # Clean up old analysis data for songs no longer in database
                cursor = conn.execute("""
                    DELETE FROM analysis_data 
                    WHERE created_date < ? 
                    AND song_id NOT IN (SELECT id FROM songs)
                """, (cutoff_str,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_count} old analysis records")
                
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def close(self):
        """Close database connections and cleanup."""
        # Any cleanup needed
        logger.info("Database manager closed")


# Utility functions for database operations
def create_test_database(db_path: str) -> DatabaseManager:
    """Create a test database with sample data."""
    config = BrowserConfig()
    config.database_path = db_path
    
    db = DatabaseManager(config)
    
    # Add sample songs
    sample_songs = [
        SongRecord(
            id="song1",
            title="Test Song 1", 
            artist="Test Artist",
            genre="Electronic",
            tempo=128.0,
            key_signature="Am",
            rating=4
        ),
        SongRecord(
            id="song2",
            title="Test Song 2",
            artist="Another Artist", 
            genre="Rock",
            tempo=120.0,
            key_signature="C",
            rating=5
        )
    ]
    
    for song in sample_songs:
        db.add_song(song)
    
    logger.info(f"Created test database with {len(sample_songs)} sample songs")
    return db
