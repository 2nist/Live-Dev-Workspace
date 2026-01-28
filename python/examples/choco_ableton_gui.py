#!/usr/bin/env python3
"""
ChoCo to Ableton Live GUI

A graphical interface for browsing the ChoCo dataset and sending
chord progressions to Ableton Live.
"""

import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import threading

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


class ChocoAbletonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ChoCo to Ableton Live")
        self.root.geometry("1000x700")
        
        # State
        self.enhanced_dir = None
        self.artist_index = {}
        self.song_index = {}
        self.current_song = None
        self.osc_client = None
        self.live_connected = False
        
        # Setup OSC client
        try:
            self.osc_client = udp_client.SimpleUDPClient("127.0.0.1", 11000)
            self.live_connected = True
        except:
            self.live_connected = False
        
        self.setup_ui()
        self.load_default_directory()
    
    def setup_ui(self):
        # Top frame - Directory selection
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Enhanced JSON Directory:").pack(side=tk.LEFT, padx=5)
        self.dir_var = tk.StringVar()
        self.dir_entry = ttk.Entry(top_frame, textvariable=self.dir_var, width=50)
        self.dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(top_frame, text="Browse", command=self.browse_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Load", command=self.load_directory).pack(side=tk.LEFT, padx=5)
        
        # Connection status
        self.status_label = ttk.Label(top_frame, text="Ableton Live: Not Connected", foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Main content area
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Search and browse
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Search frame
        search_frame = ttk.LabelFrame(left_panel, text="Search", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Results listbox
        results_frame = ttk.LabelFrame(left_panel, text="Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox with scrollbar
        listbox_frame = ttk.Frame(results_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set)
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results_listbox.bind('<<ListboxSelect>>', self.on_song_select)
        scrollbar.config(command=self.results_listbox.yview)
        
        # Right panel - Song details and controls
        right_panel = ttk.Frame(main_frame, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        right_panel.pack_propagate(False)
        
        # Song info frame
        info_frame = ttk.LabelFrame(right_panel, text="Song Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=15, width=40, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Controls frame
        controls_frame = ttk.LabelFrame(right_panel, text="Ableton Live Controls", padding="10")
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Track and clip selection
        track_frame = ttk.Frame(controls_frame)
        track_frame.pack(fill=tk.X, pady=5)
        ttk.Label(track_frame, text="Track:").pack(side=tk.LEFT)
        self.track_var = tk.IntVar(value=0)
        track_spin = ttk.Spinbox(track_frame, from_=0, to=127, textvariable=self.track_var, width=10)
        track_spin.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(track_frame, text="Clip:").pack(side=tk.LEFT, padx=(10, 0))
        self.clip_var = tk.IntVar(value=0)
        clip_spin = ttk.Spinbox(track_frame, from_=0, to=127, textvariable=self.clip_var, width=10)
        clip_spin.pack(side=tk.LEFT, padx=5)
        
        # Voicing options
        voicing_frame = ttk.Frame(controls_frame)
        voicing_frame.pack(fill=tk.X, pady=5)
        ttk.Label(voicing_frame, text="Voicing:").pack(side=tk.LEFT)
        self.voicing_var = tk.StringVar(value="close")
        voicing_combo = ttk.Combobox(voicing_frame, textvariable=self.voicing_var, 
                                     values=["close", "open", "spread"], width=15, state="readonly")
        voicing_combo.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.send_button = ttk.Button(button_frame, text="Send to Ableton Live", 
                                      command=self.send_to_live, state=tk.DISABLED)
        self.send_button.pack(fill=tk.X, pady=2)
        
        ttk.Button(button_frame, text="Test Connection", 
                  command=self.test_connection).pack(fill=tk.X, pady=2)
        
        ttk.Button(button_frame, text="Preview Chords", 
                  command=self.preview_chords).pack(fill=tk.X, pady=2)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_default_directory(self):
        """Load default enhanced directory if it exists."""
        default_dir = script_dir / "choco_enhanced" / "json_enhanced"
        if default_dir.exists():
            self.dir_var.set(str(default_dir))
            self.load_directory()
    
    def browse_directory(self):
        """Browse for enhanced JSON directory."""
        directory = filedialog.askdirectory(
            title="Select Enhanced JSON Directory",
            initialdir=str(script_dir / "choco_enhanced")
        )
        if directory:
            self.dir_var.set(directory)
    
    def load_directory(self):
        """Load the enhanced JSON directory and build indexes."""
        directory = self.dir_var.get()
        if not directory or not Path(directory).exists():
            messagebox.showerror("Error", "Directory does not exist!")
            return
        
        self.enhanced_dir = Path(directory)
        self.status_bar.config(text="Loading indexes...")
        
        # Try to load pre-built indexes
        indexes_dir = self.enhanced_dir.parent / "indexes"
        if (indexes_dir / "artist_index.json").exists():
            try:
                with open(indexes_dir / "artist_index.json", 'r') as f:
                    self.artist_index = json.load(f)
                with open(indexes_dir / "song_index.json", 'r') as f:
                    self.song_index = json.load(f)
                self.status_bar.config(text=f"Loaded indexes: {len(self.artist_index)} artists, {len(self.song_index)} songs")
                self.populate_results()
                return
            except Exception as e:
                print(f"Error loading indexes: {e}")
        
        # Build indexes on the fly
        self.status_bar.config(text="Building indexes (this may take a moment)...")
        threading.Thread(target=self.build_indexes_thread, daemon=True).start()
    
    def build_indexes_thread(self):
        """Build indexes in background thread."""
        try:
            enhancer = MetadataEnhancer()
            self.artist_index = enhancer.build_artist_index(str(self.enhanced_dir))
            self.song_index = enhancer.build_song_index(str(self.enhanced_dir))
            
            self.root.after(0, lambda: self.status_bar.config(
                text=f"Loaded: {len(self.artist_index)} artists, {len(self.song_index)} songs"
            ))
            self.root.after(0, self.populate_results)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to build indexes: {e}"))
    
    def populate_results(self):
        """Populate results listbox with songs."""
        self.results_listbox.delete(0, tk.END)
        
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
        
        # Add to listbox
        for song in all_songs:
            display = f"{song['title']} - {song['artist']}"
            self.results_listbox.insert(tk.END, display)
            self.results_listbox.itemconfig(tk.END - 1, {'data': song})
    
    def on_search_change(self, *args):
        """Handle search text change."""
        query = self.search_var.get().lower()
        if not query:
            self.populate_results()
            return
        
        # Filter results
        self.results_listbox.delete(0, tk.END)
        
        for artist, songs in self.artist_index.items():
            if query in artist.lower():
                for song in songs:
                    title = song.get('title', 'Unknown')
                    display = f"{title} - {artist}"
                    self.results_listbox.insert(tk.END, display)
                    self.results_listbox.itemconfig(tk.END - 1, {'data': {'title': title, 'artist': artist, 'file': song.get('file', '')}})
        
        # Also search in song titles
        for title, versions in self.song_index.items():
            if query in title.lower():
                for version in versions:
                    artist = version.get('artist', 'Unknown')
                    display = f"{title} - {artist}"
                    self.results_listbox.insert(tk.END, display)
                    self.results_listbox.itemconfig(tk.END - 1, {'data': {'title': title, 'artist': artist, 'file': version.get('file', '')}})
    
    def on_song_select(self, event):
        """Handle song selection from listbox."""
        selection = self.results_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        item_data = self.results_listbox.itemconfig(index, 'data')
        if not item_data or not item_data[-1]:
            return
        
        song_info = item_data[-1]
        file_path = song_info.get('file', '')
        
        if not file_path or not Path(file_path).exists():
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, "File not found!")
            self.current_song = None
            self.send_button.config(state=tk.DISABLED)
            return
        
        # Load song data
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.current_song = json.load(f)
            
            self.display_song_info()
            self.send_button.config(state=tk.NORMAL if self.live_connected else tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load song: {e}")
    
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
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
    
    def test_connection(self):
        """Test connection to Ableton Live."""
        if not OSC_AVAILABLE or not self.osc_client:
            messagebox.showerror("Error", "OSC client not available!")
            return
        
        try:
            # Send test message
            self.osc_client.send_message("/live/test", [])
            messagebox.showinfo("Success", "Test message sent to Ableton Live!\nCheck Live for confirmation.")
            self.live_connected = True
            self.status_label.config(text="Ableton Live: Connected", foreground="green")
            if self.current_song:
                self.send_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {e}")
            self.live_connected = False
            self.status_label.config(text="Ableton Live: Not Connected", foreground="red")
    
    def preview_chords(self):
        """Preview chord progression as MIDI notes."""
        if not self.current_song:
            messagebox.showwarning("Warning", "No song selected!")
            return
        
        chords = self.current_song.get('chords', [])
        if not chords:
            messagebox.showinfo("Info", "No chords in this song!")
            return
        
        preview_text = "Chord to MIDI Preview:\n\n"
        for i, chord_data in enumerate(chords[:20], 1):
            chord_str = chord_data.get('chord', '')
            if chord_str and chord_str != 'N':
                try:
                    midi_notes = harte_to_midi_notes(chord_str, voicing=self.voicing_var.get())
                    preview_text += f"{i}. {chord_str:15} -> {midi_notes}\n"
                except Exception as e:
                    preview_text += f"{i}. {chord_str:15} -> Error: {e}\n"
        
        # Show in new window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Chord Preview")
        preview_window.geometry("500x400")
        
        text_widget = tk.Text(preview_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(1.0, preview_text)
        text_widget.config(state=tk.DISABLED)
    
    def send_to_live(self):
        """Send current song to Ableton Live."""
        if not self.current_song:
            messagebox.showwarning("Warning", "No song selected!")
            return
        
        if not self.live_connected:
            messagebox.showerror("Error", "Not connected to Ableton Live!")
            return
        
        track = self.track_var.get()
        clip = self.clip_var.get()
        voicing = self.voicing_var.get()
        
        self.status_bar.config(text="Sending to Ableton Live...")
        self.send_button.config(state=tk.DISABLED)
        
        # Send in background thread
        threading.Thread(
            target=self.send_to_live_thread,
            args=(track, clip, voicing),
            daemon=True
        ).start()
    
    def send_to_live_thread(self, track, clip, voicing):
        """Send song to Live in background thread."""
        try:
            from choco_integration import send_chord_progression_to_live
            
            # Use direct OSC if LiveConnection not available
            if not OSC_AVAILABLE:
                raise ImportError("OSC not available")
            
            metadata = self.current_song.get('metadata', {})
            chords = self.current_song.get('chords', [])
            
            if not chords:
                raise ValueError("No chords in song")
            
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
            self.osc_client.send_message("/live/clip_slot/create_clip", [track, clip, clip_length])
            
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
                
                midi_notes = harte_to_midi_notes(chord_str, voicing=voicing)
                
                for note in midi_notes:
                    self.osc_client.send_message(
                        "/live/clip/add/notes",
                        [track, clip, note, start_beat, duration_beat, 100, 0]
                    )
                    note_count += 1
            
            self.root.after(0, lambda: self.status_bar.config(
                text=f"Sent {note_count} notes to track {track}, clip {clip}"
            ))
            self.root.after(0, lambda: self.send_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: messagebox.showinfo(
                "Success",
                f"Song sent to Ableton Live!\nTrack: {track}, Clip: {clip}\nNotes: {note_count}"
            ))
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to send: {e}"))
            self.root.after(0, lambda: self.status_bar.config(text="Error sending to Live"))
            self.root.after(0, lambda: self.send_button.config(state=tk.NORMAL))


def main():
    root = tk.Tk()
    app = ChocoAbletonGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
