"""
Unified persistence layer for arrangements using Pydantic models.

Supports saving/loading arrangements, sections, and chords to JSON.
"""

import json
import os
from typing import List, Optional
from pathlib import Path
from arranger.models.arrangement import Arrangement
from arranger.models.section import Section
from arranger.models.chord import Chord


def ensure_data_dir(data_path: str):
    """Ensure the data directory exists."""
    dir_path = os.path.dirname(data_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)


def save_arrangement(arrangement: Arrangement, path: str):
    """
    Save arrangement to JSON file.
    
    Args:
        arrangement: Arrangement instance
        path: Path to JSON file
    """
    ensure_data_dir(path)
    
    # Use Pydantic's JSON serialization
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(arrangement.dict(), f, indent=2, ensure_ascii=False)


def load_arrangement(path: str) -> Optional[Arrangement]:
    """
    Load arrangement from JSON file.
    
    Args:
        path: Path to JSON file
        
    Returns:
        Arrangement instance or None if file doesn't exist or is invalid
    """
    if not os.path.exists(path):
        return None
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return Arrangement(**data)
    except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
        print(f"Error loading arrangement from {path}: {e}")
        return None


def save_sections(sections: List[Section], path: str):
    """
    Save sections to JSON file (legacy format support).
    
    Args:
        sections: List of Section objects
        path: Path to JSON file
    """
    ensure_data_dir(path)
    
    sections_data = [section.dict() for section in sections]
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(sections_data, f, indent=2, ensure_ascii=False)


def load_sections(path: str) -> List[Section]:
    """
    Load sections from JSON file (legacy format support).
    
    Args:
        path: Path to JSON file
        
    Returns:
        List of Section objects
    """
    if not os.path.exists(path):
        return []
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            sections_data = json.load(f)
        
        sections = []
        for data in sections_data:
            # Handle legacy format conversion if needed
            # Legacy uses 'name' instead of 'label'
            if 'name' in data and 'label' not in data:
                data['label'] = data.pop('name')
            
            # Legacy uses different chord format
            if 'chords' in data:
                chords = []
                for chord_data in data['chords']:
                    if isinstance(chord_data, dict):
                        # Try to convert legacy chord format
                        if 'root' in chord_data and 'type_idx' in chord_data:
                            # Legacy format - convert to Pydantic
                            from arranger.utils.converters import legacy_chord_to_pydantic
                            try:
                                # Create a minimal legacy chord object for conversion
                                class LegacyChord:
                                    def __init__(self, **kwargs):
                                        for k, v in kwargs.items():
                                            setattr(self, k, v)
                                
                                legacy = LegacyChord(**chord_data)
                                chords.append(legacy_chord_to_pydantic(legacy))
                            except:
                                # Fallback: try to create Pydantic chord directly
                                try:
                                    # Map legacy fields to Pydantic
                                    if 'name' not in chord_data:
                                        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                                        root_name = note_names[chord_data.get('root', 0)]
                                        # Map type_idx to quality (simplified)
                                        type_to_quality = {
                                            1: 'maj', 2: 'min', 3: 'dim', 9: '7', 6: 'min7', 8: 'maj7'
                                        }
                                        quality = type_to_quality.get(chord_data.get('type_idx', 1), 'maj')
                                        chord_data['name'] = f"{root_name}{quality}"
                                        chord_data['quality'] = quality
                                        chord_data['beats'] = int(chord_data.get('duration_beats', 4))
                                    chords.append(Chord(**chord_data))
                                except:
                                    pass
                        else:
                            # Already in Pydantic format
                            try:
                                chords.append(Chord(**chord_data))
                            except:
                                pass
                data['chords'] = chords
            
            try:
                sections.append(Section(**data))
            except Exception as e:
                print(f"Warning: Could not load section: {e}")
                continue
        
        return sections
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error loading sections from {path}: {e}")
        return []
