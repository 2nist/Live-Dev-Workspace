"""
Chord editor panel with interactive timeline and chord editing.
Right panel of the main window.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QSpinBox, QPushButton, QGroupBox, QScrollArea, QFrame,
                             QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Optional, List
from ableton_arranger.core.section import Section
from ableton_arranger.core.chord import (Chord, get_diatonic_chords, get_chord_name,
                                         get_chord_full_name, get_chord_substitutions,
                                         get_all_secondary_dominants, get_borrowed_chords)
from ableton_arranger.gui.chord_timeline import ChordTimeline
import ableton_arranger.config as config


class ChordPanel(QWidget):
    """Full chord editor panel."""
    
    # Signals
    chords_changed = pyqtSignal()  # Emits when chords are modified
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_section: Optional[Section] = None
        self.chords: List[Chord] = []
        self.selected_chord_idx: Optional[int] = None
        
        # Editor state
        self.key_root = 0  # C=0
        self.scale_type = "ionian"
        self.chord_octave = 4
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        self.section_label = QLabel("Select a section to edit chords")
        self.section_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(self.section_label)
        
        self.section_info_label = QLabel("")
        self.section_info_label.setStyleSheet("font-size: 11px; color: #888;")
        header_layout.addStretch()
        header_layout.addWidget(self.section_info_label)
        layout.addLayout(header_layout)
        
        # Key/Scale/Octave selector
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Key:"))
        
        self.key_combo = QComboBox()
        self.key_combo.addItems(config.NOTE_NAMES)
        self.key_combo.setCurrentIndex(0)
        self.key_combo.currentIndexChanged.connect(self.on_key_changed)
        self.key_combo.setMaximumWidth(60)
        key_layout.addWidget(self.key_combo)
        
        key_layout.addWidget(QLabel("Scale:"))
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(config.SCALE_ORDER)
        self.scale_combo.setCurrentText("ionian")
        self.scale_combo.currentTextChanged.connect(self.on_scale_changed)
        self.scale_combo.setMaximumWidth(100)
        key_layout.addWidget(self.scale_combo)
        
        key_layout.addWidget(QLabel("Oct:"))
        self.octave_spin = QSpinBox()
        self.octave_spin.setMinimum(2)
        self.octave_spin.setMaximum(6)
        self.octave_spin.setValue(4)
        self.octave_spin.valueChanged.connect(self.on_octave_changed)
        self.octave_spin.setMaximumWidth(50)
        key_layout.addWidget(self.octave_spin)
        
        key_layout.addStretch()
        layout.addLayout(key_layout)
        
        # Timeline
        timeline_label = QLabel("Timeline (click chord to select, drag to move):")
        timeline_label.setStyleSheet("font-size: 11px;")
        layout.addWidget(timeline_label)
        
        self.timeline = ChordTimeline()
        self.timeline.chord_selected.connect(self.on_timeline_chord_selected)
        self.timeline.chord_moved.connect(self.on_timeline_chord_moved)
        self.timeline.chord_resized.connect(self.on_timeline_chord_resized)
        self.timeline.chord_added.connect(self.on_timeline_chord_added)
        layout.addWidget(self.timeline)
        
        # Diatonic chord palette
        palette_label = QLabel("Diatonic Chords: (click to append)")
        palette_label.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(palette_label)
        
        palette_layout = QHBoxLayout()
        self.diatonic_buttons = []
        roman_numerals = ["I", "ii", "iii", "IV", "V", "vi", "vii°"]
        
        for i in range(7):
            btn = QPushButton()
            btn.setMinimumSize(55, 36)
            btn.setMaximumSize(55, 36)
            btn.clicked.connect(lambda checked, idx=i: self.on_diatonic_clicked(idx))
            self.diatonic_buttons.append(btn)
            palette_layout.addWidget(btn)
        
        palette_layout.addStretch()
        layout.addLayout(palette_layout)
        
        self.update_diatonic_palette()
        
        # Selected chord editor
        self.chord_editor_group = QGroupBox("Selected Chord")
        self.chord_editor_group.setVisible(False)
        chord_editor_layout = QVBoxLayout()
        
        self.selected_chord_label = QLabel("")
        self.selected_chord_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #FFFF80;")
        chord_editor_layout.addWidget(self.selected_chord_label)
        
        # Root, Type, Inversion row
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Root:"))
        self.root_combo = QComboBox()
        self.root_combo.addItems(config.NOTE_NAMES)
        self.root_combo.currentIndexChanged.connect(self.on_chord_root_changed)
        self.root_combo.setMaximumWidth(60)
        row1.addWidget(self.root_combo)
        
        row1.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.currentIndexChanged.connect(self.on_chord_type_changed)
        self.type_combo.setMaximumWidth(90)
        row1.addWidget(self.type_combo)
        
        row1.addWidget(QLabel("Inv:"))
        self.inv_combo = QComboBox()
        self.inv_combo.addItems(config.INVERSION_NAMES)
        self.inv_combo.currentIndexChanged.connect(self.on_chord_inv_changed)
        self.inv_combo.setMaximumWidth(80)
        row1.addWidget(self.inv_combo)
        
        row1.addStretch()
        chord_editor_layout.addLayout(row1)
        
        # Timing row
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Beat:"))
        self.start_beat_spin = QSpinBox()
        self.start_beat_spin.setMinimum(0)
        self.start_beat_spin.setMaximum(999)
        self.start_beat_spin.valueChanged.connect(self.on_start_beat_changed)
        self.start_beat_spin.setMaximumWidth(60)
        row2.addWidget(self.start_beat_spin)
        
        row2.addWidget(QLabel("Dur:"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setMinimum(1)
        self.duration_spin.setMaximum(999)
        self.duration_spin.valueChanged.connect(self.on_duration_changed)
        self.duration_spin.setMaximumWidth(60)
        row2.addWidget(self.duration_spin)
        
        # Duration quick buttons
        for dur in [1, 2, 4, 8]:
            btn = QPushButton(str(dur))
            btn.setMaximumSize(30, 25)
            btn.clicked.connect(lambda checked, d=dur: self.set_duration(d))
            row2.addWidget(btn)
        
        row2.addStretch()
        chord_editor_layout.addLayout(row2)
        
        # Bass and Octave row
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Bass:"))
        self.bass_combo = QComboBox()
        self.bass_combo.addItem("(root)")
        self.bass_combo.addItems(config.NOTE_NAMES)
        self.bass_combo.currentIndexChanged.connect(self.on_bass_changed)
        self.bass_combo.setMaximumWidth(70)
        row3.addWidget(self.bass_combo)
        
        row3.addWidget(QLabel("Oct:"))
        self.chord_octave_spin = QSpinBox()
        self.chord_octave_spin.setMinimum(2)
        self.chord_octave_spin.setMaximum(6)
        self.chord_octave_spin.setValue(4)
        self.chord_octave_spin.valueChanged.connect(self.on_chord_octave_changed)
        self.chord_octave_spin.setMaximumWidth(50)
        row3.addWidget(self.chord_octave_spin)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_selected_chord)
        remove_btn.setMaximumWidth(70)
        row3.addWidget(remove_btn)
        
        row3.addStretch()
        chord_editor_layout.addLayout(row3)
        
        self.chord_editor_group.setLayout(chord_editor_layout)
        layout.addWidget(self.chord_editor_group)
        
        # Substitutions section (collapsible)
        self.substitutions_group = QGroupBox("Substitutions & Theory")
        self.substitutions_group.setCheckable(True)
        self.substitutions_group.setChecked(False)
        subs_layout = QVBoxLayout()
        self.substitutions_widget = QWidget()
        self.subs_layout = QVBoxLayout()
        self.substitutions_widget.setLayout(self.subs_layout)
        subs_layout.addWidget(self.substitutions_widget)
        self.substitutions_group.setLayout(subs_layout)
        layout.addWidget(self.substitutions_group)
        
        # Progression presets
        presets_group = QGroupBox("Progression Presets")
        presets_layout = QVBoxLayout()
        presets_buttons_layout = QHBoxLayout()
        presets_buttons_layout.setSpacing(5)
        
        for preset in config.PROGRESSION_PRESETS:
            btn = QPushButton(preset["name"])
            btn.setMaximumHeight(25)
            btn.clicked.connect(lambda checked, p=preset: self.apply_progression_preset(p))
            presets_buttons_layout.addWidget(btn)
        
        presets_buttons_layout.addStretch()
        presets_layout.addLayout(presets_buttons_layout)
        presets_group.setLayout(presets_layout)
        layout.addWidget(presets_group)
        
        # Current progression display
        self.progression_label = QLabel("Progression: (empty)")
        self.progression_label.setStyleSheet("font-size: 11px; color: #666;")
        self.progression_label.setWordWrap(True)
        layout.addWidget(self.progression_label)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        apply_btn = QPushButton("Apply to MIDI")
        apply_btn.clicked.connect(self.apply_to_midi)
        actions_layout.addWidget(apply_btn)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_all)
        actions_layout.addWidget(clear_btn)
        
        sort_btn = QPushButton("Sort by Time")
        sort_btn.clicked.connect(self.sort_chords)
        actions_layout.addWidget(sort_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def set_selected_section(self, section: Optional[Section]):
        """Update the panel to show the selected section."""
        self.selected_section = section
        if section:
            self.section_label.setText(f"Chords for: {section.name}")
            self.section_info_label.setText(f"{section.bars} bars | {section.timesig_num}/{section.timesig_denom} time")
            
            # Load chords from section
            self.chords = []
            for chord_data in section.chords:
                if isinstance(chord_data, dict):
                    self.chords.append(Chord.from_dict(chord_data))
                elif isinstance(chord_data, Chord):
                    self.chords.append(chord_data)
            
            # Update timeline
            self.timeline.set_section_info(section.bars, section.timesig_num, section.timesig_denom)
            self.timeline.set_chords(self.chords)
            self.selected_chord_idx = None
            self.update_chord_editor()
            self.update_progression_display()
        else:
            self.section_label.setText("Select a section to edit chords")
            self.section_info_label.setText("")
            self.chords = []
            self.timeline.set_chords([])
            self.selected_chord_idx = None
            self.chord_editor_group.setVisible(False)
            self.progression_label.setText("Progression: (empty)")
    
    def update_diatonic_palette(self):
        """Update the diatonic chord palette buttons."""
        diatonic = get_diatonic_chords(self.key_root, self.scale_type)
        roman_numerals = ["I", "ii", "iii", "IV", "V", "vi", "vii°"]
        
        for i, btn in enumerate(self.diatonic_buttons):
            if i < len(diatonic):
                chord_info = diatonic[i]
                chord_name = get_chord_name(chord_info["root"], chord_info["type_idx"])
                btn.setText(f"{roman_numerals[i]}\n{chord_name}")
                btn.setToolTip(f"Add {chord_name} to progression")
                btn.setEnabled(True)
            else:
                btn.setText("")
                btn.setEnabled(False)
    
    def on_key_changed(self, index):
        """Handle key change."""
        self.key_root = index
        self.update_diatonic_palette()
    
    def on_scale_changed(self, text):
        """Handle scale change."""
        self.scale_type = text
        self.update_diatonic_palette()
    
    def on_octave_changed(self, value):
        """Handle octave change."""
        self.chord_octave = value
    
    def on_timeline_chord_selected(self, idx):
        """Handle chord selection from timeline."""
        self.selected_chord_idx = idx if idx >= 0 else None
        self.timeline.set_selected_chord(self.selected_chord_idx)
        self.update_chord_editor()
    
    def on_timeline_chord_moved(self, idx, new_start):
        """Handle chord move from timeline."""
        if 0 <= idx < len(self.chords):
            self.chords_changed.emit()
            self.save_chords_to_section()
            self.update_progression_display()
    
    def on_timeline_chord_resized(self, idx, new_start, new_duration):
        """Handle chord resize from timeline."""
        if 0 <= idx < len(self.chords):
            self.chords[idx].start_beat = new_start
            self.chords[idx].duration_beats = new_duration
            self.chords_changed.emit()
            self.save_chords_to_section()
            self.update_progression_display()
            self.update_chord_editor()
    
    def on_timeline_chord_added(self, beat):
        """Handle chord addition from timeline double-click."""
        if not self.selected_section:
            return
        
        diatonic = get_diatonic_chords(self.key_root, self.scale_type)
        if not diatonic:
            return
        
        beats_per_bar = self.selected_section.timesig_num * (4.0 / self.selected_section.timesig_denom)
        total_beats = self.selected_section.bars * beats_per_bar
        
        new_chord = Chord(
            root=diatonic[0]["root"],
            type_idx=diatonic[0]["type_idx"],
            start_beat=beat,
            duration_beats=min(beats_per_bar, total_beats - beat),
            inversion=0,
            octave=self.chord_octave
        )
        
        self.chords.append(new_chord)
        self.selected_chord_idx = len(self.chords) - 1
        self.timeline.set_chords(self.chords)
        self.timeline.set_selected_chord(self.selected_chord_idx)
        self.chords_changed.emit()
        self.save_chords_to_section()
        self.update_chord_editor()
        self.update_progression_display()
    
    def on_diatonic_clicked(self, degree_idx):
        """Handle diatonic chord button click."""
        if not self.selected_section:
            return
        
        diatonic = get_diatonic_chords(self.key_root, self.scale_type)
        if degree_idx >= len(diatonic):
            return
        
        chord_info = diatonic[degree_idx]
        beats_per_bar = self.selected_section.timesig_num * (4.0 / self.selected_section.timesig_denom)
        total_beats = self.selected_section.bars * beats_per_bar
        
        # Find next available beat
        next_beat = 0
        if self.chords:
            last = self.chords[-1]
            next_beat = last.start_beat + last.duration_beats
        
        if next_beat < total_beats:
            new_chord = Chord(
                root=chord_info["root"],
                type_idx=chord_info["type_idx"],
                start_beat=next_beat,
                duration_beats=min(beats_per_bar, total_beats - next_beat),
                inversion=0,
                octave=self.chord_octave
            )
            self.chords.append(new_chord)
            self.selected_chord_idx = len(self.chords) - 1
            self.timeline.set_chords(self.chords)
            self.timeline.set_selected_chord(self.selected_chord_idx)
            self.chords_changed.emit()
            self.save_chords_to_section()
            self.update_chord_editor()
            self.update_progression_display()
    
    def update_chord_editor(self):
        """Update the chord editor controls."""
        if self.selected_chord_idx is None or self.selected_chord_idx >= len(self.chords):
            self.chord_editor_group.setVisible(False)
            self.update_substitutions()
            return
        
        chord = self.chords[self.selected_chord_idx]
        self.chord_editor_group.setVisible(True)
        
        # Update selected chord label
        self.selected_chord_label.setText(f"Selected Chord: {get_chord_full_name(chord)}")
        
        # Update controls
        self.root_combo.setCurrentIndex(chord.root)
        
        # Update type combo (populate if needed)
        if self.type_combo.count() == 0:
            self.populate_type_combo()
        self.type_combo.setCurrentIndex(chord.type_idx - 1)
        
        # Update inversion
        max_inv = min(len(config.CHORD_TYPES[chord.type_idx - 1]["intervals"]) - 1, 3) if chord.type_idx <= len(config.CHORD_TYPES) else 2
        while self.inv_combo.count() > max_inv + 1:
            self.inv_combo.removeItem(self.inv_combo.count() - 1)
        self.inv_combo.setCurrentIndex(chord.inversion)
        
        # Update timing
        if self.selected_section:
            total_beats = self.selected_section.total_beats
            self.start_beat_spin.setMaximum(int(total_beats))
            self.duration_spin.setMaximum(int(total_beats - chord.start_beat))
        else:
            self.start_beat_spin.setMaximum(999)
            self.duration_spin.setMaximum(999)
        self.start_beat_spin.setValue(int(chord.start_beat))
        self.duration_spin.setValue(int(chord.duration_beats))
        
        # Update bass
        if chord.bass_note is None:
            self.bass_combo.setCurrentIndex(0)
        else:
            self.bass_combo.setCurrentIndex(chord.bass_note + 1)
        
        # Update octave
        self.chord_octave_spin.setValue(chord.octave)
        
        self.update_substitutions()
    
    def populate_type_combo(self):
        """Populate the chord type combo box."""
        self.type_combo.clear()
        for i, chord_type in enumerate(config.CHORD_TYPES):
            display = chord_type["display"] if chord_type["display"] else "maj"
            self.type_combo.addItem(display)
    
    def on_chord_root_changed(self, index):
        """Handle chord root change."""
        if self.selected_chord_idx is not None and self.selected_chord_idx < len(self.chords):
            self.chords[self.selected_chord_idx].root = index
            self.chords_changed.emit()
            self.save_chords_to_section()
            self.update_chord_editor()
            self.timeline.update()
            self.update_progression_display()
    
    def on_chord_type_changed(self, index):
        """Handle chord type change."""
        if self.selected_chord_idx is not None and self.selected_chord_idx < len(self.chords):
            self.chords[self.selected_chord_idx].type_idx = index + 1
            self.chords_changed.emit()
            self.save_chords_to_section()
            self.update_chord_editor()
            self.timeline.update()
            self.update_progression_display()
    
    def on_chord_inv_changed(self, index):
        """Handle inversion change."""
        if self.selected_chord_idx is not None and self.selected_chord_idx < len(self.chords):
            self.chords[self.selected_chord_idx].inversion = index
            self.chords_changed.emit()
            self.save_chords_to_section()
            self.timeline.update()
            self.update_progression_display()
    
    def on_start_beat_changed(self, value):
        """Handle start beat change."""
        if self.selected_chord_idx is not None and self.selected_chord_idx < len(self.chords):
            self.chords[self.selected_chord_idx].start_beat = float(value)
            self.chords_changed.emit()
            self.save_chords_to_section()
            self.timeline.update()
            self.update_progression_display()
    
    def on_duration_changed(self, value):
        """Handle duration change."""
        if self.selected_chord_idx is not None and self.selected_chord_idx < len(self.chords):
            chord = self.chords[self.selected_chord_idx]
            if self.selected_section:
                max_dur = self.selected_section.total_beats - chord.start_beat
            else:
                max_dur = 999
            chord.duration_beats = float(min(value, max_dur))
            self.chords_changed.emit()
            self.save_chords_to_section()
            self.timeline.update()
            self.update_progression_display()
    
    def set_duration(self, duration):
        """Set duration using quick button."""
        if self.selected_chord_idx is not None and self.selected_chord_idx < len(self.chords):
            chord = self.chords[self.selected_chord_idx]
            if self.selected_section:
                max_dur = self.selected_section.total_beats - chord.start_beat
            else:
                max_dur = 999
            chord.duration_beats = float(min(duration, max_dur))
            self.duration_spin.setValue(int(chord.duration_beats))
            self.chords_changed.emit()
            self.save_chords_to_section()
            self.timeline.update()
            self.update_progression_display()
    
    def on_bass_changed(self, index):
        """Handle bass note change."""
        if self.selected_chord_idx is not None and self.selected_chord_idx < len(self.chords):
            self.chords[self.selected_chord_idx].bass_note = None if index == 0 else index - 1
            self.chords_changed.emit()
            self.save_chords_to_section()
            self.timeline.update()
            self.update_progression_display()
    
    def on_chord_octave_changed(self, value):
        """Handle chord octave change."""
        if self.selected_chord_idx is not None and self.selected_chord_idx < len(self.chords):
            self.chords[self.selected_chord_idx].octave = value
            self.chords_changed.emit()
            self.save_chords_to_section()
    
    def remove_selected_chord(self):
        """Remove the selected chord."""
        if self.selected_chord_idx is not None and self.selected_chord_idx < len(self.chords):
            self.chords.pop(self.selected_chord_idx)
            self.selected_chord_idx = None
            self.timeline.set_chords(self.chords)
            self.timeline.set_selected_chord(None)
            self.chords_changed.emit()
            self.save_chords_to_section()
            self.update_chord_editor()
            self.update_progression_display()
    
    def update_substitutions(self):
        """Update the substitutions section."""
        # Clear existing widgets
        while self.subs_layout.count():
            child = self.subs_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if self.selected_chord_idx is None or self.selected_chord_idx >= len(self.chords):
            return
        
        chord = self.chords[self.selected_chord_idx]
        
        # Substitutions
        subs = get_chord_substitutions(chord)
        if subs:
            subs_label = QLabel("Replace with:")
            self.subs_layout.addWidget(subs_label)
            
            subs_layout = QHBoxLayout()
            for sub in subs:
                sub_name = get_chord_name(sub.root, sub.type_idx)
                btn = QPushButton(f"{sub_name}")
                btn.setMaximumHeight(25)
                btn.clicked.connect(lambda checked, s=sub: self.apply_substitution(s))
                subs_layout.addWidget(btn)
            subs_layout.addStretch()
            self.subs_layout.addLayout(subs_layout)
        
        # Secondary dominants
        sec_doms = get_all_secondary_dominants(self.key_root, self.scale_type)
        if sec_doms:
            sd_label = QLabel("Insert Secondary Dominant before:")
            self.subs_layout.addWidget(sd_label)
            
            sd_layout = QHBoxLayout()
            for sd in sec_doms:
                sd_name = get_chord_name(sd["root"], sd["type_idx"])
                btn = QPushButton(f"{sd['name']} ({sd_name})")
                btn.setMaximumHeight(25)
                btn.clicked.connect(lambda checked, s=sd: self.insert_secondary_dominant(s))
                sd_layout.addWidget(btn)
            sd_layout.addStretch()
            self.subs_layout.addLayout(sd_layout)
        
        # Borrowed chords
        borrowed = get_borrowed_chords(self.key_root, self.scale_type)
        if borrowed:
            bc_label = QLabel("Borrowed Chords (Modal Interchange):")
            self.subs_layout.addWidget(bc_label)
            
            bc_layout = QHBoxLayout()
            for bc in borrowed:
                bc_name = get_chord_name(bc["root"], bc["type_idx"])
                btn = QPushButton(f"{bc['name']} ({bc_name})")
                btn.setMaximumHeight(25)
                btn.clicked.connect(lambda checked, b=bc: self.apply_borrowed_chord(b))
                bc_layout.addWidget(btn)
            bc_layout.addStretch()
            self.subs_layout.addLayout(bc_layout)
        
        self.subs_layout.addStretch()
    
    def apply_substitution(self, sub: Chord):
        """Apply a chord substitution."""
        if self.selected_chord_idx is not None and self.selected_chord_idx < len(self.chords):
            chord = self.chords[self.selected_chord_idx]
            chord.root = sub.root
            chord.type_idx = sub.type_idx
            chord.inversion = 0
            chord.bass_note = None
            self.chords_changed.emit()
            self.save_chords_to_section()
            self.update_chord_editor()
            self.timeline.update()
            self.update_progression_display()
    
    def insert_secondary_dominant(self, sd: dict):
        """Insert a secondary dominant before the current chord."""
        if self.selected_chord_idx is not None and self.selected_chord_idx < len(self.chords):
            chord = self.chords[self.selected_chord_idx]
            new_sd = Chord(
                root=sd["root"],
                type_idx=sd["type_idx"],
                start_beat=max(0, chord.start_beat - 2),
                duration_beats=2,
                inversion=0,
                octave=self.chord_octave
            )
            self.chords.insert(self.selected_chord_idx, new_sd)
            self.selected_chord_idx += 1
            self.timeline.set_chords(self.chords)
            self.timeline.set_selected_chord(self.selected_chord_idx)
            self.chords_changed.emit()
            self.save_chords_to_section()
            self.update_chord_editor()
            self.update_progression_display()
    
    def apply_borrowed_chord(self, bc: dict):
        """Apply a borrowed chord."""
        if self.selected_chord_idx is not None and self.selected_chord_idx < len(self.chords):
            chord = self.chords[self.selected_chord_idx]
            chord.root = bc["root"]
            chord.type_idx = bc["type_idx"]
            chord.inversion = 0
            self.chords_changed.emit()
            self.save_chords_to_section()
            self.update_chord_editor()
            self.timeline.update()
            self.update_progression_display()
    
    def apply_progression_preset(self, preset: dict):
        """Apply a progression preset."""
        if not self.selected_section:
            return
        
        self.chords = []
        diatonic = get_diatonic_chords(self.key_root, self.scale_type)
        beats_per_bar = self.selected_section.timesig_num * (4.0 / self.selected_section.timesig_denom)
        total_beats = self.selected_section.bars * beats_per_bar
        beat = 0
        dur = beats_per_bar
        
        for degree in preset["degrees"]:
            if beat + dur <= total_beats and 1 <= degree <= 7:
                chord_info = diatonic[degree - 1]
                self.chords.append(Chord(
                    root=chord_info["root"],
                    type_idx=chord_info["type_idx"],
                    start_beat=beat,
                    duration_beats=dur,
                    inversion=0,
                    octave=self.chord_octave
                ))
                beat += dur
        
        self.selected_chord_idx = None
        self.timeline.set_chords(self.chords)
        self.timeline.set_selected_chord(None)
        self.chords_changed.emit()
        self.save_chords_to_section()
        self.update_chord_editor()
        self.update_progression_display()
    
    def update_progression_display(self):
        """Update the progression text display."""
        if self.chords:
            prog_text = " → ".join([get_chord_full_name(c) for c in self.chords])
            self.progression_label.setText(f"Progression: {prog_text}")
            self.progression_label.setStyleSheet("font-size: 11px; color: #00FFFF;")
        else:
            self.progression_label.setText("Progression: (empty - double-click timeline or use palette)")
            self.progression_label.setStyleSheet("font-size: 11px; color: #666;")
    
    def apply_to_midi(self):
        """Apply chords to MIDI (placeholder for now)."""
        # TODO: Implement MIDI application
        pass
    
    def clear_all(self):
        """Clear all chords."""
        self.chords = []
        self.selected_chord_idx = None
        self.timeline.set_chords([])
        self.timeline.set_selected_chord(None)
        self.chords_changed.emit()
        self.save_chords_to_section()
        self.update_chord_editor()
        self.update_progression_display()
    
    def sort_chords(self):
        """Sort chords by start time."""
        self.chords.sort(key=lambda c: c.start_beat)
        self.selected_chord_idx = None
        self.timeline.set_chords(self.chords)
        self.timeline.set_selected_chord(None)
        self.chords_changed.emit()
        self.save_chords_to_section()
        self.update_progression_display()
    
    def save_chords_to_section(self):
        """Save chords back to the selected section."""
        if self.selected_section:
            self.selected_section.chords = [c.to_dict() for c in self.chords]
