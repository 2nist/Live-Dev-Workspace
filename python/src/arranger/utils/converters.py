"""
Model converters for backward compatibility and migration.

Provides conversion functions between old dataclass-based models
and new Pydantic-based models.
"""

from typing import List, Optional
from arranger.models.chord import Chord as PydanticChord, ChordQuality
from arranger.models.section import Section as PydanticSection, SectionType
from arranger.models.arrangement import Arrangement as PydanticArrangement, OrderItem


# Legacy models (from ableton_arranger/core/)
# These are the old dataclass-based models that need conversion
try:
    from ableton_arranger.core.chord import Chord as LegacyChord
    from ableton_arranger.core.section import Section as LegacySection
    LEGACY_AVAILABLE = True
except ImportError:
    LEGACY_AVAILABLE = False
    LegacyChord = None
    LegacySection = None


def legacy_chord_to_pydantic(legacy_chord) -> PydanticChord:
    """
    Convert legacy dataclass Chord to Pydantic Chord.
    
    Args:
        legacy_chord: Legacy Chord instance from ableton_arranger.core.chord
        
    Returns:
        PydanticChord instance
    """
    if not LEGACY_AVAILABLE:
        raise ImportError("Legacy models not available")
    
    # Map legacy type_idx to ChordQuality
    # This is a simplified mapping - may need adjustment based on actual CHORD_TYPES
    type_to_quality = {
        1: ChordQuality.MAJOR,  # maj
        2: ChordQuality.MINOR,   # min
        3: ChordQuality.DIMINISHED,  # dim
        9: ChordQuality.DOMINANT,  # 7
        6: ChordQuality.MINOR7,  # m7
        8: ChordQuality.MAJOR7,  # maj7
    }
    
    quality = type_to_quality.get(legacy_chord.type_idx, ChordQuality.MAJOR)
    
    # Build chord name from root and quality
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    root_name = note_names[legacy_chord.root]
    chord_name = f"{root_name}{quality.value}"
    
    # Calculate beats from duration_beats
    beats = int(legacy_chord.duration_beats) if legacy_chord.duration_beats >= 1 else 4
    
    return PydanticChord(
        name=chord_name,
        root=legacy_chord.root,
        quality=quality,
        beats=beats,
        inversion=legacy_chord.inversion,
        extensions=[]  # Legacy doesn't have extensions
    )


def pydantic_chord_to_legacy(pydantic_chord: PydanticChord) -> Optional[object]:
    """
    Convert Pydantic Chord to legacy dataclass Chord.
    
    Args:
        pydantic_chord: PydanticChord instance
        
    Returns:
        Legacy Chord instance or None if legacy models unavailable
    """
    if not LEGACY_AVAILABLE:
        return None
    
    # Map ChordQuality to type_idx
    quality_to_type = {
        ChordQuality.MAJOR: 1,
        ChordQuality.MINOR: 2,
        ChordQuality.DIMINISHED: 3,
        ChordQuality.DOMINANT: 9,
        ChordQuality.MINOR7: 6,
        ChordQuality.MAJOR7: 8,
    }
    
    type_idx = quality_to_type.get(pydantic_chord.quality, 1)
    
    return LegacyChord(
        root=pydantic_chord.root,
        type_idx=type_idx,
        start_beat=0.0,  # Default, would need to track this separately
        duration_beats=float(pydantic_chord.beats),
        inversion=pydantic_chord.inversion,
        bass_note=None,
        octave=4
    )


def legacy_section_to_pydantic(legacy_section) -> PydanticSection:
    """
    Convert legacy dataclass Section to Pydantic Section.
    
    Args:
        legacy_section: Legacy Section instance from ableton_arranger.core.section
        
    Returns:
        PydanticSection instance
    """
    if not LEGACY_AVAILABLE:
        raise ImportError("Legacy models not available")
    
    # Map section name to SectionType
    name_lower = legacy_section.name.lower()
    section_type_map = {
        'intro': SectionType.INTRO,
        'verse': SectionType.VERSE,
        'chorus': SectionType.CHORUS,
        'bridge': SectionType.BRIDGE,
        'breakdown': SectionType.BREAKDOWN,
        'drop': SectionType.DROP,
        'outro': SectionType.OUTRO,
    }
    
    section_type = section_type_map.get(name_lower, SectionType.CUSTOM)
    
    # Convert legacy chords to Pydantic chords
    chords = []
    if legacy_section.chords:
        for chord in legacy_section.chords:
            if isinstance(chord, LegacyChord):
                chords.append(legacy_chord_to_pydantic(chord))
            elif isinstance(chord, dict):
                # Try to convert from dict
                try:
                    chords.append(PydanticChord(**chord))
                except:
                    pass
    
    return PydanticSection(
        label=legacy_section.name[:8],  # Truncate to max 8 chars
        type=section_type,
        bars=legacy_section.bars,
        tempo_override=legacy_section.tempo,
        time_signature=(legacy_section.timesig_num, legacy_section.timesig_denom),
        chords=chords,
        metadata={}  # Legacy doesn't have metadata
    )


def pydantic_section_to_legacy(pydantic_section: PydanticSection) -> Optional[object]:
    """
    Convert Pydantic Section to legacy dataclass Section.
    
    Args:
        pydantic_section: PydanticSection instance
        
    Returns:
        Legacy Section instance or None if legacy models unavailable
    """
    if not LEGACY_AVAILABLE:
        return None
    
    # Convert chords
    legacy_chords = []
    for chord in pydantic_section.chords:
        legacy_chord = pydantic_chord_to_legacy(chord)
        if legacy_chord:
            legacy_chords.append(legacy_chord)
    
    return LegacySection(
        name=pydantic_section.label,
        bars=pydantic_section.bars,
        tempo=pydantic_section.tempo_override,
        timesig_num=pydantic_section.time_signature[0],
        timesig_denom=pydantic_section.time_signature[1],
        chords=legacy_chords,
        lyrics=None
    )


def convert_sections_list(legacy_sections: List) -> List[PydanticSection]:
    """
    Convert a list of legacy sections to Pydantic sections.
    
    Args:
        legacy_sections: List of legacy Section instances
        
    Returns:
        List of PydanticSection instances
    """
    return [legacy_section_to_pydantic(s) for s in legacy_sections if LEGACY_AVAILABLE]


def convert_chords_list(legacy_chords: List) -> List[PydanticChord]:
    """
    Convert a list of legacy chords to Pydantic chords.
    
    Args:
        legacy_chords: List of legacy Chord instances
        
    Returns:
        List of PydanticChord instances
    """
    return [legacy_chord_to_pydantic(c) for c in legacy_chords if LEGACY_AVAILABLE]
