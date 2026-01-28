"""
Compatibility adapters for migrating from legacy models to Pydantic models.

Provides property-based adapters that make Pydantic models compatible
with legacy code expectations.
"""

from typing import List, Optional
from arranger.models.section import Section as PydanticSection, SectionType
from arranger.models.chord import Chord as PydanticChord, ChordQuality


class SectionAdapter:
    """
    Adapter that makes Pydantic Section compatible with legacy code.
    
    Provides 'name' property that maps to 'label', and other
    legacy-compatible properties.
    """
    
    def __init__(self, section: PydanticSection):
        self._section = section
    
    @property
    def name(self) -> str:
        """Legacy 'name' property maps to 'label'."""
        return self._section.label
    
    @name.setter
    def name(self, value: str):
        """Set name (updates label)."""
        self._section.label = value[:8]  # Truncate to max 8 chars
    
    @property
    def bars(self) -> int:
        """Bars property."""
        return self._section.bars
    
    @bars.setter
    def bars(self, value: int):
        """Set bars."""
        self._section.bars = value
    
    @property
    def tempo(self) -> Optional[float]:
        """Tempo property maps to tempo_override."""
        return self._section.tempo_override
    
    @tempo.setter
    def tempo(self, value: Optional[float]):
        """Set tempo."""
        self._section.tempo_override = value
    
    @property
    def timesig_num(self) -> int:
        """Time signature numerator."""
        return self._section.time_signature[0]
    
    @timesig_num.setter
    def timesig_num(self, value: int):
        """Set time signature numerator."""
        self._section.time_signature = (value, self._section.time_signature[1])
    
    @property
    def timesig_denom(self) -> int:
        """Time signature denominator."""
        return self._section.time_signature[1]
    
    @timesig_denom.setter
    def timesig_denom(self, value: int):
        """Set time signature denominator."""
        self._section.time_signature = (self._section.time_signature[0], value)
    
    @property
    def chords(self) -> List:
        """Chords list - returns ChordAdapter instances."""
        return [ChordAdapter(c) for c in self._section.chords]
    
    @chords.setter
    def chords(self, value: List):
        """Set chords - accepts ChordAdapter or PydanticChord."""
        self._section.chords = [
            c._chord if isinstance(c, ChordAdapter) else c 
            for c in value
            if isinstance(c, (ChordAdapter, PydanticChord))
        ]
    
    @property
    def lyrics(self) -> Optional[str]:
        """Lyrics from metadata."""
        return self._section.metadata.get('lyrics')
    
    @lyrics.setter
    def lyrics(self, value: Optional[str]):
        """Set lyrics in metadata."""
        if value:
            self._section.metadata['lyrics'] = value
        elif 'lyrics' in self._section.metadata:
            del self._section.metadata['lyrics']
    
    def get_color(self) -> int:
        """Get color as integer (legacy format)."""
        if self._section.color:
            # Convert hex to integer (0xRRGGBB format)
            hex_color = self._section.color.lstrip('#')
            return int(hex_color, 16)
        # Default color based on section type
        return 0x808080
    
    @property
    def total_beats(self) -> float:
        """Calculate total beats in this section."""
        beats_per_bar = self.timesig_num * (4.0 / self.timesig_denom)
        return self.bars * beats_per_bar
    
    def length_seconds(self, default_tempo: float = 120.0) -> float:
        """Calculate length in seconds."""
        tempo = self.tempo if self.tempo and self.tempo > 0 else default_tempo
        beats_per_bar = self.timesig_num * (4.0 / self.timesig_denom)
        beats = self.bars * beats_per_bar
        return (beats * 60.0) / tempo
    
    def to_dict(self) -> dict:
        """Convert to dictionary (legacy format)."""
        return {
            "name": self.name,
            "bars": self.bars,
            "tempo": self.tempo,
            "timesig_num": self.timesig_num,
            "timesig_denom": self.timesig_denom,
            "chords": [c.to_dict() for c in self.chords],
            "lyrics": self.lyrics
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary (legacy format)."""
        # Convert legacy format to Pydantic format
        pydantic_data = {
            "label": data.get("name", data.get("label", "Section")),
            "type": SectionType.CUSTOM,  # Default
            "bars": data.get("bars", 4),
            "tempo_override": data.get("tempo"),
            "time_signature": (
                data.get("timesig_num", 4),
                data.get("timesig_denom", 4)
            ),
            "chords": [],
            "metadata": {}
        }
        
        # Convert chords
        if "chords" in data:
            for chord_data in data["chords"]:
                if isinstance(chord_data, dict):
                    # Try to create Pydantic chord
                    try:
                        pydantic_data["chords"].append(PydanticChord(**chord_data))
                    except:
                        # Fallback: use adapter conversion
                        from arranger.utils.converters import legacy_chord_to_pydantic
                        try:
                            class LegacyChord:
                                def __init__(self, **kwargs):
                                    for k, v in kwargs.items():
                                        setattr(self, k, v)
                            legacy = LegacyChord(**chord_data)
                            pydantic_data["chords"].append(legacy_chord_to_pydantic(legacy))
                        except:
                            pass
        
        # Add lyrics to metadata
        if "lyrics" in data:
            pydantic_data["metadata"]["lyrics"] = data["lyrics"]
        
        section = PydanticSection(**pydantic_data)
        return cls(section)
    
    def __getattr__(self, name):
        """Forward any other attributes to the underlying section."""
        return getattr(self._section, name)


class ChordAdapter:
    """
    Adapter that makes Pydantic Chord compatible with legacy code.
    
    Provides legacy-compatible properties like 'type_idx', 'start_beat', etc.
    """
    
    def __init__(self, chord: PydanticChord):
        self._chord = chord
        # Store timing info in metadata if not in model
        if 'start_beat' not in self._chord.metadata:
            self._chord.metadata['start_beat'] = 0.0
        if 'duration_beats' not in self._chord.metadata:
            self._chord.metadata['duration_beats'] = float(chord.beats)
    
    @property
    def root(self) -> int:
        """Root note (0-11)."""
        return self._chord.root
    
    @root.setter
    def root(self, value: int):
        """Set root note."""
        self._chord.root = value
        # Update name
        self._update_name()
    
    @property
    def type_idx(self) -> int:
        """Type index (legacy format) - maps to quality."""
        quality_to_type = {
            ChordQuality.MAJOR: 1,
            ChordQuality.MINOR: 2,
            ChordQuality.DIMINISHED: 3,
            ChordQuality.DOMINANT: 9,
            ChordQuality.MINOR7: 6,
            ChordQuality.MAJOR7: 8,
        }
        return quality_to_type.get(self._chord.quality, 1)
    
    @type_idx.setter
    def type_idx(self, value: int):
        """Set type index (maps to quality)."""
        type_to_quality = {
            1: ChordQuality.MAJOR,
            2: ChordQuality.MINOR,
            3: ChordQuality.DIMINISHED,
            9: ChordQuality.DOMINANT,
            6: ChordQuality.MINOR7,
            8: ChordQuality.MAJOR7,
        }
        self._chord.quality = type_to_quality.get(value, ChordQuality.MAJOR)
        self._update_name()
    
    @property
    def start_beat(self) -> float:
        """Start beat (stored in metadata)."""
        return self._chord.metadata.get('start_beat', 0.0)
    
    @start_beat.setter
    def start_beat(self, value: float):
        """Set start beat."""
        self._chord.metadata['start_beat'] = value
    
    @property
    def duration_beats(self) -> float:
        """Duration in beats."""
        return self._chord.metadata.get('duration_beats', float(self._chord.beats))
    
    @duration_beats.setter
    def duration_beats(self, value: float):
        """Set duration in beats."""
        self._chord.metadata['duration_beats'] = value
        self._chord.beats = int(value)
    
    @property
    def inversion(self) -> int:
        """Inversion."""
        return self._chord.inversion
    
    @inversion.setter
    def inversion(self, value: int):
        """Set inversion."""
        self._chord.inversion = value
    
    @property
    def bass_note(self) -> Optional[int]:
        """Bass note (from extensions or metadata)."""
        return self._chord.metadata.get('bass_note')
    
    @bass_note.setter
    def bass_note(self, value: Optional[int]):
        """Set bass note."""
        if value is not None:
            self._chord.metadata['bass_note'] = value
        elif 'bass_note' in self._chord.metadata:
            del self._chord.metadata['bass_note']
    
    @property
    def octave(self) -> int:
        """Octave (from metadata, default 4)."""
        return self._chord.metadata.get('octave', 4)
    
    @octave.setter
    def octave(self, value: int):
        """Set octave."""
        self._chord.metadata['octave'] = value
    
    def _update_name(self):
        """Update chord name from root and quality."""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        root_name = note_names[self._chord.root]
        self._chord.name = f"{root_name}{self._chord.quality.value}"
    
    def to_dict(self) -> dict:
        """Convert to dictionary (legacy format)."""
        return {
            "root": self.root,
            "type_idx": self.type_idx,
            "start_beat": self.start_beat,
            "duration_beats": self.duration_beats,
            "inversion": self.inversion,
            "bass_note": self.bass_note,
            "octave": self.octave
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary (legacy format)."""
        # Convert to Pydantic format
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        root = data.get("root", 0)
        type_idx = data.get("type_idx", 1)
        
        type_to_quality = {
            1: ChordQuality.MAJOR,
            2: ChordQuality.MINOR,
            3: ChordQuality.DIMINISHED,
            9: ChordQuality.DOMINANT,
            6: ChordQuality.MINOR7,
            8: ChordQuality.MAJOR7,
        }
        quality = type_to_quality.get(type_idx, ChordQuality.MAJOR)
        root_name = note_names[root]
        
        pydantic_data = {
            "name": f"{root_name}{quality.value}",
            "root": root,
            "quality": quality,
            "beats": int(data.get("duration_beats", 4)),
            "inversion": data.get("inversion", 0),
            "metadata": {
                "start_beat": data.get("start_beat", 0.0),
                "duration_beats": data.get("duration_beats", 4.0),
                "octave": data.get("octave", 4)
            }
        }
        
        if "bass_note" in data and data["bass_note"] is not None:
            pydantic_data["metadata"]["bass_note"] = data["bass_note"]
        
        chord = PydanticChord(**pydantic_data)
        return cls(chord)
    
    def __getattr__(self, name):
        """Forward any other attributes to the underlying chord."""
        return getattr(self._chord, name)
