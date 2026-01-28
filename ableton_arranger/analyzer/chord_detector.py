"""
Chord progression detection from audio.
Uses various algorithms and API services.
"""
import os
import logging
from typing import List, Dict, Any
from pathlib import Path

from ableton_arranger.shared.data_models import ChordData, AnalysisConfig


logger = logging.getLogger(__name__)


class ChordDetector:
    """
    Detects chord progressions from audio.
    Designed for M4L compatibility with simple API.
    """
    
    def __init__(self, config: AnalysisConfig):
        """
        Initialize chord detector.
        
        Args:
            config: Analysis configuration
        """
        self.config = config
        self.api_costs: Dict[str, float] = {}
    
    def detect_chords(self, audio_path: str) -> List[ChordData]:
        """
        Detect chord progressions from audio.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            List of detected chords with timing
        """
        try:
            # Try librosa-based detection first (free, local)
            return self._detect_with_librosa(audio_path)
            
        except Exception as e:
            logger.error(f"Chord detection failed: {e}")
            return []
    
    def _detect_with_librosa(self, audio_path: str) -> List[ChordData]:
        """
        Use librosa for chord detection.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            List of detected chords
        """
        try:
            import librosa
            import numpy as np
        except ImportError:
            raise ImportError("librosa required for chord detection. Install with: pip install librosa")
        
        # Load audio
        y, sr = librosa.load(audio_path)
        
        # Extract chroma features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        
        # Detect chord changes using chroma
        # This is a simplified implementation
        chords = []
        hop_length = 512
        frame_time = hop_length / sr
        
        # Analyze chroma in windows
        window_size = 2048  # frames
        for i in range(0, chroma.shape[1] - window_size, window_size // 2):
            window_chroma = chroma[:, i:i+window_size]
            avg_chroma = np.mean(window_chroma, axis=1)
            
            # Find root note (highest chroma value)
            root_idx = np.argmax(avg_chroma)
            root_name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"][root_idx]
            
            # Determine chord quality (simplified)
            # Check for major/minor based on intervals
            quality = "maj"  # Default to major
            
            # Simple heuristic: check 3rd and 5th intervals
            third = avg_chroma[(root_idx + 4) % 12]
            minor_third = avg_chroma[(root_idx + 3) % 12]
            
            if minor_third > third * 0.8:
                quality = "min"
            
            # Calculate timing
            start_time = i * frame_time
            end_time = (i + window_size) * frame_time
            
            chord = ChordData(
                root=root_name,
                quality=quality,
                start_time=start_time,
                end_time=end_time,
                confidence=0.7  # Moderate confidence for librosa detection
            )
            
            chords.append(chord)
        
        logger.info(f"Detected {len(chords)} chords using librosa")
        return chords
    
    def get_api_costs(self) -> Dict[str, float]:
        """Get accumulated API costs."""
        return self.api_costs.copy()
