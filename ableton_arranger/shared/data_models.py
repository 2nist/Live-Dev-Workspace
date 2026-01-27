"""
Shared data models for inter-module communication.
Designed for easy serialization and M4L device communication.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import json


class AnalysisStatus(Enum):
    """Status of analysis process."""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class SongInfo:
    """Basic song metadata."""
    title: str = ""
    artist: str = ""
    duration_seconds: float = 0.0
    file_path: str = ""
    source_url: str = ""  # For YouTube imports
    file_format: str = ""


@dataclass
class SectionData:
    """Detected section information."""
    name: str
    start_time: float  # seconds
    end_time: float  # seconds
    confidence: float  # 0.0 to 1.0
    section_type: str  # intro, verse, chorus, bridge, outro, etc.
    energy_level: float = 0.0  # 0.0 to 1.0
    
    def duration_seconds(self) -> float:
        return self.end_time - self.start_time
    
    def to_arrangement_section(self, tempo: float = 120.0):
        """Convert to Section object for arrangement building."""
        from ableton_arranger.core.section import Section
        
        # Calculate bars from duration and tempo
        beats_per_second = tempo / 60.0
        duration_beats = self.duration_seconds() * beats_per_second
        bars = max(1, round(duration_beats / 4.0))  # Assume 4/4
        
        return Section(
            name=self.name,
            bars=bars,
            tempo=tempo,
            timesig_num=4,
            timesig_denom=4
        )


@dataclass
class ChordData:
    """Detected chord information."""
    root: str  # C, D, E, etc.
    quality: str  # maj, min, dim, aug, etc.
    extensions: List[str] = field(default_factory=list)  # 7, 9, sus4, etc.
    bass_note: str = ""  # For slash chords
    start_time: float = 0.0  # seconds
    end_time: float = 0.0  # seconds
    confidence: float = 0.0  # 0.0 to 1.0
    
    def to_chord_object(self, start_beat: float, duration_beats: float):
        """Convert to Chord object for timeline display."""
        from ableton_arranger.core.chord import Chord, get_chord_name
        import ableton_arranger.config as config
        
        # Convert root name to index
        root_idx = config.NOTE_NAMES.index(self.root) if self.root in config.NOTE_NAMES else 0
        
        # Find type_idx from quality
        type_idx = 1  # Default to major
        for i, chord_type in enumerate(config.CHORD_TYPES):
            if chord_type["name"] == self.quality.lower():
                type_idx = i + 1
                break
        
        # Convert bass note
        bass_note_idx = None
        if self.bass_note and self.bass_note in config.NOTE_NAMES:
            bass_note_idx = config.NOTE_NAMES.index(self.bass_note)
        
        return Chord(
            root=root_idx,
            type_idx=type_idx,
            start_beat=start_beat,
            duration_beats=duration_beats,
            inversion=0,  # Could be calculated from bass_note
            bass_note=bass_note_idx,
            octave=4
        )


@dataclass
class LyricsData:
    """Transcribed lyrics with timing."""
    full_text: str = ""
    words: List[Dict[str, Any]] = field(default_factory=list)  # [{"word": "hello", "start": 1.5, "end": 1.8, "confidence": 0.9}]
    language: str = "en"
    confidence: float = 0.0


@dataclass
class StemData:
    """Audio stem separation results."""
    vocals_path: str = ""
    drums_path: str = ""
    bass_path: str = ""
    other_path: str = ""
    melody_path: str = ""  # May be same as "other" initially
    
    def get_stem_paths(self) -> Dict[str, str]:
        """Get mapping of role names to file paths."""
        return {
            "Vocals": self.vocals_path,
            "Drums": self.drums_path,
            "Bass": self.bass_path,
            "Melody": self.melody_path,
            "Other": self.other_path
        }


@dataclass
class AnalysisData:
    """Complete analysis result from audio file."""
    song_info: SongInfo
    sections: List[SectionData] = field(default_factory=list)
    chords: List[ChordData] = field(default_factory=list)
    lyrics: LyricsData = field(default_factory=LyricsData)
    stems: StemData = field(default_factory=StemData)
    
    # Musical analysis
    tempo: float = 120.0
    key_signature: str = "C"
    time_signature_num: int = 4
    time_signature_denom: int = 4
    
    # Analysis metadata
    status: AnalysisStatus = AnalysisStatus.IDLE
    error_message: str = ""
    analysis_time: float = 0.0  # seconds to complete
    api_costs: Dict[str, float] = field(default_factory=dict)  # track API usage
    
    def to_json(self) -> str:
        """Serialize to JSON for storage/transmission."""
        # Convert dataclass to dict, handle enums
        data_dict = {}
        for key, value in self.__dict__.items():
            if isinstance(value, AnalysisStatus):
                data_dict[key] = value.value
            elif hasattr(value, '__dict__'):
                data_dict[key] = value.__dict__
            elif isinstance(value, list):
                data_dict[key] = [item.__dict__ if hasattr(item, '__dict__') else item for item in value]
            else:
                data_dict[key] = value
        
        return json.dumps(data_dict, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str):
        """Deserialize from JSON."""
        data = json.loads(json_str)
        
        # Reconstruct nested objects
        song_info = SongInfo(**data.get('song_info', {}))
        
        sections = []
        for section_data in data.get('sections', []):
            sections.append(SectionData(**section_data))
        
        chords = []
        for chord_data in data.get('chords', []):
            chords.append(ChordData(**chord_data))
        
        lyrics = LyricsData(**data.get('lyrics', {}))
        stems = StemData(**data.get('stems', {}))
        
        return cls(
            song_info=song_info,
            sections=sections,
            chords=chords,
            lyrics=lyrics,
            stems=stems,
            tempo=data.get('tempo', 120.0),
            key_signature=data.get('key_signature', 'C'),
            time_signature_num=data.get('time_signature_num', 4),
            time_signature_denom=data.get('time_signature_denom', 4),
            status=AnalysisStatus(data.get('status', 'idle')),
            error_message=data.get('error_message', ''),
            analysis_time=data.get('analysis_time', 0.0),
            api_costs=data.get('api_costs', {})
        )


@dataclass  
class AnalysisConfig:
    """Configuration for analysis process."""
    # API settings
    sonoteller_api_key: str = ""
    use_local_whisper: bool = True
    whisper_model: str = "base"  # tiny, base, small, medium, large
    
    # Processing options
    enable_stem_separation: bool = True
    enable_chord_detection: bool = True
    enable_lyrics_transcription: bool = True
    enable_structure_detection: bool = True
    
    # Quality settings
    audio_quality: str = "medium"  # low, medium, high
    tempo_detection_method: str = "api"  # api, ableton, both
    
    # Output paths
    temp_dir: str = "data/temp"
    cache_results: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for M4L compatibility."""
        return self.__dict__.copy()
