"""
Section data model and helper functions.
"""
from dataclasses import dataclass, field
from typing import Optional, List
import ableton_arranger.config as config


@dataclass
class Section:
    """Represents a section in the arrangement."""
    name: str
    bars: int = 4
    tempo: Optional[float] = None
    timesig_num: int = 4
    timesig_denom: int = 4
    chords: List = field(default_factory=list)  # Will be List[Chord] when chord.py is imported
    lyrics: Optional[str] = None  # Optional lyrics text for this section
    
    def get_color(self) -> int:
        """Get the color for this section based on its name."""
        return config.get_section_color(self.name)
    
    @property
    def total_beats(self) -> float:
        """Calculate total beats in this section."""
        beats_per_bar = self.timesig_num * (4.0 / self.timesig_denom)
        return self.bars * beats_per_bar
    
    def length_seconds(self, default_tempo: float = 120.0) -> float:
        """
        Calculate the length of this section in seconds.
        
        Args:
            default_tempo: Tempo to use if section doesn't specify one
            
        Returns:
            Length in seconds
        """
        tempo = self.tempo if self.tempo and self.tempo > 0 else default_tempo
        
        # Calculate beats based on time signature
        # For x/4 signatures, beats per bar = x
        # For x/8 signatures, beats per bar = x/2 (in quarter notes)
        beats_per_bar = self.timesig_num * (4.0 / self.timesig_denom)
        beats = self.bars * beats_per_bar
        
        # Convert beats to seconds
        return (beats * 60.0) / tempo
    
    def to_dict(self) -> dict:
        """Convert section to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "bars": self.bars,
            "tempo": self.tempo,
            "timesig_num": self.timesig_num,
            "timesig_denom": self.timesig_denom,
            "chords": [chord.to_dict() if hasattr(chord, 'to_dict') else chord for chord in self.chords],
            "lyrics": self.lyrics
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create section from dictionary."""
        # Import here to avoid circular imports
        from ableton_arranger.core.chord import Chord
        
        chords_data = data.get("chords", [])
        chords = []
        for chord_data in chords_data:
            if isinstance(chord_data, dict):
                chords.append(Chord.from_dict(chord_data))
            else:
                chords.append(chord_data)
        
        section = cls(
            name=data.get("name", "Section"),
            bars=data.get("bars", 4),
            tempo=data.get("tempo"),
            timesig_num=data.get("timesig_num", 4),
            timesig_denom=data.get("timesig_denom", 4),
            chords=chords,
            lyrics=data.get("lyrics")
        )
        return section
