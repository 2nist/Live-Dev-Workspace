#!/usr/bin/env python3
"""
ChoCo Metadata Coverage Analysis

Analyzes the ChoCo dataset to determine:
- How many files have artist names
- How many files have song titles
- Which datasets have the best/worst coverage
- What resources are available for expansion
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import argparse

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "src"))

try:
    import jams
    JAMS_AVAILABLE = True
except ImportError:
    JAMS_AVAILABLE = False
    print("Warning: jams library not available. Install with: pip install jams")


def analyze_jams_file(jams_path):
    """Analyze a single JAMS file for metadata coverage."""
    try:
        # Suppress warnings for non-standard chord notations
        import warnings
        import jams.exceptions
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                jam = jams.load(str(jams_path), strict=False)
            except (jams.exceptions.NamespaceError, Exception) as e:
                # Try loading as JSON to bypass validation
                import json
                try:
                    with open(jams_path, 'r') as f:
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
                        # Sandbox can be dict or needs to be set differently
                        sandbox_val = jam_dict['sandbox']
                        if isinstance(sandbox_val, dict):
                            # Set sandbox as dict
                            jam.sandbox = sandbox_val
                        else:
                            jam.sandbox = sandbox_val
                    if 'annotations' in jam_dict:
                        # Skip annotations for now to avoid namespace issues
                        pass
                except Exception as e2:
                    raise e  # Re-raise original error
        
        # Handle artist which might be string or list
        artist = jam.file_metadata.artist
        if isinstance(artist, list):
            artist = ", ".join(str(a) for a in artist) if artist else ""
        else:
            artist = str(artist) if artist else ""
        
        metadata = {
            "has_title": bool(jam.file_metadata.title),
            "has_artist": bool(artist),
            "has_release": bool(jam.file_metadata.release),
            "has_duration": bool(jam.file_metadata.duration),
            "title": str(jam.file_metadata.title) if jam.file_metadata.title else "",
            "artist": artist,
            "release": str(jam.file_metadata.release) if jam.file_metadata.release else "",
            "duration": float(jam.file_metadata.duration) if jam.file_metadata.duration else None,
        }
        
        # Check sandbox metadata (sandbox can be dict or Sandbox object)
        if hasattr(jam, 'sandbox') and jam.sandbox:
            # Try to access as dict first, then as object attributes
            try:
                if isinstance(jam.sandbox, dict):
                    sandbox_data = jam.sandbox
                else:
                    # Convert Sandbox object to dict-like access
                    sandbox_data = {}
                    for key in ['genre', 'dataset', 'composers', 'performers', 'type']:
                        if hasattr(jam.sandbox, key):
                            sandbox_data[key] = getattr(jam.sandbox, key)
            except:
                sandbox_data = {}
            
            metadata.update({
                "has_genre": bool(sandbox_data.get("genre")),
                "has_dataset": bool(sandbox_data.get("dataset")),
                "has_composers": bool(sandbox_data.get("composers")),
                "has_performers": bool(sandbox_data.get("performers")),
                "genre": sandbox_data.get("genre", ""),
                "dataset": sandbox_data.get("dataset", ""),
                "composers": sandbox_data.get("composers", []),
                "performers": sandbox_data.get("performers", []),
            })
        else:
            metadata.update({
                "has_genre": False,
                "has_dataset": False,
                "has_composers": False,
                "has_performers": False,
                "genre": "",
                "dataset": "",
                "composers": [],
                "performers": [],
            })
        
        # Check identifiers
        identifiers = {}
        if jam.file_metadata.identifiers:
            identifiers = dict(jam.file_metadata.identifiers)
        
        # Check for MusicBrainz ID (can be "MB" or "musicbrainz" key)
        has_mb = False
        identifiers_lower = {k.lower(): v for k, v in identifiers.items()}
        if "MB" in identifiers or "musicbrainz" in identifiers_lower:
            has_mb = True
        
        metadata.update({
            "has_identifiers": len(identifiers) > 0,
            "identifiers": identifiers,
            "has_musicbrainz": has_mb,
            "has_isrc": "ISRC" in identifiers or "isrc" in identifiers_lower,
        })
        
        # Check chord annotations (try multiple namespaces)
        chord_ann = None
        for namespace in ["chord_harte", "chord", "chord_jparser_harte", "chord_weimar"]:
            try:
                chord_ann = jam.search(namespace=namespace)
                if chord_ann:
                    break
            except:
                continue
        
        metadata["has_chords"] = bool(chord_ann)
        metadata["chord_count"] = len(chord_ann[0].data) if chord_ann and len(chord_ann) > 0 else 0
        
        # Add file path for reference
        metadata["file_path"] = str(jams_path)
        metadata["file_name"] = Path(jams_path).name
        
        return metadata
        
    except Exception as e:
        # Return minimal metadata on error
        return {
            "error": str(e),
            "has_title": False,
            "has_artist": False,
            "has_release": False,
            "has_duration": False,
            "has_genre": False,
            "has_dataset": False,
            "has_identifiers": False,
            "has_chords": False,
            "chord_count": 0,
            "file_path": str(jams_path),
            "file_name": Path(jams_path).name,
        }


def analyze_dataset(jams_directory, sample_size=None):
    """Analyze metadata coverage across the dataset."""
    jams_dir = Path(jams_directory)
    
    if not jams_dir.exists():
        print(f"Error: Directory not found: {jams_directory}")
        return None
    
    # Find all JAMS files
    jams_files = list(jams_dir.rglob("*.jams"))
    
    if not jams_files:
        print(f"No JAMS files found in {jams_directory}")
        return None
    
    if sample_size:
        import random
        jams_files = random.sample(jams_files, min(sample_size, len(jams_files)))
        print(f"Analyzing sample of {len(jams_files)} files...")
    else:
        print(f"Analyzing {len(jams_files)} JAMS files...")
    
    # Analyze files
    results = []
    errors = 0
    
    import warnings
    warnings.filterwarnings('ignore')
    
    for i, jams_file in enumerate(jams_files, 1):
        if i % 100 == 0:
            print(f"  Processed {i}/{len(jams_files)} files...")
        
        try:
            metadata = analyze_jams_file(jams_file)
            
            # Only count as error if there's an actual exception, not just missing data
            if "error" in metadata and metadata["error"]:
                errors += 1
                # Still include in results for error tracking
                results.append(metadata)
            else:
                # Valid file, even if metadata is missing
                results.append(metadata)
        except Exception as e:
            errors += 1
            results.append({
                "error": str(e),
                "has_title": False,
                "has_artist": False,
                "file_path": str(jams_file),
            })
            continue
        
        # Add file path for reference
        metadata["file_path"] = str(jams_file)
        metadata["file_name"] = jams_file.name
        
        results.append(metadata)
    
    print(f"✓ Analyzed {len(results)} files ({errors} errors)")
    
    return {
        "total_files": len(results),
        "errors": errors,
        "results": results,
    }


def generate_statistics(analysis):
    """Generate statistics from analysis results."""
    if not analysis:
        return None
    
    results = analysis["results"]
    total = len(results)
    
    if total == 0:
        return None
    
    stats = {
        "total_files": total,
        "coverage": {
            "has_title": sum(1 for r in results if r.get("has_title")),
            "has_artist": sum(1 for r in results if r.get("has_artist")),
            "has_both": sum(1 for r in results if r.get("has_title") and r.get("has_artist")),
            "has_release": sum(1 for r in results if r.get("has_release")),
            "has_duration": sum(1 for r in results if r.get("has_duration")),
            "has_genre": sum(1 for r in results if r.get("has_genre")),
            "has_identifiers": sum(1 for r in results if r.get("has_identifiers")),
            "has_musicbrainz": sum(1 for r in results if r.get("has_musicbrainz")),
            "has_composers": sum(1 for r in results if r.get("has_composers")),
            "has_performers": sum(1 for r in results if r.get("has_performers")),
        },
        "by_dataset": defaultdict(lambda: {
            "count": 0,
            "has_title": 0,
            "has_artist": 0,
            "has_both": 0,
        }),
    }
    
    # Calculate percentages (create new dict to avoid modification during iteration)
    coverage_with_percent = stats["coverage"].copy()
    for key in list(stats["coverage"].keys()):
        if not key.endswith("_percent"):
            count = stats["coverage"][key]
            coverage_with_percent[f"{key}_percent"] = (count / total) * 100
    stats["coverage"] = coverage_with_percent
    
    # Analyze by dataset
    for result in results:
        dataset = result.get("dataset", "unknown")
        stats["by_dataset"][dataset]["count"] += 1
        if result.get("has_title"):
            stats["by_dataset"][dataset]["has_title"] += 1
        if result.get("has_artist"):
            stats["by_dataset"][dataset]["has_artist"] += 1
        if result.get("has_title") and result.get("has_artist"):
            stats["by_dataset"][dataset]["has_both"] += 1
    
    # Convert to regular dict and calculate percentages
    dataset_stats = {}
    for dataset, data in stats["by_dataset"].items():
        dataset_stats[dataset] = {
            "count": data["count"],
            "has_title": data["has_title"],
            "has_artist": data["has_artist"],
            "has_both": data["has_both"],
            "title_percent": (data["has_title"] / data["count"] * 100) if data["count"] > 0 else 0,
            "artist_percent": (data["has_artist"] / data["count"] * 100) if data["count"] > 0 else 0,
            "both_percent": (data["has_both"] / data["count"] * 100) if data["count"] > 0 else 0,
        }
    
    stats["by_dataset"] = dataset_stats
    
    return stats


def print_report(stats, output_file=None):
    """Print a formatted report."""
    if not stats:
        print("No statistics available")
        return
    
    report_lines = []
    
    report_lines.append("="*70)
    report_lines.append("ChoCo Dataset Metadata Coverage Report")
    report_lines.append("="*70)
    report_lines.append("")
    
    # Overall coverage
    report_lines.append("Overall Coverage:")
    report_lines.append("-" * 70)
    total = stats["total_files"]
    
    coverage = stats["coverage"]
    report_lines.append(f"Total files analyzed: {total:,}")
    report_lines.append("")
    report_lines.append("Metadata Fields:")
    report_lines.append(f"  Title:        {coverage['has_title']:,} ({coverage['has_title_percent']:.1f}%)")
    report_lines.append(f"  Artist:       {coverage['has_artist']:,} ({coverage['has_artist_percent']:.1f}%)")
    report_lines.append(f"  Both:         {coverage['has_both']:,} ({coverage['has_both_percent']:.1f}%)")
    report_lines.append(f"  Release:      {coverage['has_release']:,} ({coverage['has_release_percent']:.1f}%)")
    report_lines.append(f"  Duration:     {coverage['has_duration']:,} ({coverage['has_duration_percent']:.1f}%)")
    report_lines.append(f"  Genre:        {coverage['has_genre']:,} ({coverage['has_genre_percent']:.1f}%)")
    report_lines.append("")
    report_lines.append("Identifiers:")
    report_lines.append(f"  Any ID:       {coverage['has_identifiers']:,} ({coverage['has_identifiers_percent']:.1f}%)")
    report_lines.append(f"  MusicBrainz:  {coverage['has_musicbrainz']:,} ({coverage['has_musicbrainz_percent']:.1f}%)")
    report_lines.append("")
    
    # Missing metadata
    missing_title = total - coverage['has_title']
    missing_artist = total - coverage['has_artist']
    missing_both = total - coverage['has_both']
    
    report_lines.append("Missing Metadata:")
    report_lines.append(f"  Missing title:  {missing_title:,} ({100 - coverage['has_title_percent']:.1f}%)")
    report_lines.append(f"  Missing artist: {missing_artist:,} ({100 - coverage['has_artist_percent']:.1f}%)")
    report_lines.append(f"  Missing both:   {missing_both:,} ({100 - coverage['has_both_percent']:.1f}%)")
    report_lines.append("")
    
    # By dataset
    report_lines.append("Coverage by Dataset:")
    report_lines.append("-" * 70)
    report_lines.append(f"{'Dataset':<30} {'Files':<10} {'Title%':<10} {'Artist%':<10} {'Both%':<10}")
    report_lines.append("-" * 70)
    
    sorted_datasets = sorted(
        stats["by_dataset"].items(),
        key=lambda x: x[1]["count"],
        reverse=True
    )
    
    for dataset, data in sorted_datasets:
        report_lines.append(
            f"{dataset[:28]:<30} {data['count']:<10} "
            f"{data['title_percent']:>6.1f}%   {data['artist_percent']:>6.1f}%   "
            f"{data['both_percent']:>6.1f}%"
        )
    
    report_lines.append("")
    report_lines.append("="*70)
    
    # Print report
    report_text = "\n".join(report_lines)
    print(report_text)
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report_text)
        print(f"\n✓ Report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze ChoCo dataset metadata coverage"
    )
    parser.add_argument(
        "--jams-dir",
        type=str,
        required=True,
        help="Directory containing JAMS files"
    )
    parser.add_argument(
        "--sample",
        type=int,
        help="Analyze only a sample of files (for faster testing)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Save report to file"
    )
    parser.add_argument(
        "--json",
        type=str,
        help="Save detailed statistics as JSON"
    )
    
    args = parser.parse_args()
    
    if not JAMS_AVAILABLE:
        print("Error: jams library required")
        print("Install with: pip install jams")
        sys.exit(1)
    
    # Analyze dataset
    analysis = analyze_dataset(args.jams_dir, sample_size=args.sample)
    
    if not analysis:
        sys.exit(1)
    
    # Generate statistics
    stats = generate_statistics(analysis)
    
    if not stats:
        print("Error generating statistics")
        sys.exit(1)
    
    # Print report
    print_report(stats, output_file=args.output)
    
    # Save JSON if requested
    if args.json:
        with open(args.json, 'w') as f:
            json.dump({
                "statistics": stats,
                "analysis": analysis,
            }, f, indent=2)
        print(f"✓ Detailed data saved to: {args.json}")


if __name__ == "__main__":
    main()
