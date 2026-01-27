"""
Custom timeline widget for chord visualization and interaction.
"""
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from typing import List, Optional, Tuple
from ableton_arranger.core.chord import Chord, get_chord_full_name
import ableton_arranger.config as config


class ChordTimeline(QWidget):
    """Interactive timeline widget for chord editing."""
    
    # Signals
    chord_selected = pyqtSignal(int)  # Emits chord index
    chord_moved = pyqtSignal(int, float)  # Emits chord index, new start_beat
    chord_resized = pyqtSignal(int, float, float)  # Emits chord index, new start, new duration
    chord_added = pyqtSignal(float)  # Emits beat position
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chords: List[Chord] = []
        self.selected_chord_idx: Optional[int] = None
        self.dragging_chord_idx: Optional[int] = None
        self.drag_mode: Optional[str] = None  # "move", "resize_left", "resize_right"
        self.drag_start_beat: float = 0.0
        self.drag_start_pos: QPoint = QPoint()
        
        self.bars = 4
        self.timesig_num = 4
        self.timesig_denom = 4
        self.beats_per_bar = 4
        self.total_beats = 16
        
        self.handle_width = 6  # pixels
        self.timeline_height = 60
        
        self.setMinimumHeight(self.timeline_height + 20)
        self.setMouseTracking(True)
    
    def set_section_info(self, bars: int, timesig_num: int, timesig_denom: int):
        """Update section information."""
        self.bars = bars
        self.timesig_num = timesig_num
        self.timesig_denom = timesig_denom
        self.beats_per_bar = timesig_num * (4.0 / timesig_denom)
        self.total_beats = bars * self.beats_per_bar
        self.update()
    
    def set_chords(self, chords: List[Chord]):
        """Set the chords to display."""
        self.chords = chords
        self.update()
    
    def set_selected_chord(self, idx: Optional[int]):
        """Set the selected chord index."""
        self.selected_chord_idx = idx
        self.update()
    
    def paintEvent(self, event):
        """Paint the timeline."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.timeline_height
        beat_width = width / self.total_beats if self.total_beats > 0 else 1
        
        # Draw background
        painter.fillRect(0, 0, width, height, QColor(32, 32, 32))
        
        # Draw beat subdivision lines
        for beat in range(int(self.total_beats) + 1):
            x = beat * beat_width
            if beat % self.beats_per_bar == 0:
                # Bar line
                color = QColor(255, 255, 255) if beat == 0 or beat == self.total_beats else QColor(80, 80, 80)
                painter.setPen(QPen(color, 1))
                painter.drawLine(int(x), 0, int(x), height)
                # Bar number
                if beat < self.total_beats:
                    bar_num = int(beat / self.beats_per_bar) + 1
                    painter.setPen(QColor(136, 136, 136))
                    painter.setFont(QFont("Arial", 9))
                    painter.drawText(int(x) + 2, 12, str(bar_num))
            else:
                # Beat line
                painter.setPen(QPen(QColor(56, 56, 56), 1))
                painter.drawLine(int(x), height - 8, int(x), height)
        
        # Draw chord blocks
        for idx, chord in enumerate(self.chords):
            x1 = chord.start_beat * beat_width
            x2 = (chord.start_beat + chord.duration_beats) * beat_width
            is_selected = (idx == self.selected_chord_idx)
            is_dragging = (idx == self.dragging_chord_idx)
            
            # Get chord color (format: 0xRRGGBBAA)
            color_value = config.get_chord_color(chord.root)
            r = (color_value >> 24) & 0xFF
            g = (color_value >> 16) & 0xFF
            b = (color_value >> 8) & 0xFF
            a = color_value & 0xFF
            chord_color = QColor(r, g, b, a)
            
            block_y1 = 14
            block_y2 = height - 2
            
            # Selection glow
            if is_selected:
                glow_rect = QRect(int(x1) - 2, block_y1 - 2, int(x2 - x1) + 4, block_y2 - block_y1 + 4)
                painter.fillRect(glow_rect, QColor(255, 255, 255, 64))
            
            # Chord block
            block_rect = QRect(int(x1) + 1, block_y1, int(x2 - x1) - 2, block_y2 - block_y1)
            painter.fillRect(block_rect, chord_color)
            
            # Border
            border_color = QColor(255, 255, 255) if is_selected else QColor(160, 160, 160)
            pen_width = 2 if is_selected else 1
            painter.setPen(QPen(border_color, pen_width))
            painter.drawRect(block_rect)
            
            # Drag handles
            handle_color = QColor(255, 255, 255, 204) if is_selected else QColor(255, 255, 255, 102)
            if is_dragging and self.drag_mode == "resize_left":
                handle_color = QColor(0, 255, 0)
            elif is_dragging and self.drag_mode == "resize_right":
                handle_color = QColor(0, 255, 0)
            
            # Left handle
            left_handle = QRect(int(x1) + 1, block_y1, self.handle_width, block_y2 - block_y1)
            painter.fillRect(left_handle, handle_color)
            
            # Right handle
            right_handle = QRect(int(x2) - self.handle_width - 1, block_y1, self.handle_width, block_y2 - block_y1)
            painter.fillRect(right_handle, handle_color)
            
            # Chord name
            chord_name = get_chord_full_name(chord)
            text_width = painter.fontMetrics().width(chord_name)
            if text_width < (x2 - x1 - self.handle_width * 2 - 4):
                painter.setPen(QColor(0, 0, 0))
                painter.setFont(QFont("Arial", 9))
                painter.drawText(int(x1) + self.handle_width + 2, block_y1 + 14, chord_name)
            
            # Inversion indicator
            if chord.inversion > 0:
                inv_text = f"/{chord.inversion}"
                painter.setPen(QColor(0, 0, 0, 170))
                painter.drawText(int(x2) - self.handle_width - 16, block_y2 - 2, inv_text)
    
    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() != Qt.LeftButton:
            return
        
        width = self.width()
        beat_width = width / self.total_beats if self.total_beats > 0 else 1
        mouse_x = event.x()
        mouse_y = event.y()
        
        if mouse_y < 0 or mouse_y > self.timeline_height:
            return
        
        click_beat = mouse_x / beat_width
        
        # Find which chord (if any) was clicked
        hovered_chord = None
        hover_zone = None
        
        for idx, chord in enumerate(self.chords):
            x1 = chord.start_beat * beat_width
            x2 = (chord.start_beat + chord.duration_beats) * beat_width
            
            if x1 <= mouse_x <= x2:
                hovered_chord = idx
                if mouse_x <= x1 + self.handle_width:
                    hover_zone = "left"
                elif mouse_x >= x2 - self.handle_width:
                    hover_zone = "right"
                else:
                    hover_zone = "middle"
                break
        
        if hovered_chord is not None:
            self.selected_chord_idx = hovered_chord
            self.dragging_chord_idx = hovered_chord
            self.chord_selected.emit(hovered_chord)
            
            chord = self.chords[hovered_chord]
            if hover_zone == "left":
                self.drag_mode = "resize_left"
                self.drag_start_beat = chord.start_beat
            elif hover_zone == "right":
                self.drag_mode = "resize_right"
                self.drag_start_beat = chord.start_beat + chord.duration_beats
            else:
                self.drag_mode = "move"
                self.drag_start_beat = click_beat - chord.start_beat
            
            self.drag_start_pos = event.pos()
        else:
            self.selected_chord_idx = None
            self.chord_selected.emit(-1)
        
        self.update()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move."""
        width = self.width()
        beat_width = width / self.total_beats if self.total_beats > 0 else 1
        mouse_x = event.x()
        
        # Update cursor based on hover
        if event.buttons() == Qt.NoButton:
            hovered_chord = None
            hover_zone = None
            
            for idx, chord in enumerate(self.chords):
                x1 = chord.start_beat * beat_width
                x2 = (chord.start_beat + chord.duration_beats) * beat_width
                
                if x1 <= mouse_x <= x2:
                    hovered_chord = idx
                    if mouse_x <= x1 + self.handle_width:
                        hover_zone = "left"
                    elif mouse_x >= x2 - self.handle_width:
                        hover_zone = "right"
                    else:
                        hover_zone = "middle"
                    break
            
            if hovered_chord is not None and (hover_zone == "left" or hover_zone == "right"):
                self.setCursor(Qt.SizeHorCursor)
            elif hovered_chord is not None and hover_zone == "middle":
                self.setCursor(Qt.PointingHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        
        # Handle dragging
        if event.buttons() == Qt.LeftButton and self.dragging_chord_idx is not None:
            click_beat = mouse_x / beat_width
            chord = self.chords[self.dragging_chord_idx]
            
            if self.drag_mode == "move":
                new_start = round(click_beat - self.drag_start_beat)
                new_start = max(0, min(new_start, self.total_beats - chord.duration_beats))
                if new_start != chord.start_beat:
                    chord.start_beat = new_start
                    self.chord_moved.emit(self.dragging_chord_idx, new_start)
                    self.update()
            elif self.drag_mode == "resize_left":
                new_start = round(click_beat)
                new_start = max(0, min(new_start, chord.start_beat + chord.duration_beats - 1))
                delta = chord.start_beat - new_start
                if delta != 0:
                    chord.start_beat = new_start
                    chord.duration_beats += delta
                    self.chord_resized.emit(self.dragging_chord_idx, new_start, chord.duration_beats)
                    self.update()
            elif self.drag_mode == "resize_right":
                new_end = round(click_beat)
                new_end = max(chord.start_beat + 1, min(new_end, self.total_beats))
                new_duration = new_end - chord.start_beat
                if new_duration != chord.duration_beats:
                    chord.duration_beats = new_duration
                    self.chord_resized.emit(self.dragging_chord_idx, chord.start_beat, new_duration)
                    self.update()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.LeftButton:
            self.dragging_chord_idx = None
            self.drag_mode = None
            self.update()
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click to add chord."""
        if event.button() != Qt.LeftButton:
            return
        
        width = self.width()
        beat_width = width / self.total_beats if self.total_beats > 0 else 1
        mouse_x = event.x()
        mouse_y = event.y()
        
        if mouse_y < 0 or mouse_y > self.timeline_height:
            return
        
        click_beat = mouse_x / beat_width
        snap_beat = round(click_beat)
        
        # Check if clicking on empty space
        clicked_on_chord = False
        for chord in self.chords:
            x1 = chord.start_beat * beat_width
            x2 = (chord.start_beat + chord.duration_beats) * beat_width
            if x1 <= mouse_x <= x2:
                clicked_on_chord = True
                break
        
        if not clicked_on_chord:
            self.chord_added.emit(snap_beat)
