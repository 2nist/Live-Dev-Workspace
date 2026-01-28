"""
Data persistence for sections and chords.
Saves/loads to JSON format.
"""
import json
import os
from typing import List
from ableton_arranger.core.section import Section
from ableton_arranger.core.chord import Chord


def ensure_data_dir(data_path: str):
    """Ensure the data directory exists."""
    dir_path = os.path.dirname(data_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)


def save_sections(sections: List[Section], path: str):
    """
    Save sections to JSON file.
    
    Args:
        sections: List of Section objects
        path: Path to JSON file
    """
    ensure_data_dir(path)
    
    sections_data = []
    for section in sections:
        section_dict = section.to_dict()
        # Convert chords to dicts if they're Chord objects
        if section.chords:
            chords_data = []
            for chord in section.chords:
                if isinstance(chord, Chord):
                    chords_data.append(chord.to_dict())
                elif isinstance(chord, dict):
                    chords_data.append(chord)
            section_dict["chords"] = chords_data
        sections_data.append(section_dict)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(sections_data, f, indent=2, ensure_ascii=False)


def load_sections(path: str) -> List[Section]:
    """
    Load sections from JSON file.
    
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
            # Convert chord dicts to Chord objects
            if "chords" in data and data["chords"]:
                chords = []
                for chord_data in data["chords"]:
                    if isinstance(chord_data, dict):
                        chords.append(Chord.from_dict(chord_data))
                    else:
                        chords.append(chord_data)
                data["chords"] = chords
            
            section = Section.from_dict(data)
            sections.append(section)
        
        return sections
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error loading sections from {path}: {e}")
        return []
