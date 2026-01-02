#!/usr/bin/env python3
"""
Generates new crossword game files.
"""
import argparse
import json
import random
import sys
import time
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

    if verbose:
        print(f"Found {len(slots)} clues to fill in the crossword shape.")
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


def pick_random_clues_for_word(word, clues, max_clues=10):
    word_entry = clues.get(word, [])
    if not word_entry:
        return []
    word_clues = word_entry['clues']
    return random.sample(word_clues, min(len(word_clues), max_clues))


def format_crossword_clues(filled_slots, clues_index):
    """
    Format the game JSON structure with the final crossword shape with clue indices and the clue + answer pairs.
    """
    # Sort slots by row first, then by column (top to bottom, left to right)
    filled_slots.sort(key=lambda s: (s['row'], s['col']))

    clue_index = 0
    last_row, last_col = -1, -1
    formatted_clues = []
    
    for slot in filled_slots:
        row, col = slot['row'], slot['col']
        if not (row == last_row and col == last_col):
            clue_index += 1
            last_row, last_col = row, col

        clues = pick_random_clues_for_word(slot['answer'], clues_index)
        if not clues:
            print(f"✗ No clues found for word '{slot['answer']}'", file=sys.stderr)
            raise ValueError(f"No clues for word '{slot['answer']}'")

        formatted_clues.append({
            'index': clue_index,
            'direction': slot['direction'],
            'row': row,
            'col': col,
            'length': slot['length'],
            'answer': slot['answer'],
            'clues': clues,
        })

    return formatted_clues


def fill_puzzle_grid_with_answers(puzzle_grid, filled_slots):
    puzzle = [ [ '' if cell == 1 else '#' for cell in row ] for row in puzzle_grid ]

    def safe_set_cell(r, c, val):
        if puzzle[r][c] == '' or puzzle[r][c] == val:
            puzzle[r][c] = val
        else:
            raise ValueError(f"Conflict in filling puzzle grid at ({r}, {c}): existing '{puzzle[r][c]}', new '{val}'")

    for slot in filled_slots:
        answer = slot['answer']
        row, col = slot['row'], slot['col']
        for i in range(slot['length']):
            if slot['direction'] == 'across':
                safe_set_cell(row, col + i, answer[i])
            else:
                safe_set_cell(row + i, col, answer[i])

    return puzzle


def pick_random_valid_word(slot, puzzle, word_index):
    length = slot['length']
    row, col = slot['row'], slot['col']
    pattern = []
    for i in range(length):
        if slot['direction'] == 'across':
            cell = puzzle[row][col + i]
        else:
            cell = puzzle[row + i][col]
        pattern.append(cell if cell != '' else '?')
    
    word_pattern = ''.join(pattern)
    possible_words = word_index.get(word_pattern, [])
    if not possible_words:
        return None, word_pattern

    chosen_word = random.choice(list(possible_words))
    return chosen_word, word_pattern


def try_fill_slots(empty_slots, filled_slots, puzzle_grid, word_index, level_retries, metrics, verbose=False):
    if not empty_slots:
        return filled_slots
    
    puzzle_wip = fill_puzzle_grid_with_answers(puzzle_grid, filled_slots)

    retry_count = 0
    while retry_count <= level_retries:
        slot = random.choice(empty_slots)
        word, pattern = pick_random_valid_word(slot, puzzle_wip, word_index)

        if word:
            if verbose:
                print(f"+ '{word}' matches '{pattern}' (dir={slot['direction']}, row={slot['row']}, col={slot['col']})")
            metrics['words_found'] += 1

            new_empty_slots = [s for s in empty_slots if s != slot]
            new_filled_slots = filled_slots + [ { **slot, 'answer': word } ]

            valid_solution = try_fill_slots(
                new_empty_slots,
                new_filled_slots,
                puzzle_grid,
                word_index,
                level_retries / 2, # NB: halve retries to limit backtracking in deeper levels
                metrics,
                verbose=verbose) 
        else:
            if verbose:
                print(f"- No match for '{pattern}' (dir={slot['direction']}, row={slot['row']}, col={slot['col']})")
                print(f"=== Intermediate puzzle state ===")
                for row in puzzle_wip:
                    print(''.join([cell if cell != '' else '.' for cell in row]))
            metrics['backtracks'] += 1
            valid_solution = None

        if valid_solution:
            return valid_solution

        retry_count += 1
        metrics['retry_count'] += 1
    return None


