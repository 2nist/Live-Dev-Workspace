#!/usr/bin/env python3
"""
Complete ChoCo Enhancement Pipeline

This script demonstrates the full workflow:
1. Convert JAMS files to JSON
2. Enhance metadata for better identification
3. Build search indexes
4. Find and report duplicates
"""

import sys
import json
import logging
from pathlib import Path
import argparse

# Add parent directory to path for imports
script_dir = Path(__file__).resolve().parent
parent_dir = script_dir.parent
src_dir = parent_dir / "src"
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(src_dir))

try:
    from choco_integration import (
        batch_convert_jams_to_json,
        MetadataEnhancer,
        search_json_files,
    )
except ImportError as e:
    # Try alternative import path
    try:
        import importlib.util
        choco_init = src_dir / "choco_integration" / "__init__.py"
        if choco_init.exists():
            spec = importlib.util.spec_from_file_location(
                "choco_integration",
                choco_init
            )
            choco_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(choco_module)
            batch_convert_jams_to_json = choco_module.batch_convert_jams_to_json
            MetadataEnhancer = choco_module.MetadataEnhancer
            search_json_files = choco_module.search_json_files
        else:
            raise ImportError(f"Module not found at {choco_init}")
    except Exception as e2:
        print(f"Error importing choco_integration: {e}")
        print(f"Also tried direct import: {e2}")
        print(f"Script dir: {script_dir}")
        print(f"Parent dir: {parent_dir}")
        print(f"Src dir: {src_dir}")
        print(f"Looking for: {src_dir / 'choco_integration' / '__init__.py'}")
        print(f"Current path: {sys.path}")
        print("Make sure you're in the correct directory and dependencies are installed.")
        print("Try: pip install jams music21 rapidfuzz")
        sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def convert_jams_to_json(jams_dir, json_output_dir, pattern="*.jams"):
    """Step 1: Convert JAMS files to JSON."""
    logger.info(f"Converting JAMS files from {jams_dir} to {json_output_dir}")
    
    try:
        output_files = batch_convert_jams_to_json(
            jams_dir,
            json_output_dir,
            pattern=pattern
        )
        logger.info(f"✓ Converted {len(output_files)} JAMS files to JSON")
        return output_files
    except Exception as e:
        logger.error(f"Error converting JAMS files: {e}")
        raise


def enhance_metadata(json_input_dir, json_output_dir, overwrite=False):
    """Step 2: Enhance metadata for better identification."""
    logger.info(f"Enhancing metadata from {json_input_dir} to {json_output_dir}")
    
    enhancer = MetadataEnhancer()
    
    try:
        enhanced_files = enhancer.batch_enhance(
            json_input_dir,
            json_output_dir,
            overwrite=overwrite
        )
        logger.info(f"✓ Enhanced {len(enhanced_files)} JSON files")
        return enhanced_files
    except Exception as e:
        logger.error(f"Error enhancing metadata: {e}")
        raise


