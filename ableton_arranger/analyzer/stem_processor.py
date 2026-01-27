"""
Stem separation processor.
Uses Ableton Live 12.3 native stem separation or fallback to external services.
"""
import os
import logging
import subprocess
from typing import Dict, Optional
from pathlib import Path

from ableton_arranger.shared.data_models import StemData, AnalysisConfig
from ableton_arranger.core.connection import LiveConnection


logger = logging.getLogger(__name__)


class StemProcessor:
    """
    Separates audio into stems (vocals, drums, bass, other).
    Designed for Ableton Live 12.3 native integration.
    """
    
    def __init__(self, config: AnalysisConfig):
        """
        Initialize stem processor.
        
        Args:
            config: Analysis configuration
        """
        self.config = config
        self.connection: Optional[LiveConnection] = None
    
    def separate_stems(self, audio_path: str) -> StemData:
        """
        Separate audio file into stems.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            StemData with paths to separated stems
        """
        try:
            # Try Ableton Live 12.3 native stem separation first
            if self._try_ableton_native_separation(audio_path):
                return self._get_ableton_stems(audio_path)
            
            # Fallback to external services
            logger.warning("Ableton native separation not available, using fallback")
            return self._separate_with_fallback(audio_path)
            
        except Exception as e:
            logger.error(f"Stem separation failed: {e}")
            return StemData()  # Return empty stems
    
    def _try_ableton_native_separation(self, audio_path: str) -> bool:
        """
        Try to use Ableton Live 12.3 native stem separation.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            True if Ableton separation is available
        """
        try:
            # Check if Live connection is available
            if not self.connection:
                self.connection = LiveConnection()
            
            if not self.connection.is_connected():
                return False
            
            # Ableton Live 12.3 has native stem separation via Audio-to-MIDI
            # This would use OSC commands to trigger Live's stem separation
            # For now, return False as placeholder
            logger.info("Ableton native stem separation not yet implemented")
            return False
            
        except Exception as e:
            logger.warning(f"Ableton native separation check failed: {e}")
            return False
    
    def _get_ableton_stems(self, audio_path: str) -> StemData:
        """Get stems from Ableton Live separation."""
        # This would retrieve stems created by Live
        # Placeholder implementation
        base_path = Path(audio_path).parent
        stem_name = Path(audio_path).stem
        
        stems = StemData(
            vocals_path=str(base_path / f"{stem_name}_vocals.wav"),
            drums_path=str(base_path / f"{stem_name}_drums.wav"),
            bass_path=str(base_path / f"{stem_name}_bass.wav"),
            other_path=str(base_path / f"{stem_name}_other.wav"),
            melody_path=str(base_path / f"{stem_name}_melody.wav")
        )
        
        return stems
    
    def _separate_with_fallback(self, audio_path: str) -> StemData:
        """
        Use external services for stem separation.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            StemData with separated stems
        """
        # Try spleeter (free, local)
        try:
            return self._separate_with_spleeter(audio_path)
        except Exception as e:
            logger.warning(f"Spleeter separation failed: {e}")
        
        # Try demucs (free, local, better quality)
        try:
            return self._separate_with_demucs(audio_path)
        except Exception as e:
            logger.warning(f"Demucs separation failed: {e}")
        
        # Return empty stems if all methods fail
        logger.error("All stem separation methods failed")
        return StemData()
    
    def _separate_with_spleeter(self, audio_path: str) -> StemData:
        """
        Use Spleeter for stem separation.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            StemData with separated stems
        """
        try:
            import spleeter
        except ImportError:
            raise ImportError("spleeter not installed. Install with: pip install spleeter")
        
        # Spleeter separates into: vocals, drums, bass, piano, other
        output_dir = os.path.join(self.config.temp_dir, "stems", Path(audio_path).stem)
        os.makedirs(output_dir, exist_ok=True)
        
        # Run spleeter separation (2stems or 4stems model)
        from spleeter.separator import Separator
        
        separator = Separator('spleeter:4stems-16kHz')
        separator.separate_to_file(audio_path, output_dir)
        
        # Map spleeter outputs to our stem structure
        stems = StemData(
            vocals_path=os.path.join(output_dir, Path(audio_path).stem, "vocals.wav"),
            drums_path=os.path.join(output_dir, Path(audio_path).stem, "drums.wav"),
            bass_path=os.path.join(output_dir, Path(audio_path).stem, "bass.wav"),
            other_path=os.path.join(output_dir, Path(audio_path).stem, "other.wav"),
            melody_path=os.path.join(output_dir, Path(audio_path).stem, "other.wav")  # Use other as melody
        )
        
        logger.info(f"Spleeter separation completed: {output_dir}")
        return stems
    
    def _separate_with_demucs(self, audio_path: str) -> StemData:
        """
        Use Demucs for stem separation (better quality than Spleeter).
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            StemData with separated stems
        """
        try:
            import demucs.separate
        except ImportError:
            raise ImportError("demucs not installed. Install with: pip install demucs")
        
        output_dir = os.path.join(self.config.temp_dir, "stems", Path(audio_path).stem)
        os.makedirs(output_dir, exist_ok=True)
        
        # Run demucs separation
        # Demucs separates into: drums, bass, other, vocals
        demucs.separate.main([
            '--out', output_dir,
            '--two-stems', 'vocals',  # Separate vocals and instrumental
            audio_path
        ])
        
        # Map demucs outputs
        base_name = Path(audio_path).stem
        stems = StemData(
            vocals_path=os.path.join(output_dir, "htdemucs", base_name, "vocals.wav"),
            drums_path=os.path.join(output_dir, "htdemucs", base_name, "drums.wav"),
            bass_path=os.path.join(output_dir, "htdemucs", base_name, "bass.wav"),
            other_path=os.path.join(output_dir, "htdemucs", base_name, "other.wav"),
            melody_path=os.path.join(output_dir, "htdemucs", base_name, "other.wav")
        )
        
        logger.info(f"Demucs separation completed: {output_dir}")
        return stems
