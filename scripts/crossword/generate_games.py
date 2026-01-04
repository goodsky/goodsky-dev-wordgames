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


def get_slot_pattern(slot, puzzle):
    """Get the current pattern for a slot based on filled cells in the puzzle."""
    length = slot['length']
    row, col = slot['row'], slot['col']
    pattern = []
    for i in range(length):
        if slot['direction'] == 'across':
            cell = puzzle[row][col + i]
        else:
            cell = puzzle[row + i][col]
        pattern.append(cell if cell != '' else '?')
    return ''.join(pattern)


def get_slot_cells(slot):
    """Get list of (row, col) cells that a slot occupies."""
    cells = []
    for i in range(slot['length']):
        if slot['direction'] == 'across':
            cells.append((slot['row'], slot['col'] + i))
        else:
            cells.append((slot['row'] + i, slot['col']))
    return cells


def find_intersecting_slots(slot, empty_slots):
    """Find all empty slots that intersect with the given slot."""
    slot_cells = set(get_slot_cells(slot))
    intersecting = []
    for other_slot in empty_slots:
        if other_slot == slot:
            continue
        other_cells = get_slot_cells(other_slot)
        for idx, cell in enumerate(other_cells):
            if cell in slot_cells:
                intersecting.append((other_slot, idx, cell))
                break  # Each slot can only intersect once
    return intersecting


def calculate_word_heuristic(word, slot, empty_slots, puzzle, word_index):
    """
    Calculate a heuristic score for placing a word in a slot.
    The score is the sum of possible words remaining for each intersecting empty slot.
    If any intersecting slot is left with 0 options, subtract 1,000,000.
    """
    intersecting = find_intersecting_slots(slot, empty_slots)
    if not intersecting:
        return 0  # No intersections, neutral score
    
    total_score = 0
    slot_cells = get_slot_cells(slot)
    
    for other_slot, other_idx, intersect_cell in intersecting:
        # Find which character from our word goes at the intersection
        word_idx = slot_cells.index(intersect_cell)
        new_char = word[word_idx]
        
        # Get current pattern for the other slot and update with the new character
        other_pattern = list(get_slot_pattern(other_slot, puzzle))
        other_pattern[other_idx] = new_char
        updated_pattern = ''.join(other_pattern)
        
        # Count possible words for this updated pattern
        possible_count = len(word_index.get(updated_pattern, []))
        
        if possible_count == 0:
            total_score -= 1_000_000
        else:
            total_score += possible_count
    
    return total_score


def pick_random_valid_word(slot, puzzle, word_index, empty_slots=None, used_words=None, top_n=10, verbose=False):
    """
    Pick a random word from the top N words with highest heuristic scores.
    If empty_slots is None, falls back to pure random selection.
    """
    word_pattern = get_slot_pattern(slot, puzzle)
    possible_words = word_index.get(word_pattern, [])
    if not possible_words:
        if verbose:
            print(f"  [heuristic] No candidates for pattern '{word_pattern}'")
        return None, word_pattern

    possible_words = list(possible_words)
    
    # Filter out words that have already been used in this puzzle
    if used_words:
        possible_words = [w for w in possible_words if w not in used_words]
        if not possible_words:
            if verbose:
                print(f"  [heuristic] All candidates for pattern '{word_pattern}' already used")
            return None, word_pattern
    
    # If no empty slots provided or only one word available, pick randomly
    if empty_slots is None or len(possible_words) == 1:
        chosen_word = random.choice(possible_words)
        return chosen_word, word_pattern
    
    # Calculate heuristic scores for all possible words
    scored_words = []
    for word in possible_words:
        score = calculate_word_heuristic(word, slot, empty_slots, puzzle, word_index)
        scored_words.append((word, score))
    
    # Sort by score descending
    scored_words.sort(key=lambda x: x[1], reverse=True)
    
    # Filter to only positive scores, then take top N
    positive_scored = [(w, s) for w, s in scored_words if s >= 0]
    negative_count = len(scored_words) - len(positive_scored)
    
    if positive_scored:
        top_candidates = positive_scored[:top_n]
    else:
        # If no positive scores then we have no possible ways forward - backtrack
        if verbose:
            print(f"  [heuristic] All candidates negative for pattern '{word_pattern}' out of {len(possible_words)}")
        return None, word_pattern
    
    if verbose:
        best_score = scored_words[0][1] if scored_words else 0
        worst_score = scored_words[-1][1] if scored_words else 0
        print(f"  [heuristic] Selected from {len(top_candidates)} of {len(possible_words)} candidates, filtered out {negative_count} negative options (scores: {best_score} to {worst_score})")
    
    # Pick randomly from top candidates
    chosen_word = random.choice([w for w, s in top_candidates])
    return chosen_word, word_pattern


