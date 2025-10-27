"""Unit tests for data models."""

import pytest
from arranger.models import Section, SectionType, Chord, ChordQuality, Arrangement, OrderItem
from pydantic import ValidationError


class TestSectionModel:
    """Test Section model validation and functionality."""
    
    def test_valid_section_creation(self):
        """Test creating a valid section."""
        section = Section(
            label="V1",
            type=SectionType.VERSE,
            bars=8,
            color="#FF5733"
        )
        
        assert section.label == "V1"
        assert section.type == SectionType.VERSE
        assert section.bars == 8
        assert section.color == "#FF5733"
        assert section.time_signature == (4, 4)
    
    def test_label_validation(self):
        """Test label length validation."""
        # Too long
        with pytest.raises(ValidationError):
            Section(label="VERYLONGLABEL", type=SectionType.VERSE, bars=8)
        
        # Empty
        with pytest.raises(ValidationError):
            Section(label="", type=SectionType.VERSE, bars=8)
    
    def test_bars_validation(self):
        """Test bars validation."""
        # Zero bars
        with pytest.raises(ValidationError):
            Section(label="A", type=SectionType.VERSE, bars=0)
        
        # Too many bars
        with pytest.raises(ValidationError):
            Section(label="A", type=SectionType.VERSE, bars=128)
        
        # Valid range
        section = Section(label="A", type=SectionType.VERSE, bars=16)
        assert section.bars == 16
    
    def test_color_validation(self):
        """Test color hex validation."""
        # Valid colors
        section = Section(label="A", type=SectionType.VERSE, bars=8, color="#FF00FF")
        assert section.color == "#FF00FF"
        
        # Invalid format
        with pytest.raises(ValidationError):
            Section(label="A", type=SectionType.VERSE, bars=8, color="red")
        
        with pytest.raises(ValidationError):
            Section(label="A", type=SectionType.VERSE, bars=8, color="#GG0000")
    
    def test_time_signature_validation(self):
        """Test time signature validation."""
        # Valid signatures
        section = Section(
            label="A",
            type=SectionType.VERSE,
            bars=8,
            time_signature=(3, 4)
        )
        assert section.time_signature == (3, 4)
        
        # Invalid denominator
        with pytest.raises(ValidationError):
            Section(
                label="A",
                type=SectionType.VERSE,
                bars=8,
                time_signature=(4, 3)
            )
    
    def test_chord_timing_validation(self):
        """Test chord progression timing validation."""
        # Correct timing (8 bars * 4 beats = 32 beats)
        chords = [
            Chord.from_name("Cmaj7", beats=8),
            Chord.from_name("Dm7", beats=8),
            Chord.from_name("G7", beats=8),
            Chord.from_name("Cmaj7", beats=8)
        ]
        
        section = Section(
            label="CH",
            type=SectionType.CHORUS,
            bars=8,
            chords=chords
        )
        assert len(section.chords) == 4
        
        # Incorrect timing (too many beats)
        with pytest.raises(ValidationError):
            Section(
                label="CH",
                type=SectionType.CHORUS,
                bars=4,
                chords=chords  # 32 beats but only 4 bars (16 beats)
            )


class TestChordModel:
    """Test Chord model and parsing."""
    
    def test_chord_from_name_parsing(self):
        """Test parsing various chord names."""
        # Major
        chord = Chord.from_name("C", beats=4)
        assert chord.root == 0
        assert chord.quality == ChordQuality.MAJOR
        
        # Minor
        chord = Chord.from_name("Dm", beats=4)
        assert chord.root == 2
        assert chord.quality == ChordQuality.MINOR
        
        # Dominant 7th
        chord = Chord.from_name("G7", beats=4)
        assert chord.root == 7
        assert chord.quality == ChordQuality.DOMINANT
        
        # Major 7th
        chord = Chord.from_name("Fmaj7", beats=4)
        assert chord.root == 5
        assert chord.quality == ChordQuality.MAJOR7
    
    def test_chord_sharps_flats(self):
        """Test sharp and flat parsing."""
        # Sharp
        chord = Chord.from_name("F#m7", beats=4)
        assert chord.root == 6
        assert chord.quality == ChordQuality.MINOR7
        
        # Flat
        chord = Chord.from_name("Bb7", beats=4)
        assert chord.root == 10
        assert chord.quality == ChordQuality.DOMINANT
    
    def test_to_midi_notes(self):
        """Test MIDI note generation."""
        # C major triad
        chord = Chord.from_name("C", beats=4)
        notes = chord.to_midi_notes(octave=4)
        assert notes == [48, 52, 55]  # C4, E4, G4
        
        # Dm7 chord
        chord = Chord.from_name("Dm7", beats=4)
        notes = chord.to_midi_notes(octave=4)
        assert notes == [50, 53, 57, 60]  # D4, F4, A4, C5
    
    def test_chord_inversions(self):
        """Test chord inversions."""
        chord = Chord.from_name("C", beats=4)
        
        # Root position
        chord.inversion = 0
        notes = chord.to_midi_notes(octave=4)
        assert notes[0] == 48  # C4
        
        # First inversion
        chord.inversion = 1
        notes = chord.to_midi_notes(octave=4)
        assert notes == [52, 55, 60]  # E4, G4, C5
    
    def test_extensions_validation(self):
        """Test chord extension validation."""
        # Valid extensions
        chord = Chord.from_name("Cmaj7", beats=4)
        chord.extensions = [9, 13]
        assert chord.extensions == [9, 13]
        
        # Invalid extension
        with pytest.raises(ValidationError):
            Chord(
                name="C",
                root=0,
                quality=ChordQuality.MAJOR,
                beats=4,
                extensions=[7]  # Invalid
            )


