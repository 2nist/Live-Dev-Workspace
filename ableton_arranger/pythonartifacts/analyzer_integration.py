"""
Integration example: Adding the Analyzer module to MainWindow.

This shows how to extend your existing GUI with audio analysis capabilities
while maintaining the modular architecture for M4L conversion.
"""
import os
from typing import Optional, List
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QProgressBar, QFileDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

# Import the new analyzer module
from ableton_arranger.analyzer import AudioAnalyzer
from ableton_arranger.shared import AnalysisData, AnalysisConfig, AnalysisStatus
from ableton_arranger.core.section import Section


class AnalysisWorker(QThread):
    """Worker thread for running analysis without blocking the GUI."""
    
    progress_updated = pyqtSignal(str, float)  # message, progress (0.0-1.0)
    analysis_completed = pyqtSignal(object)    # AnalysisData
    analysis_failed = pyqtSignal(str)          # error message
    
    def __init__(self, audio_path: str, config: AnalysisConfig):
        super().__init__()
        self.audio_path = audio_path
        self.config = config
        self.analyzer = None
    
    def run(self):
        """Run analysis in background thread."""
        try:
            self.analyzer = AudioAnalyzer(self.config)
            self.analyzer.set_progress_callback(self.progress_updated.emit)
            
            result = self.analyzer.analyze_file(self.audio_path)
            self.analysis_completed.emit(result)
            
        except Exception as e:
            self.analysis_failed.emit(str(e))
    
    def cancel_analysis(self):
        """Cancel the running analysis."""
        if self.analyzer:
            self.analyzer.cancel_analysis()
        self.terminate()


