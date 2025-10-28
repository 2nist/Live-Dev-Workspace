# Song Arrangement System - Improved Architecture & Implementation Plan

**Status**: Design Phase  
**Target**: Production-ready, testable, extensible M4L + Python arranger system  
**Created**: October 26, 2025

---

## Executive Summary

### Current MVP Analysis
The attached MVP provides a solid proof-of-concept with:
- ✅ Basic OSC communication structure
- ✅ Section/chord/order data model
- ✅ Placeholder Live integration
- ⚠️ Monolithic backend design
- ⚠️ No error recovery or state persistence
- ⚠️ Limited testing strategy
- ⚠️ Tight coupling between concerns

### Improvements Overview
This plan transforms the MVP into a **production-grade system** by:
1. **Leveraging existing infrastructure** (live_dev package)
2. **Modular architecture** with clear separation of concerns
3. **Comprehensive testing** at all layers
4. **State management** with undo/redo and persistence
5. **Extensibility** for future features (MIDI variations, audio clips, automation)
6. **Robust error handling** and recovery
7. **Developer experience** with debugging tools and documentation

---

## Part 1: Architecture Improvements

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Max for Live Device (M4L)                     │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │  Structure   │    Chords    │    Order     │   Playback   │  │
│  │     UI       │      UI      │      UI      │   Controls   │  │
│  └──────┬───────┴──────┬───────┴──────┬───────┴──────┬───────┘  │
│         └───────────────┴──────────────┴──────────────┘          │
│                            ↕ OSC (12000/12001)                   │
└─────────────────────────────────────────────────────────────────┘
                                 ↕
┌─────────────────────────────────────────────────────────────────┐
│              Python Backend (arranger_service.py)                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  API Layer (FastAPI/OSC Router)                          │   │
│  │  - Request validation                                    │   │
│  │  - Response formatting                                   │   │
│  │  - Error handling                                        │   │
│  └────────────────────┬─────────────────────────────────────┘   │
│  ┌────────────────────▼─────────────────────────────────────┐   │
│  │  Business Logic Layer                                    │   │
│  │  ┌─────────────┬─────────────┬──────────────────────┐    │   │
│  │  │ Arrangement │    Chord    │   Scene/Clip         │    │   │
│  │  │   Manager   │   Resolver  │   Builder            │    │   │
│  │  └─────────────┴─────────────┴──────────────────────┘    │   │
│  └────────────────────┬─────────────────────────────────────┘   │
│  ┌────────────────────▼─────────────────────────────────────┐   │
│  │  Data Layer                                              │   │
│  │  - State management (with undo/redo)                     │   │
│  │  - Validation engine                                     │   │
│  │  - Persistence (JSON/SQLite)                             │   │
│  └────────────────────┬─────────────────────────────────────┘   │
│  ┌────────────────────▼─────────────────────────────────────┐   │
│  │  Live Integration Layer (live_dev wrapper)              │   │
│  │  - Scene management                                      │   │
│  │  - Clip creation (MIDI + Audio)                          │   │
│  │  - Playback control                                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                 ↕
┌─────────────────────────────────────────────────────────────────┐
│              Ableton Live (via AbletonOSC)                       │
│              Port 11000 (existing live_dev integration)          │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Module Breakdown

#### **Core Modules** (python/src/arranger/)

```
arranger/
├── __init__.py
├── config.py                    # Configuration management
├── models/                      # Data models (Pydantic)
│   ├── __init__.py
│   ├── section.py              # Section, SectionType
│   ├── chord.py                # Chord, ChordProgression
│   ├── arrangement.py          # Arrangement, OrderItem
│   └── validation.py           # Validation rules
├── services/                    # Business logic
│   ├── __init__.py
│   ├── arrangement_manager.py  # Main orchestrator
│   ├── chord_resolver.py       # Chord → MIDI conversion
│   ├── scene_builder.py        # Scene/clip creation
│   ├── playback_scheduler.py   # Real-time playback sequencing
│   └── state_manager.py        # Undo/redo, persistence
├── api/                         # API layer
│   ├── __init__.py
│   ├── osc_server.py           # OSC endpoint handlers
│   ├── validators.py           # Request validation
│   └── responses.py            # Response formatters
├── live_bridge/                 # Live integration
│   ├── __init__.py
│   ├── scene_manager.py        # Scene CRUD operations
│   ├── clip_factory.py         # Clip creation strategies
│   └── transport_control.py    # Playback control
└── utils/                       # Utilities
    ├── __init__.py
    ├── chord_notation.py       # Chord parsing (Cmaj7, roman numerals)
    ├── midi_builder.py         # MIDI note generation
    └── logger.py               # Structured logging
```

