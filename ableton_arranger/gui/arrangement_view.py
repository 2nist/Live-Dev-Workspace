"""
Arrangement Timeline View.

Displays sections as bars with chord indicators in a timeline.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont
from typing import List, Optional
import sys
import os

workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
python_src = os.path.join(workspace_root, "python", "src")
if python_src not in sys.path:
    sys.path.insert(0, python_src)

from arranger.utils.adapters import SectionAdapter


class ArrangementTimeline(QWidget):
    """Timeline widget showing sections as bars."""
    
    section_clicked = pyqtSignal(int)  # Emits section index
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sections: List[SectionAdapter] = []
        self.selected_index = -1
        self.bar_width = 60  # Pixels per bar
        self.bar_height = 40
        
        self.setMinimumHeight(100)
        self.setStyleSheet("background-color: #2b2b2b;")
    
    def set_sections(self, sections: List[SectionAdapter]):
        """Set sections to display."""
        self.sections = sections
        self.update()
    
    def set_selected_index(self, index: int):
        """Set selected section index."""
        self.selected_index = index
        self.update()
    
    def paintEvent(self, event):
        """Paint the timeline."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.sections:
            painter.setPen(QColor(200, 200, 200))
            painter.drawText(self.rect(), Qt.AlignCenter, "No sections - add sections to see timeline")
            return
        
        x = 10
        y = 10
        
        for i, section in enumerate(self.sections):
            # Calculate section width
            width = section.bars * self.bar_width
            
            # Draw section bar
            if i == self.selected_index:
                color = QColor(100, 150, 255)
            else:
                # Use section color or default
                section_color = section.get_color()
                r = (section_color >> 16) & 0xFF
                g = (section_color >> 8) & 0xFF
                b = section_color & 0xFF
                color = QColor(r, g, b)
            
            painter.setBrush(color)
            painter.setPen(QColor(255, 255, 255))
            painter.drawRoundedRect(x, y, width, self.bar_height, 5, 5)
            
            # Draw section label
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            painter.drawText(x + 5, y + 20, section.name)
            
            # Draw bar count
            painter.setFont(QFont("Arial", 8))
            painter.drawText(x + 5, y + 35, f"{section.bars} bars")
            
            # Draw chord indicators (simplified)
            if section.chords:
                chord_count = len(section.chords)
                indicator_width = min(width - 10, chord_count * 8)
                indicator_x = x + width - indicator_width - 5
                indicator_y = y + 5
                
                painter.setBrush(QColor(255, 255, 0))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(indicator_x, indicator_y, 8, 8)
                
                if chord_count > 1:
                    painter.drawText(indicator_x + 10, indicator_y + 8, f"{chord_count}")
            
            x += width + 5
        
        # Update widget size
        total_width = x + 10
        self.setMinimumWidth(total_width)
    
    def mousePressEvent(self, event):
        """Handle mouse click to select section."""
        if event.button() == Qt.LeftButton:
            x = event.x()
            y = event.y()
            
            # Find which section was clicked
            current_x = 10
            for i, section in enumerate(self.sections):
                width = section.bars * self.bar_width
                if (current_x <= x <= current_x + width and 
                    10 <= y <= 10 + self.bar_height):
                    self.selected_index = i
                    self.section_clicked.emit(i)
                    self.update()
                    return
                current_x += width + 5


class ArrangementView(QWidget):
    """Main arrangement view widget with timeline."""
    
    section_selected = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title = QLabel("Arrangement Timeline")
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(title)
        
        # Scrollable timeline
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarNever)
        
        self.timeline = ArrangementTimeline()
        self.timeline.section_clicked.connect(self.section_selected.emit)
        scroll.setWidget(self.timeline)
        
        layout.addWidget(scroll)
        self.setLayout(layout)
    
    def set_sections(self, sections: List[SectionAdapter]):
        """Set sections to display."""
        self.timeline.set_sections(sections)
    
    def set_selected_index(self, index: int):
        """Set selected section index."""
        self.timeline.set_selected_index(index)
