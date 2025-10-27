"""
Chord model - represents musical chords with timing and voicing
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum
import re


class ChordQuality(str, Enum):
    """Standard chord qualities."""
    MAJOR = "maj"
    MINOR = "min"
    DOMINANT = "7"
    MAJOR7 = "maj7"
    MINOR7 = "min7"
    MAJOR6 = "maj6"
    MINOR6 = "min6"
    DIMINISHED = "dim"
    DIMINISHED7 = "dim7"
    HALF_DIMINISHED = "m7b5"
    AUGMENTED = "aug"
    SUS2 = "sus2"
    SUS4 = "sus4"


class Chord(BaseModel):
    """
    Musical chord with timing and voicing information.
    
    Represents a chord with its root note, quality, duration,
    and optional voicing/inversion details.
    """
    name: str = Field(
        ...,
        description="Chord name (e.g., Cmaj7, Dm7, G7)"
    )
    root: int = Field(
        ...,
        ge=0,
        le=11,
        description="MIDI root note (0=C, 1=C#, 2=D, etc.)"
    )
    quality: ChordQuality = Field(
        ...,
        description="Chord quality (maj, min, 7, etc.)"
    )
    beats: int = Field(
        ...,
        gt=0,
        description="Duration in beats"
    )
    roman: Optional[str] = Field(
        None,
        description="Roman numeral notation (I, ii, V7, etc.)"
    )
    inversion: int = Field(
        0,
        ge=0,
        le=3,
        description="Inversion (0=root, 1=1st, 2=2nd, 3=3rd)"
    )
    extensions: List[int] = Field(
        default_factory=list,
        description="Extensions (e.g., [9, 11, 13])"
    )
    voicing: Optional[List[int]] = Field(
        None,
        description="Custom MIDI notes (overrides generated voicing)"
    )
    
    @validator("extensions")
    def validate_extensions(cls, v):
        """Validate chord extensions."""
        valid_extensions = {9, 11, 13}
        for ext in v:
            if ext not in valid_extensions:
                raise ValueError(f"Invalid extension: {ext}. Must be 9, 11, or 13")
        return v
    
    @classmethod
    def from_name(cls, name: str, beats: int = 4) -> "Chord":
        """
        Parse chord from string notation.
        
        Examples:
            - "Cmaj7" -> root=0, quality=maj7
            - "Dm7" -> root=2, quality=min7
            - "G7" -> root=7, quality=7
            
        Args:
            name: Chord name string
            beats: Duration in beats
            
        Returns:
            Chord instance
        """
        # Parse root note
        note_map = {
            'C': 0, 'D': 2, 'E': 4, 'F': 5,
            'G': 7, 'A': 9, 'B': 11
        }
        
        # Handle sharps and flats
        root_match = re.match(r'^([A-G][#b]?)', name)
        if not root_match:
            raise ValueError(f"Invalid chord name: {name}")
        
        root_str = root_match.group(1)
        base_note = note_map[root_str[0]]
        
        if len(root_str) > 1:
            if root_str[1] == '#':
                base_note = (base_note + 1) % 12
            elif root_str[1] == 'b':
                base_note = (base_note - 1) % 12
        
        # Parse quality
        quality_str = name[len(root_str):].lower()
        
        # Map common variations to ChordQuality
        quality_map = {
            '': ChordQuality.MAJOR,
            'maj': ChordQuality.MAJOR,
            'M': ChordQuality.MAJOR,
            'm': ChordQuality.MINOR,
            'min': ChordQuality.MINOR,
            '-': ChordQuality.MINOR,
            '7': ChordQuality.DOMINANT,
            'maj7': ChordQuality.MAJOR7,
            'M7': ChordQuality.MAJOR7,
            'm7': ChordQuality.MINOR7,
            'min7': ChordQuality.MINOR7,
            '-7': ChordQuality.MINOR7,
            'dim': ChordQuality.DIMINISHED,
            'aug': ChordQuality.AUGMENTED,
            'sus2': ChordQuality.SUS2,
            'sus4': ChordQuality.SUS4,
        }
        
        quality = quality_map.get(quality_str, ChordQuality.MAJOR)
        
        return cls(
            name=name,
            root=base_note,
            quality=quality,
            beats=beats
        )
    
    def to_midi_notes(self, octave: int = 3, style: str = "close") -> List[int]:
        """
        Generate MIDI note numbers for this chord.
        
        Args:
            octave: Base octave (3 = middle C range)
            style: Voicing style ('close', 'open', 'drop2', 'shell')
            
        Returns:
            List of MIDI note numbers
        """
        if self.voicing:
            return self.voicing
        
        base_note = (octave * 12) + self.root
        
        # Intervals for each quality (semitones from root)
        quality_intervals = {
            ChordQuality.MAJOR: [0, 4, 7],
            ChordQuality.MINOR: [0, 3, 7],
            ChordQuality.DOMINANT: [0, 4, 7, 10],
            ChordQuality.MAJOR7: [0, 4, 7, 11],
            ChordQuality.MINOR7: [0, 3, 7, 10],
            ChordQuality.MAJOR6: [0, 4, 7, 9],
            ChordQuality.MINOR6: [0, 3, 7, 9],
            ChordQuality.DIMINISHED: [0, 3, 6],
            ChordQuality.DIMINISHED7: [0, 3, 6, 9],
            ChordQuality.HALF_DIMINISHED: [0, 3, 6, 10],
            ChordQuality.AUGMENTED: [0, 4, 8],
            ChordQuality.SUS2: [0, 2, 7],
            ChordQuality.SUS4: [0, 5, 7],
        }
        
        intervals = quality_intervals.get(self.quality, [0, 4, 7])
        notes = [base_note + interval for interval in intervals]
        
        # Apply inversion
        for _ in range(self.inversion):
            notes[0] += 12
            notes.sort()
        
        # Add extensions
        for ext in self.extensions:
            # Extensions are added in the next octave
            ext_interval = {9: 2, 11: 5, 13: 9}[ext]
            notes.append(base_note + 12 + ext_interval)
        
        return notes
    
    class Config:
        use_enum_values = True
        json_encoders = {
            ChordQuality: lambda v: v.value
        }