def build_indexes(json_dir, output_dir):
    """Step 3: Build search indexes."""
    logger.info(f"Building search indexes from {json_dir}")
    
    enhancer = MetadataEnhancer()
    
    try:
        # Build indexes
        artist_index = enhancer.build_artist_index(json_dir)
        song_index = enhancer.build_song_index(json_dir)
        
        # Save indexes
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        artist_index_path = output_path / "artist_index.json"
        song_index_path = output_path / "song_index.json"
        
        with open(artist_index_path, 'w', encoding='utf-8') as f:
            json.dump(artist_index, f, indent=2, ensure_ascii=False)
        
        with open(song_index_path, 'w', encoding='utf-8') as f:
            json.dump(song_index, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Built indexes: {len(artist_index)} artists, {len(song_index)} songs")
        logger.info(f"  Saved to: {artist_index_path} and {song_index_path}")
        
        return artist_index, song_index
    except Exception as e:
        logger.error(f"Error building indexes: {e}")
        raise


def find_duplicates(json_dir, output_dir, similarity_threshold=0.85):
    """Step 4: Find duplicate songs."""
    logger.info(f"Finding duplicates in {json_dir}")
    
    import glob
    
    enhancer = MetadataEnhancer()
    
    try:
        # Get all JSON files
        json_files = list(Path(json_dir).rglob("*.json"))
        json_file_paths = [str(f) for f in json_files]
        
        logger.info(f"Analyzing {len(json_file_paths)} files for duplicates...")
        
        duplicates = enhancer.find_duplicates(
            json_file_paths,
            similarity_threshold=similarity_threshold
        )
        
        # Save duplicate report
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        duplicates_path = output_path / "duplicates.json"
        
        with open(duplicates_path, 'w', encoding='utf-8') as f:
            json.dump(duplicates, f, indent=2, ensure_ascii=False)
        
        # Report statistics
        total_duplicates = sum(len(files) for files in duplicates.values() if len(files) > 1)
        duplicate_groups = len([f for f in duplicates.values() if len(f) > 1])
        
        logger.info(f"✓ Found {duplicate_groups} duplicate groups ({total_duplicates} total files)")
        logger.info(f"  Saved to: {duplicates_path}")
        
        # Print top duplicates
        if duplicate_groups > 0:
            logger.info("\nTop duplicate groups:")
            sorted_dups = sorted(
                [(k, v) for k, v in duplicates.items() if len(v) > 1],
                key=lambda x: len(x[1]),
                reverse=True
            )[:10]
            
            for canonical_id, files in sorted_dups:
                logger.info(f"  {canonical_id}: {len(files)} versions")
        
        return duplicates
    except Exception as e:
        logger.error(f"Error finding duplicates: {e}")
        raise


def generate_statistics(json_dir, output_dir):
    """Step 5: Generate dataset statistics."""
    logger.info(f"Generating statistics for {json_dir}")
    
    import glob
    from collections import Counter
    
    stats = {
        "total_files": 0,
        "artists": Counter(),
        "genres": Counter(),
        "datasets": Counter(),
        "songs_with_chords": 0,
        "total_chords": 0,
    }
    
    json_files = list(Path(json_dir).rglob("*.json"))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            stats["total_files"] += 1
            metadata = data.get("metadata", {})
            
            # Count artists
            artist = metadata.get("artist_normalized") or metadata.get("artist", "")
            if artist:
                stats["artists"][artist] += 1
            
            # Count genres
            genre = metadata.get("genre", "")
            if genre:
                stats["genres"][genre] += 1
            
            # Count datasets
            dataset = metadata.get("dataset", "")
            if dataset:
                stats["datasets"][dataset] += 1
            
            # Count chords
            chords = data.get("chords", [])
            if chords:
                stats["songs_with_chords"] += 1
                stats["total_chords"] += len(chords)
        
        except Exception as e:
            logger.warning(f"Error processing {json_file}: {e}")
    
    # Convert counters to dicts for JSON
    stats["artists"] = dict(stats["artists"].most_common(20))
    stats["genres"] = dict(stats["genres"])
    stats["datasets"] = dict(stats["datasets"])
    
    # Save statistics
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    stats_path = output_path / "statistics.json"
    
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✓ Generated statistics:")
    logger.info(f"  Total files: {stats['total_files']}")
    logger.info(f"  Songs with chords: {stats['songs_with_chords']}")
    logger.info(f"  Total chords: {stats['total_chords']}")
    logger.info(f"  Unique artists: {len(stats['artists'])}")
    logger.info(f"  Genres: {len(stats['genres'])}")
    logger.info(f"  Datasets: {len(stats['datasets'])}")
    logger.info(f"  Saved to: {stats_path}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Complete ChoCo Enhancement Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline
  python choco_enhancement_pipeline.py --jams-dir /path/to/jams --output-dir ./output

  # Skip JAMS conversion (already have JSON)
  python choco_enhancement_pipeline.py --json-dir ./json --output-dir ./enhanced --skip-convert

  # Only enhance metadata
  python choco_enhancement_pipeline.py --json-dir ./json --output-dir ./enhanced --only-enhance
        """
    )
    
    parser.add_argument(
        "--jams-dir",
        type=str,
        help="Directory containing JAMS files"
    )
    parser.add_argument(
        "--json-dir",
        type=str,
        help="Directory containing JSON files (if already converted)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./choco_enhanced",
        help="Output directory for enhanced files and indexes (default: ./choco_enhanced)"
    )
    parser.add_argument(
        "--skip-convert",
        action="store_true",
        help="Skip JAMS to JSON conversion (use existing JSON)"
    )
    parser.add_argument(
        "--only-enhance",
        action="store_true",
        help="Only run enhancement (skip indexes and duplicates)"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing enhanced files"
    )
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.85,
        help="Similarity threshold for duplicate detection (0-1, default: 0.85)"
    )
    
    args = parser.parse_args()
    
    # Determine input directory
    if args.skip_convert and not args.json_dir:
        logger.error("--json-dir required when using --skip-convert")
        sys.exit(1)
    
    if not args.skip_convert and not args.jams_dir:
        logger.error("--jams-dir required (or use --skip-convert with --json-dir)")
        sys.exit(1)
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Convert JAMS to JSON (if needed)
    if not args.skip_convert:
        json_intermediate = output_dir / "json_intermediate"
        convert_jams_to_json(args.jams_dir, str(json_intermediate))
        json_input_dir = str(json_intermediate)
    else:
        json_input_dir = args.json_dir
    
    # Step 2: Enhance metadata
    json_enhanced = output_dir / "json_enhanced"
    enhance_metadata(json_input_dir, str(json_enhanced), overwrite=args.overwrite)
    
    if args.only_enhance:
        logger.info("✓ Enhancement complete (skipped indexes and duplicates)")
        return
    
    # Step 3: Build indexes
    indexes_dir = output_dir / "indexes"
    build_indexes(str(json_enhanced), str(indexes_dir))
    
    # Step 4: Find duplicates
    find_duplicates(
        str(json_enhanced),
        str(indexes_dir),
        similarity_threshold=args.similarity_threshold
    )
    
    # Step 5: Generate statistics
    generate_statistics(str(json_enhanced), str(indexes_dir))
    
    logger.info("\n" + "="*60)
    logger.info("✓ Enhancement pipeline complete!")
    logger.info(f"  Enhanced files: {json_enhanced}")
    logger.info(f"  Indexes and reports: {indexes_dir}")
    logger.info("="*60)


if __name__ == "__main__":
    main()
