"""
Integrated Main Window with 4-panel layout:
Sections | Chords | Analyzer | Data Browser

This is the complete integrated application combining all modules.
"""
import json
import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QMenuBar, QMenu, QAction, QStatusBar,
                             QMessageBox, QFileDialog, QTabWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List, Optional
import logging

from ableton_arranger.core.section import Section
from ableton_arranger.core.persistence import save_sections, load_sections
from ableton_arranger.core.connection import LiveConnection
from ableton_arranger.core.arrangement_builder import ArrangementBuilder
from ableton_arranger.gui.section_panel import SectionPanel
from ableton_arranger.gui.chord_panel import ChordPanel
from ableton_arranger.gui.analyzer_panel import AnalyzerPanel
from ableton_arranger.data.browser_ui import DataBrowserMainWidget
from ableton_arranger.data.database import DatabaseManager
from ableton_arranger.data.project_manager import ProjectManager
from ableton_arranger.data.models import BrowserConfig, SongRecord
from ableton_arranger.shared.data_models import AnalysisData
from pathlib import Path


logger = logging.getLogger(__name__)


class IntegratedMainWindow(QMainWindow):
    """
    Complete integrated main window with 4-panel layout.
    Combines sections, chords, analyzer, and data browser.
    """
    
    def __init__(self):
        super().__init__()
        self.sections: List[Section] = []
        
        # Get data directory path
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(package_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        self.data_path = os.path.join(data_dir, "sections.json")
        
        # Initialize database and project manager
        browser_config = BrowserConfig()
        browser_config.database_path = os.path.join(data_dir, "songs.db")
        self.database = DatabaseManager(browser_config)
        self.project_manager = ProjectManager(self.database, browser_config)
        
        # Connection and builder
        self.connection: Optional[LiveConnection] = None
        self.builder: Optional[ArrangementBuilder] = None
        
        self.init_ui()
        self.init_connection()
        self.load_sections()
    
    def init_ui(self):
        """Initialize the UI with 4-panel layout."""
        self.setWindowTitle("Ableton Arranger - Integrated")
        self.setGeometry(100, 100, 1600, 900)
        
        # Menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        save_action = QAction("Save Sections", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_sections)
        file_menu.addAction(save_action)
        
        load_action = QAction("Load Sections", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_sections_dialog)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Central widget with 4-panel splitter
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left side: Sections and Chords (vertical splitter)
        left_splitter = QSplitter(Qt.Vertical)
        
        # Sections panel (top left)
        self.section_panel = SectionPanel()
        self.section_panel.section_selected.connect(self.on_section_selected)
        self.section_panel.section_changed.connect(self.on_sections_changed)
        self.section_panel.rebuild_requested.connect(self.on_rebuild_requested)
        left_splitter.addWidget(self.section_panel)
        
        # Chord panel (bottom left)
        self.chord_panel = ChordPanel()
        self.chord_panel.chords_changed.connect(self.on_chords_changed)
        left_splitter.addWidget(self.chord_panel)
        
        # Set left splitter sizes (sections: 300px, chords: rest)
        left_splitter.setSizes([300, 500])
        left_splitter.setStretchFactor(0, 0)
        left_splitter.setStretchFactor(1, 1)
        
        main_splitter.addWidget(left_splitter)
        
        # Right side: Analyzer and Data Browser (vertical splitter)
        right_splitter = QSplitter(Qt.Vertical)
        
        # Analyzer panel (top right)
        self.analyzer_panel = AnalyzerPanel()
        self.analyzer_panel.analysis_completed.connect(self.on_analysis_completed)
        right_splitter.addWidget(self.analyzer_panel)
        
        # Data Browser panel (bottom right)
        self.data_browser = DataBrowserMainWidget(self.database, self.project_manager)
        self.data_browser.analyze_requested.connect(self.on_browser_analyze_requested)
        self.data_browser.song_selected.connect(self.on_song_selected)
        self.data_browser.metadata_project_requested.connect(self.load_catalog_project)
        right_splitter.addWidget(self.data_browser)
        
        # Set right splitter sizes (analyzer: 300px, browser: rest)
        right_splitter.setSizes([300, 500])
        right_splitter.setStretchFactor(0, 0)
        right_splitter.setStretchFactor(1, 1)
        
        main_splitter.addWidget(right_splitter)
        
        # Set main splitter sizes (left: 800px, right: 800px)
        main_splitter.setSizes([800, 800])
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 1)
        
        layout.addWidget(main_splitter)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def init_connection(self):
        """Initialize connection to Ableton Live."""
        try:
            self.connection = LiveConnection()
            if self.connection.is_connected():
                self.builder = ArrangementBuilder(self.connection)
                self.status_bar.showMessage("Connected to Ableton Live", 3000)
            else:
                self.status_bar.showMessage("Not connected to Ableton Live - some features unavailable", 5000)
        except Exception as e:
            logger.error(f"Failed to initialize connection: {e}")
            self.status_bar.showMessage(f"Connection error: {e}", 5000)
    
    def on_section_selected(self, index: int):
        """Handle section selection."""
        if 0 <= index < len(self.sections):
            section = self.sections[index]
            self.chord_panel.set_selected_section(section)
        else:
            self.chord_panel.set_selected_section(None)
    
    def on_sections_changed(self):
        """Handle sections modification."""
        pass
    
    def on_chords_changed(self):
        """Handle chords modification."""
        try:
            save_sections(self.sections, self.data_path)
        except Exception as e:
            logger.error(f"Error auto-saving on chord change: {e}")
    
    def on_rebuild_requested(self):
        """Handle rebuild arrangement request."""
        if not self.builder:
            QMessageBox.warning(self, "Not Connected", 
                              "Not connected to Ableton Live. Please ensure AbletonOSC is running.")
            return
        
        if not self.sections:
            QMessageBox.information(self, "No Sections", 
                                   "Please add sections before rebuilding.")
            return
        
        # Update section panel's sections list
        self.section_panel.set_sections(self.sections)
        
        # Build arrangement
        try:
            success = self.builder.build_arrangement(self.sections)
            if success:
                self.status_bar.showMessage(f"Rebuilt arrangement with {len(self.sections)} sections", 5000)
                self.section_panel.set_status(f"Rebuilt {len(self.sections)} sections")
            else:
                QMessageBox.warning(self, "Build Failed", 
                                  "Failed to build arrangement. Check console for details.")
                self.status_bar.showMessage("Build failed", 5000)
        except Exception as e:
            logger.error(f"Error building arrangement: {e}")
            QMessageBox.critical(self, "Error", f"Error building arrangement:\n{e}")
            self.status_bar.showMessage(f"Error: {e}", 5000)
    
    def on_analysis_completed(self, analysis_data: AnalysisData):
        """
        Handle analysis completion - convert to Section objects.
        
        Args:
            analysis_data: Complete analysis results
        """
        # Convert detected sections to Section objects
        new_sections: List[Section] = []
        
        for section_data in analysis_data.sections:
            section = section_data.to_arrangement_section(analysis_data.tempo)
            
            # Add chord data if available
            section_chords = []
            for chord_data in analysis_data.chords:
                # Check if chord falls within this section
                if (chord_data.start_time >= section_data.start_time and 
                    chord_data.start_time < section_data.end_time):
                    
                    # Convert timing to beats
                    beats_per_second = analysis_data.tempo / 60.0
                    start_beat = (chord_data.start_time - section_data.start_time) * beats_per_second
                    duration_beats = (chord_data.end_time - chord_data.start_time) * beats_per_second
                    
                    chord_obj = chord_data.to_chord_object(start_beat, duration_beats)
                    section_chords.append(chord_obj)
            
            section.chords = section_chords
            
            # Add lyrics if available - extract words that fall within this section
            if analysis_data.lyrics and analysis_data.lyrics.words:
                section_lyrics_words = []
                for word_info in analysis_data.lyrics.words:
                    word_start = word_info.get("start", 0.0)
                    # Check if word falls within this section's time range
                    if (word_start >= section_data.start_time and 
                        word_start < section_data.end_time):
                        section_lyrics_words.append(word_info.get("word", ""))
                
                # Join words into lyrics text for this section
                if section_lyrics_words:
                    section.lyrics = " ".join(section_lyrics_words)
                else:
                    # Fallback: if no word-level timing, use full text if section is the main part
                    # (This is a simple heuristic - could be improved)
                    if (section_data.start_time < analysis_data.song_info.duration_seconds * 0.1 or
                        section_data.section_type in ["verse", "chorus"]):
                        # For early sections or verse/chorus, try to extract relevant portion
                        # Simple approach: use full text if it's the first major section
                        if section_data.section_type in ["verse", "chorus"] and len(new_sections) == 0:
                            section.lyrics = analysis_data.lyrics.full_text
            elif analysis_data.lyrics and analysis_data.lyrics.full_text:
                # If only full text is available (no word timing), assign to first major section
                if section_data.section_type in ["verse", "chorus"] and len(new_sections) == 0:
                    section.lyrics = analysis_data.lyrics.full_text
            
            new_sections.append(section)
        
        # Update the sections
        self.sections = new_sections
        self.section_panel.set_sections(new_sections)
        
        # Auto-select first section
        if new_sections:
            self.section_panel.selected_index = 0
            self.section_panel.table.selectRow(0)
            self.on_section_selected(0)
        
        # Show success message with lyrics info
        lyrics_count = sum(1 for s in new_sections if s.lyrics)
        message = (
            f"Successfully imported {len(new_sections)} sections with "
            f"{sum(len(s.chords or []) for s in new_sections)} chords"
        )
        if lyrics_count > 0:
            message += f" and lyrics in {lyrics_count} sections"
        message += ".\n\nUse 'Rebuild' to create the arrangement in Ableton Live."
        
        QMessageBox.information(
            self,
            "Analysis Complete",
            message
        )
        
        # Optionally save to database
        self._save_analysis_to_database(analysis_data)
    
    def _save_analysis_to_database(self, analysis_data: AnalysisData):
        """Save analysis results to database."""
        try:
            from pathlib import Path
            # Create song record
            song = SongRecord(
                id=f"song_{Path(analysis_data.song_info.file_path).stem}",
                title=analysis_data.song_info.title or Path(analysis_data.song_info.file_path).stem,
                artist=analysis_data.song_info.artist or "Unknown",
                tempo=analysis_data.tempo,
                key_signature=analysis_data.key_signature,
                duration_seconds=analysis_data.song_info.duration_seconds,
                original_file_path=analysis_data.song_info.file_path,
                has_stems=bool(analysis_data.stems.vocals_path),
                has_midi=len(analysis_data.chords) > 0,
                has_lyrics=bool(analysis_data.lyrics.full_text.strip())
            )
            
            # Add to database
            self.database.add_song(song)
            
            # Store analysis data
            self.database.store_analysis_data(song.id, analysis_data)
            
            # Refresh browser
            self.data_browser.refresh_data()
            
            logger.info(f"Saved analysis to database: {song.title}")
            
        except Exception as e:
            logger.error(f"Failed to save analysis to database: {e}")
    
    def on_browser_analyze_requested(self, song_id: str):
        """Handle analyze request from data browser."""
        try:
            song = self.database.get_song(song_id)
            if song and song.original_file_path and os.path.exists(song.original_file_path):
                # Set file in analyzer and start analysis
                self.analyzer_panel.selected_file = song.original_file_path
                self.analyzer_panel.file_label.setText(os.path.basename(song.original_file_path))
                self.analyzer_panel.structure_btn.setEnabled(True)
                self.analyzer_panel.full_analysis_btn.setEnabled(True)
                # Could auto-start analysis here if desired
            else:
                QMessageBox.warning(self, "File Not Found", 
                                  f"Audio file not found for song: {song.title if song else song_id}")
        except Exception as e:
            logger.error(f"Error handling browser analyze request: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load song for analysis:\n{e}")
    
    def on_song_selected(self, song_id: str):
        """Handle song selection from browser."""
        try:
            song = self.database.get_song(song_id)
            if song:
                # Load analysis data if available
                analysis = self.database.get_analysis_data(song_id)
                if analysis:
                    self.on_analysis_completed(analysis)
        except Exception as e:
            logger.error(f"Error loading song: {e}")
    
    def load_catalog_project(self, project_path: str):
        """Load an Ableton project JSON from the catalog."""
        try:
            path = Path(project_path)
            if not path.exists():
                QMessageBox.warning(self, "Project Not Found", f"Project file missing:\n{project_path}")
                return
            with path.open("r", encoding="utf-8") as fh:
                project_json = json.load(fh)
            sections_data = project_json.get("sections", [])
            if not sections_data:
                QMessageBox.information(self, "Empty Project", "Selected project has no sections.")
                return
            new_sections = [Section.from_dict(sec) for sec in sections_data]
            self.sections = new_sections
            self.section_panel.set_sections(new_sections)
            if new_sections:
                self.section_panel.selected_index = 0
                self.section_panel.table.selectRow(0)
                self.on_section_selected(0)
            self.status_bar.showMessage(f"Loaded {len(new_sections)} sections from catalog", 5000)
        except Exception as e:
            logger.error(f"Failed to load catalog project: {e}")
            QMessageBox.critical(self, "Load Error", f"Failed to load project:\n{e}")

    def save_sections(self):
        """Save sections to file."""
        try:
            save_sections(self.sections, self.data_path)
            self.status_bar.showMessage(f"Saved {len(self.sections)} sections", 3000)
        except Exception as e:
            logger.error(f"Error saving sections: {e}")
            QMessageBox.critical(self, "Save Error", f"Failed to save sections:\n{e}")
    
    def load_sections(self):
        """Load sections from default file."""
        try:
            if os.path.exists(self.data_path):
                self.sections = load_sections(self.data_path)
                self.section_panel.set_sections(self.sections)
                self.status_bar.showMessage(f"Loaded {len(self.sections)} sections", 3000)
        except Exception as e:
            logger.error(f"Error loading sections: {e}")
    
    def load_sections_dialog(self):
        """Show dialog to load sections from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Sections", "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                self.sections = load_sections(file_path)
                self.section_panel.set_sections(self.sections)
                self.data_path = file_path
                self.status_bar.showMessage(f"Loaded {len(self.sections)} sections from {os.path.basename(file_path)}", 3000)
            except Exception as e:
                logger.error(f"Error loading sections: {e}")
                QMessageBox.critical(self, "Load Error", f"Failed to load sections:\n{e}")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About Ableton Arranger",
                         "Ableton Arranger - Integrated\n\n"
                         "Section-based arrangement helper for Ableton Live.\n\n"
                         "Features:\n"
                         "- Section and chord management\n"
                         "- Audio analysis and structure detection\n"
                         "- Song library and project management\n"
                         "- OSC integration with Ableton Live\n\n"
                         "Requires AbletonOSC to be running in Ableton Live.")
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Auto-save on close
        try:
            save_sections(self.sections, self.data_path)
        except Exception as e:
            logger.error(f"Error auto-saving on close: {e}")
        event.accept()