#### **Testing Structure** (python/tests/arranger/)

```
tests/arranger/
├── __init__.py
├── conftest.py                 # Pytest fixtures
├── unit/                       # Unit tests (isolated)
│   ├── test_models.py
│   ├── test_chord_resolver.py
│   ├── test_validation.py
│   └── test_state_manager.py
├── integration/                # Integration tests
│   ├── test_arrangement_flow.py
│   ├── test_live_bridge.py
│   └── test_osc_api.py
├── fixtures/                   # Test data
│   ├── sample_arrangements.json
│   └── chord_progressions.json
└── mocks/                      # Mock objects
    ├── mock_live.py
    └── mock_osc_client.py
```

---

## Part 2: Data Model Enhancement

### 2.1 Core Models (Using Pydantic for Validation)

```python
# models/section.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum

class SectionType(str, Enum):
    INTRO = "intro"
    VERSE = "verse"
    CHORUS = "chorus"
    BRIDGE = "bridge"
    BREAKDOWN = "breakdown"
    DROP = "drop"
    OUTRO = "outro"
    CUSTOM = "custom"

class Section(BaseModel):
    """Represents a musical section with metadata."""
    label: str = Field(..., min_length=1, max_length=8, 
                      description="Short identifier (A, B, C, etc.)")
    type: SectionType
    bars: int = Field(..., gt=0, le=64, description="Length in bars")
    color: Optional[str] = Field(None, regex=r"^#[0-9A-Fa-f]{6}$")
    tempo_override: Optional[float] = Field(None, ge=20.0, le=999.0)
    time_signature: tuple[int, int] = (4, 4)
    chords: List["Chord"] = []
    metadata: dict = {}
    
    @validator("chords")
    def validate_chord_timing(cls, chords, values):
        """Ensure chord beats sum matches section bars."""
        if not chords:
            return chords
        total_beats = sum(c.beats for c in chords)
        expected_beats = values["bars"] * values["time_signature"][0]
        if total_beats != expected_beats:
            raise ValueError(
                f"Chord beats ({total_beats}) must equal "
                f"section beats ({expected_beats})"
            )
        return chords

    class Config:
        use_enum_values = True


# models/chord.py
class ChordQuality(str, Enum):
    MAJOR = "maj"
    MINOR = "min"
    DOMINANT = "7"
    MAJOR7 = "maj7"
    MINOR7 = "min7"
    DIMINISHED = "dim"
    AUGMENTED = "aug"
    SUS2 = "sus2"
    SUS4 = "sus4"

class Chord(BaseModel):
    """Musical chord with timing and voicing."""
    name: str = Field(..., description="Chord name (e.g., Cmaj7)")
    root: int = Field(..., ge=0, le=11, description="MIDI root note (0=C)")
    quality: ChordQuality
    beats: int = Field(..., gt=0, description="Duration in beats")
    roman: Optional[str] = None
    inversion: int = Field(0, ge=0, le=3)
    extensions: List[int] = []  # e.g., [9, 11, 13]
    voicing: Optional[List[int]] = None  # Custom MIDI notes
    
    @classmethod
    def from_name(cls, name: str, beats: int = 4):
        """Parse chord from string (Cmaj7, Dm7, etc.)."""
        # Implement chord parsing logic
        pass


# models/arrangement.py
class OrderItem(BaseModel):
    """Item in the arrangement order sequence."""
    section_label: str
    bars: Optional[int] = None  # Override section default
    repeat: int = Field(1, ge=1, le=16)
    transpose: int = Field(0, ge=-12, le=12)
    
class Arrangement(BaseModel):
    """Complete song arrangement."""
    title: str = "Untitled"
    bpm: float = Field(120.0, ge=20.0, le=999.0)
    key: str = "C"
    time_signature: tuple[int, int] = (4, 4)
    sections: List[Section] = []
    order: List[OrderItem] = []
    created_at: datetime
    modified_at: datetime
    version: int = 1
    
    @property
    def total_bars(self) -> int:
        """Calculate total arrangement length."""
        return sum(
            (item.bars or self._get_section(item.section_label).bars) * item.repeat
            for item in self.order
        )
    
    def _get_section(self, label: str) -> Section:
        """Find section by label."""
        for s in self.sections:
            if s.label == label:
                return s
        raise ValueError(f"Section {label} not found")
    
    def validate_order(self) -> List[str]:
        """Validate order references existing sections."""
        errors = []
        for item in self.order:
            try:
                self._get_section(item.section_label)
            except ValueError as e:
                errors.append(str(e))
        return errors
```

