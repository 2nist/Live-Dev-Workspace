"""
Core audio analyzer interface.
Main entry point for the analyzer module.
"""
import os
import logging
import asyncio
import time
from typing import Optional, Callable, Any
from pathlib import Path

from ableton_arranger.shared.data_models import (
    AnalysisData, AnalysisConfig, AnalysisStatus, SongInfo
)


logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """
    Main audio analyzer interface.
    Coordinates all analysis processes and provides clean API for M4L conversion.
    """
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        """
        Initialize analyzer with configuration.
        
        Args:
            config: Analysis configuration, uses defaults if None
        """
        self.config = config or AnalysisConfig()
        self.current_analysis: Optional[AnalysisData] = None
        self.is_processing = False
        
        # Progress callback for UI updates
        self.progress_callback: Optional[Callable[[str, float], None]] = None
        
        # Ensure temp directory exists
        os.makedirs(self.config.temp_dir, exist_ok=True)
        
        logger.info(f"AudioAnalyzer initialized with temp_dir: {self.config.temp_dir}")
    
    def set_progress_callback(self, callback: Callable[[str, float], None]):
        """
        Set callback for progress updates.
        
        Args:
            callback: Function(message: str, progress: float) called during analysis
        """
        self.progress_callback = callback
    
    def _update_progress(self, message: str, progress: float):
        """Update progress via callback if set."""
        if self.progress_callback:
            self.progress_callback(message, progress)
        logger.info(f"Progress: {message} ({progress:.1%})")
    
    def analyze_file(self, file_path: str) -> AnalysisData:
        """
        Analyze audio file completely.
        
        Args:
            file_path: Path to audio file (MP3, WAV, etc.)
            
        Returns:
            Complete analysis data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: For analysis errors
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        if self.is_processing:
            raise RuntimeError("Analysis already in progress")
        
        try:
            self.is_processing = True
            start_time = time.time()
            
            # Initialize analysis data
            song_info = SongInfo(
                file_path=file_path,
                title=Path(file_path).stem,
                file_format=Path(file_path).suffix.lower()
            )
            
            analysis = AnalysisData(
                song_info=song_info,
                status=AnalysisStatus.PROCESSING
            )
            
            self.current_analysis = analysis
            self._update_progress("Starting analysis...", 0.0)
            
            # Step 1: Basic audio info extraction
            self._update_progress("Extracting audio information...", 0.1)
            self._extract_basic_info(analysis)
            
            # Step 2: Structure detection (if enabled)
            if self.config.enable_structure_detection:
                self._update_progress("Detecting song structure...", 0.2)
                self._detect_structure(analysis)
            
            # Step 3: Stem separation (if enabled)  
            if self.config.enable_stem_separation:
                self._update_progress("Separating audio stems...", 0.4)
                self._separate_stems(analysis)
            
            # Step 4: Chord detection (if enabled)
            if self.config.enable_chord_detection:
                self._update_progress("Detecting chord progressions...", 0.6)
                self._detect_chords(analysis)
            
            # Step 5: Lyrics transcription (if enabled)
            if self.config.enable_lyrics_transcription:
                self._update_progress("Transcribing lyrics...", 0.8)
                self._transcribe_lyrics(analysis)
            
            # Finalize
            analysis.analysis_time = time.time() - start_time
            analysis.status = AnalysisStatus.COMPLETED
            self._update_progress("Analysis complete!", 1.0)
            
            # Cache results if enabled
            if self.config.cache_results:
                self._cache_analysis(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            if self.current_analysis:
                self.current_analysis.status = AnalysisStatus.ERROR
                self.current_analysis.error_message = str(e)
            raise
        finally:
            self.is_processing = False
    
    async def analyze_file_async(self, file_path: str) -> AnalysisData:
        """
        Async version of analyze_file for non-blocking operation.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Complete analysis data
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.analyze_file, file_path)
    
    def analyze_url(self, url: str) -> AnalysisData:
        """
        Analyze audio from URL (YouTube, etc.).
        
        Args:
            url: Audio/video URL
            
        Returns:
            Complete analysis data
        """
        # Import here to avoid dependency if not used
        try:
            import yt_dlp
        except ImportError:
            raise ImportError("yt-dlp required for URL analysis. Install with: pip install yt-dlp")
        
        self._update_progress("Downloading audio from URL...", 0.05)
        
        # Download to temp file
        temp_audio_path = os.path.join(self.config.temp_dir, "downloaded_audio.mp3")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': temp_audio_path.replace('.mp3', '.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Unknown')
            artist = info.get('uploader', 'Unknown')
        
        # Update song info with downloaded metadata
        song_info = SongInfo(
            title=title,
            artist=artist,
            source_url=url,
            file_path=temp_audio_path,
            file_format='.mp3'
        )
        
        # Run normal file analysis
        analysis = self.analyze_file(temp_audio_path)
        analysis.song_info = song_info  # Update with downloaded metadata
        
        return analysis
    
    def get_analysis_status(self) -> AnalysisStatus:
        """Get current analysis status."""
        if self.current_analysis:
            return self.current_analysis.status
        return AnalysisStatus.IDLE
    
    def cancel_analysis(self):
        """Cancel current analysis if running."""
        if self.is_processing and self.current_analysis:
            self.current_analysis.status = AnalysisStatus.ERROR
            self.current_analysis.error_message = "Analysis cancelled by user"
            self.is_processing = False
            logger.info("Analysis cancelled")
    
    # Private methods for each analysis step
    def _extract_basic_info(self, analysis: AnalysisData):
        """Extract basic audio information using librosa or similar."""
        try:
            import librosa
            y, sr = librosa.load(analysis.song_info.file_path)
            
            # Update duration
            analysis.song_info.duration_seconds = len(y) / sr
            
            # Basic tempo detection
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            analysis.tempo = float(tempo)
            
            logger.info(f"Basic info extracted: {analysis.song_info.duration_seconds:.1f}s, {analysis.tempo:.1f} BPM")
            
        except ImportError:
            logger.warning("librosa not available, using minimal info extraction")
            # Fallback: use file size for rough duration estimate
            file_size = os.path.getsize(analysis.song_info.file_path)
            # Rough estimate: 1MB ≈ 1 minute for MP3
            analysis.song_info.duration_seconds = file_size / 1_000_000 * 60
    
    def _detect_structure(self, analysis: AnalysisData):
        """Detect song structure using API services."""
        # Import individual analyzers
        from ableton_arranger.analyzer.structure_detector import StructureDetector
        
        detector = StructureDetector(self.config)
        sections = detector.detect_sections(analysis.song_info.file_path)
        analysis.sections = sections
        
        # Update API costs
        analysis.api_costs.update(detector.get_api_costs())
    
    def _separate_stems(self, analysis: AnalysisData):
        """Separate audio into stems."""
        from ableton_arranger.analyzer.stem_processor import StemProcessor
        
        processor = StemProcessor(self.config)
        stems = processor.separate_stems(analysis.song_info.file_path)
        analysis.stems = stems
    
    def _detect_chords(self, analysis: AnalysisData):
        """Detect chord progressions."""
        from ableton_arranger.analyzer.chord_detector import ChordDetector
        
        detector = ChordDetector(self.config)
        chords = detector.detect_chords(analysis.song_info.file_path)
        analysis.chords = chords
        
        # Update API costs
        analysis.api_costs.update(detector.get_api_costs())
    
    def _transcribe_lyrics(self, analysis: AnalysisData):
        """Transcribe lyrics using Whisper or API."""
        from ableton_arranger.analyzer.lyrics_transcriber import LyricsTranscriber
        
        transcriber = LyricsTranscriber(self.config)
        
        # Use vocal stem if available, otherwise full audio
        audio_path = analysis.stems.vocals_path or analysis.song_info.file_path
        lyrics = transcriber.transcribe(audio_path)
        analysis.lyrics = lyrics
    
    def _cache_analysis(self, analysis: AnalysisData):
        """Cache analysis results for future use."""
        cache_file = os.path.join(
            self.config.temp_dir,
            f"{Path(analysis.song_info.file_path).stem}_analysis.json"
        )
        
        try:
            with open(cache_file, 'w') as f:
                f.write(analysis.to_json())
            logger.info(f"Analysis cached to: {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to cache analysis: {e}")


# Convenience function for simple usage
def analyze_audio_file(file_path: str, config: Optional[AnalysisConfig] = None) -> AnalysisData:
    """
    Convenience function to analyze a single audio file.
    
    Args:
        file_path: Path to audio file
        config: Analysis configuration
        
    Returns:
        Complete analysis data
    """
    analyzer = AudioAnalyzer(config)
    return analyzer.analyze_file(file_path)
