#!/usr/bin/env python3
"""
Extracts answer/clue pairs from the next unjudged .new.json file into a ratings file.
Creates one .ratings.tsv file for the next game that needs judging.
"""

import json
import glob
import os
import csv


def main():
    new_files = sorted(glob.glob("*.new.json"))

    if not new_files:
        print("No .new.json files found.")
        return

    # Find the first unjudged file
    for filepath in new_files:
        # Skip if already judged
        output_filepath = filepath.replace(".new.json", ".json")
        if os.path.exists(output_filepath):
            continue

        # Skip if ratings file already exists
        # e.g., game_1.new.json -> game_1.ratings.tsv
        base_name = filepath.replace(".new.json", "")
        ratings_filepath = f"{base_name}.ratings.tsv"
        if os.path.exists(ratings_filepath):
            continue

        # Process this file
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        rows = []
        for entry in data.get("clues", []):
            answer = entry["answer"]
            clue_texts = entry.get("clues", [])

            for clue_text in clue_texts:
                rows.append({
                    "CLUE": clue_text,
                    "ANSWER": answer,
                    "DIFFICULTY": ""  # To be filled: EASY, HARD, or REJECT
                })

        # Write individual ratings TSV file
        with open(ratings_filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["CLUE", "ANSWER", "DIFFICULTY"], delimiter='\t')
            writer.writeheader()
            writer.writerows(rows)

        print(f"Created {ratings_filepath} ({len(rows)} clues)")
        print("\nFill in the 'DIFFICULTY' column for each clue with: EASY, HARD, or REJECT")
        print(f"(Optional) Edit clues using: `./edit_clues.py --add-clue {ratings_filepath} <Answer> <Clue> <Difficulty>`")
        print(f"Then run: `./judge_commit.py {ratings_filepath}`")
        return

    print("\nNo new crossword puzzles to judge. You are done!")


if __name__ == "__main__":
    main()