### 2.2 State Management with Undo/Redo

```python
# services/state_manager.py
from typing import List, Optional, Any
from dataclasses import dataclass
from copy import deepcopy
import json

@dataclass
class StateSnapshot:
    """Immutable snapshot of arrangement state."""
    arrangement: Arrangement
    timestamp: datetime
    description: str

class StateManager:
    """Manages arrangement state with undo/redo support."""
    
    def __init__(self, max_history: int = 50):
        self._current: Optional[Arrangement] = None
        self._history: List[StateSnapshot] = []
        self._redo_stack: List[StateSnapshot] = []
        self._max_history = max_history
        self._autosave_enabled = True
    
    def initialize(self, arrangement: Arrangement):
        """Initialize with new arrangement."""
        self._current = arrangement
        self._save_snapshot("Initial state")
    
    def update(self, arrangement: Arrangement, description: str):
        """Update state and save to history."""
        if self._current is None:
            return self.initialize(arrangement)
        
        snapshot = StateSnapshot(
            arrangement=deepcopy(self._current),
            timestamp=datetime.now(),
            description=description
        )
        self._history.append(snapshot)
        
        # Trim history if needed
        if len(self._history) > self._max_history:
            self._history.pop(0)
        
        self._current = arrangement
        self._redo_stack.clear()  # Clear redo on new action
        
        if self._autosave_enabled:
            self._autosave()
    
    def undo(self) -> Optional[Arrangement]:
        """Undo last change."""
        if not self._history:
            return None
        
        # Save current to redo stack
        redo_snapshot = StateSnapshot(
            arrangement=deepcopy(self._current),
            timestamp=datetime.now(),
            description="Redo point"
        )
        self._redo_stack.append(redo_snapshot)
        
        # Restore from history
        snapshot = self._history.pop()
        self._current = snapshot.arrangement
        return self._current
    
    def redo(self) -> Optional[Arrangement]:
        """Redo last undone change."""
        if not self._redo_stack:
            return None
        
        # Save current to history
        self._save_snapshot("Undo point")
        
        # Restore from redo stack
        snapshot = self._redo_stack.pop()
        self._current = snapshot.arrangement
        return self._current
    
    def save_to_file(self, filepath: str):
        """Persist arrangement to JSON."""
        with open(filepath, 'w') as f:
            json.dump(self._current.dict(), f, indent=2, default=str)
    
    def load_from_file(self, filepath: str) -> Arrangement:
        """Load arrangement from JSON."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        arrangement = Arrangement(**data)
        self.initialize(arrangement)
        return arrangement
    
    def _save_snapshot(self, description: str):
        """Internal snapshot helper."""
        snapshot = StateSnapshot(
            arrangement=deepcopy(self._current),
            timestamp=datetime.now(),
            description=description
        )
        self._history.append(snapshot)
    
    def _autosave(self):
        """Auto-save to temp file."""
        import tempfile
        temp_path = Path(tempfile.gettempdir()) / "arranger_autosave.json"
        self.save_to_file(str(temp_path))
```

---

## Part 3: Live Integration Layer

### 3.1 Enhanced Scene Manager (Builds on live_dev)

