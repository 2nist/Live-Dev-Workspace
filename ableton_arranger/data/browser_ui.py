"""
Browser UI components for the Data Browser module.
Provides song library, project browser, and search interface.
"""
import os
from typing import List, Optional, Dict, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QPushButton, QComboBox, QLabel, QTabWidget,
    QListWidget, QListWidgetItem, QProgressBar, QTextEdit,
    QHeaderView, QAbstractItemView, QMenu, QAction,
    QFileDialog, QMessageBox, QDialog, QDialogButtonBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox,
    QSplitter, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor

from ableton_arranger.data.models import (
    SongRecord, ProjectRecord, SearchQuery, ProjectStatus, SongSource, Tag
)
from ableton_arranger.data.database import DatabaseManager
from ableton_arranger.data.project_manager import ProjectManager
from ableton_arranger.shared.data_models import AnalysisData


class SongBrowserWidget(QWidget):
    """
    Main song browser with search, filters, and song list.
    This could become a separate M4L device.
    """
    
    song_selected = pyqtSignal(str)  # Emits song ID
    song_double_clicked = pyqtSignal(str)  # Emits song ID for loading
    analyze_requested = pyqtSignal(str)  # Request analysis for song
    
    def __init__(self, database: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = database
        self.current_songs: List[SongRecord] = []
        self.current_query = SearchQuery()
        
        self.init_ui()
        self.load_songs()
    
    def init_ui(self):
        """Initialize the browser UI."""
        layout = QVBoxLayout()
        
        # Search and filter section
        search_layout = self._create_search_section()
        layout.addLayout(search_layout)
        
        # Main content area
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left: Filters and categories
        filters_widget = self._create_filters_panel()
        content_splitter.addWidget(filters_widget)
        
        # Right: Song list
        songs_widget = self._create_songs_panel()
        content_splitter.addWidget(songs_widget)
        
        # Set splitter sizes (filters: 250px, songs: rest)
        content_splitter.setSizes([250, 600])
        content_splitter.setStretchFactor(1, 1)
        
        layout.addWidget(content_splitter)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def _create_search_section(self) -> QHBoxLayout:
        """Create search bar and quick filters."""
        layout = QHBoxLayout()
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search songs, artists, genres...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        layout.addWidget(self.search_input)
        
        # Quick genre filter
        self.genre_filter = QComboBox()
        self.genre_filter.addItem("All Genres")
        self.genre_filter.currentTextChanged.connect(self.on_genre_filter_changed)
        layout.addWidget(self.genre_filter)
        
        # Search button
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.perform_search)
        layout.addWidget(search_btn)
        
        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_search)
        layout.addWidget(clear_btn)
        
        return layout
    
    def _create_filters_panel(self) -> QWidget:
        """Create filters and categories panel."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Musical filters
        musical_group = QGroupBox("Musical Properties")
        musical_layout = QVBoxLayout()
        
        # Tempo range
        tempo_layout = QHBoxLayout()
        tempo_layout.addWidget(QLabel("Tempo:"))
        self.tempo_min = QSpinBox()
        self.tempo_min.setRange(60, 200)
        self.tempo_min.setValue(60)
        self.tempo_max = QSpinBox()
        self.tempo_max.setRange(60, 200)
        self.tempo_max.setValue(200)
        tempo_layout.addWidget(self.tempo_min)
        tempo_layout.addWidget(QLabel("-"))
        tempo_layout.addWidget(self.tempo_max)
        musical_layout.addLayout(tempo_layout)
        
        # Key filter
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Key:"))
        self.key_filter = QComboBox()
        self.key_filter.addItems(["Any", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])
        key_layout.addWidget(self.key_filter)
        musical_layout.addLayout(key_layout)
        
        musical_group.setLayout(musical_layout)
        layout.addWidget(musical_group)
        
        # Analysis filters
        analysis_group = QGroupBox("Analysis")
        analysis_layout = QVBoxLayout()
        
        self.has_stems_filter = QCheckBox("Has Stems")
        self.has_midi_filter = QCheckBox("Has MIDI")
        self.has_lyrics_filter = QCheckBox("Has Lyrics")
        
        analysis_layout.addWidget(self.has_stems_filter)
        analysis_layout.addWidget(self.has_midi_filter) 
        analysis_layout.addWidget(self.has_lyrics_filter)
        
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)
        
        # Rating filter
        rating_group = QGroupBox("Rating")
        rating_layout = QVBoxLayout()
        
        rating_layout.addWidget(QLabel("Minimum:"))
        self.rating_filter = QComboBox()
        self.rating_filter.addItems(["Any", "⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
        rating_layout.addWidget(self.rating_filter)
        
        rating_group.setLayout(rating_layout)
        layout.addWidget(rating_group)
        
        # Apply filters button
        apply_btn = QPushButton("Apply Filters")
        apply_btn.clicked.connect(self.apply_filters)
        layout.addWidget(apply_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_songs_panel(self) -> QWidget:
        """Create songs list/grid panel."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # View controls
        controls_layout = QHBoxLayout()
        
        # View mode buttons
        self.list_view_btn = QPushButton("List")
        self.grid_view_btn = QPushButton("Grid")
        self.list_view_btn.clicked.connect(lambda: self.set_view_mode("list"))
        self.grid_view_btn.clicked.connect(lambda: self.set_view_mode("grid"))
        
        controls_layout.addWidget(QLabel("View:"))
        controls_layout.addWidget(self.list_view_btn)
        controls_layout.addWidget(self.grid_view_btn)
        controls_layout.addStretch()
        
        # Sort options
        controls_layout.addWidget(QLabel("Sort by:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Last Accessed", "Title", "Artist", "Date Added", "Rating", "Tempo"])
        self.sort_combo.currentTextChanged.connect(self.on_sort_changed)
        controls_layout.addWidget(self.sort_combo)
        
        layout.addLayout(controls_layout)
        
        # Songs table
        self.songs_table = QTableWidget()
        self.songs_table.setColumnCount(8)
        self.songs_table.setHorizontalHeaderLabels([
            "Title", "Artist", "Genre", "Tempo", "Key", "Rating", "Analysis", "Actions"
        ])
        
        # Configure table
        header = self.songs_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Title column
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Artist column
        
        self.songs_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.songs_table.setAlternatingRowColors(True)
        self.songs_table.itemSelectionChanged.connect(self.on_song_selected)
        self.songs_table.itemDoubleClicked.connect(self.on_song_double_clicked)
        
        # Context menu
        self.songs_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.songs_table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.songs_table)
        
        widget.setLayout(layout)
        return widget
    
    def load_songs(self, query: Optional[SearchQuery] = None):
        """Load songs into the table."""
        try:
            if not query:
                query = SearchQuery()
            
            self.current_songs = self.db.search_songs(query)
            self.populate_songs_table()
            
            # Update genre filter
            self.update_genre_filter()
            
            # Update status
            self.status_label.setText(f"Found {len(self.current_songs)} songs")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load songs: {e}")
    
    def populate_songs_table(self):
        """Populate the songs table with current songs."""
        self.songs_table.setRowCount(len(self.current_songs))
        
        for row, song in enumerate(self.current_songs):
            # Title
            self.songs_table.setItem(row, 0, QTableWidgetItem(song.title))
            
            # Artist
            self.songs_table.setItem(row, 1, QTableWidgetItem(song.artist))
            
            # Genre
            self.songs_table.setItem(row, 2, QTableWidgetItem(song.genre))
            
            # Tempo
            self.songs_table.setItem(row, 3, QTableWidgetItem(f"{song.tempo:.0f}"))
            
            # Key
            self.songs_table.setItem(row, 4, QTableWidgetItem(song.key_signature))
            
            # Rating
            rating_text = "⭐" * song.rating if song.rating > 0 else ""
            self.songs_table.setItem(row, 5, QTableWidgetItem(rating_text))
            
            # Analysis status
            analysis_parts = []
            if song.has_stems:
                analysis_parts.append("Stems")
            if song.has_midi:
                analysis_parts.append("MIDI")
            if song.has_lyrics:
                analysis_parts.append("Lyrics")
            
            analysis_text = ", ".join(analysis_parts) if analysis_parts else "None"
            self.songs_table.setItem(row, 6, QTableWidgetItem(analysis_text))
            
            # Actions (buttons)
            actions_widget = self._create_actions_widget(song)
            self.songs_table.setCellWidget(row, 7, actions_widget)
            
            # Store song ID in first column for reference
            title_item = self.songs_table.item(row, 0)
            title_item.setData(Qt.UserRole, song.id)
    
    def _create_actions_widget(self, song: SongRecord) -> QWidget:
        """Create action buttons for a song row."""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Analyze button
        analyze_btn = QPushButton("Analyze")
        analyze_btn.setMaximumWidth(60)
        analyze_btn.clicked.connect(lambda: self.analyze_requested.emit(song.id))
        layout.addWidget(analyze_btn)
        
        # Play button (placeholder)
        play_btn = QPushButton("▶")
        play_btn.setMaximumWidth(30)
        play_btn.setToolTip("Play preview")
        layout.addWidget(play_btn)
        
        widget.setLayout(layout)
        return widget
    
    def update_genre_filter(self):
        """Update genre filter with available genres."""
        current_text = self.genre_filter.currentText()
        
        self.genre_filter.clear()
        self.genre_filter.addItem("All Genres")
        
        # Get unique genres from current songs
        genres = set()
        for song in self.current_songs:
            if song.genre:
                genres.add(song.genre)
        
        for genre in sorted(genres):
            self.genre_filter.addItem(genre)
        
        # Restore selection if possible
        index = self.genre_filter.findText(current_text)
        if index >= 0:
            self.genre_filter.setCurrentIndex(index)
    
    def on_search_text_changed(self, text: str):
        """Handle search text changes with debounce."""
        # Use timer to debounce search
        if not hasattr(self, 'search_timer'):
            self.search_timer = QTimer()
            self.search_timer.setSingleShot(True)
            self.search_timer.timeout.connect(self.perform_search)
        
        self.search_timer.stop()
        self.search_timer.start(500)  # 500ms delay
    
    def on_genre_filter_changed(self, text: str):
        """Handle genre filter change."""
        self.perform_search()
    
    def on_sort_changed(self, sort_text: str):
        """Handle sort option change."""
        sort_mapping = {
            "Last Accessed": "last_accessed",
            "Title": "title", 
            "Artist": "artist",
            "Date Added": "created_date",
            "Rating": "rating",
            "Tempo": "tempo"
        }
        
        self.current_query.sort_by = sort_mapping.get(sort_text, "last_accessed")
        self.perform_search()
    
    def perform_search(self):
        """Perform search with current criteria."""
        query = SearchQuery()
        
        # Text search
        search_text = self.search_input.text().strip()
        if search_text:
            query.text = search_text
        
        # Genre filter
        genre = self.genre_filter.currentText()
        if genre and genre != "All Genres":
            query.genres = [genre]
        
        # Apply musical filters
        if hasattr(self, 'tempo_min'):
            query.tempo_range = (self.tempo_min.value(), self.tempo_max.value())
        
        if hasattr(self, 'key_filter'):
            key = self.key_filter.currentText()
            if key != "Any":
                query.key_signatures = [key]
        
        # Analysis filters
        if hasattr(self, 'has_stems_filter') and self.has_stems_filter.isChecked():
            query.has_stems = True
        if hasattr(self, 'has_midi_filter') and self.has_midi_filter.isChecked():
            query.has_midi = True
        if hasattr(self, 'has_lyrics_filter') and self.has_lyrics_filter.isChecked():
            query.has_lyrics = True
        
        # Rating filter
        if hasattr(self, 'rating_filter'):
            rating_text = self.rating_filter.currentText()
            if rating_text != "Any":
                query.min_rating = rating_text.count("⭐")
        
        # Sort
        if hasattr(self, 'sort_combo'):
            sort_mapping = {
                "Last Accessed": "last_accessed",
                "Title": "title",
                "Artist": "artist", 
                "Date Added": "created_date",
                "Rating": "rating",
                "Tempo": "tempo"
            }
            query.sort_by = sort_mapping.get(self.sort_combo.currentText(), "last_accessed")
        
        self.current_query = query
        self.load_songs(query)
    
    def apply_filters(self):
        """Apply all current filters."""
        self.perform_search()
    
    def clear_search(self):
        """Clear all search criteria."""
        self.search_input.clear()
        self.genre_filter.setCurrentText("All Genres")
        
        if hasattr(self, 'tempo_min'):
            self.tempo_min.setValue(60)
            self.tempo_max.setValue(200)
        
        if hasattr(self, 'key_filter'):
            self.key_filter.setCurrentText("Any")
        
        if hasattr(self, 'has_stems_filter'):
            self.has_stems_filter.setChecked(False)
            self.has_midi_filter.setChecked(False)
            self.has_lyrics_filter.setChecked(False)
        
        if hasattr(self, 'rating_filter'):
            self.rating_filter.setCurrentText("Any")
        
        self.current_query = SearchQuery()
        self.load_songs()
    
    def set_view_mode(self, mode: str):
        """Switch between list and grid view."""
        if mode == "list":
            # Already in list mode with table
            self.list_view_btn.setEnabled(False)
            self.grid_view_btn.setEnabled(True)
        elif mode == "grid":
            # TODO: Implement grid view
            self.list_view_btn.setEnabled(True)
            self.grid_view_btn.setEnabled(False)
    
    def on_song_selected(self):
        """Handle song selection."""
        current_row = self.songs_table.currentRow()
        if current_row >= 0:
            title_item = self.songs_table.item(current_row, 0)
            song_id = title_item.data(Qt.UserRole)
            if song_id:
                self.song_selected.emit(song_id)
    
    def on_song_double_clicked(self):
        """Handle song double-click."""
        current_row = self.songs_table.currentRow()
        if current_row >= 0:
            title_item = self.songs_table.item(current_row, 0)
            song_id = title_item.data(Qt.UserRole)
            if song_id:
                self.song_double_clicked.emit(song_id)
    
    def show_context_menu(self, position):
        """Show context menu for songs table."""
        item = self.songs_table.itemAt(position)
        if not item:
            return
        
        menu = QMenu()
        
        # Get song ID
        row = item.row()
        title_item = self.songs_table.item(row, 0)
        song_id = title_item.data(Qt.UserRole)
        
        if song_id:
            # Add to project action
            add_to_project_action = QAction("Add to Project...", self)
            add_to_project_action.triggered.connect(lambda: self.add_to_project_dialog(song_id))
            menu.addAction(add_to_project_action)
            
            # Analyze action
            analyze_action = QAction("Analyze", self)
            analyze_action.triggered.connect(lambda: self.analyze_requested.emit(song_id))
            menu.addAction(analyze_action)
            
            menu.addSeparator()
            
            # Edit info action
            edit_action = QAction("Edit Info...", self)
            edit_action.triggered.connect(lambda: self.edit_song_info(song_id))
            menu.addAction(edit_action)
            
            # Delete action
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(lambda: self.delete_song(song_id))
            menu.addAction(delete_action)
        
        menu.exec_(self.songs_table.mapToGlobal(position))
    
    def add_to_project_dialog(self, song_id: str):
        """Show dialog to add song to project."""
        # This would show a project selection dialog
        QMessageBox.information(self, "Add to Project", f"Would add song {song_id} to project")
    
    def edit_song_info(self, song_id: str):
        """Show song info editor dialog."""
        # This would show a song editing dialog
        QMessageBox.information(self, "Edit Song", f"Would edit song {song_id}")
    
    def delete_song(self, song_id: str):
        """Delete a song after confirmation."""
        reply = QMessageBox.question(
            self, "Delete Song", 
            "Are you sure you want to delete this song?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete from database
            # Refresh view
            self.perform_search()


class ProjectBrowserWidget(QWidget):
    """
    Project browser and management interface.
    """
    
    project_selected = pyqtSignal(str)  # Emits project ID
    project_opened = pyqtSignal(str)   # Request to open project
    
    def __init__(self, project_manager: ProjectManager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.current_projects: List[ProjectRecord] = []
        
        self.init_ui()
        self.load_projects()
    
    def init_ui(self):
        """Initialize project browser UI."""
        layout = QVBoxLayout()
        
        # Header with create button
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Projects"))
        
        create_btn = QPushButton("New Project")
        create_btn.clicked.connect(self.create_new_project)
        header_layout.addWidget(create_btn)
        
        layout.addLayout(header_layout)
        
        # Projects table
        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(5)
        self.projects_table.setHorizontalHeaderLabels([
            "Name", "Status", "Songs", "Modified", "Actions"
        ])
        
        header = self.projects_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        
        self.projects_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.projects_table.itemDoubleClicked.connect(self.on_project_double_clicked)
        
        layout.addWidget(self.projects_table)
        
        self.setLayout(layout)
    
    def load_projects(self):
        """Load projects into table."""
        self.current_projects = self.project_manager.list_projects()
        self.populate_projects_table()
    
    def populate_projects_table(self):
        """Populate projects table."""
        self.projects_table.setRowCount(len(self.current_projects))
        
        for row, project in enumerate(self.current_projects):
            # Name
            self.projects_table.setItem(row, 0, QTableWidgetItem(project.name))
            
            # Status
            status_text = project.status.value.replace('_', ' ').title()
            self.projects_table.setItem(row, 1, QTableWidgetItem(status_text))
            
            # Song count
            song_count = len(project.songs)
            self.projects_table.setItem(row, 2, QTableWidgetItem(str(song_count)))
            
            # Modified date
            modified_text = project.modified_date.strftime('%Y-%m-%d')
            self.projects_table.setItem(row, 3, QTableWidgetItem(modified_text))
            
            # Actions
            actions_widget = self._create_project_actions_widget(project)
            self.projects_table.setCellWidget(row, 4, actions_widget)
            
            # Store project ID
            name_item = self.projects_table.item(row, 0)
            name_item.setData(Qt.UserRole, project.id)
    
    def _create_project_actions_widget(self, project: ProjectRecord) -> QWidget:
        """Create action buttons for project row."""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Open button
        open_btn = QPushButton("Open")
        open_btn.setMaximumWidth(50)
        open_btn.clicked.connect(lambda: self.project_opened.emit(project.id))
        layout.addWidget(open_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_new_project(self):
        """Show new project dialog."""
        # This would show a new project creation dialog
        QMessageBox.information(self, "New Project", "Would show new project dialog")
    
    def on_project_double_clicked(self):
        """Handle project double-click."""
        current_row = self.projects_table.currentRow()
        if current_row >= 0:
            name_item = self.projects_table.item(current_row, 0)
            project_id = name_item.data(Qt.UserRole)
            if project_id:
                self.project_opened.emit(project_id)


class DataBrowserMainWidget(QTabWidget):
    """
    Main data browser interface combining songs and projects.
    This would be the complete M4L Data Browser device.
    """
    
    song_selected = pyqtSignal(str)
    project_selected = pyqtSignal(str)
    analyze_requested = pyqtSignal(str)
    
    def __init__(self, database: DatabaseManager, project_manager: ProjectManager, parent=None):
        super().__init__(parent)
        self.db = database
        self.project_manager = project_manager
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize main browser interface."""
        # Songs tab
        self.song_browser = SongBrowserWidget(self.db)
        self.song_browser.song_selected.connect(self.song_selected)
        self.song_browser.analyze_requested.connect(self.analyze_requested)
        self.addTab(self.song_browser, "Songs")
        
        # Projects tab  
        self.project_browser = ProjectBrowserWidget(self.project_manager)
        self.project_browser.project_selected.connect(self.project_selected)
        self.addTab(self.project_browser, "Projects")
    
    def refresh_data(self):
        """Refresh all browser data."""
        self.song_browser.load_songs()
        self.project_browser.load_projects()


# Example integration
def create_data_browser_panel(database: DatabaseManager, project_manager: ProjectManager) -> DataBrowserMainWidget:
    """
    Create complete data browser panel.
    
    Args:
        database: Database manager instance
        project_manager: Project manager instance
        
    Returns:
        Complete data browser widget
    """
    browser = DataBrowserMainWidget(database, project_manager)
    
    # Connect signals for integration
    browser.song_selected.connect(lambda song_id: print(f"Song selected: {song_id}"))
    browser.project_selected.connect(lambda project_id: print(f"Project selected: {project_id}"))
    browser.analyze_requested.connect(lambda song_id: print(f"Analysis requested: {song_id}"))
    
    return browser