class AnalyzerPanel(QWidget):
    """
    Panel for audio analysis controls and results.
    This could become a separate M4L device.
    """
    
    analysis_completed = pyqtSignal(object)  # Emits AnalysisData
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_analysis: Optional[AnalysisData] = None
        self.worker: Optional[AnalysisWorker] = None
        self.config = AnalysisConfig()
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the analyzer panel UI."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Audio Analyzer")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # File selection
        file_layout = QHBoxLayout()
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #666; font-size: 11px;")
        file_layout.addWidget(self.file_label)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_audio_file)
        file_layout.addWidget(self.browse_btn)
        
        layout.addLayout(file_layout)
        
        # Analysis options (simple for now)
        options_layout = QVBoxLayout()
        
        self.structure_btn = QPushButton("Detect Structure")
        self.structure_btn.clicked.connect(lambda: self.start_analysis(structure_only=True))
        self.structure_btn.setEnabled(False)
        options_layout.addWidget(self.structure_btn)
        
        self.full_analysis_btn = QPushButton("Full Analysis")
        self.full_analysis_btn.clicked.connect(lambda: self.start_analysis(structure_only=False))
        self.full_analysis_btn.setEnabled(False)
        options_layout.addWidget(self.full_analysis_btn)
        
        layout.addLayout(options_layout)
        
        # Progress display
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #0a0; font-size: 11px;")
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_analysis)
        self.cancel_btn.setVisible(False)
        layout.addWidget(self.cancel_btn)
        
        # Results summary
        self.results_label = QLabel("")
        self.results_label.setWordWrap(True)
        self.results_label.setStyleSheet("color: #333; font-size: 11px; margin-top: 10px;")
        layout.addWidget(self.results_label)
        
        # Apply to Arrangement button
        self.apply_btn = QPushButton("Apply to Arrangement")
        self.apply_btn.clicked.connect(self.apply_to_arrangement)
        self.apply_btn.setEnabled(False)
        layout.addWidget(self.apply_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def browse_audio_file(self):
        """Browse for audio file to analyze."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.mp3 *.wav *.flac *.m4a *.ogg);;All Files (*)"
        )
        
        if file_path:
            self.file_label.setText(os.path.basename(file_path))
            self.selected_file = file_path
            self.structure_btn.setEnabled(True)
            self.full_analysis_btn.setEnabled(True)
            self.apply_btn.setEnabled(False)
            self.current_analysis = None
            self.results_label.setText("")
    
    def start_analysis(self, structure_only: bool = False):
        """Start audio analysis in background thread."""
        if not hasattr(self, 'selected_file'):
            return
        
        # Configure analysis options
        self.config.enable_structure_detection = True
        self.config.enable_stem_separation = not structure_only
        self.config.enable_chord_detection = not structure_only  
        self.config.enable_lyrics_transcription = not structure_only
        
        # Create and start worker thread
        self.worker = AnalysisWorker(self.selected_file, self.config)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.analysis_completed.connect(self.on_analysis_completed)
        self.worker.analysis_failed.connect(self.on_analysis_failed)
        
        # Update UI for analysis state
        self.structure_btn.setEnabled(False)
        self.full_analysis_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.cancel_btn.setVisible(True)
        self.apply_btn.setEnabled(False)
        
        self.worker.start()
    
    def cancel_analysis(self):
        """Cancel running analysis."""
        if self.worker:
            self.worker.cancel_analysis()
            self.worker.wait(3000)  # Wait up to 3 seconds
        
        self.reset_ui_state()
    
    def update_progress(self, message: str, progress: float):
        """Update analysis progress display."""
        self.progress_label.setText(message)
        self.progress_bar.setValue(int(progress * 100))
    
    def on_analysis_completed(self, analysis_data: AnalysisData):
        """Handle completed analysis."""
        self.current_analysis = analysis_data
        self.reset_ui_state()
        
        # Display results summary
        sections_count = len(analysis_data.sections)
        chords_count = len(analysis_data.chords)
        has_lyrics = bool(analysis_data.lyrics.full_text.strip())
        has_stems = bool(analysis_data.stems.vocals_path)
        
        results = [
            f"✓ {sections_count} sections detected",
            f"✓ {chords_count} chords detected" if chords_count else "○ No chords detected",
            f"✓ Lyrics transcribed ({len(analysis_data.lyrics.words)} words)" if has_lyrics else "○ No lyrics detected", 
            f"✓ Stems separated" if has_stems else "○ No stems created",
            f"Tempo: {analysis_data.tempo:.1f} BPM",
            f"Key: {analysis_data.key_signature}",
            f"Analysis time: {analysis_data.analysis_time:.1f}s"
        ]
        
        self.results_label.setText("\n".join(results))
        self.apply_btn.setEnabled(True)
        
        # Emit for other components to use
        self.analysis_completed.emit(analysis_data)
    
    def on_analysis_failed(self, error_message: str):
        """Handle analysis failure."""
        self.reset_ui_state()
        QMessageBox.critical(self, "Analysis Failed", f"Analysis failed:\n{error_message}")
    
    def reset_ui_state(self):
        """Reset UI to normal state after analysis."""
        if hasattr(self, 'selected_file'):
            self.structure_btn.setEnabled(True)
            self.full_analysis_btn.setEnabled(True)
        
        self.progress_bar.setVisible(False)
        self.cancel_btn.setVisible(False)
        self.progress_label.setText("")
    
    def apply_to_arrangement(self):
        """Apply analysis results to arrangement (emit for MainWindow to handle)."""
        if self.current_analysis:
            self.analysis_completed.emit(self.current_analysis)


class IntegratedMainWindow:
    """
    Example of how to integrate AnalyzerPanel into your existing MainWindow.
    This shows the integration pattern without modifying your actual MainWindow.
    """
    
    def __init__(self, main_window):
        """
        Initialize integration with existing MainWindow.
        
        Args:
            main_window: Your existing MainWindow instance
        """
        self.main_window = main_window
        self.analyzer_panel = None
        
        self.add_analyzer_panel()
    
    def add_analyzer_panel(self):
        """Add analyzer panel to the main window."""
        # Get the existing splitter from your MainWindow
        splitter = self.main_window.centralWidget().layout().itemAt(0).widget()
        
        # Create analyzer panel
        self.analyzer_panel = AnalyzerPanel()
        self.analyzer_panel.analysis_completed.connect(self.on_analysis_completed)
        
        # Add as third panel (sections | chords | analyzer)
        splitter.addWidget(self.analyzer_panel)
        
        # Adjust splitter sizes (sections: 420px, chords: 400px, analyzer: 380px)
        splitter.setSizes([420, 400, 380])
        splitter.setStretchFactor(2, 0)  # Don't stretch analyzer panel
    
    def on_analysis_completed(self, analysis_data: AnalysisData):
        """
        Handle analysis completion - convert to your existing Section objects.
        
        Args:
            analysis_data: Complete analysis results
        """
        # Convert detected sections to your Section objects
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
            new_sections.append(section)
        
        # Update the main window's sections
        self.main_window.sections = new_sections
        self.main_window.section_panel.set_sections(new_sections)
        
        # Auto-select first section
        if new_sections:
            self.main_window.section_panel.selected_index = 0
            self.main_window.section_panel.table.selectRow(0)
            self.main_window.on_section_selected(0)
        
        # Show success message
        QMessageBox.information(
            self.main_window,
            "Analysis Complete",
            f"Successfully imported {len(new_sections)} sections with "
            f"{sum(len(s.chords or []) for s in new_sections)} chords.\n\n"
            f"Use 'Rebuild' to create the arrangement in Ableton Live."
        )


# Example usage:
# To integrate this into your existing application, add this to your MainWindow.__init__():
#
# # After your existing UI setup:
# self.analyzer_integration = IntegratedMainWindow(self)
#
# This will add the analyzer as a third panel and automatically convert
# analysis results to your existing Section/Chord format.