```python
# live_bridge/scene_manager.py
from live_dev import LiveConnection, M4LDeviceHelper
from typing import List, Dict, Optional
from ..models import Section, Arrangement

class SceneManager:
    """Manages Ableton Live scenes for arrangements."""
    
    def __init__(self, live: LiveConnection):
        self.live = live
        self.helper = M4LDeviceHelper(live)
        self._scene_map: Dict[str, int] = {}  # section_label -> scene_index
    
    def build_arrangement_scenes(
        self,
        arrangement: Arrangement,
        mode: str = "scenesClips",
        overwrite: str = "append"
    ) -> Dict[str, int]:
        """
        Create scenes and clips for entire arrangement.
        
        Args:
            arrangement: Arrangement model
            mode: 'scenesOnly' or 'scenesClips'
            overwrite: 'append' or 'replace'
            
        Returns:
            Mapping of section labels to scene indices
        """
        if overwrite == "replace":
            self._clear_existing_scenes()
        
        start_idx = 0 if overwrite == "replace" else self._get_scene_count()
        
        for idx, section in enumerate(arrangement.sections):
            scene_idx = start_idx + idx
            
            # Create scene
            self.live.send_osc("/live/song/create_scene", scene_idx)
            
            # Set scene name
            scene_name = f"{section.type.value.upper()} {section.label}"
            self.live.send_osc("/live/scene/set/name", scene_idx, scene_name)
            
            # Set scene color
            if section.color:
                color_int = self._hex_to_live_color(section.color)
                self.live.send_osc("/live/scene/set/color_index", scene_idx, color_int)
            
            # Set tempo if overridden
            if section.tempo_override:
                self.live.send_osc("/live/scene/set/tempo", scene_idx, section.tempo_override)
                self.live.send_osc("/live/scene/set/tempo_enabled", scene_idx, 1)
            
            self._scene_map[section.label] = scene_idx
            
            # Create clips if requested
            if mode == "scenesClips" and section.chords:
                self._create_section_clips(section, scene_idx, arrangement.bpm)
        
        return self._scene_map
    
    def _create_section_clips(self, section: Section, scene_idx: int, bpm: float):
        """Create MIDI clips for section chords."""
        # Ensure chord track exists
        chord_track_idx = self._ensure_chord_track()
        
        # Create clip slot
        clip_length = section.bars
        self.live.send_osc(
            "/live/clip_slot/create_clip",
            chord_track_idx,
            scene_idx,
            clip_length
        )
        
        # Add chord notes
        from ..live_bridge.clip_factory import ChordClipFactory
        factory = ChordClipFactory(self.live)
        factory.populate_chord_clip(
            track_idx=chord_track_idx,
            clip_idx=scene_idx,
            chords=section.chords,
            bars=section.bars,
            bpm=bpm
        )
    
    def _ensure_chord_track(self) -> int:
        """Ensure chord track exists, create if needed."""
        tracks = self.live.get_track_names()
        try:
            return tracks.index("Chords")
        except ValueError:
            # Create new MIDI track
            self.live.create_midi_track(0)
            self.live.scan()
            self.live.send_osc("/live/track/set/name", 0, "Chords")
            return 0
    
    def _get_scene_count(self) -> int:
        """Get current scene count."""
        # Use AbletonOSC to query
        # This needs callback handling - simplified for now
        return len(self.live.set.scenes) if hasattr(self.live.set, 'scenes') else 0
    
    def _clear_existing_scenes(self):
        """Delete all scenes (use with caution)."""
        scene_count = self._get_scene_count()
        for i in range(scene_count - 1, -1, -1):
            self.live.send_osc("/live/song/delete_scene", i)
    
    def _hex_to_live_color(self, hex_color: str) -> int:
        """Convert hex color to Live color index (0-69)."""
        # Live has 70 predefined colors
        # Implement color matching logic or use predefined mapping
        color_map = {
            "#ff0000": 4,   # Red
            "#ff9f3a": 12,  # Orange
            "#3aa3ff": 60,  # Blue
            # ... add more mappings
        }
        return color_map.get(hex_color.lower(), 0)
```

### 3.2 Chord Clip Factory

```python
# live_bridge/clip_factory.py
from typing import List, Dict
from ..models import Chord
from ..utils.midi_builder import MIDIBuilder

class ChordClipFactory:
    """Factory for creating MIDI clips with chord progressions."""
    
    def __init__(self, live: LiveConnection):
        self.live = live
        self.midi_builder = MIDIBuilder()
    
    def populate_chord_clip(
        self,
        track_idx: int,
        clip_idx: int,
        chords: List[Chord],
        bars: int,
        bpm: float,
        voicing_style: str = "close"
    ):
        """
        Populate a clip with chord MIDI notes.
        
        Args:
            track_idx: Track index
            clip_idx: Clip/scene index
            chords: List of Chord objects
            bars: Total clip length
            bpm: Tempo
            voicing_style: 'close', 'open', 'drop2', 'shell'
        """
        # Clear existing notes
        self.live.send_osc("/live/clip/remove/notes", track_idx, clip_idx)
        
        # Generate MIDI notes for each chord
        current_beat = 0.0
        for chord in chords:
            notes = self.midi_builder.chord_to_notes(
                chord=chord,
                style=voicing_style,
                octave=3  # Middle C range
            )
            
            # Add each note in the chord
            for midi_note in notes:
                self.live.send_osc(
                    "/live/clip/add/notes",
                    track_idx,
                    clip_idx,
                    midi_note,           # pitch
                    current_beat,        # start time
                    chord.beats,         # duration
                    100,                 # velocity
                    False                # not muted
                )
            
            current_beat += chord.beats
```