def try_fill_slots(empty_slots, filled_slots, puzzle_grid, word_index, level_retries, metrics, top_n=10, verbose=False):
    if not empty_slots:
        return filled_slots
    
    puzzle_wip = fill_puzzle_grid_with_answers(puzzle_grid, filled_slots)
    used_words = set(slot['answer'] for slot in filled_slots)

    retry_count = 0
    while retry_count <= level_retries:
        slot = random.choice(empty_slots)
        word, pattern = pick_random_valid_word(slot, puzzle_wip, word_index, empty_slots=empty_slots, used_words=used_words, top_n=top_n, verbose=verbose)

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
                max(0, level_retries - 1), # NB: lower retries to limit backtracking in deeper levels
                metrics,
                top_n=top_n,
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


def generate_game(shape, clues_index, word_index, top_n=10, verbose=False):
    puzzle_grid = shape['grid']
    puzzle_slots = find_crossword_word_slots(shape, verbose=verbose)
    
    metrics = {
        'retry_count': 0,
        'words_found': 0,
        'backtracks': 0,
    }

    print("Building crossword with backtracking...")
    filled_slots = try_fill_slots(puzzle_slots, [], puzzle_grid, word_index, level_retries=5, metrics=metrics, top_n=top_n, verbose=verbose)

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
        'clues': clues,
        'shape': puzzle_grid,
    }


def main(clues_file, shapes_file, output_dir, games_to_generate=1, shape_name=None, top_n=100, verbose=False):
    print("Building clues and word indices...")
    clues_index = load_json_file(clues_file)
    word_index = build_word_index(clues_index.keys(), verbose=verbose)

    for i in range(games_to_generate):
        print(f"\nGenerating crossword game {i + 1}/{games_to_generate}...")
        crossword_shape = load_crossword_shape(shapes_file, shape_name=shape_name, verbose=verbose)

        start_time = time.time()
        game = generate_game(crossword_shape, clues_index, word_index, top_n=top_n, verbose=verbose)
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
        # We will generate files with the file suffix .new.json to indicate they are newly generated
        # But we still want to keep counting up from existing files without .new
        candidate_file = output_path / f"{base_name}_{index}.new{extension}"
        existing_files = list(output_path.glob(f"{base_name}_{index}*{extension}"))
        if not existing_files:
            return candidate_file
        index += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate crossword game files.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("-n", "--number", type=int, default=1, help="Number of crossword games to generate")
    parser.add_argument("-o", "--output", type=str, help="Output directory for generated games")
    parser.add_argument("-s", "--shape", type=str, help="Specify the name of the crossword shape to use")
    parser.add_argument("-t", "--top", type=int, default=100, help="Number of top-scored words to randomly select from (default: 10)")
    args = parser.parse_args()

    data_directory = Path(__file__).parent / "data"
    clues_file = data_directory / "crossword_clues.json"
    shapes_file = data_directory / "crossword_shapes.json"

    default_output_dir = Path(__file__).parent / ".." / ".." / "server" / "data" / "crossword"
    output_dir = args.output if args.output else default_output_dir

    main(clues_file, shapes_file, output_dir, games_to_generate=args.number, shape_name=args.shape, top_n=args.top, verbose=args.verbose)
