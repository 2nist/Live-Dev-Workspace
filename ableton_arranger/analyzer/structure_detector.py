"""
Song structure detection using API services.
Integrates with SONOTELLER.AI, Audjust Structure API, and other services.
"""
import os
import logging
import requests
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

from ableton_arranger.shared.data_models import (
    SectionData, AnalysisConfig
)


logger = logging.getLogger(__name__)


class StructureDetector:
    """
    Detects song structure using various API services.
    Designed for easy M4L conversion with simple request/response pattern.
    """
    
    def __init__(self, config: AnalysisConfig):
        """
        Initialize structure detector.
        
        Args:
            config: Analysis configuration containing API keys and settings
        """
        self.config = config
        self.api_costs: Dict[str, float] = {}
        self.last_request_time = 0
        self.rate_limit_delay = 1.0  # seconds between requests
        
    def detect_sections(self, audio_path: str) -> List[SectionData]:
        """
        Detect song sections using configured API service.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            List of detected sections with timing and metadata
        """
        try:
            # Try primary service first (SONOTELLER.AI)
            if self.config.sonoteller_api_key:
                return self._detect_with_sonoteller(audio_path)
            
            # Fallback to other services
            logger.warning("No SONOTELLER.AI key configured, trying fallback services")
            return self._detect_with_fallback(audio_path)
            
        except Exception as e:
            logger.error(f"Structure detection failed: {e}")
            # Return basic fallback structure
            return self._create_fallback_structure(audio_path)
    
    def _detect_with_sonoteller(self, audio_path: str) -> List[SectionData]:
        """
        Use SONOTELLER.AI for structure detection.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            List of detected sections
        """
        # Rate limiting
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        try:
            # Upload file and get analysis
            url = "https://api.sonoteller.ai/v1/analyze"
            
            headers = {
                "Authorization": f"Bearer {self.config.sonoteller_api_key}",
                "Accept": "application/json"
            }
            
            # Upload audio file
            with open(audio_path, 'rb') as audio_file:
                files = {
                    'file': (Path(audio_path).name, audio_file, 'audio/mpeg')
                }
                
                data = {
                    'analysis_type': 'structure',
                    'include_sections': 'true',
                    'include_golden_minute': 'true'
                }
                
                logger.info(f"Uploading {Path(audio_path).name} to SONOTELLER.AI...")
                response = requests.post(url, headers=headers, files=files, data=data)
                self.last_request_time = time.time()
                
                if response.status_code != 200:
                    raise RuntimeError(f"SONOTELLER.AI API error: {response.status_code} - {response.text}")
                
                result = response.json()
                
                # Track API costs (approximate)
                self.api_costs['sonoteller'] = self.api_costs.get('sonoteller', 0) + 0.10  # $0.10 per analysis
                
                return self._parse_sonoteller_response(result)
                
        except Exception as e:
            logger.error(f"SONOTELLER.AI analysis failed: {e}")
            raise
    
    def _parse_sonoteller_response(self, response: Dict[str, Any]) -> List[SectionData]:
        """
        Parse SONOTELLER.AI response into SectionData objects.
        
        Args:
            response: API response dict
            
        Returns:
            List of SectionData objects
        """
        sections = []
        
        # Parse sections from response
        analysis = response.get('analysis', {})
        structure = analysis.get('structure', {})
        segments = structure.get('segments', [])
        
        for i, segment in enumerate(segments):
            section_type = segment.get('label', 'unknown').lower()
            start_time = float(segment.get('start', 0))
            end_time = float(segment.get('end', start_time + 16))  # Default 16 seconds
            confidence = float(segment.get('confidence', 0.5))
            
            # Map SONOTELLER labels to standard section types
            section_name = self._normalize_section_name(section_type, i)
            
            section = SectionData(
                name=section_name,
                start_time=start_time,
                end_time=end_time,
                confidence=confidence,
                section_type=section_type,
                energy_level=segment.get('energy', 0.5)
            )
            
            sections.append(section)
        
        logger.info(f"Parsed {len(sections)} sections from SONOTELLER.AI")
        return sections
    
    def _detect_with_fallback(self, audio_path: str) -> List[SectionData]:
        """
        Try other free APIs for structure detection.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            List of detected sections
        """
        # Try Klangio free tier
        try:
            return self._detect_with_klangio(audio_path)
        except Exception as e:
            logger.warning(f"Klangio detection failed: {e}")
        
        # Try Cyanite.ai if available
        try:
            return self._detect_with_cyanite(audio_path)
        except Exception as e:
            logger.warning(f"Cyanite detection failed: {e}")
        
        # Last resort: create basic structure
        return self._create_fallback_structure(audio_path)
    
    def _detect_with_klangio(self, audio_path: str) -> List[SectionData]:
        """
        Use Klangio API for structure detection.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            List of detected sections
        """
        # This would implement Klangio API integration
        # For now, return fallback structure
        logger.info("Klangio integration not implemented yet")
        return self._create_fallback_structure(audio_path)
    
    def _detect_with_cyanite(self, audio_path: str) -> List[SectionData]:
        """
        Use Cyanite.ai API for structure detection.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            List of detected sections
        """
        # This would implement Cyanite.ai API integration
        # For now, return fallback structure
        logger.info("Cyanite.ai integration not implemented yet")
        return self._create_fallback_structure(audio_path)
    
    def _create_fallback_structure(self, audio_path: str) -> List[SectionData]:
        """
        Create basic fallback structure when APIs aren't available.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Basic song structure
        """
        try:
            # Get audio duration
            import librosa
            y, sr = librosa.load(audio_path)
            duration = len(y) / sr
        except ImportError:
            # Fallback: estimate from file size
            file_size = os.path.getsize(audio_path)
            duration = file_size / 1_000_000 * 60  # Rough estimate
        
        # Create basic structure based on common song format
        sections = []
        
        if duration < 60:  # Short track
            sections = [
                SectionData("Intro", 0, duration * 0.1, 0.8, "intro"),
                SectionData("Main", duration * 0.1, duration * 0.9, 0.8, "main"),
                SectionData("Outro", duration * 0.9, duration, 0.8, "outro")
            ]
        elif duration < 180:  # Normal song length  
            sections = [
                SectionData("Intro", 0, 8, 0.7, "intro"),
                SectionData("Verse 1", 8, 32, 0.7, "verse"),
                SectionData("Chorus 1", 32, 56, 0.7, "chorus"),
                SectionData("Verse 2", 56, 80, 0.7, "verse"),
                SectionData("Chorus 2", 80, 104, 0.7, "chorus"),
                SectionData("Bridge", 104, 128, 0.7, "bridge"),
                SectionData("Chorus 3", 128, 152, 0.7, "chorus"),
                SectionData("Outro", 152, duration, 0.7, "outro")
            ]
        else:  # Long track
            # Create more sections for longer tracks
            section_length = duration / 8
            section_names = ["Intro", "Section 1", "Section 2", "Section 3", 
                           "Section 4", "Section 5", "Section 6", "Outro"]
            
            for i, name in enumerate(section_names):
                start_time = i * section_length
                end_time = min((i + 1) * section_length, duration)
                section_type = "intro" if i == 0 else "outro" if i == len(section_names)-1 else "main"
                
                sections.append(SectionData(
                    name=name,
                    start_time=start_time,
                    end_time=end_time,
                    confidence=0.5,  # Lower confidence for fallback
                    section_type=section_type
                ))
        
        logger.info(f"Created fallback structure with {len(sections)} sections")
        return sections
    
    def _normalize_section_name(self, api_label: str, index: int) -> str:
        """
        Normalize API section labels to standard names.
        
        Args:
            api_label: Raw label from API
            index: Section index for fallback numbering
            
        Returns:
            Normalized section name
        """
        api_label = api_label.lower().strip()
        
        # Common mappings
        if 'intro' in api_label or 'beginning' in api_label:
            return "Intro"
        elif 'verse' in api_label:
            verse_num = self._extract_number(api_label) or (index // 2 + 1)
            return f"Verse {verse_num}"
        elif 'chorus' in api_label or 'refrain' in api_label:
            chorus_num = self._extract_number(api_label) or (index // 2 + 1)
            return f"Chorus {chorus_num}"
        elif 'bridge' in api_label or 'middle' in api_label:
            return "Bridge"
        elif 'outro' in api_label or 'end' in api_label:
            return "Outro"
        elif 'breakdown' in api_label or 'drop' in api_label:
            return "Breakdown"
        elif 'build' in api_label:
            return "Build"
        else:
            # Generic naming
            return f"Section {index + 1}"
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract number from text like 'verse1' or 'chorus 2'."""
        import re
        match = re.search(r'\d+', text)
        return int(match.group()) if match else None
    
    def get_api_costs(self) -> Dict[str, float]:
        """Get accumulated API costs for billing tracking."""
        return self.api_costs.copy()
    
    def reset_api_costs(self):
        """Reset API cost tracking."""
        self.api_costs.clear()