class TestArrangementModel:
    """Test Arrangement model."""
    
    def test_arrangement_creation(self):
        """Test creating arrangement."""
        arr = Arrangement(
            title="Test Song",
            bpm=128.0,
            key="Am"
        )
        
        assert arr.title == "Test Song"
        assert arr.bpm == 128.0
        assert arr.key == "Am"
        assert arr.version == 1
    
    def test_key_validation(self):
        """Test musical key validation."""
        # Valid keys
        arr = Arrangement(key="C#m")
        assert arr.key == "C#m"
        
        # Invalid key
        with pytest.raises(ValidationError):
            Arrangement(key="H")
    
    def test_add_section(self):
        """Test adding sections."""
        arr = Arrangement()
        
        section = Section(label="V1", type=SectionType.VERSE, bars=8)
        arr.add_section(section)
        
        assert arr.section_count == 1
        assert arr.sections[0].label == "V1"
    
    def test_duplicate_section_label(self):
        """Test duplicate label prevention."""
        arr = Arrangement()
        
        section1 = Section(label="V1", type=SectionType.VERSE, bars=8)
        arr.add_section(section1)
        
        # Try to add duplicate
        section2 = Section(label="V1", type=SectionType.CHORUS, bars=8)
        with pytest.raises(ValueError):
            arr.add_section(section2)
    
    def test_remove_section(self):
        """Test section removal."""
        arr = Arrangement()
        
        section = Section(label="V1", type=SectionType.VERSE, bars=8)
        arr.add_section(section)
        
        # Remove section
        removed = arr.remove_section("V1")
        assert removed is True
        assert arr.section_count == 0
        
        # Try to remove non-existent
        removed = arr.remove_section("XYZ")
        assert removed is False
    
    def test_order_items(self):
        """Test arrangement order."""
        arr = Arrangement()
        
        # Add sections
        arr.add_section(Section(label="V1", type=SectionType.VERSE, bars=8))
        arr.add_section(Section(label="CH", type=SectionType.CHORUS, bars=8))
        
        # Create order
        arr.order = [
            OrderItem(section_label="V1", repeat=2),
            OrderItem(section_label="CH", repeat=1)
        ]
        
        assert len(arr.order) == 2
        assert arr.order[0].section_label == "V1"
        assert arr.order[0].repeat == 2
    
    def test_total_bars_calculation(self):
        """Test total bars calculation."""
        arr = Arrangement()
        
        arr.add_section(Section(label="V1", type=SectionType.VERSE, bars=8))
        arr.add_section(Section(label="CH", type=SectionType.CHORUS, bars=4))
        
        arr.order = [
            OrderItem(section_label="V1", repeat=2),  # 8 * 2 = 16
            OrderItem(section_label="CH", repeat=1),  # 4 * 1 = 4
        ]
        
        assert arr.total_bars == 20
    
    def test_validate_order(self):
        """Test order validation."""
        arr = Arrangement()
        arr.add_section(Section(label="V1", type=SectionType.VERSE, bars=8))
        
        # Valid order
        arr.order = [OrderItem(section_label="V1")]
        errors = arr.validate_order()
        assert len(errors) == 0
        
        # Invalid order (non-existent section)
        arr.order.append(OrderItem(section_label="INVALID"))
        errors = arr.validate_order()
        assert len(errors) == 1
        assert "INVALID" in errors[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
