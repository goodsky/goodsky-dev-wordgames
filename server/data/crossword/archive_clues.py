#!/usr/bin/env python3
"""
Archives old crossword puzzles to keep the active directory manageable.
Moves the oldest puzzles (by timestamp) to an _archive folder.
"""

import json
import os
import sys
import glob
import shutil


def load_game_with_timestamp(filepath):
    """Load a game file and return its data with filepath."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {
        'filepath': filepath,
        'difficulty': data.get('difficulty', 'UNKNOWN'),
        'timestamp': data.get('timestamp', '1970-01-01T00:00:00'),
        'data': data
    }


def archive_puzzles(keep_easy, keep_hard):
    """Archive puzzles exceeding the keep limits."""
    # Find all game files (excluding .new.json)
    game_files = [f for f in glob.glob('game_*.json') if '.new.json' not in f]

    if not game_files:
        print("No game files found.")
        return

    # Load all games
    games = [load_game_with_timestamp(f) for f in game_files]

    # Separate by difficulty
    easy_games = [g for g in games if g['difficulty'] == 'EASY']
    hard_games = [g for g in games if g['difficulty'] == 'HARD']
    other_games = [g for g in games if g['difficulty'] not in ('EASY', 'HARD')]

    # Sort by timestamp (oldest first)
    easy_games.sort(key=lambda g: g['timestamp'])
    hard_games.sort(key=lambda g: g['timestamp'])

    # Determine which to archive (oldest ones beyond the keep limit)
    easy_to_archive = easy_games[:-keep_easy] if len(easy_games) > keep_easy else []
    hard_to_archive = hard_games[:-keep_hard] if len(hard_games) > keep_hard else []

    to_archive = easy_to_archive + hard_to_archive

    if not to_archive:
        print(f"Nothing to archive.")
        print(f"  EASY: {len(easy_games)} puzzles (keeping {keep_easy})")
        print(f"  HARD: {len(hard_games)} puzzles (keeping {keep_hard})")
        return

    # Create archive directory if needed
    archive_dir = '_archive'
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        print(f"Created {archive_dir}/ directory")

    # Move files to archive
    for game in to_archive:
        src = game['filepath']
        dst = os.path.join(archive_dir, os.path.basename(src))
        shutil.move(src, dst)
        print(f"Archived {src} -> {dst} ({game['difficulty']}, {game['timestamp']})")

    print(f"\nArchived {len(to_archive)} puzzle(s):")
    print(f"  EASY: {len(easy_to_archive)} archived, {len(easy_games) - len(easy_to_archive)} remaining")
    print(f"  HARD: {len(hard_to_archive)} archived, {len(hard_games) - len(hard_to_archive)} remaining")
    if other_games:
        print(f"  OTHER: {len(other_games)} puzzles (not archived)")


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 archive_clues.py <keep_easy> <keep_hard>")
        print("Example: python3 archive_clues.py 10 5")
        print("  Keeps the 10 newest EASY puzzles and 5 newest HARD puzzles")
        return

    try:
        keep_easy = int(sys.argv[1])
        keep_hard = int(sys.argv[2])
    except ValueError:
        print("Error: Both arguments must be integers")
        return

    if keep_easy < 0 or keep_hard < 0:
        print("Error: Keep counts must be non-negative")
        return

    archive_puzzles(keep_easy, keep_hard)


if __name__ == "__main__":
    main()
