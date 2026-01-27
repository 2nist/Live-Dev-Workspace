"""
Lyrics transcription using Whisper or API services.
"""
import os
import logging
from typing import Dict, Any

from ableton_arranger.shared.data_models import LyricsData, AnalysisConfig


logger = logging.getLogger(__name__)


class LyricsTranscriber:
    """
    Transcribes lyrics from audio.
    Uses OpenAI Whisper (local) or API services.
    """
    
    def __init__(self, config: AnalysisConfig):
        """
        Initialize lyrics transcriber.
        
        Args:
            config: Analysis configuration
        """
        self.config = config
    
    def transcribe(self, audio_path: str) -> LyricsData:
        """
        Transcribe lyrics from audio.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            LyricsData with transcribed text and word timings
        """
        try:
            if self.config.use_local_whisper:
                return self._transcribe_with_whisper(audio_path)
            else:
                # Would use API service
                logger.warning("API transcription not implemented yet")
                return LyricsData()
                
        except Exception as e:
            logger.error(f"Lyrics transcription failed: {e}")
            return LyricsData()
    
    def _transcribe_with_whisper(self, audio_path: str) -> LyricsData:
        """
        Use OpenAI Whisper for transcription.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            LyricsData with transcription
        """
        try:
            import whisper
        except ImportError:
            raise ImportError("whisper not installed. Install with: pip install openai-whisper")
        
        # Load Whisper model
        model = whisper.load_model(self.config.whisper_model)
        
        # Transcribe
        logger.info(f"Transcribing {Path(audio_path).name} with Whisper {self.config.whisper_model}...")
        result = model.transcribe(audio_path, word_timestamps=True)
        
        # Extract words with timing
        words = []
        for segment in result.get("segments", []):
            for word_info in segment.get("words", []):
                words.append({
                    "word": word_info.get("word", ""),
                    "start": word_info.get("start", 0.0),
                    "end": word_info.get("end", 0.0),
                    "confidence": word_info.get("probability", 0.0)
                })
        
        lyrics = LyricsData(
            full_text=result.get("text", ""),
            words=words,
            language=result.get("language", "en"),
            confidence=0.8  # Whisper generally has good confidence
        )
        
        logger.info(f"Transcribed {len(words)} words")
        return lyrics
