"""
Main window for Ableton Arranger.
Contains splitter with section panel (left) and chord panel (right).
"""
import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QMenuBar, QMenu, QAction, QStatusBar,
                             QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QSettings
from typing import List, Optional
import logging

# Use unified models from arranger package
import sys
import os
# Add python/src to path for arranger imports
workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
python_src = os.path.join(workspace_root, "python", "src")
if python_src not in sys.path:
    sys.path.insert(0, python_src)

from arranger.utils.adapters import SectionAdapter
from arranger.utils.persistence import save_sections, load_sections
from arranger.live_bridge.ableton_connection import AbletonConnection
from arranger.services.state_manager import StateManager
from ableton_arranger.core.arrangement_builder import ArrangementBuilder

# Legacy Section import for type hints (will be removed in Phase 2)
from ableton_arranger.core.section import Section as LegacySection
from ableton_arranger.gui.section_panel import SectionPanel
from ableton_arranger.gui.chord_panel import ChordPanel
from ableton_arranger.gui.arrangement_view import ArrangementView
from ableton_arranger.gui.theory_panel import TheoryPanel


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.sections: List[SectionAdapter] = []
        # Get data directory path (relative to ableton_arranger package)
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(package_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        self.data_path = os.path.join(data_dir, "sections.json")
        self.connection: Optional[AbletonConnection] = None
        self.builder: Optional[ArrangementBuilder] = None
        
        # Initialize state manager
        self.state_manager = StateManager(
            initial_state={"sections": []},
            max_history=50,
            auto_checkpoint=True
        )
        self.state_manager.on_change(self.on_state_changed)
        
        self.init_ui()
        self.init_connection()
        self.load_sections()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Ableton Arranger")
        self.setGeometry(100, 100, 1200, 800)
        
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
        
        # Edit menu (for undo/redo)
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Shift+Z")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        self.undo_action = undo_action
        self.redo_action = redo_action
        self.update_undo_redo_actions()
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Central widget with redesigned layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Top: Arrangement timeline
        self.arrangement_view = ArrangementView()
        self.arrangement_view.section_selected.connect(self.on_section_selected)
        main_layout.addWidget(self.arrangement_view)
        
        # Bottom: Splitter with left (sections) and right (chords + theory)
        bottom_splitter = QSplitter(Qt.Horizontal)
        
        # Left: Sections panel
        self.section_panel = SectionPanel()
        self.section_panel.section_selected.connect(self.on_section_selected)
        self.section_panel.section_changed.connect(self.on_sections_changed)
        self.section_panel.rebuild_requested.connect(self.on_rebuild_requested)
        bottom_splitter.addWidget(self.section_panel)
        
        # Right: Splitter with chord editor (top) and theory panel (bottom)
        right_splitter = QSplitter(Qt.Vertical)
        
        # Top right: Chord editor
        self.chord_panel = ChordPanel()
        self.chord_panel.chords_changed.connect(self.on_chords_changed)
        right_splitter.addWidget(self.chord_panel)
        
        # Bottom right: Theory panel
        self.theory_panel = TheoryPanel()
        self.theory_panel.chord_suggested.connect(self.on_theory_chord_suggested)
        self.theory_panel.progression_suggested.connect(self.on_theory_progression_suggested)
        right_splitter.addWidget(self.theory_panel)
        
        right_splitter.setSizes([400, 200])
        right_splitter.setStretchFactor(0, 2)
        right_splitter.setStretchFactor(1, 1)
        
        bottom_splitter.addWidget(right_splitter)
        bottom_splitter.setSizes([350, 850])
        bottom_splitter.setStretchFactor(0, 0)
        bottom_splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(bottom_splitter)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def init_connection(self):
        """Initialize connection to Ableton Live."""
        try:
            # Use AbletonConnection with auto-reconnect
            self.connection = AbletonConnection(
                hostname="127.0.0.1",
                port=11000,
                client_port=11001,
                mock=False,
                auto_reconnect=True
            )
            if self.connection.is_connected():
                self.builder = ArrangementBuilder(self.connection)
                self.status_bar.showMessage("Connected to Ableton Live", 3000)
            else:
                self.status_bar.showMessage("Not connected to Ableton Live - using mock mode", 5000)
                # Still create builder with mock connection
                self.builder = ArrangementBuilder(self.connection)
        except Exception as e:
            logger.error(f"Failed to initialize connection: {e}")
            self.status_bar.showMessage(f"Connection error: {e}", 5000)
            # Create mock connection as fallback
            try:
                self.connection = AbletonConnection(mock=True)
                self.builder = ArrangementBuilder(self.connection)
            except:
                pass
    
    def on_section_selected(self, index: int):
        """Handle section selection."""
        if 0 <= index < len(self.sections):
            section = self.sections[index]
            self.chord_panel.set_selected_section(section)
            self.arrangement_view.set_selected_index(index)
            # Update theory panel with section
            if hasattr(self, 'theory_panel'):
                self.theory_panel.set_section(section._section)
        else:
            self.chord_panel.set_selected_section(None)
            self.arrangement_view.set_selected_index(-1)
            if hasattr(self, 'theory_panel'):
                self.theory_panel.set_section(None)
    
    def on_theory_chord_suggested(self, chord_name: str):
        """Handle theory panel chord suggestion."""
        # Forward to chord panel if it has a method to add chord
        if hasattr(self.chord_panel, 'add_chord_by_name'):
            self.chord_panel.add_chord_by_name(chord_name)
    
    def on_theory_progression_suggested(self, progression: List[str]):
        """Handle theory panel progression suggestion."""
        # Forward to chord panel if it has a method to add progression
        if hasattr(self.chord_panel, 'add_progression'):
            self.chord_panel.add_progression(progression)
    
    def on_sections_changed(self):
        """Handle sections modification."""
        # Update state manager
        self.state_manager.update_state(
            {"sections": [s._section.dict() for s in self.sections]},
            operation="sections_changed",
            description=f"Modified sections"
        )
        self.update_undo_redo_actions()
    
    def on_chords_changed(self):
        """Handle chords modification."""
        # Update state manager
        self.state_manager.update_state(
            {"sections": [s._section.dict() for s in self.sections]},
            operation="chords_changed",
            description="Modified chords"
        )
        self.update_undo_redo_actions()
        
        # Auto-save
        try:
            # Extract Pydantic sections from adapters
            pydantic_sections = [s._section for s in self.sections]
            save_sections(pydantic_sections, self.data_path)
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
    
    def save_sections(self):
        """Save sections to file."""
        try:
            # Extract Pydantic sections from adapters
            pydantic_sections = [s._section for s in self.sections]
            save_sections(pydantic_sections, self.data_path)
            self.status_bar.showMessage(f"Saved {len(self.sections)} sections", 3000)
        except Exception as e:
            logger.error(f"Error saving sections: {e}")
            QMessageBox.critical(self, "Save Error", f"Failed to save sections:\n{e}")
    
    def load_sections(self):
        """Load sections from default file."""
        try:
            if os.path.exists(self.data_path):
                # Load Pydantic sections and wrap in adapters
                pydantic_sections = load_sections(self.data_path)
                self.sections = [SectionAdapter(s) for s in pydantic_sections]
                self.section_panel.set_sections(self.sections)
                self.arrangement_view.set_sections(self.sections)
                
                # Update state manager
                self.state_manager.update_state(
                    {"sections": [s._section.dict() for s in self.sections]},
                    operation="load",
                    description=f"Loaded {len(self.sections)} sections"
                )
                self.update_undo_redo_actions()
                
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
                # Load Pydantic sections and wrap in adapters
                pydantic_sections = load_sections(file_path)
                self.sections = [SectionAdapter(s) for s in pydantic_sections]
                self.section_panel.set_sections(self.sections)
                self.arrangement_view.set_sections(self.sections)
                self.data_path = file_path
                self.status_bar.showMessage(f"Loaded {len(self.sections)} sections from {os.path.basename(file_path)}", 3000)
            except Exception as e:
                logger.error(f"Error loading sections: {e}")
                QMessageBox.critical(self, "Load Error", f"Failed to load sections:\n{e}")
    
    def undo(self):
        """Undo last operation."""
        state = self.state_manager.undo()
        if state:
            # Restore sections from state
            sections_data = state.get("sections", [])
            from arranger.models.section import Section
            pydantic_sections = [Section(**s) for s in sections_data]
            self.sections = [SectionAdapter(s) for s in pydantic_sections]
            self.section_panel.set_sections(self.sections)
            self.update_undo_redo_actions()
            self.status_bar.showMessage("Undone", 2000)
    
    def redo(self):
        """Redo last undone operation."""
        state = self.state_manager.redo()
        if state:
            # Restore sections from state
            sections_data = state.get("sections", [])
            from arranger.models.section import Section
            pydantic_sections = [Section(**s) for s in sections_data]
            self.sections = [SectionAdapter(s) for s in pydantic_sections]
            self.section_panel.set_sections(self.sections)
            self.update_undo_redo_actions()
            self.status_bar.showMessage("Redone", 2000)
    
    def update_undo_redo_actions(self):
        """Update undo/redo action enabled states."""
        if hasattr(self, 'undo_action'):
            self.undo_action.setEnabled(self.state_manager.can_undo)
        if hasattr(self, 'redo_action'):
            self.redo_action.setEnabled(self.state_manager.can_redo)
    
    def on_state_changed(self, operation: str):
        """Handle state change notification."""
        logger.debug(f"State changed: {operation}")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About Ableton Arranger",
                         "Ableton Arranger\n\n"
                         "Section-based arrangement helper for Ableton Live.\n\n"
                         "Port of REAPER Lua script to Python with PyQt5.\n\n"
                         "Requires AbletonOSC to be running in Ableton Live.")
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Auto-save on close
        try:
            # Extract Pydantic sections from adapters
            pydantic_sections = [s._section for s in self.sections]
            save_sections(pydantic_sections, self.data_path)
        except Exception as e:
            logger.error(f"Error auto-saving on close: {e}")
        event.accept()
