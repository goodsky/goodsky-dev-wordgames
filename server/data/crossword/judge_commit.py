#!/usr/bin/env python3
"""
Commits rated clues from game_N.ratings.tsv files back to the game files.
Reads each ratings file, validates all ratings are filled, and writes final .json files.
"""

import json
import os
import glob
import csv
import sys
from collections import defaultdict


def calculate_difficulty(clue_entries):
    """
    Calculate overall puzzle difficulty based on clue ratings.

    Rules:
    - EASY: Every answer has at least one EASY clue
    - HARD: Every answer has at least one non-REJECT clue, but not all have EASY
    - REJECT: Any answer has only REJECT clues (no clues or hardClues)
    """
    # Check if any answer has no clues at all (neither easy nor hard)
    for entry in clue_entries:
        easy_clues = entry.get("clues", [])
        hard_clues = entry.get("hardClues", [])
        if not easy_clues and not hard_clues:
            return "REJECT"

    # Check if all answers have at least one EASY clue
    all_have_easy = all(
        len(entry.get("clues", [])) > 0
        for entry in clue_entries
    )

    if all_have_easy:
        return "EASY"
    else:
        return "HARD"


def process_ratings_file(ratings_filepath):
    """Process a single ratings file and create the final game file."""
    # Read TSV file
    rated_clues = []
    with open(ratings_filepath, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rated_clues = list(reader)

    # Derive source file from ratings filename
    # e.g., game_1.ratings.tsv -> game_1.new.json
    base_name = ratings_filepath.replace(".ratings.tsv", "")
    source_file = f"{base_name}.new.json"

    # Check all ratings are filled
    missing = [c for c in rated_clues if not c["DIFFICULTY"].strip()]
    if missing:
        print(f"Error: {ratings_filepath} has {len(missing)} unrated clues. Skipping.")
        for m in missing[:3]:
            print(f"  - {m['ANSWER']}: {m['CLUE']}")
        if len(missing) > 3:
            print(f"  ... and {len(missing) - 3} more")
        return False

    # Load original game file
    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Build a lookup from (answer, clue_text) -> rating
    rating_lookup = {(c["ANSWER"], c["CLUE"]): c["DIFFICULTY"] for c in rated_clues}

    # Apply ratings to the original structure
    for entry in data.get("clues", []):
        answer = entry["answer"]
        clue_texts = entry.get("clues", [])
        easy_clues = []
        hard_clues = []

        for clue_text in clue_texts:
            rating = rating_lookup.get((answer, clue_text), "REJECT")
            if rating == "EASY":
                easy_clues.append(clue_text)
            elif rating == "HARD":
                hard_clues.append(clue_text)
            # REJECT clues are omitted

        entry["clues"] = easy_clues
        entry["hardClues"] = hard_clues

    # Calculate overall difficulty
    difficulty = calculate_difficulty(data["clues"])

    # Add difficulty at top level
    data = {"difficulty": difficulty, **data}

    # Write output file
    output_filepath = source_file.replace(".new.json", ".json")
    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Wrote {output_filepath} | Difficulty: {difficulty}")

    # Delete the ratings file and source file after successful commit
    os.remove(ratings_filepath)
    print(f"Deleted {ratings_filepath}")
    
    os.remove(source_file)
    print(f"Deleted {source_file}")

    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 judge_commit.py <ratings_file.tsv>")
        print("Example: python3 judge_commit.py game_1.ratings.tsv")
        return

    ratings_filepath = sys.argv[1]

    if not os.path.exists(ratings_filepath):
        print(f"Error: File not found: {ratings_filepath}")
        return

    if not ratings_filepath.endswith(".ratings.tsv"):
        print(f"Error: File must be a .ratings.tsv file")
        return

    if process_ratings_file(ratings_filepath):
        print("\nDone! Successfully committed game.")
    else:
        print("\nFailed to commit game. Please fix the errors and try again.")


if __name__ == "__main__":
    main()
