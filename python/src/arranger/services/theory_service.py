"""
Theory Service - provides music theory guidance and suggestions.

Wraps theory functions and provides a unified API for theory operations.
"""

from typing import List, Dict, Optional
from arranger.utils.music_theory import (
    get_common_progressions,
    get_cadence,
    get_borrowed_chords,
    get_substitutions,
    get_diatonic_degrees,
    get_modal_degrees,
    get_theory_guidance,
)
from arranger.models.chord import Chord, ChordQuality
from arranger.models.section import Section


class TheoryService:
    """Service for music theory operations and guidance."""
    
    def __init__(self):
        """Initialize theory service."""
        pass
    
    def get_diatonic_chords(self, key: str, mode: str = "major") -> List[Dict]:
        """
        Get diatonic chords for a key and mode.
        
        Args:
            key: Key name (e.g., "C", "D#", "Bb")
            mode: Mode name (e.g., "major", "minor", "dorian", "mixolydian")
            
        Returns:
            List of chord dictionaries with root, quality, and degree info
        """
        degrees = get_diatonic_degrees(mode)
        # Convert key name to root number
        root = self._key_name_to_root(key)
        
        # Map degrees to chord qualities
        degree_to_quality = {
            "I": ChordQuality.MAJOR,
            "ii": ChordQuality.MINOR,
            "iii": ChordQuality.MINOR,
            "IV": ChordQuality.MAJOR,
            "V": ChordQuality.MAJOR,
            "vi": ChordQuality.MINOR,
            "vii°": ChordQuality.DIMINISHED,
            "i": ChordQuality.MINOR,
            "ii°": ChordQuality.DIMINISHED,
            "bIII": ChordQuality.MAJOR,
            "iv": ChordQuality.MINOR,
            "v": ChordQuality.MINOR,
            "VI": ChordQuality.MAJOR,
            "VII": ChordQuality.MAJOR,
        }
        
        chords = []
        for i, degree in enumerate(degrees):
            # Calculate root note for this degree
            scale_notes = self._get_scale_notes(root, mode)
            if i < len(scale_notes):
                chord_root = scale_notes[i]
                quality = degree_to_quality.get(degree, ChordQuality.MAJOR)
                
                # Build chord name
                note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                root_name = note_names[chord_root]
                chord_name = f"{root_name}{quality.value}"
                
                chords.append({
                    "degree": degree,
                    "root": chord_root,
                    "quality": quality,
                    "name": chord_name,
                    "roman": degree
                })
        
        return chords
    
    def get_modal_chords(self, key: str, mode: str) -> List[Dict]:
        """
        Get modal chords for a key and mode.
        
        Args:
            key: Key name
            mode: Modal mode (dorian, mixolydian, etc.)
            
        Returns:
            List of chord dictionaries
        """
        degrees = get_modal_degrees(mode)
        root = self._key_name_to_root(key)
        
        # Similar to diatonic but with modal-specific qualities
        degree_to_quality = {
            "I": ChordQuality.MAJOR,
            "i": ChordQuality.MINOR,
            "ii": ChordQuality.MINOR,
            "bIII": ChordQuality.MAJOR,
            "IV": ChordQuality.MAJOR,
            "v": ChordQuality.MINOR,
            "vi°": ChordQuality.DIMINISHED,
            "bVII": ChordQuality.MAJOR,
        }
        
        chords = []
        scale_notes = self._get_scale_notes(root, mode)
        
        for i, degree in enumerate(degrees):
            if i < len(scale_notes):
                chord_root = scale_notes[i]
                quality = degree_to_quality.get(degree, ChordQuality.MINOR)
                
                note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                root_name = note_names[chord_root]
                chord_name = f"{root_name}{quality.value}"
                
                chords.append({
                    "degree": degree,
                    "root": chord_root,
                    "quality": quality,
                    "name": chord_name,
                    "roman": degree
                })
        
        return chords
    
    def get_progressions(self, key: str, mode: str = "major") -> List[List[str]]:
        """
        Get common progressions for key and mode.
        
        Args:
            key: Key name
            mode: Mode name
            
        Returns:
            List of progression lists (each progression is a list of roman numerals)
        """
        return get_common_progressions(key, mode)
    
    def get_cadences(self) -> Dict[str, List[str]]:
        """
        Get all cadence types.
        
        Returns:
            Dictionary mapping cadence names to chord sequences
        """
        return {
            "authentic": get_cadence("authentic"),
            "plagal": get_cadence("plagal"),
            "deceptive": get_cadence("deceptive"),
            "half": get_cadence("half"),
        }
    
    def get_borrowed_chords_for_key(self, key: str, mode: str = "major") -> List[Dict]:
        """
        Get borrowed chords (modal interchange) for key and mode.
        
        Args:
            key: Key name
            mode: Mode name
            
        Returns:
            List of borrowed chord dictionaries
        """
        borrowed = get_borrowed_chords(key, mode)
        root = self._key_name_to_root(key)
        
        result = []
        for bc in borrowed:
            # bc is a string like "bVII" or "iv"
            # Parse and create chord info
            result.append({
                "name": bc,
                "description": f"Borrowed from parallel {mode}",
                "chord": self._parse_roman_numeral(bc, root, mode)
            })
        
        return result
    
    def get_substitutions_for_chord(self, chord: Chord, sub_type: str = "tritone") -> List[Chord]:
        """
        Get chord substitutions for a given chord.
        
        Args:
            chord: Chord to find substitutions for
            sub_type: Type of substitution ("tritone", "diatonic", "chromatic")
            
        Returns:
            List of substitute chords
        """
        # Convert chord to string representation
        chord_str = chord.name
        
        subs = get_substitutions(chord_str, sub_type)
        
        # Convert substitution strings to Chord objects
        result = []
        for sub_str in subs:
            try:
                sub_chord = Chord.from_name(sub_str, beats=chord.beats)
                result.append(sub_chord)
            except:
                pass
        
        return result
    
    def analyze_section(self, section: Section, key: str, mode: str = "major") -> Dict:
        """
        Analyze a section and provide theory feedback.
        
        Args:
            section: Section to analyze
            key: Key of the arrangement
            mode: Mode of the arrangement
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "key": key,
            "mode": mode,
            "chords": [],
            "suggestions": [],
            "borrowed_chords": [],
            "cadences": []
        }
        
        # Analyze each chord
        for chord in section.chords:
            chord_info = {
                "chord": chord.name,
                "root": chord.root,
                "quality": chord.quality.value,
                "diatonic": self._is_diatonic(chord, key, mode),
                "borrowed": self._is_borrowed(chord, key, mode),
                "substitutions": [s.name for s in self.get_substitutions_for_chord(chord)]
            }
            analysis["chords"].append(chord_info)
            
            if not chord_info["diatonic"] and chord_info["borrowed"]:
                analysis["borrowed_chords"].append(chord.name)
        
        # Check for cadences
        chord_names = [c.name for c in section.chords]
        for cadence_name, cadence_chords in self.get_cadences().items():
            if self._matches_cadence(chord_names, cadence_chords):
                analysis["cadences"].append(cadence_name)
        
        return analysis
    
    def _key_name_to_root(self, key: str) -> int:
        """Convert key name to root note number (0-11)."""
        note_map = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }
        # Remove 'm' suffix if present
        key_clean = key.rstrip('m').rstrip('M')
        return note_map.get(key_clean, 0)
    
    def _get_scale_notes(self, root: int, mode: str) -> List[int]:
        """Get scale notes for a root and mode."""
        intervals_map = {
            "major": [0, 2, 4, 5, 7, 9, 11],
            "ionian": [0, 2, 4, 5, 7, 9, 11],
            "minor": [0, 2, 3, 5, 7, 8, 10],
            "aeolian": [0, 2, 3, 5, 7, 8, 10],
            "dorian": [0, 2, 3, 5, 7, 9, 10],
            "mixolydian": [0, 2, 4, 5, 7, 9, 10],
            "phrygian": [0, 1, 3, 5, 7, 8, 10],
            "lydian": [0, 2, 4, 6, 7, 9, 11],
            "locrian": [0, 1, 3, 5, 6, 8, 10],
        }
        
        intervals = intervals_map.get(mode.lower(), intervals_map["major"])
        return [(root + interval) % 12 for interval in intervals]
    
    def _is_diatonic(self, chord: Chord, key: str, mode: str) -> bool:
        """Check if chord is diatonic to the key/mode."""
        diatonic_chords = self.get_diatonic_chords(key, mode)
        for dc in diatonic_chords:
            if dc["root"] == chord.root and dc["quality"] == chord.quality:
                return True
        return False
    
    def _is_borrowed(self, chord: Chord, key: str, mode: str) -> bool:
        """Check if chord is a borrowed chord."""
        borrowed = get_borrowed_chords(key, mode)
        # Simplified check - would need more sophisticated analysis
        return False
    
    def _matches_cadence(self, chord_names: List[str], cadence_chords: List[str]) -> bool:
        """Check if chord sequence matches a cadence pattern."""
        if len(chord_names) < len(cadence_chords):
            return False
        
        # Check if cadence appears at the end
        end_chords = chord_names[-len(cadence_chords):]
        # Simplified matching - would need roman numeral analysis
        return False
    
    def _parse_roman_numeral(self, roman: str, root: int, mode: str) -> Optional[Dict]:
        """Parse a roman numeral and return chord info."""
        # Simplified - would need full roman numeral parser
        return None
