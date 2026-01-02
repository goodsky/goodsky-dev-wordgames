#!/usr/bin/env python3
"""
Pretty prints a crossword game file showing the solved puzzle and clues.
"""
import argparse
import json
import sys
from pathlib import Path
from generate_games import fill_puzzle_grid_with_answers


def print_solved_puzzle(puzzle_grid):
    """Print the solved puzzle grid in a readable format."""
    print("\n=== Solved Puzzle ===")
    for row in puzzle_grid:
        print('  ' + ' '.join([cell if cell != '' else '.' for cell in row]))
    print()


def print_clues(clues):
    """Print all clues organized by direction."""
    across_clues = [c for c in clues if c['direction'] == 'across']
    down_clues = [c for c in clues if c['direction'] == 'down']
    
    if across_clues:
        print("=== Across ===")
        for clue in across_clues:
            print(f"  {clue['index']}. {clue['answer'].upper()} ({clue['length']} letters)")
            for i, clue_text in enumerate(clue['clues'][:3], 1):  # Show first 3 clues
                print(f"      {i}) {clue_text}")
        print()
    
    if down_clues:
        print("=== Down ===")
        for clue in down_clues:
            print(f"  {clue['index']}. {clue['answer'].upper()} ({clue['length']} letters)")
            for i, clue_text in enumerate(clue['clues'][:3], 1):  # Show first 3 clues
                print(f"      {i}) {clue_text}")
        print()


def main(game_file):
    """Load and print a crossword game file."""
    game_path = Path(game_file)
    
    # If path doesn't exist and it's not absolute, try the default server directory
    if not game_path.exists() and not game_path.is_absolute():
        # Try appending .json if not present
        if not game_file.endswith('.json'):
            game_file = f"{game_file}.json"
        
        # Check in the default server data directory
        default_dir = Path(__file__).parent / ".." / ".." / "server" / "data" / "crosswords"
        game_path = default_dir / game_file
    
    if not game_path.exists():
        print(f"✗ Game file not found: {game_file}", file=sys.stderr)
        print(f"  Searched in: {game_path.absolute()}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(game_path, 'r', encoding='utf-8') as f:
            game = json.load(f)
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in game file: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"Crossword Game: {game_path.name}")
    print(f"{'='*60}")
    
    # Fill and print the solved puzzle
    puzzle_grid = game['shape']
    clues = game['clues']
    
    # Convert clues to the format expected by fill_puzzle_grid_with_answers
    filled_slots = []
    for clue in clues:
        filled_slots.append({
            'row': clue['row'],
            'col': clue['col'],
            'length': clue['length'],
            'direction': clue['direction'],
            'answer': clue['answer']
        })
    
    solved_puzzle = fill_puzzle_grid_with_answers(puzzle_grid, filled_slots)
    print_solved_puzzle(solved_puzzle)
    
    # Print clues
    print_clues(clues)
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pretty print a crossword game file.")
    parser.add_argument("game_file", type=str, help="Path to the game JSON file")
    args = parser.parse_args()
    
    main(args.game_file)
