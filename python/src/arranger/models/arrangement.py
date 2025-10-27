"""
Arrangement model - represents complete song arrangement
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from .section import Section


class OrderItem(BaseModel):
    """
    Item in the arrangement order sequence.
    
    References a section by label and specifies how it should be played.
    """
    section_label: str = Field(
        ...,
        description="Label of the section to play"
    )
    bars: Optional[int] = Field(
        None,
        gt=0,
        description="Override section default length"
    )
    repeat: int = Field(
        1,
        ge=1,
        le=16,
        description="Number of times to repeat"
    )
    transpose: int = Field(
        0,
        ge=-12,
        le=12,
        description="Transpose semitones"
    )


class Arrangement(BaseModel):
    """
    Complete song arrangement with sections and playback order.
    
    Manages the structure of a song including all sections,
    their order, and global properties like tempo and key.
    """
    title: str = Field(
        "Untitled",
        min_length=1,
        max_length=100,
        description="Arrangement title"
    )
    bpm: float = Field(
        120.0,
        ge=20.0,
        le=999.0,
        description="Tempo in beats per minute"
    )
    key: str = Field(
        "C",
        description="Musical key"
    )
    time_signature: tuple = Field(
        (4, 4),
        description="Global time signature"
    )
    sections: List[Section] = Field(
        default_factory=list,
        description="List of sections"
    )
    order: List[OrderItem] = Field(
        default_factory=list,
        description="Playback order"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Creation timestamp"
    )
    modified_at: datetime = Field(
        default_factory=datetime.now,
        description="Last modification timestamp"
    )
    version: int = Field(
        1,
        ge=1,
        description="Version number"
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    @validator("key")
    def validate_key(cls, v):
        """Validate musical key."""
        valid_keys = [
            'C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F',
            'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B',
            'Cm', 'C#m', 'Dm', 'D#m', 'Ebm', 'Em', 'Fm',
            'F#m', 'Gm', 'G#m', 'Am', 'A#m', 'Bbm', 'Bm'
        ]
        if v not in valid_keys:
            raise ValueError(f"Invalid key: {v}")
        return v
    
    @property
    def total_bars(self) -> int:
        """Calculate total arrangement length in bars."""
        total = 0
        for item in self.order:
            section = self._get_section(item.section_label)
            if section:
                bars = item.bars if item.bars else section.bars
                total += bars * item.repeat
        return total
    
    @property
    def section_count(self) -> int:
        """Get number of sections."""
        return len(self.sections)
    
    def _get_section(self, label: str) -> Optional[Section]:
        """Find section by label."""
        for section in self.sections:
            if section.label == label:
                return section
        return None
    
    def validate_order(self) -> List[str]:
        """
        Validate that order references existing sections.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        for idx, item in enumerate(self.order):
            if not self._get_section(item.section_label):
                errors.append(
                    f"Order item {idx}: Section '{item.section_label}' not found"
                )
        return errors
    
    def add_section(self, section: Section) -> None:
        """Add a new section."""
        # Check for duplicate labels
        if self._get_section(section.label):
            raise ValueError(f"Section with label '{section.label}' already exists")
        self.sections.append(section)
        self.modified_at = datetime.now()
    
    def remove_section(self, label: str) -> bool:
        """
        Remove section by label.
        
        Returns:
            True if section was removed, False if not found
        """
        for idx, section in enumerate(self.sections):
            if section.label == label:
                self.sections.pop(idx)
                # Remove from order as well
                self.order = [
                    item for item in self.order 
                    if item.section_label != label
                ]
                self.modified_at = datetime.now()
                return True
        return False
    
    def update_section(self, label: str, updated_section: Section) -> bool:
        """
        Update existing section.
        
        Returns:
            True if updated, False if not found
        """
        for idx, section in enumerate(self.sections):
            if section.label == label:
                self.sections[idx] = updated_section
                self.modified_at = datetime.now()
                return True
        return False
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
