"""
Utility functions for Live development integration
"""

import logging
import sys
from typing import Optional
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
        return super().format(record)


def configure_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    colored: bool = True
) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (e.g., logging.INFO, logging.DEBUG)
        log_file: Optional file path to write logs to
        colored: Whether to use colored console output
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("live_dev")
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if colored:
        formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


# Default logger instance
logger = configure_logging()


def format_time(beats: float) -> str:
    """
    Format beat time as bars:beats:ticks.
    
    Args:
        beats: Time in beats
        
    Returns:
        Formatted string (e.g., "1:1:0")
    """
    bars = int(beats // 4)
    remaining_beats = int(beats % 4)
    ticks = int((beats % 1) * 960)  # 960 ticks per beat
    return f"{bars + 1}:{remaining_beats + 1}:{ticks}"


def beats_to_ms(beats: float, tempo: float) -> float:
    """
    Convert beats to milliseconds at a given tempo.
    
    Args:
        beats: Number of beats
        tempo: Tempo in BPM
        
    Returns:
        Time in milliseconds
    """
    return (beats / tempo) * 60000


def ms_to_beats(milliseconds: float, tempo: float) -> float:
    """
    Convert milliseconds to beats at a given tempo.
    
    Args:
        milliseconds: Time in milliseconds
        tempo: Tempo in BPM
        
    Returns:
        Time in beats
    """
    return (milliseconds * tempo) / 60000


def midi_note_to_name(note: int) -> str:
    """
    Convert MIDI note number to note name.
    
    Args:
        note: MIDI note number (0-127)
        
    Returns:
        Note name (e.g., "C4", "A#5")
    """
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (note // 12) - 1
    note_name = notes[note % 12]
    return f"{note_name}{octave}"


def note_name_to_midi(name: str) -> int:
    """
    Convert note name to MIDI note number.
    
    Args:
        name: Note name (e.g., "C4", "A#5")
        
    Returns:
        MIDI note number (0-127)
    """
    notes = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
             'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    
    # Handle flats
    name = name.replace('Db', 'C#').replace('Eb', 'D#').replace('Gb', 'F#')
    name = name.replace('Ab', 'G#').replace('Bb', 'A#')
    
    # Extract note and octave
    note = name[:-1]
    octave = int(name[-1])
    
    return notes[note] + (octave + 1) * 12


def create_scale(root: int, scale_type: str = "major") -> list:
    """
    Create a musical scale.
    
    Args:
        root: Root MIDI note number
        scale_type: Type of scale (major, minor, dorian, etc.)
        
    Returns:
        List of MIDI note numbers in the scale
    """
    scales = {
        "major": [0, 2, 4, 5, 7, 9, 11],
        "minor": [0, 2, 3, 5, 7, 8, 10],
        "dorian": [0, 2, 3, 5, 7, 9, 10],
        "phrygian": [0, 1, 3, 5, 7, 8, 10],
        "lydian": [0, 2, 4, 6, 7, 9, 11],
        "mixolydian": [0, 2, 4, 5, 7, 9, 10],
        "aeolian": [0, 2, 3, 5, 7, 8, 10],
        "locrian": [0, 1, 3, 5, 6, 8, 10],
        "pentatonic_major": [0, 2, 4, 7, 9],
        "pentatonic_minor": [0, 3, 5, 7, 10],
    }
    
    if scale_type not in scales:
        raise ValueError(f"Unknown scale type: {scale_type}")
    
    intervals = scales[scale_type]
    return [root + interval for interval in intervals]


def quantize_to_grid(time: float, grid: float = 0.25) -> float:
    """
    Quantize a time value to a grid.
    
    Args:
        time: Time in beats
        grid: Grid resolution in beats (e.g., 0.25 for 16th notes)
        
    Returns:
        Quantized time
    """
    return round(time / grid) * grid
