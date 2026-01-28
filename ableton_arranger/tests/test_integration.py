"""
Integration tests for the complete Ableton Arranger system.
Tests the full pipeline: MP3 → Analysis → Database → Project Creation
"""
import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add workspace root to path
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, workspace_root)

from ableton_arranger.shared.data_models import AnalysisConfig, AnalysisData, SongInfo, SectionData
from ableton_arranger.analyzer.audio_analyzer import AudioAnalyzer
from ableton_arranger.data.models import BrowserConfig, SongRecord
from ableton_arranger.data.database import DatabaseManager
from ableton_arranger.data.project_manager import ProjectManager


class TestIntegration(unittest.TestCase):
    """Integration tests for complete pipeline."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test.db")
        
        # Create test config
        self.browser_config = BrowserConfig()
        self.browser_config.database_path = self.test_db_path
        
        # Initialize database
        self.database = DatabaseManager(self.browser_config)
        
        # Initialize project manager
        self.project_manager = ProjectManager(self.database, self.browser_config)
        
        # Analysis config
        self.analysis_config = AnalysisConfig()
        self.analysis_config.temp_dir = os.path.join(self.temp_dir, "analysis")
        self.analysis_config.enable_stem_separation = False  # Skip for tests
        self.analysis_config.enable_lyrics_transcription = False  # Skip for tests
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_database_creation(self):
        """Test database creation and basic operations."""
        # Add a test song
        song = SongRecord(
            id="test_song_1",
            title="Test Song",
            artist="Test Artist",
            tempo=120.0,
            key_signature="C"
        )
        
        success = self.database.add_song(song)
        self.assertTrue(success, "Should add song to database")
        
        # Retrieve song
        retrieved = self.database.get_song("test_song_1")
        self.assertIsNotNone(retrieved, "Should retrieve song from database")
        self.assertEqual(retrieved.title, "Test Song")
        self.assertEqual(retrieved.artist, "Test Artist")
    
    def test_analysis_to_sections(self):
        """Test converting analysis data to sections."""
        # Create mock analysis data
        song_info = SongInfo(
            title="Test Song",
            file_path="/tmp/test.mp3",
            duration_seconds=120.0
        )
        
        analysis = AnalysisData(
            song_info=song_info,
            tempo=120.0,
            key_signature="C"
        )
        
        # Add sections
        analysis.sections = [
            SectionData("Intro", 0, 8, 0.8, "intro"),
            SectionData("Verse 1", 8, 32, 0.8, "verse"),
            SectionData("Chorus 1", 32, 56, 0.8, "chorus")
        ]
        
        # Convert to arrangement sections
        from ableton_arranger.core.section import Section
        
        sections = []
        for section_data in analysis.sections:
            section = section_data.to_arrangement_section(analysis.tempo)
            sections.append(section)
        
        self.assertEqual(len(sections), 3)
        self.assertEqual(sections[0].name, "Intro")
        self.assertEqual(sections[1].name, "Verse 1")
        self.assertEqual(sections[2].name, "Chorus 1")
    
    def test_project_creation(self):
        """Test project creation and management."""
        project = self.project_manager.create_project(
            name="Test Project",
            description="Test project description"
        )
        
        self.assertIsNotNone(project, "Should create project")
        self.assertEqual(project.name, "Test Project")
        self.assertEqual(project.status.value, "draft")
        
        # List projects
        projects = self.project_manager.list_projects()
        self.assertGreaterEqual(len(projects), 1)
    
    def test_analysis_storage(self):
        """Test storing analysis data in database."""
        # Create song
        song = SongRecord(
            id="test_song_2",
            title="Analyzed Song",
            artist="Test Artist"
        )
        self.database.add_song(song)
        
        # Create analysis data
        song_info = SongInfo(
            title="Analyzed Song",
            file_path="/tmp/test.mp3"
        )
        analysis = AnalysisData(song_info=song_info, tempo=128.0)
        analysis.sections = [SectionData("Intro", 0, 16, 0.8, "intro")]
        
        # Store analysis
        success = self.database.store_analysis_data(song.id, analysis)
        self.assertTrue(success, "Should store analysis data")
        
        # Retrieve analysis
        retrieved = self.database.get_analysis_data(song.id)
        self.assertIsNotNone(retrieved, "Should retrieve analysis data")
        self.assertEqual(len(retrieved.sections), 1)
        self.assertEqual(retrieved.tempo, 128.0)


class TestPerformance(unittest.TestCase):
    """Performance tests for large song libraries."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "perf_test.db")
        
        self.browser_config = BrowserConfig()
        self.browser_config.database_path = self.test_db_path
        self.database = DatabaseManager(self.browser_config)
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_large_library_search(self):
        """Test search performance with large library."""
        import time
        
        # Add many songs
        for i in range(100):
            song = SongRecord(
                id=f"song_{i}",
                title=f"Song {i}",
                artist=f"Artist {i % 10}",
                genre=f"Genre {i % 5}",
                tempo=100.0 + (i % 50)
            )
            self.database.add_song(song)
        
        # Test search performance
        from ableton_arranger.data.models import SearchQuery
        
        start_time = time.time()
        query = SearchQuery(text="Song")
        results = self.database.search_songs(query)
        search_time = time.time() - start_time
        
        self.assertGreater(len(results), 0)
        self.assertLess(search_time, 1.0, "Search should complete in under 1 second")


if __name__ == "__main__":
    unittest.main()
