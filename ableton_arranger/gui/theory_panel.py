"""
Theory Panel - displays music theory guidance and suggestions.

Shows diatonic chords, modal degrees, progressions, and substitutions.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QGroupBox, QScrollArea,
                             QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Optional
import sys
import os

# Add python/src to path
workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
python_src = os.path.join(workspace_root, "python", "src")
if python_src not in sys.path:
    sys.path.insert(0, python_src)

from arranger.services.theory_service import TheoryService
from arranger.models.section import Section


class TheoryPanel(QWidget):
    """Panel displaying music theory guidance."""
    
    # Signals
    chord_suggested = pyqtSignal(str)  # Emits chord name when user clicks suggestion
    progression_suggested = pyqtSignal(list)  # Emits list of chord names
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theory_service = TheoryService()
        self.current_key = "C"
        self.current_mode = "major"
        self.current_section: Optional[Section] = None
        
        self.init_ui()
        self.update_display()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QLabel("Music Theory Guide")
        header.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(header)
        
        # Key and Mode selector
        key_mode_layout = QHBoxLayout()
        key_mode_layout.addWidget(QLabel("Key:"))
        
        self.key_combo = QComboBox()
        self.key_combo.addItems(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])
        self.key_combo.setCurrentText("C")
        self.key_combo.currentTextChanged.connect(self.on_key_changed)
        self.key_combo.setMaximumWidth(70)
        key_mode_layout.addWidget(self.key_combo)
        
        key_mode_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['major', 'minor', 'dorian', 'mixolydian', 'phrygian', 'lydian', 'locrian'])
        self.mode_combo.setCurrentText("major")
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        self.mode_combo.setMaximumWidth(100)
        key_mode_layout.addWidget(self.mode_combo)
        
        key_mode_layout.addStretch()
        layout.addLayout(key_mode_layout)
        
        # Diatonic Chords
        diatonic_group = QGroupBox("Diatonic Chords")
        diatonic_layout = QVBoxLayout()
        
        self.diatonic_label = QLabel("")
        self.diatonic_label.setWordWrap(True)
        self.diatonic_label.setStyleSheet("font-size: 11px;")
        diatonic_layout.addWidget(self.diatonic_label)
        
        self.diatonic_buttons_layout = QHBoxLayout()
        self.diatonic_buttons = []
        diatonic_layout.addLayout(self.diatonic_buttons_layout)
        
        diatonic_group.setLayout(diatonic_layout)
        layout.addWidget(diatonic_group)
        
        # Common Progressions
        progressions_group = QGroupBox("Common Progressions")
        progressions_layout = QVBoxLayout()
        
        self.progressions_scroll = QScrollArea()
        self.progressions_widget = QWidget()
        self.progressions_layout = QVBoxLayout()
        self.progressions_widget.setLayout(self.progressions_layout)
        self.progressions_scroll.setWidget(self.progressions_widget)
        self.progressions_scroll.setWidgetResizable(True)
        self.progressions_scroll.setMaximumHeight(120)
        progressions_layout.addWidget(self.progressions_scroll)
        
        progressions_group.setLayout(progressions_layout)
        layout.addWidget(progressions_group)
        
        # Cadences
        cadences_group = QGroupBox("Cadences")
        cadences_layout = QVBoxLayout()
        
        self.cadences_layout = QHBoxLayout()
        self.cadence_buttons = []
        cadences_layout.addLayout(self.cadences_layout)
        
        cadences_group.setLayout(cadences_layout)
        layout.addWidget(cadences_group)
        
        # Borrowed Chords
        borrowed_group = QGroupBox("Borrowed Chords (Modal Interchange)")
        borrowed_layout = QVBoxLayout()
        
        self.borrowed_label = QLabel("")
        self.borrowed_label.setWordWrap(True)
        self.borrowed_label.setStyleSheet("font-size: 11px; color: #888;")
        borrowed_layout.addWidget(self.borrowed_label)
        
        borrowed_group.setLayout(borrowed_layout)
        layout.addWidget(borrowed_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def on_key_changed(self, key: str):
        """Handle key change."""
        self.current_key = key
        self.update_display()
    
    def on_mode_changed(self, mode: str):
        """Handle mode change."""
        self.current_mode = mode
        self.update_display()
    
    def set_section(self, section: Optional[Section]):
        """Set the current section for analysis."""
        self.current_section = section
        if section:
            self.update_display()
    
    def update_display(self):
        """Update all theory displays."""
        self.update_diatonic_chords()
        self.update_progressions()
        self.update_cadences()
        self.update_borrowed_chords()
    
    def update_diatonic_chords(self):
        """Update diatonic chords display."""
        chords = self.theory_service.get_diatonic_chords(self.current_key, self.current_mode)
        
        # Update label
        if chords:
            chord_names = "  ".join([f"{c['roman']}: {c['name']}" for c in chords])
            self.diatonic_label.setText(f"Diatonic: {chord_names}")
        else:
            self.diatonic_label.setText("Diatonic: (none)")
        
        # Clear and recreate buttons
        for btn in self.diatonic_buttons:
            btn.deleteLater()
        self.diatonic_buttons.clear()
        
        # Create buttons for each chord
        for chord_info in chords:
            btn = QPushButton(f"{chord_info['roman']}\n{chord_info['name']}")
            btn.setMinimumSize(60, 50)
            btn.setMaximumSize(60, 50)
            btn.setToolTip(f"Click to add {chord_info['name']} to progression")
            btn.clicked.connect(lambda checked, name=chord_info['name']: self.chord_suggested.emit(name))
            self.diatonic_buttons.append(btn)
            self.diatonic_buttons_layout.addWidget(btn)
        
        self.diatonic_buttons_layout.addStretch()
    
    def update_progressions(self):
        """Update common progressions display."""
        # Clear existing
        while self.progressions_layout.count():
            child = self.progressions_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        progressions = self.theory_service.get_progressions(self.current_key, self.current_mode)
        
        for i, progression in enumerate(progressions[:5]):  # Show first 5
            prog_str = " → ".join(progression)
            btn = QPushButton(prog_str)
            btn.setMaximumHeight(25)
            btn.clicked.connect(lambda checked, p=progression: self.progression_suggested.emit(p))
            self.progressions_layout.addWidget(btn)
        
        if not progressions:
            label = QLabel("No progressions available")
            label.setStyleSheet("font-size: 11px; color: #888;")
            self.progressions_layout.addWidget(label)
        
        self.progressions_layout.addStretch()
    
    def update_cadences(self):
        """Update cadences display."""
        # Clear existing
        for btn in self.cadence_buttons:
            btn.deleteLater()
        self.cadence_buttons.clear()
        
        cadences = self.theory_service.get_cadences()
        
        for name, chords in cadences.items():
            btn = QPushButton(f"{name.title()}\n{' → '.join(chords)}")
            btn.setMinimumSize(80, 50)
            btn.setMaximumSize(80, 50)
            btn.setToolTip(f"Click to add {name} cadence")
            btn.clicked.connect(lambda checked, c=chords: self.progression_suggested.emit(c))
            self.cadence_buttons.append(btn)
            self.cadences_layout.addWidget(btn)
        
        self.cadences_layout.addStretch()
    
    def update_borrowed_chords(self):
        """Update borrowed chords display."""
        borrowed = self.theory_service.get_borrowed_chords_for_key(self.current_key, self.current_mode)
        
        if borrowed:
            borrowed_names = ", ".join([b["name"] for b in borrowed])
            self.borrowed_label.setText(f"Available: {borrowed_names}")
        else:
            self.borrowed_label.setText("No borrowed chords for this key/mode")
