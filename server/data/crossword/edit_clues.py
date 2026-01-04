#!/usr/bin/env python3
"""
Utility script for editing clue ratings files.

Modes:
- --find-hard: Find answers that have no EASY clues
- --add-clue: Add a new clue to a ratings file
"""

import csv
import sys
from collections import defaultdict


def find_hard_answers(ratings_filepath):
    """Find and print answers that have no EASY clues."""
    # Read TSV file
    with open(ratings_filepath, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    
    # Group clues by answer and check for EASY ratings
    answer_ratings = defaultdict(list)
    for row in rows:
        answer = row['ANSWER']
        difficulty = row['DIFFICULTY'].strip()
        answer_ratings[answer].append(difficulty)
    
    # Find answers with no EASY clues
    hard_answers = []
    for answer, ratings in answer_ratings.items():
        has_easy = any(r == 'EASY' for r in ratings)
        if not has_easy:
            hard_answers.append(answer)
    
    if hard_answers:
        print(f"Found {len(hard_answers)} answer(s) with no EASY clues:")
        for answer in sorted(hard_answers):
            print(f"  {answer}")
    else:
        print("All answers have at least one EASY clue!")


def add_clue(ratings_filepath, answer, clue, difficulty):
    """Add a new clue to the ratings file."""
    # Validate difficulty
    if difficulty not in ['EASY', 'HARD', 'REJECT']:
        print(f"Error: Difficulty must be EASY, HARD, or REJECT (got: {difficulty})")
        return
    
    # Append new row to TSV file
    with open(ratings_filepath, 'a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['CLUE', 'ANSWER', 'DIFFICULTY'], delimiter='\t')
        writer.writerow({
            'CLUE': clue,
            'ANSWER': answer,
            'DIFFICULTY': difficulty
        })
    
    print(f"Added clue for {answer}:")
    print(f"  Clue: {clue}")
    print(f"  Difficulty: {difficulty}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 edit_clues.py --find-hard <ratings.tsv>")
        print("  python3 edit_clues.py --add-clue <ratings.tsv> <Answer> <Clue> <Difficulty>")
        print()
        print("Examples:")
        print("  python3 edit_clues.py --find-hard game_1.ratings.tsv")
        print('  python3 edit_clues.py --add-clue game_1.ratings.tsv PYTHON "Snake language" EASY')
        return
    
    mode = sys.argv[1]
    
    if mode == '--find-hard':
        if len(sys.argv) != 3:
            print("Error: --find-hard requires a ratings file path")
            print("Usage: python3 edit_clues.py --find-hard <ratings.tsv>")
            return
        
        ratings_filepath = sys.argv[2]
        find_hard_answers(ratings_filepath)
    
    elif mode == '--add-clue':
        if len(sys.argv) != 6:
            print("Error: --add-clue requires 4 arguments: <ratings.tsv> <Answer> <Clue> <Difficulty>")
            print('Usage: python3 edit_clues.py --add-clue <ratings.tsv> <Answer> <Clue> <Difficulty>')
            return
        
        ratings_filepath = sys.argv[2]
        answer = sys.argv[3]
        clue = sys.argv[4]
        difficulty = sys.argv[5]
        add_clue(ratings_filepath, answer, clue, difficulty)
    
    else:
        print(f"Error: Unknown mode '{mode}'")
        print("Valid modes: --find-hard, --add-clue")


if __name__ == "__main__":
    main()