### 3.3 Playback Scheduler

```python
# services/playback_scheduler.py
import threading
import time
from typing import Optional, Callable
from ..models import Arrangement, OrderItem

class PlaybackScheduler:
    """Handles real-time playback sequencing."""
    
    def __init__(self, live: LiveConnection, scene_map: Dict[str, int]):
        self.live = live
        self.scene_map = scene_map
        self._playing = False
        self._follow_order = False
        self._current_order_idx = 0
        self._playback_thread: Optional[threading.Thread] = None
        self._on_section_change: Optional[Callable] = None
    
    def start_playback(self, arrangement: Arrangement, follow_order: bool = False):
        """Start playback from current position."""
        self._playing = True
        self._follow_order = follow_order
        
        if follow_order and arrangement.order:
            self._current_order_idx = 0
            self._playback_thread = threading.Thread(
                target=self._playback_loop,
                args=(arrangement,),
                daemon=True
            )
            self._playback_thread.start()
        else:
            # Just fire current scene
            self.live.send_osc("/live/song/start_playing")
    
    def stop_playback(self):
        """Stop playback."""
        self._playing = False
        self.live.send_osc("/live/song/stop_playing")
    
    def jump_to_section(self, section_label: str):
        """Jump to specific section."""
        if section_label in self.scene_map:
            scene_idx = self.scene_map[section_label]
            self.live.send_osc("/live/scene/fire", scene_idx)
        else:
            raise ValueError(f"Section {section_label} not found in scene map")
    
    def _playback_loop(self, arrangement: Arrangement):
        """Background thread for order-following playback."""
        while self._playing and self._current_order_idx < len(arrangement.order):
            order_item = arrangement.order[self._current_order_idx]
            section = arrangement._get_section(order_item.section_label)
            
            # Fire scene
            self.jump_to_section(order_item.section_label)
            
            # Notify listeners
            if self._on_section_change:
                self._on_section_change(section, self._current_order_idx)
            
            # Calculate wait time (bars to seconds)
            bars = order_item.bars or section.bars
            beats = bars * 4  # assuming 4/4
            seconds_per_beat = 60.0 / arrangement.bpm
            wait_time = beats * seconds_per_beat
            
            # Wait for section to complete
            time.sleep(wait_time)
            
            self._current_order_idx += 1
        
        self._playing = False
    
    def set_section_change_callback(self, callback: Callable):
        """Set callback for section changes."""
        self._on_section_change = callback
```

---

## Part 4: API Layer & OSC Server

### 4.1 Enhanced OSC Server with Error Handling

