"""
JAMS to JSON Converter

Converts ChoCo JAMS files to lightweight JSON format for easier processing.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import jams
except ImportError:
    raise ImportError(
        "jams library required. Install with: pip install jams"
    )

logger = logging.getLogger(__name__)


def jams_to_json(
    jams_path: str,
    output_path: Optional[str] = None,
    include_metadata: bool = True,
    include_chords: bool = True,
    include_key: bool = True,
    include_structure: bool = False,
) -> Dict[str, Any]:
    """
    Convert a JAMS file to simplified JSON format.
    
    Args:
        jams_path: Path to JAMS file
        output_path: Optional output JSON path
        include_metadata: Include file metadata
        include_chords: Include chord annotations
        include_key: Include key/mode annotations
        include_structure: Include structural annotations (segments)
    
    Returns:
        Dictionary with converted data
    """
    import json
    import warnings
    
    try:
        jam = jams.load(jams_path, strict=False)
    except (jams.exceptions.NamespaceError, Exception) as e:
        # Try loading as JSON to bypass validation for unknown namespaces
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                with open(jams_path, 'r', encoding='utf-8') as f:
                    jam_dict = json.load(f)
                # Create JAMS object from dict, skipping validation
                jam = jams.JAMS()
                if 'file_metadata' in jam_dict:
                    for key, value in jam_dict['file_metadata'].items():
                        try:
                            setattr(jam.file_metadata, key, value)
                        except:
                            pass
                if 'sandbox' in jam_dict:
                    jam.sandbox = jam_dict['sandbox']
                # Skip annotations to avoid namespace issues - we'll extract chords differently
        except Exception as e2:
            logger.error(f"Error loading JAMS file {jams_path}: {e} (also tried JSON: {e2})")
            raise e
    
    result: Dict[str, Any] = {}
    
    # Extract metadata
    if include_metadata:
        metadata = {
            "title": jam.file_metadata.title or "",
            "artist": jam.file_metadata.artist or "",
            "duration": float(jam.file_metadata.duration) if jam.file_metadata.duration else 0.0,
            "release": jam.file_metadata.release or "",
        }
        
        # Extract sandbox metadata (handle both dict and Sandbox object)
        if hasattr(jam, 'sandbox') and jam.sandbox:
            # Try to access as dict first, then as object attributes
            try:
                if isinstance(jam.sandbox, dict):
                    sandbox_data = jam.sandbox
                else:
                    # Convert Sandbox object to dict-like access
                    sandbox_data = {}
                    for key in ['genre', 'dataset', 'type', 'composers', 'performers', 'release_year', 'track_number']:
                        if hasattr(jam.sandbox, key):
                            sandbox_data[key] = getattr(jam.sandbox, key)
            except:
                sandbox_data = {}
            
            metadata.update({
                "genre": sandbox_data.get("genre", ""),
                "dataset": sandbox_data.get("dataset", ""),
                "type": sandbox_data.get("type", ""),  # 'audio' or 'score'
                "composers": sandbox_data.get("composers", []),
                "performers": sandbox_data.get("performers", []),
            })
        
        # Extract identifiers
        if jam.file_metadata.identifiers:
            metadata["identifiers"] = dict(jam.file_metadata.identifiers)
        
        result["metadata"] = metadata
    
    # Extract chord annotations
    if include_chords:
        chords = []
        
        # Try different chord namespaces
        chord_namespaces = ["chord_harte", "chord", "chord_jparser_harte", "chord_jparser_functional"]
        chord_ann = None
        
        for namespace in chord_namespaces:
            chord_ann = jam.search(namespace=namespace)
            if chord_ann:
                break
        
        if chord_ann:
            for obs in chord_ann[0].data:
                chord_data = {
                    "time": float(obs.time),
                    "duration": float(obs.duration),
                    "chord": str(obs.value),
                    "confidence": float(obs.confidence) if obs.confidence else 1.0,
                }
                chords.append(chord_data)
        
        result["chords"] = chords
    
    # Extract key/mode annotations
    if include_key:
        key_ann = jam.search(namespace="key_mode")
        key_data = None
        
        if key_ann:
            # Get the most prominent key (first annotation or most common)
            key_obs = key_ann[0].data
            if key_obs:
                # Use the first key annotation
                first_key = key_obs[0]
                key_data = {
                    "key": str(first_key.value),
                    "time": float(first_key.time),
                    "duration": float(first_key.duration),
                    "confidence": float(first_key.confidence) if first_key.confidence else 1.0,
                }
        
        result["key"] = key_data
    
    # Extract structural annotations (segments)
    if include_structure:
        structure_ann = jam.search(namespace="segment_open")
        segments = []
        
        if structure_ann:
            for obs in structure_ann[0].data:
                segments.append({
                    "time": float(obs.time),
                    "duration": float(obs.duration),
                    "value": str(obs.value),  # e.g., "verse", "chorus"
                    "confidence": float(obs.confidence) if obs.confidence else 1.0,
                })
        
        result["structure"] = segments
    
    # Extract time signature if available
    timesig_ann = jam.search(namespace="timesig")
    if timesig_ann:
        timesig_obs = timesig_ann[0].data
        if timesig_obs:
            first_timesig = timesig_obs[0].value
            if isinstance(first_timesig, dict):
                result["time_signature"] = {
                    "numerator": first_timesig.get("numerator", 4),
                    "denominator": first_timesig.get("denominator", 4),
                }
            else:
                result["time_signature"] = str(first_timesig)
    
    # Save to file if output path provided
    if output_path:
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Converted JAMS to JSON: {output_path}")
    
    return result


def batch_convert_jams_to_json(
    jams_directory: str,
    output_directory: str,
    pattern: str = "*.jams",
    **kwargs
) -> List[str]:
    """
    Convert all JAMS files in a directory to JSON.
    
    Args:
        jams_directory: Directory containing JAMS files
        output_directory: Directory for JSON output
        pattern: Glob pattern for JAMS files (default: "*.jams")
        **kwargs: Additional arguments passed to jams_to_json
    
    Returns:
        List of output file paths
    """
    jams_dir = Path(jams_directory)
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    jams_files = list(jams_dir.rglob(pattern))
    logger.info(f"Found {len(jams_files)} JAMS files in {jams_directory}")
    
    output_files = []
    success_count = 0
    error_count = 0
    
    for jams_file in jams_files:
        try:
            # Preserve directory structure
            relative_path = jams_file.relative_to(jams_dir)
            output_path = output_dir / relative_path.with_suffix('.json')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            json_data = jams_to_json(str(jams_file), str(output_path), **kwargs)
            output_files.append(str(output_path))
            success_count += 1
            
            if success_count % 100 == 0:
                logger.info(f"Processed {success_count} files...")
                
        except Exception as e:
            error_count += 1
            logger.error(f"Error converting {jams_file.name}: {e}")
    
    logger.info(
        f"Conversion complete: {success_count} successful, {error_count} errors"
    )
    
    return output_files


def search_json_files(
    json_directory: str,
    search_term: str = "",
    genre: Optional[str] = None,
    dataset: Optional[str] = None,
    min_chords: int = 0,
) -> List[Dict[str, Any]]:
    """
    Search JSON files by metadata.
    
    Args:
        json_directory: Directory containing JSON files
        search_term: Search in title/artist
        genre: Filter by genre
        dataset: Filter by dataset name
        min_chords: Minimum number of chords
    
    Returns:
        List of matching JSON data dictionaries
    """
    json_dir = Path(json_directory)
    results = []
    
    for json_file in json_dir.rglob("*.json"):
        try:
            with open(json_file, encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = data.get('metadata', {})
            chords = data.get('chords', [])
            
            # Apply filters
            if min_chords > 0 and len(chords) < min_chords:
                continue
            
            if genre and metadata.get('genre', '').lower() != genre.lower():
                continue
            
            if dataset and metadata.get('dataset', '').lower() != dataset.lower():
                continue
            
            if search_term:
                search_lower = search_term.lower()
                title = metadata.get('title', '').lower()
                artist = metadata.get('artist', '').lower()
                if search_lower not in title and search_lower not in artist:
                    continue
            
            # Add file path for reference
            data['_file_path'] = str(json_file)
            results.append(data)
            
        except Exception as e:
            logger.warning(f"Error reading {json_file}: {e}")
    
    return results