def generate_game(shape, clues_index, word_index, verbose=False):
    puzzle_grid = shape['grid']
    puzzle_slots = find_crossword_word_slots(shape, verbose=verbose)
    
    metrics = {
        'retry_count': 0,
        'words_found': 0,
        'backtracks': 0,
    }

    print("Building crossword with backtracking...")
    filled_slots = try_fill_slots(puzzle_slots, [], puzzle_grid, word_index, level_retries=64, metrics=metrics, verbose=verbose)

    if not filled_slots:
        print(f"Diagnostics:\n{json.dumps(metrics, indent=2)}")
        return None

    if verbose:
        print(f"Diagnostics:\n{json.dumps(metrics, indent=2)}")

    print(f"Filled puzzle with {len(filled_slots)} words after {metrics['backtracks']} backtracks.")
    if verbose:
        print("Final puzzle:")
        final_puzzle = fill_puzzle_grid_with_answers(puzzle_grid, filled_slots)
        for row in final_puzzle:
            print(''.join([cell if cell != '' else '.' for cell in row]))

    clues = format_crossword_clues(filled_slots, clues_index)

    return {
        'shape': puzzle_grid,
        'clues': clues
    }


def main(clues_file, shapes_file, output_dir, games_to_generate=1, shape_name=None, verbose=False):
    print("Building clues and word indices...")
    clues_index = load_json_file(clues_file)
    word_index = build_word_index(clues_index.keys(), verbose=verbose)

    crossword_shape = load_crossword_shape(shapes_file, shape_name=shape_name, verbose=verbose)

    for i in range(games_to_generate):
        print(f"\nGenerating crossword game {i + 1}/{games_to_generate}...")

        start_time = time.time()
        game = generate_game(crossword_shape, clues_index, word_index, verbose=verbose)
        elapsed_ms = int((time.time() - start_time) * 1000)

        if game:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            game_file = get_next_available_file(output_path, base_name="game", extension=".json")
            with open(game_file, 'w', encoding='utf-8') as f:
                json.dump(game, f, indent=2)
                
            relative_path = Path(game_file).relative_to(Path(__file__).parent)
            print(f"✓ Generated crossword game file: {relative_path} ({elapsed_ms}ms)")
        else:
            print(f"✗ Failed to generate crossword game! ({elapsed_ms}ms)", file=sys.stderr)


def get_next_available_file(output_dir, base_name="game", extension=".json"):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    index = 1
    while True:
        candidate_file = output_path / f"{base_name}_{index}{extension}"
        if not candidate_file.exists():
            return candidate_file
        index += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate crossword game files.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("-n", "--number", type=int, default=1, help="Number of crossword games to generate")
    parser.add_argument("-o", "--output", type=str, help="Output directory for generated games")
    parser.add_argument("-s", "--shape", type=str, help="Specify the name of the crossword shape to use")
    args = parser.parse_args()

    data_directory = Path(__file__).parent / "data"
    clues_file = data_directory / "crossword_clues.json"
    shapes_file = data_directory / "crossword_shapes.json"

    default_output_dir = Path(__file__).parent / ".." / ".." / "server" / "data" / "crosswords"
    output_dir = args.output if args.output else default_output_dir

    main(clues_file, shapes_file, output_dir, games_to_generate=args.number, shape_name=args.shape, verbose=args.verbose)