```python
# api/osc_server.py
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from typing import Optional
import json
import traceback

from ..services.arrangement_manager import ArrangementManager
from .validators import validate_json_payload, validate_commit_params
from .responses import ResponseFormatter

class ArrangerOSCServer:
    """OSC server for arranger with improved error handling."""
    
    def __init__(
        self,
        host: str = "127.0.0.1",
        listen_port: int = 12000,
        send_port: int = 12001
    ):
        self.host = host
        self.listen_port = listen_port
        self.send_port = send_port
        
        # Initialize services
        self.manager = ArrangementManager()
        self.ui_client = SimpleUDPClient(host, send_port)
        self.formatter = ResponseFormatter()
        
        # Setup OSC dispatcher
        self.dispatcher = Dispatcher()
        self._register_handlers()
        
        self.server: Optional[ThreadingOSCUDPServer] = None
    
    def _register_handlers(self):
        """Register all OSC endpoint handlers."""
        handlers = {
            "/session/new": self._handle_new_session,
            "/session/load_json": self._handle_load_json,
            "/session/save_json": self._handle_save_json,
            "/structure/set_sections": self._handle_set_sections,
            "/structure/add_section": self._handle_add_section,
            "/structure/remove_section": self._handle_remove_section,
            "/chords/set_for_section": self._handle_set_chords,
            "/order/set": self._handle_set_order,
            "/validate": self._handle_validate,
            "/commit": self._handle_commit,
            "/play": self._handle_play,
            "/stop": self._handle_stop,
            "/jump_to_section": self._handle_jump,
            "/follow_order": self._handle_follow_order,
            "/undo": self._handle_undo,
            "/redo": self._handle_redo,
        }
        
        for addr, handler in handlers.items():
            self.dispatcher.map(addr, self._wrap_handler(handler))
    
    def _wrap_handler(self, handler):
        """Wrap handler with error handling and logging."""
        def wrapped(addr, *args):
            try:
                logger.info(f"OSC <- {addr} {args}")
                result = handler(addr, *args)
                return result
            except Exception as e:
                error_msg = f"Error in {addr}: {str(e)}"
                logger.error(error_msg)
                logger.debug(traceback.format_exc())
                self._send_error(error_msg)
        return wrapped
    
    # Handler implementations
    def _handle_new_session(self, addr, *args):
        """Create new arrangement session."""
        self.manager.new_session()
        self._send_state_update()
    
    def _handle_load_json(self, addr, json_str):
        """Load arrangement from JSON."""
        data = validate_json_payload(json_str)
        self.manager.load_from_dict(data)
        self._send_state_update()
    
    def _handle_save_json(self, addr, filepath):
        """Save arrangement to file."""
        self.manager.save_to_file(filepath)
        self._send_ui("/live/done", "saved")
    
    def _handle_set_sections(self, addr, json_str):
        """Set all sections."""
        sections_data = validate_json_payload(json_str)
        self.manager.set_sections(sections_data)
        self._send_state_update()
    
    def _handle_set_chords(self, addr, json_str):
        """Set chords for a section."""
        data = validate_json_payload(json_str)
        section_label = data["sectionLabel"]
        chords = data["chords"]
        self.manager.set_section_chords(section_label, chords)
        self._send_state_update()
    
    def _handle_validate(self, addr, *args):
        """Validate current arrangement."""
        errors = self.manager.validate()
        result = {
            "ok": len(errors) == 0,
            "errors": errors
        }
        summary = self.manager.get_summary()
        summary.update(result)
        self._send_ui("/state/summary", summary)
    
    def _handle_commit(self, addr, mode="scenesClips", overwrite="append"):
        """Commit arrangement to Live."""
        mode, overwrite = validate_commit_params(mode, overwrite)
        
        # Send progress updates
        def progress_callback(phase: str, percent: float):
            self._send_ui("/live/progress", {"phase": phase, "percent": percent})
        
        try:
            self.manager.commit_to_live(
                mode=mode,
                overwrite=overwrite,
                progress_callback=progress_callback
            )
            self._send_ui("/live/done", "commit_ok")
        except Exception as e:
            self._send_error(f"Commit failed: {e}")
    
    def _handle_undo(self, addr, *args):
        """Undo last change."""
        if self.manager.undo():
            self._send_state_update()
        else:
            self._send_error("Nothing to undo")
    
    def _handle_redo(self, addr, *args):
        """Redo last undone change."""
        if self.manager.redo():
            self._send_state_update()
        else:
            self._send_error("Nothing to redo")
    
    # UI communication helpers
    def _send_state_update(self):
        """Send current state to UI."""
        summary = self.manager.get_summary()
        self._send_ui("/state/summary", summary)
    
    def _send_ui(self, addr: str, payload):
        """Send message to UI."""
        if not isinstance(payload, (str, int, float)):
            payload = json.dumps(payload, default=str)
        logger.info(f"OSC -> {addr} {payload}")
        self.ui_client.send_message(addr, payload)
    
    def _send_error(self, message: str):
        """Send error message to UI."""
        self._send_ui("/live/error", message)
    
    def start(self):
        """Start OSC server."""
        self.server = ThreadingOSCUDPServer(
            (self.host, self.listen_port),
            self.dispatcher
        )
        logger.info(f"Arranger OSC server listening on {self.host}:{self.listen_port}")
        self.server.serve_forever()
    
    def stop(self):
        """Stop OSC server."""
        if self.server:
            self.server.shutdown()
```

---

## Part 5: Testing Strategy

### 5.1 Unit Tests

