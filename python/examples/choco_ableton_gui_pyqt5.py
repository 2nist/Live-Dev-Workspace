#!/usr/bin/env python3
"""
ChoCo to Ableton Live GUI (PyQt5)

A graphical interface for browsing the ChoCo dataset and sending
chord progressions to Ableton Live.
"""

import sys
import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QTextEdit, QSpinBox,
    QComboBox, QGroupBox, QFileDialog, QMessageBox, QStatusBar, QSplitter
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

# Add src to path
script_dir = Path(__file__).resolve().parent
parent_dir = script_dir.parent
src_dir = parent_dir / "src"
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(src_dir))

try:
    from choco_integration import (
        ChocoLiveBridge,
        MetadataEnhancer,
        harte_to_midi_notes,
    )
    from pythonosc import udp_client
    OSC_AVAILABLE = True
except ImportError as e:
    OSC_AVAILABLE = False
    print(f"Warning: Some imports not available: {e}")


class LoadIndexesThread(QThread):
    """Thread for loading indexes in background."""
    finished = pyqtSignal(dict, dict)
    error = pyqtSignal(str)
    
    def __init__(self, enhanced_dir):
        super().__init__()
        self.enhanced_dir = enhanced_dir
    
    def run(self):
        try:
            enhancer = MetadataEnhancer()
            artist_index = enhancer.build_artist_index(str(self.enhanced_dir))
            song_index = enhancer.build_song_index(str(self.enhanced_dir))
            self.finished.emit(artist_index, song_index)
        except Exception as e:
            self.error.emit(str(e))


class SendToLiveThread(QThread):
    """Thread for sending to Live in background."""
    finished = pyqtSignal(int)
    error = pyqtSignal(str)
    
    def __init__(self, osc_client, song_data, track, clip, voicing):
        super().__init__()
        self.osc_client = osc_client
        self.song_data = song_data
        self.track = track
        self.clip = clip
        self.voicing = voicing
    
    def run(self):
        try:
            metadata = self.song_data.get('metadata', {})
            chords = self.song_data.get('chords', [])
            
            if not chords:
                self.error.emit("No chords in song")
                return
            
            # Calculate clip length
            tempo = metadata.get('tempo', 120.0)
            duration = metadata.get('duration', 0.0)
            beats_per_sec = tempo / 60.0
            
            if duration > 0:
                clip_length = duration * beats_per_sec
            else:
                last_chord = chords[-1]
                clip_length = (last_chord['time'] + last_chord['duration']) * beats_per_sec
            
            clip_length = max(clip_length, 4.0)
            
            # Create clip
            self.osc_client.send_message("/live/clip_slot/create_clip", [self.track, self.clip, clip_length])
            
            # Add chords
            note_count = 0
            for chord_data in chords:
                chord_str = chord_data.get('chord', '')
                if not chord_str or chord_str == 'N':
                    continue
                
                time_sec = chord_data.get('time', 0.0)
                duration_sec = chord_data.get('duration', 2.0)
                
                start_beat = time_sec * beats_per_sec
                duration_beat = duration_sec * beats_per_sec
                
                midi_notes = harte_to_midi_notes(chord_str, voicing=self.voicing)
                
                for note in midi_notes:
                    self.osc_client.send_message(
                        "/live/clip/add/notes",
                        [self.track, self.clip, note, start_beat, duration_beat, 100, 0]
                    )
                    note_count += 1
            
            self.finished.emit(note_count)
        except Exception as e:
            self.error.emit(str(e))


class ChocoAbletonGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChoCo to Ableton Live")
        self.setGeometry(100, 100, 1200, 800)
        
        # State
        self.enhanced_dir = None
        self.artist_index = {}
        self.song_index = {}
        self.current_song = None
        self.osc_client = None
        self.live_connected = False
        self.song_files = {}  # Map list items to file paths
        
        # Setup OSC client
        try:
            self.osc_client = udp_client.SimpleUDPClient("127.0.0.1", 11000)
            self.live_connected = True
        except:
            self.live_connected = False
        
        self.setup_ui()
        self.load_default_directory()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Top frame - Directory selection
        top_frame = QWidget()
        top_layout = QHBoxLayout(top_frame)
        
        top_layout.addWidget(QLabel("Enhanced JSON Directory:"))
        self.dir_entry = QLineEdit()
        self.dir_entry.setMinimumWidth(400)
        top_layout.addWidget(self.dir_entry)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_directory)
        top_layout.addWidget(browse_btn)
        
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_directory)
        top_layout.addWidget(load_btn)
        
        self.status_label = QLabel("Ableton Live: Not Connected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        top_layout.addWidget(self.status_label)
        
        top_layout.addStretch()
        main_layout.addWidget(top_frame)
        
        # Main content area
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Search and browse
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Search frame
        search_group = QGroupBox("Search")
        search_layout = QVBoxLayout()
        
        search_input_layout = QHBoxLayout()
        search_input_layout.addWidget(QLabel("Search:"))
        self.search_entry = QLineEdit()
        self.search_entry.textChanged.connect(self.on_search_change)
        search_input_layout.addWidget(self.search_entry)
        search_layout.addLayout(search_input_layout)
        
        search_group.setLayout(search_layout)
        left_layout.addWidget(search_group)
        
        # Results listbox
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.on_song_select)
        results_layout.addWidget(self.results_list)
        
        results_group.setLayout(results_layout)
        left_layout.addWidget(results_group)
        
        splitter.addWidget(left_panel)
        
        # Right panel - Song details and controls
        right_panel = QWidget()
        right_panel.setMinimumWidth(450)
        right_layout = QVBoxLayout(right_panel)
        
        # Song info frame
        info_group = QGroupBox("Song Information")
        info_layout = QVBoxLayout()
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setFont(QFont("Courier", 10))
        info_layout.addWidget(self.info_text)
        
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)
        
        # Controls frame
        controls_group = QGroupBox("Ableton Live Controls")
        controls_layout = QVBoxLayout()
        
        # Track and clip selection
        track_clip_layout = QHBoxLayout()
        track_clip_layout.addWidget(QLabel("Track:"))
        self.track_spin = QSpinBox()
        self.track_spin.setMinimum(0)
        self.track_spin.setMaximum(127)
        self.track_spin.setValue(0)
        track_clip_layout.addWidget(self.track_spin)
        
        track_clip_layout.addWidget(QLabel("Clip:"))
        self.clip_spin = QSpinBox()
        self.clip_spin.setMinimum(0)
        self.clip_spin.setMaximum(127)
        self.clip_spin.setValue(0)
        track_clip_layout.addWidget(self.clip_spin)
        
        track_clip_layout.addStretch()
        controls_layout.addLayout(track_clip_layout)
        
        # Voicing options
        voicing_layout = QHBoxLayout()
        voicing_layout.addWidget(QLabel("Voicing:"))
        self.voicing_combo = QComboBox()
        self.voicing_combo.addItems(["close", "open", "spread"])
        self.voicing_combo.setCurrentText("close")
        voicing_layout.addWidget(self.voicing_combo)
        voicing_layout.addStretch()
        controls_layout.addLayout(voicing_layout)
        
        # Action buttons
        self.send_button = QPushButton("Send to Ableton Live")
        self.send_button.clicked.connect(self.send_to_live)
        self.send_button.setEnabled(False)
        controls_layout.addWidget(self.send_button)
        
        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self.test_connection)
        controls_layout.addWidget(test_btn)
        
        preview_btn = QPushButton("Preview Chords")
        preview_btn.clicked.connect(self.preview_chords)
        controls_layout.addWidget(preview_btn)
        
        controls_group.setLayout(controls_layout)
        right_layout.addWidget(controls_group)
        
        right_layout.addStretch()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def load_default_directory(self):
        """Load default enhanced directory if it exists."""
        default_dir = script_dir / "choco_enhanced" / "json_enhanced"
        if default_dir.exists():
            self.dir_entry.setText(str(default_dir))
            self.load_directory()
    
    def browse_directory(self):
        """Browse for enhanced JSON directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Enhanced JSON Directory",
            str(script_dir / "choco_enhanced")
        )
        if directory:
            self.dir_entry.setText(directory)
    
    def load_directory(self):
        """Load the enhanced JSON directory and build indexes."""
        directory = self.dir_entry.text()
        if not directory or not Path(directory).exists():
            QMessageBox.critical(self, "Error", "Directory does not exist!")
            return
        
        self.enhanced_dir = Path(directory)
        self.status_bar.showMessage("Loading indexes...")
        
        # Try to load pre-built indexes
        indexes_dir = self.enhanced_dir.parent / "indexes"
        if (indexes_dir / "artist_index.json").exists():
            try:
                with open(indexes_dir / "artist_index.json", 'r', encoding='utf-8') as f:
                    self.artist_index = json.load(f)
                with open(indexes_dir / "song_index.json", 'r', encoding='utf-8') as f:
                    self.song_index = json.load(f)
                self.status_bar.showMessage(
                    f"Loaded indexes: {len(self.artist_index)} artists, {len(self.song_index)} songs"
                )
                self.populate_results()
                return
            except Exception as e:
                print(f"Error loading indexes: {e}")
        
        # Build indexes on the fly
        self.status_bar.showMessage("Building indexes (this may take a moment)...")
        self.load_thread = LoadIndexesThread(self.enhanced_dir)
        self.load_thread.finished.connect(self.on_indexes_loaded)
        self.load_thread.error.connect(self.on_indexes_error)
        self.load_thread.start()
    
    def on_indexes_loaded(self, artist_index, song_index):
        """Handle indexes loaded."""
        self.artist_index = artist_index
        self.song_index = song_index
        self.status_bar.showMessage(
            f"Loaded: {len(self.artist_index)} artists, {len(self.song_index)} songs"
        )
        self.populate_results()
    
    def on_indexes_error(self, error):
        """Handle indexes loading error."""
        QMessageBox.critical(self, "Error", f"Failed to build indexes: {error}")
        self.status_bar.showMessage("Error loading indexes")
    
    def populate_results(self):
        """Populate results list with songs."""
        self.results_list.clear()
        self.song_files.clear()
        
        # Combine all songs from indexes
        all_songs = []
        for artist, songs in self.artist_index.items():
            for song in songs:
                all_songs.append({
                    'title': song.get('title', 'Unknown'),
                    'artist': artist,
                    'file': song.get('file', '')
                })
        
        # Sort by title
        all_songs.sort(key=lambda x: x['title'].lower())
        
        # Add to list
        for song in all_songs:
            display = f"{song['title']} - {song['artist']}"
            item = self.results_list.addItem(display)
            self.song_files[display] = song['file']
    
    def on_search_change(self, text):
        """Handle search text change."""
        query = text.lower()
        self.results_list.clear()
        self.song_files.clear()
        
        if not query:
            self.populate_results()
            return
        
        # Filter results
        for artist, songs in self.artist_index.items():
            if query in artist.lower():
                for song in songs:
                    title = song.get('title', 'Unknown')
                    display = f"{title} - {artist}"
                    self.results_list.addItem(display)
                    self.song_files[display] = song.get('file', '')
        
        # Also search in song titles
        for title, versions in self.song_index.items():
            if query in title.lower():
                for version in versions:
                    artist = version.get('artist', 'Unknown')
                    display = f"{title} - {artist}"
                    self.results_list.addItem(display)
                    self.song_files[display] = version.get('file', '')
    
    def on_song_select(self, item):
        """Handle song selection from list."""
        display = item.text()
        file_path = self.song_files.get(display, '')
        
        if not file_path or not Path(file_path).exists():
            self.info_text.setPlainText("File not found!")
            self.current_song = None
            self.send_button.setEnabled(False)
            return
        
        # Load song data
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.current_song = json.load(f)
            
            self.display_song_info()
            self.send_button.setEnabled(self.live_connected)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load song: {e}")
    
    def display_song_info(self):
        """Display current song information."""
        if not self.current_song:
            return
        
        metadata = self.current_song.get('metadata', {})
        chords = self.current_song.get('chords', [])
        
        info = f"Title: {metadata.get('title', 'N/A')}\n"
        info += f"Artist: {metadata.get('artist', 'N/A')}\n"
        info += f"Genre: {metadata.get('genre', 'N/A')}\n"
        info += f"Dataset: {metadata.get('dataset', 'N/A')}\n"
        info += f"Duration: {metadata.get('duration', 0):.1f}s\n"
        info += f"\nChords: {len(chords)}\n"
        
        if chords:
            info += "\nFirst 10 chords:\n"
            for i, chord_data in enumerate(chords[:10], 1):
                chord = chord_data.get('chord', 'N/A')
                time = chord_data.get('time', 0)
                duration = chord_data.get('duration', 0)
                info += f"  {i}. {chord:10} @ {time:6.1f}s (dur: {duration:.1f}s)\n"
        
        self.info_text.setPlainText(info)
    
    def test_connection(self):
        """Test connection to Ableton Live."""
        if not OSC_AVAILABLE or not self.osc_client:
            QMessageBox.critical(self, "Error", "OSC client not available!")
            return
        
        try:
            # Send test message
            self.osc_client.send_message("/live/test", [])
            QMessageBox.information(
                self,
                "Success",
                "Test message sent to Ableton Live!\nCheck Live for confirmation."
            )
            self.live_connected = True
            self.status_label.setText("Ableton Live: Connected")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            if self.current_song:
                self.send_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect: {e}")
            self.live_connected = False
            self.status_label.setText("Ableton Live: Not Connected")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
    
    def preview_chords(self):
        """Preview chord progression as MIDI notes."""
        if not self.current_song:
            QMessageBox.warning(self, "Warning", "No song selected!")
            return
        
        chords = self.current_song.get('chords', [])
        if not chords:
            QMessageBox.information(self, "Info", "No chords in this song!")
            return
        
        voicing = self.voicing_combo.currentText()
        preview_text = "Chord to MIDI Preview:\n\n"
        
        for i, chord_data in enumerate(chords[:20], 1):
            chord_str = chord_data.get('chord', '')
            if chord_str and chord_str != 'N':
                try:
                    midi_notes = harte_to_midi_notes(chord_str, voicing=voicing)
                    preview_text += f"{i}. {chord_str:15} -> {midi_notes}\n"
                except Exception as e:
                    preview_text += f"{i}. {chord_str:15} -> Error: {e}\n"
        
        # Show in message box
        preview_dialog = QMessageBox(self)
        preview_dialog.setWindowTitle("Chord Preview")
        preview_dialog.setText(preview_text)
        preview_dialog.setStandardButtons(QMessageBox.Ok)
        preview_dialog.exec_()
    
    def send_to_live(self):
        """Send current song to Ableton Live."""
        if not self.current_song:
            QMessageBox.warning(self, "Warning", "No song selected!")
            return
        
        if not self.live_connected:
            QMessageBox.critical(self, "Error", "Not connected to Ableton Live!")
            return
        
        track = self.track_spin.value()
        clip = self.clip_spin.value()
        voicing = self.voicing_combo.currentText()
        
        self.status_bar.showMessage("Sending to Ableton Live...")
        self.send_button.setEnabled(False)
        
        # Send in background thread
        self.send_thread = SendToLiveThread(
            self.osc_client, self.current_song, track, clip, voicing
        )
        self.send_thread.finished.connect(self.on_send_finished)
        self.send_thread.error.connect(self.on_send_error)
        self.send_thread.start()
    
    def on_send_finished(self, note_count):
        """Handle successful send."""
        track = self.track_spin.value()
        clip = self.clip_spin.value()
        self.status_bar.showMessage(f"Sent {note_count} notes to track {track}, clip {clip}")
        self.send_button.setEnabled(True)
        QMessageBox.information(
            self,
            "Success",
            f"Song sent to Ableton Live!\nTrack: {track}, Clip: {clip}\nNotes: {note_count}"
        )
    
    def on_send_error(self, error):
        """Handle send error."""
        self.status_bar.showMessage("Error sending to Live")
        self.send_button.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Failed to send: {error}")


def main():
    app = QApplication(sys.argv)
    window = ChocoAbletonGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
