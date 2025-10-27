"""
Section model - represents a musical section with metadata
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum


class SectionType(str, Enum):
    """Standard song section types."""
    INTRO = "intro"
    VERSE = "verse"
    CHORUS = "chorus"
    BRIDGE = "bridge"
    BREAKDOWN = "breakdown"
    DROP = "drop"
    OUTRO = "outro"
    CUSTOM = "custom"


class Section(BaseModel):
    """
    Represents a musical section with metadata.
    
    A section is a distinct part of a song (verse, chorus, etc.)
    with specific length, chords, and visual properties.
    """
    label: str = Field(
        ..., 
        min_length=1, 
        max_length=8,
        description="Short identifier (A, B, C, V1, CH, etc.)"
    )
    type: SectionType = Field(
        ...,
        description="Section type (verse, chorus, etc.)"
    )
    bars: int = Field(
        ..., 
        gt=0, 
        le=64,
        description="Length in bars"
    )
    color: Optional[str] = Field(
        None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Hex color code"
    )
    tempo_override: Optional[float] = Field(
        None,
        ge=20.0,
        le=999.0,
        description="Override tempo for this section"
    )
    time_signature: tuple = Field(
        (4, 4),
        description="Time signature (numerator, denominator)"
    )
    chords: List["Chord"] = Field(
        default_factory=list,
        description="Chord progression for this section"
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    @validator("time_signature")
    def validate_time_signature(cls, v):
        """Validate time signature format."""
        if not isinstance(v, (tuple, list)) or len(v) != 2:
            raise ValueError("Time signature must be (numerator, denominator)")
        num, denom = v
        if num <= 0 or denom not in [2, 4, 8, 16]:
            raise ValueError("Invalid time signature values")
        return tuple(v)
    
    @validator("chords")
    def validate_chord_timing(cls, chords, values):
        """Ensure chord beats sum matches section bars."""
        if not chords:
            return chords
        
        # Import here to avoid circular dependency
        from .chord import Chord
        
        total_beats = sum(c.beats for c in chords)
        time_sig = values.get("time_signature", (4, 4))
        expected_beats = values["bars"] * time_sig[0]
        
        if total_beats != expected_beats:
            raise ValueError(
                f"Chord beats ({total_beats}) must equal "
                f"section beats ({expected_beats})"
            )
        return chords
    
    class Config:
        use_enum_values = True
        json_encoders = {
            SectionType: lambda v: v.value
        }


# Allow forward references
from .chord import Chord
Section.update_forward_refs()