```python
# tests/arranger/unit/test_models.py
import pytest
from arranger.models import Section, Chord, Arrangement, SectionType

def test_section_validation():
    """Test section model validation."""
    # Valid section
    section = Section(label="A", type=SectionType.VERSE, bars=8)
    assert section.bars == 8
    
    # Invalid bars
    with pytest.raises(ValueError):
        Section(label="A", type=SectionType.VERSE, bars=0)
    
    # Invalid color
    with pytest.raises(ValueError):
        Section(label="A", type=SectionType.VERSE, bars=8, color="invalid")

def test_chord_beat_validation():
    """Test chord timing validation."""
    chords = [
        Chord(name="Cmaj7", root=0, quality="maj7", beats=4),
        Chord(name="Am7", root=9, quality="min7", beats=4),
    ]
    section = Section(
        label="A",
        type=SectionType.VERSE,
        bars=2,
        chords=chords
    )
    # 2 bars * 4 beats = 8 beats total, matches chord sum
    assert sum(c.beats for c in section.chords) == 8

def test_arrangement_order_validation():
    """Test arrangement order validation."""
    arrangement = Arrangement(
        sections=[
            Section(label="A", type=SectionType.VERSE, bars=8),
            Section(label="B", type=SectionType.CHORUS, bars=8),
        ],
        order=[
            {"sectionLabel": "A", "bars": None, "repeat": 1},
            {"sectionLabel": "C", "bars": None, "repeat": 1},  # Invalid!
        ]
    )
    errors = arrangement.validate_order()
    assert len(errors) == 1
    assert "C" in errors[0]
```

### 5.2 Integration Tests

```python
# tests/arranger/integration/test_arrangement_flow.py
import pytest
from arranger.services.arrangement_manager import ArrangementManager

@pytest.fixture
def manager():
    """Create arrangement manager for tests."""
    return ArrangementManager()

@pytest.fixture
def sample_arrangement(manager):
    """Create sample arrangement."""
    manager.new_session()
    manager.set_sections([
        {"label": "A", "type": "verse", "bars": 8},
        {"label": "B", "type": "chorus", "bars": 8},
    ])
    manager.set_section_chords("A", [
        {"name": "Cmaj7", "root": 0, "quality": "maj7", "beats": 4},
        {"name": "Am7", "root": 9, "quality": "min7", "beats": 4},
    ])
    return manager

def test_full_arrangement_workflow(sample_arrangement):
    """Test complete arrangement creation workflow."""
    manager = sample_arrangement
    
    # Set order
    manager.set_order([
        {"sectionLabel": "A", "repeat": 2},
        {"sectionLabel": "B", "repeat": 1},
    ])
    
    # Validate
    errors = manager.validate()
    assert len(errors) == 0
    
    # Get summary
    summary = manager.get_summary()
    assert summary["title"] == "Untitled"
    assert len(summary["sections"]) == 2
    assert len(summary["order"]) == 3  # A twice, B once

def test_undo_redo(manager):
    """Test state management."""
    manager.new_session()
    
    # Make changes
    manager.set_sections([{"label": "A", "type": "verse", "bars": 8}])
    state1 = manager.get_summary()
    
    manager.set_sections([{"label": "B", "type": "chorus", "bars": 8}])
    state2 = manager.get_summary()
    
    # Undo
    manager.undo()
    state_undone = manager.get_summary()
    assert state_undone == state1
    
    # Redo
    manager.redo()
    state_redone = manager.get_summary()
    assert state_redone == state2
```

### 5.3 Mock Live Bridge for Testing

```python
# tests/arranger/mocks/mock_live.py
from typing import List, Dict, Any

class MockLiveConnection:
    """Mock Live connection for testing without Ableton."""
    
    def __init__(self):
        self.osc_calls: List[tuple] = []
        self.scenes: List[Dict] = []
        self.tracks: List[Dict] = []
    
    def send_osc(self, addr: str, *args):
        """Record OSC calls."""
        self.osc_calls.append((addr, args))
        
        # Simulate scene creation
        if addr == "/live/song/create_scene":
            self.scenes.append({"index": args[0], "name": "", "color": None})
    
    def get_last_osc_call(self) -> tuple:
        """Get most recent OSC call."""
        return self.osc_calls[-1] if self.osc_calls else None
    
    def clear_calls(self):
        """Clear call history."""
        self.osc_calls.clear()
```

