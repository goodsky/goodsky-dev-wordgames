#!/usr/bin/env python3
"""
Generates new crossword game files.
"""
import argparse
import json
import random
import sys
from pathlib import Path


def load_json_file(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def load_crossword_shape(shapes_file, shape_name=None, verbose=False):
    """
    Loads template crossword shape grid from the available shapes.
    Identifies where the word slots are located to fill in the puzzle.
    ["grid"]: 2D array with 0=black cell, 1=white cell
    ["slots"]: list of word slots with row, col, length, direction
    """
    shapes = load_json_file(shapes_file)
    if verbose:
        print(f"Loaded {len(shapes)} crossword shapes from {shapes_file}")

    shape = None
    if shape_name:
        candidate_shapes = [s for s in shapes if s['name'] == shape_name]
        if candidate_shapes:
            shape = candidate_shapes[0]
            print(f"✓ Loaded crossword shape '{shape_name}'")
        else:
            print(f"✗ No crossword shape found with name '{shape_name}'", file=sys.stderr)

    if not shape:
        shape = random.choice(shapes)
        print(f"✓ Loaded random crossword shape '{shape['name']}'")

    if verbose:
        for row in shape['grid']:
            print(''.join(['#' if cell == 0 else '.' for cell in row]))

    word_slots = find_crossword_word_slots(shape, verbose=verbose)
    shape['slots'] = word_slots
    return shape


def find_crossword_word_slots(crossword_shape, verbose=False):
    slots = []
    grid = crossword_shape['grid']
    rows = len(grid)
    cols = len(grid[0])

    # Find horizontal slots
    for r in range(rows):
        c = 0
        while c < cols:
            if grid[r][c] == 1:
                start_c = c
                while c < cols and grid[r][c] == 1:
                    c += 1
                length = c - start_c
                if length > 1:
                    slots.append({'row': r, 'col': start_c, 'length': length, 'direction': 'across'})
            else:
                c += 1

    # Find vertical slots
    for c in range(cols):
        r = 0
        while r < rows:
            if grid[r][c] == 1:
                start_r = r
                while r < rows and grid[r][c] == 1:
                    r += 1
                length = r - start_r
                if length > 1:
                    slots.append({'row': start_r, 'col': c, 'length': length, 'direction': 'down'})
            else:
                r += 1

    print(f"Found {len(slots)} word slots in the crossword shape.")
    if verbose:
        for slot in slots:
            print(f"  - {slot['direction'].capitalize()} slot at (row={slot['row']}, col={slot['col']}) length={slot['length']}")
    return slots


def build_word_wildcard_variants(word):
    wildcards = []
    length = len(word)
    for mask in range(1 << length):
        variant = list(word)
        for i in range(length):
            if (mask >> i) & 1:
                variant[i] = '?'
        wildcards.append(''.join(variant))
    return wildcards


def build_word_index(words, verbose=False):
    """
    Builds an index of all possible matches for different wildcard patterns.
    e.g. C?T would match CAT, COT, CUT, etc.
    """
    word_index = {}
    for word in words:
        for wildcard in build_word_wildcard_variants(word):
            if wildcard not in word_index:
                word_index[wildcard] = set()
            word_index[wildcard].add(word)
    print(f"Built word index for {len(words)} words with {len(word_index)} wildcard indices.")
    return word_index


def generate_game(shape, clues, word_index):
    slots = shape['slots']
    # Todo: implement


def main(clues_file, shapes_file, shape_name=None, verbose=False):
    crossword_shape = load_crossword_shape(shapes_file, shape_name=shape_name, verbose=verbose)

    clues = load_json_file(clues_file)
    word_index = build_word_index(clues.keys(), verbose=verbose)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate crossword game files.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("-s", "--shape", type=str, help="Specify the name of the crossword shape to use")
    args = parser.parse_args()

    data_directory = Path(__file__).parent / "data"
    clues_file = data_directory / "crossword_clues.json"
    shapes_file = data_directory / "crossword_shapes.json"

    main(clues_file, shapes_file, shape_name=args.shape, verbose=args.verbose)
