#!/usr/bin/env python3
"""
ChoCo Dataset Search Example

Demonstrates how to search the enhanced ChoCo dataset using
the metadata enhancement features.
"""

import sys
import json
import argparse
from pathlib import Path

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "src"))

from choco_integration import MetadataEnhancer, search_json_files


def search_artists_example(enhanced_json_dir, query, limit=10):
    """Example: Search for artists."""
    print(f"\n{'='*60}")
    print(f"Searching for artists: '{query}'")
    print(f"{'='*60}\n")
    
    enhancer = MetadataEnhancer()
    
    # Build or load artist index
    index_path = Path(enhanced_json_dir).parent / "indexes" / "artist_index.json"
    
    if index_path.exists():
        print(f"Loading artist index from {index_path}...")
        with open(index_path, 'r', encoding='utf-8') as f:
            artist_index = json.load(f)
    else:
        print(f"Building artist index from {enhanced_json_dir}...")
        artist_index = enhancer.build_artist_index(enhanced_json_dir)
    
    # Search
    results = enhancer.search_artists(query, artist_index, limit=limit)
    
    if not results:
        print("No artists found.")
        return
    
    print(f"Found {len(results)} artists:\n")
    for i, (artist, score, songs) in enumerate(results, 1):
        print(f"{i}. {artist} ({score:.1%} match)")
        print(f"   {len(songs)} songs")
        print(f"   Examples: {', '.join([s['title'] for s in songs[:3]])}")
        print()


def search_songs_example(enhanced_json_dir, query, limit=10):
    """Example: Search for songs."""
    print(f"\n{'='*60}")
    print(f"Searching for songs: '{query}'")
    print(f"{'='*60}\n")
    
    enhancer = MetadataEnhancer()
    
    # Build or load song index
    index_path = Path(enhanced_json_dir).parent / "indexes" / "song_index.json"
    
    if index_path.exists():
        print(f"Loading song index from {index_path}...")
        with open(index_path, 'r', encoding='utf-8') as f:
            song_index = json.load(f)
    else:
        print(f"Building song index from {enhanced_json_dir}...")
        song_index = enhancer.build_song_index(enhanced_json_dir)
    
    # Search
    results = enhancer.search_songs(query, song_index, limit=limit)
    
    if not results:
        print("No songs found.")
        return
    
    print(f"Found {len(results)} songs:\n")
    for i, (title, score, versions) in enumerate(results, 1):
        print(f"{i}. {title} ({score:.1%} match)")
        print(f"   {len(versions)} versions")
        artists = set(v['artist'] for v in versions if v.get('artist'))
        if artists:
            print(f"   Artists: {', '.join(list(artists)[:5])}")
        print()


def filter_example(enhanced_json_dir, genre=None, dataset=None, min_chords=0):
    """Example: Filter songs by criteria."""
    print(f"\n{'='*60}")
    print("Filtering songs by criteria:")
    if genre:
        print(f"  Genre: {genre}")
    if dataset:
        print(f"  Dataset: {dataset}")
    if min_chords > 0:
        print(f"  Minimum chords: {min_chords}")
    print(f"{'='*60}\n")
    
    results = search_json_files(
        enhanced_json_dir,
        genre=genre,
        dataset=dataset,
        min_chords=min_chords
    )
    
    print(f"Found {len(results)} songs matching criteria\n")
    
    # Show examples
    for i, song in enumerate(results[:10], 1):
        metadata = song.get('metadata', {})
        title = metadata.get('title', 'Unknown')
        artist = metadata.get('artist', 'Unknown')
        chords_count = len(song.get('chords', []))
        
        print(f"{i}. {title} - {artist}")
        print(f"   {chords_count} chords, Genre: {metadata.get('genre', 'N/A')}")
        print()


def show_duplicates_example(indexes_dir):
    """Example: Show duplicate songs."""
    print(f"\n{'='*60}")
    print("Duplicate Songs Report")
    print(f"{'='*60}\n")
    
    duplicates_path = Path(indexes_dir) / "duplicates.json"
    
    if not duplicates_path.exists():
        print(f"Duplicates file not found: {duplicates_path}")
        print("Run the enhancement pipeline first to generate duplicates.")
        return
    
    with open(duplicates_path, 'r', encoding='utf-8') as f:
        duplicates = json.load(f)
    
    # Filter to only groups with multiple files
    duplicate_groups = {
        k: v for k, v in duplicates.items() if len(v) > 1
    }
    
    print(f"Found {len(duplicate_groups)} duplicate groups\n")
    
    # Show top duplicates
    sorted_dups = sorted(
        duplicate_groups.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )[:20]
    
    for canonical_id, files in sorted_dups:
        print(f"{canonical_id}:")
        print(f"  {len(files)} versions:")
        for file_path in files[:5]:  # Show first 5
            print(f"    - {Path(file_path).name}")
        if len(files) > 5:
            print(f"    ... and {len(files) - 5} more")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Search and explore the enhanced ChoCo dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--enhanced-dir",
        type=str,
        required=True,
        help="Directory containing enhanced JSON files"
    )
    parser.add_argument(
        "--indexes-dir",
        type=str,
        help="Directory containing indexes (default: enhanced-dir/../indexes)"
    )
    parser.add_argument(
        "--search-artist",
        type=str,
        help="Search for an artist"
    )
    parser.add_argument(
        "--search-song",
        type=str,
        help="Search for a song"
    )
    parser.add_argument(
        "--filter-genre",
        type=str,
        help="Filter by genre"
    )
    parser.add_argument(
        "--filter-dataset",
        type=str,
        help="Filter by dataset"
    )
    parser.add_argument(
        "--min-chords",
        type=int,
        default=0,
        help="Minimum number of chords"
    )
    parser.add_argument(
        "--show-duplicates",
        action="store_true",
        help="Show duplicate songs report"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum results to show (default: 10)"
    )
    
    args = parser.parse_args()
    
    enhanced_dir = Path(args.enhanced_dir)
    if not enhanced_dir.exists():
        print(f"Error: Enhanced directory not found: {enhanced_dir}")
        sys.exit(1)
    
    indexes_dir = args.indexes_dir
    if not indexes_dir:
        indexes_dir = enhanced_dir.parent / "indexes"
    
    # Run examples based on arguments
    if args.search_artist:
        search_artists_example(str(enhanced_dir), args.search_artist, args.limit)
    
    if args.search_song:
        search_songs_example(str(enhanced_dir), args.search_song, args.limit)
    
    if args.filter_genre or args.filter_dataset or args.min_chords > 0:
        filter_example(
            str(enhanced_dir),
            genre=args.filter_genre,
            dataset=args.filter_dataset,
            min_chords=args.min_chords
        )
    
    if args.show_duplicates:
        show_duplicates_example(str(indexes_dir))
    
    # If no specific action, show help
    if not any([
        args.search_artist,
        args.search_song,
        args.filter_genre,
        args.filter_dataset,
        args.show_duplicates
    ]):
        parser.print_help()
        print("\nExamples:")
        print("  # Search for artist")
        print("  python choco_search_example.py --enhanced-dir ./enhanced --search-artist 'miles davis'")
        print()
        print("  # Search for song")
        print("  python choco_search_example.py --enhanced-dir ./enhanced --search-song 'autumn leaves'")
        print()
        print("  # Filter by genre")
        print("  python choco_search_example.py --enhanced-dir ./enhanced --filter-genre jazz")
        print()
        print("  # Show duplicates")
        print("  python choco_search_example.py --enhanced-dir ./enhanced --show-duplicates")


if __name__ == "__main__":
    main()