---

## Part 6: Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal**: Core data models and state management

- [ ] Create `arranger/models/` with Pydantic models
- [ ] Implement `StateManager` with undo/redo
- [ ] Write unit tests for models (>90% coverage)
- [ ] Add JSON serialization/deserialization
- [ ] Create sample fixture files

**Deliverable**: Validated data models with persistence

### Phase 2: Live Bridge (Week 2)
**Goal**: Robust Live integration

- [ ] Implement `SceneManager` using live_dev
- [ ] Create `ChordClipFactory` with MIDI generation
- [ ] Add `TransportControl` for playback
- [ ] Build `PlaybackScheduler` for order following
- [ ] Write integration tests with mock Live

**Deliverable**: Working Live scene/clip creation

### Phase 3: Business Logic (Week 3)
**Goal**: Arrangement management and validation

- [ ] Implement `ArrangementManager` orchestrator
- [ ] Create `ChordResolver` for notation parsing
- [ ] Add comprehensive validation rules
- [ ] Build chord notation parser (Cmaj7, roman numerals)
- [ ] Write workflow integration tests

**Deliverable**: Complete backend logic

### Phase 4: API Layer (Week 4)
**Goal**: OSC server with error handling

- [ ] Implement `ArrangerOSCServer` with all endpoints
- [ ] Add request validation layer
- [ ] Create response formatters
- [ ] Add structured logging
- [ ] Write OSC endpoint tests

**Deliverable**: Production-ready backend service

### Phase 5: Max for Live Device (Week 5-6)
**Goal**: Professional UI

- [ ] Create base device structure with tabs
- [ ] Build Structure UI (section grid)
- [ ] Build Chords UI (per-section editor)
- [ ] Build Order UI (sequencer grid)
- [ ] Add Commit UI with preview
- [ ] Implement bi-directional state sync

**Deliverable**: Complete M4L device

### Phase 6: Polish & Extensions (Week 7-8)
**Goal**: Production features

- [ ] Add keyboard shortcuts
- [ ] Implement drag-and-drop in Order view
- [ ] Add color theming system
- [ ] Create preset library system
- [ ] Build export/import for sharing
- [ ] Add hardware controller support
- [ ] Performance optimization
- [ ] Documentation and tutorials

**Deliverable**: Release-ready system

---

## Part 7: Key Improvements Summary

### ✅ Architectural
1. **Modular design** - Clear separation of concerns
2. **Leverages existing code** - Builds on live_dev integration
3. **Testable** - Comprehensive test coverage at all layers
4. **Extensible** - Easy to add features (audio clips, automation, etc.)

### ✅ Robustness
1. **Error handling** - Graceful failure recovery
2. **State management** - Undo/redo support
3. **Validation** - Multiple validation layers
4. **Persistence** - Auto-save and file management

### ✅ Developer Experience
1. **Type safety** - Pydantic models with validation
2. **Logging** - Structured logging throughout
3. **Documentation** - Inline docs and examples
4. **Debugging** - Mock objects for testing

### ✅ User Experience
1. **Real-time feedback** - Progress indicators
2. **Error messages** - Clear, actionable errors
3. **State preservation** - Undo/redo
4. **Persistence** - Save/load arrangements

---

## Part 8: Next Steps

### Immediate Actions
1. **Create feature branch**: `feature/song-arranger-system`
2. **Set up project structure**: Create directory hierarchy
3. **Install dependencies**: Add to requirements.txt
4. **Create Phase 1 scaffold**: Models and tests

### Development Workflow
1. Test-driven development (TDD)
2. Feature branches for each phase
3. Code review before merge
4. Continuous integration (pytest on commit)
5. Documentation as you go

---

## Appendix: Technology Stack

### Backend
- **Python 3.8+**
- **Pydantic** - Data validation
- **python-osc** - OSC communication
- **pytest** - Testing framework
- **live_dev** - Existing Live integration

### Max for Live
- **Max 8.5+**
- **live.* objects** - Native UI components
- **jit.cellblock** - Data grids
- **dict** - Data structures

### Optional Enhancements
- **FastAPI** - Alternative to pure OSC (HTTP API)
- **SQLite** - Arrangement library database
- **Redis** - Real-time state sync
- **WebSocket** - Browser-based editor

---

**Ready to begin implementation?** 
I can create the feature branch and scaffold the Phase 1 structure now.
