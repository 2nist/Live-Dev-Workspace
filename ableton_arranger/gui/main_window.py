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

from ableton_arranger.core.section import Section
from ableton_arranger.core.persistence import save_sections, load_sections
from ableton_arranger.core.connection import LiveConnection
from ableton_arranger.core.arrangement_builder import ArrangementBuilder
from ableton_arranger.gui.section_panel import SectionPanel
from ableton_arranger.gui.chord_panel import ChordPanel


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.sections: List[Section] = []
        # Get data directory path (relative to ableton_arranger package)
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(package_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        self.data_path = os.path.join(data_dir, "sections.json")
        self.connection: Optional[LiveConnection] = None
        self.builder: Optional[ArrangementBuilder] = None
        
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
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Central widget with splitter
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel: Sections
        self.section_panel = SectionPanel()
        self.section_panel.section_selected.connect(self.on_section_selected)
        self.section_panel.section_changed.connect(self.on_sections_changed)
        self.section_panel.rebuild_requested.connect(self.on_rebuild_requested)
        splitter.addWidget(self.section_panel)
        
        # Right panel: Chord editor
        self.chord_panel = ChordPanel()
        self.chord_panel.chords_changed.connect(self.on_chords_changed)
        splitter.addWidget(self.chord_panel)
        
        # Set splitter sizes (left: 420px, right: rest)
        splitter.setSizes([420, 800])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
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
        # Auto-save could be added here
        pass
    
    def on_chords_changed(self):
        """Handle chords modification."""
        # Save sections when chords change
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
                         "Ableton Arranger\n\n"
                         "Section-based arrangement helper for Ableton Live.\n\n"
                         "Port of REAPER Lua script to Python with PyQt5.\n\n"
                         "Requires AbletonOSC to be running in Ableton Live.")
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Auto-save on close
        try:
            save_sections(self.sections, self.data_path)
        except Exception as e:
            logger.error(f"Error auto-saving on close: {e}")
        event.accept()
