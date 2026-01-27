"""
Section management panel.
Left panel of the main window with section list and controls.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QComboBox, QLineEdit,
                             QSpinBox, QLabel, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from typing import List, Optional
from ableton_arranger.core.section import Section
import ableton_arranger.config as config


class SectionPanel(QWidget):
    """Panel for managing sections."""
    
    # Signals
    section_selected = pyqtSignal(int)  # Emits section index
    section_changed = pyqtSignal()  # Emits when sections are modified
    rebuild_requested = pyqtSignal()  # Emits when rebuild is requested
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sections: List[Section] = []
        self.selected_index = -1
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Sections")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #0a0; font-size: 11px;")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.add_section)
        button_layout.addWidget(self.add_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_selected)
        button_layout.addWidget(self.delete_btn)
        
        self.rebuild_btn = QPushButton("Rebuild")
        self.rebuild_btn.clicked.connect(self.rebuild_arrangement)
        button_layout.addWidget(self.rebuild_btn)
        
        layout.addLayout(button_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Bars", "Time Sig", "Tempo"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 50)
        self.table.setColumnWidth(2, 70)
        self.table.setColumnWidth(3, 60)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemChanged.connect(self.on_item_changed)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def set_sections(self, sections: List[Section]):
        """Set the sections list and refresh the table."""
        self.sections = sections
        self.refresh_table()
    
    def refresh_table(self):
        """Refresh the table with current sections."""
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.sections))
        
        for i, section in enumerate(self.sections):
            # Name column - combo box for presets + text field
            name_widget = QWidget()
            name_layout = QHBoxLayout()
            name_layout.setContentsMargins(2, 2, 2, 2)
            
            preset_combo = QComboBox()
            preset_combo.addItems(config.SECTION_PRESETS)
            preset_combo.setCurrentText(section.name if section.name in config.SECTION_PRESETS else "Custom")
            preset_combo.currentTextChanged.connect(lambda text, idx=i: self.on_preset_changed(idx, text))
            preset_combo.setMaximumWidth(100)
            name_layout.addWidget(preset_combo)
            
            name_edit = QLineEdit(section.name)
            name_edit.editingFinished.connect(lambda idx=i: self.on_name_changed(idx))
            name_layout.addWidget(name_edit)
            
            name_widget.setLayout(name_layout)
            self.table.setCellWidget(i, 0, name_widget)
            
            # Bars column
            bars_spin = QSpinBox()
            bars_spin.setMinimum(1)
            bars_spin.setMaximum(256)
            bars_spin.setValue(section.bars)
            bars_spin.valueChanged.connect(lambda val, idx=i: self.on_bars_changed(idx, val))
            self.table.setCellWidget(i, 1, bars_spin)
            
            # Time signature column
            ts_combo = QComboBox()
            for ts in config.TIME_SIG_PRESETS:
                ts_combo.addItem(ts["display"], ts)
            # Find current time sig
            current_ts = f"{section.timesig_num}/{section.timesig_denom}"
            index = ts_combo.findText(current_ts)
            if index >= 0:
                ts_combo.setCurrentIndex(index)
            ts_combo.currentIndexChanged.connect(lambda idx, row=i: self.on_timesig_changed(row, idx))
            self.table.setCellWidget(i, 2, ts_combo)
            
            # Tempo column
            tempo_spin = QSpinBox()
            tempo_spin.setMinimum(0)
            tempo_spin.setMaximum(300)
            tempo_spin.setValue(int(section.tempo) if section.tempo else 0)
            tempo_spin.setSpecialValueText("--")
            tempo_spin.valueChanged.connect(lambda val, idx=i: self.on_tempo_changed(idx, val))
            self.table.setCellWidget(i, 3, tempo_spin)
            
            # Color row background based on section name
            color = section.get_color()
            # Convert REAPER color (0xBBGGRR) to QColor
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF
            bg_color = QColor(r, g, b)
            # Set background on widgets
            for col in range(4):
                widget = self.table.cellWidget(i, col)
                if widget:
                    widget.setStyleSheet(f"background-color: rgb({r}, {g}, {b});")
                else:
                    # If no widget, create an item for background
                    item = QTableWidgetItem()
                    item.setBackground(bg_color)
                    if (r + g + b) < 384:
                        item.setForeground(QColor(255, 255, 255))
                    self.table.setItem(i, col, item)
        
        # Highlight selected row
        if 0 <= self.selected_index < len(self.sections):
            self.table.selectRow(self.selected_index)
        
        self.table.blockSignals(False)
    
    def on_selection_changed(self):
        """Handle table selection change."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            self.selected_index = selected_rows[0].row()
            self.section_selected.emit(self.selected_index)
        else:
            self.selected_index = -1
            self.section_selected.emit(-1)
    
    def on_item_changed(self, item):
        """Handle item change in table."""
        pass  # Handled by individual widget signals
    
    def on_preset_changed(self, row: int, text: str):
        """Handle preset combo box change."""
        if 0 <= row < len(self.sections):
            if text != "Custom":
                self.sections[row].name = text
                self.refresh_table()
                self.section_changed.emit()
    
    def on_name_changed(self, row: int):
        """Handle name field change."""
        if 0 <= row < len(self.sections):
            widget = self.table.cellWidget(row, 0)
            if widget:
                name_edit = widget.findChild(QLineEdit)
                if name_edit:
                    self.sections[row].name = name_edit.text()
                    self.refresh_table()
                    self.section_changed.emit()
    
    def on_bars_changed(self, row: int, value: int):
        """Handle bars spin box change."""
        if 0 <= row < len(self.sections):
            self.sections[row].bars = value
            self.section_changed.emit()
    
    def on_timesig_changed(self, row: int, combo_index: int):
        """Handle time signature combo box change."""
        if 0 <= row < len(self.sections):
            widget = self.table.cellWidget(row, 2)
            if isinstance(widget, QComboBox):
                ts_data = widget.itemData(combo_index)
                if ts_data:
                    self.sections[row].timesig_num = ts_data["num"]
                    self.sections[row].timesig_denom = ts_data["denom"]
                    self.section_changed.emit()
    
    def on_tempo_changed(self, row: int, value: int):
        """Handle tempo spin box change."""
        if 0 <= row < len(self.sections):
            self.sections[row].tempo = float(value) if value > 0 else None
            self.section_changed.emit()
    
    def add_section(self):
        """Add a new section."""
        new_section = Section(
            name=f"Section {len(self.sections) + 1}",
            bars=4,
            tempo=None
        )
        self.sections.append(new_section)
        self.refresh_table()
        self.selected_index = len(self.sections) - 1
        self.table.selectRow(self.selected_index)
        self.section_selected.emit(self.selected_index)
        self.section_changed.emit()
        self.set_status(f"Added section: {new_section.name}")
    
    def delete_selected(self):
        """Delete the selected section."""
        if 0 <= self.selected_index < len(self.sections):
            deleted = self.sections.pop(self.selected_index)
            self.selected_index = min(self.selected_index, len(self.sections) - 1)
            self.refresh_table()
            if self.selected_index >= 0:
                self.table.selectRow(self.selected_index)
                self.section_selected.emit(self.selected_index)
            else:
                self.section_selected.emit(-1)
            self.section_changed.emit()
            self.set_status(f"Deleted section: {deleted.name}")
    
    def rebuild_arrangement(self):
        """Request arrangement rebuild."""
        self.rebuild_requested.emit()
    
    def set_status(self, message: str):
        """Set status message."""
        self.status_label.setText(message)
    
    def get_selected_section(self) -> Optional[Section]:
        """Get the currently selected section."""
        if 0 <= self.selected_index < len(self.sections):
            return self.sections[self.selected_index]
        return None
