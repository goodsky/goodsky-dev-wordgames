#!/usr/bin/env python3
"""
Filters and formats crossword clue files from the raw datasets, reducing the size on disk.
NOTE: This script is automatically called by init.py - you probably don't need to run it manually.
"""
import os
import json

def read_clues(file_path, min_length=None, max_length=None, min_year=None, max_year=None):
    """Read crossword clues from a text file and return as a list."""
    clues = []
    total_clues = 0
    invalid_clues = 0
    clues_too_old = 0
    clues_too_new = 0
    words_too_short = 0
    words_too_long = 0

    with open(file_path, 'r', encoding='utf-8') as f:
        # skip first line (header)
        next(f)

        for line in f:
            # read pubid	year	answer	clue split by tabs
            parts = line.strip().split('\t')
            total_clues += 1

            if len(parts) != 4:
                invalid_clues += 1
                continue
            
            pubid, year, answer, clue = parts[:4]
            year = int(year)
            if (min_year is not None and year < min_year):
                clues_too_old += 1
                continue

            if (max_year is not None and year > max_year):
                clues_too_new += 1
                continue

            answer_length = len(answer)
            if (min_length is not None and answer_length < min_length):
                words_too_short += 1
                continue

            if (max_length is not None and answer_length > max_length):
                words_too_long += 1
                continue

            clues.append({
                'pubid': pubid,
                'year': year,
                'answer': answer,
                'clue': clue
            })

    print("=== Clue file processing summary ===")
    print(f"Invalid clues skipped: {invalid_clues}")
    print(f"Invalid clue date: {clues_too_old + clues_too_new}")
    print(f"    - Too old: {clues_too_old}")
    print(f"    - Too new: {clues_too_new}")
    print(f"Invalid answer length: {words_too_short + words_too_long}")
    print(f"    - Too short: {words_too_short}")
    print(f"    - Too long: {words_too_long}")
    print(f"Total clues processed: {total_clues}")
    print(f"Valid clues retained: {len(clues)}")
    print()
    return clues


def read_wordlist(file_path):
    """Read words from a text file and return as a list."""
    words = []
    total_words = 0
    invalid_words = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(';')
            total_words += 1

            if len(parts) != 2:
                invalid_words += 1
                continue
            
            word, score = parts
            words.append({
                'word': word,
                'score': int(score)
            })

    print("=== Wordlist file processing summary ===")
    print(f"Invalid words skipped: {invalid_words}")
    print(f"Total words processed: {total_words}")
    print(f"Valid words retained: {len(words)}")
    print()
    return words

def format_crossword_clues_dictionary(wordlist_file, clues_file, output_file, parameters=None):
    """Merge clues for crossword answers - add with wordlist score for filtering."""

    total_answers = 0
    total_clues = 0
    clues_missing_count = 0
    score_missing_count = 0
    score_below_threshold_count = 0
    answers_with_digits = 0

    if parameters is None:
        parameters = {
            'min_length': 2,
            'max_length': 7,
            'min_year': 2009,
            'max_year': None,
            'min_score': 50
        }

    wordlist = read_wordlist(wordlist_file)
    clues = read_clues(clues_file, 
                       min_length=parameters['min_length'],
                       max_length=parameters['max_length'],
                       min_year=parameters['min_year'],
                       max_year=parameters['max_year'])

    clues_by_answer = {}
    for clue in clues:
        answer = clue['answer']
        if answer not in clues_by_answer:
            total_answers += 1
            clues_by_answer[answer] = { 'score': None, 'clues': set()}
        clues_by_answer[answer]['clues'].add(clue['clue'])
        total_clues += 1

    for word_entry in wordlist:
        answer = word_entry['word']
        score = word_entry['score']
        if answer in clues_by_answer:
            if score >= parameters['min_score']:
                clues_by_answer[answer]['score'] = score
            else:
                score_below_threshold_count += 1
                del clues_by_answer[answer]
        else:
            clues_missing_count += 1

    score_missing_words = [answer for answer, entry in clues_by_answer.items() if entry['score'] is None]
    for answer in score_missing_words:
        score_missing_count += 1
        del clues_by_answer[answer]
    
    words_with_numbers = [answer for answer in clues_by_answer.keys() if any(char.isdigit() for char in answer)]
    for answer in words_with_numbers:
        answers_with_digits += 1
        del clues_by_answer[answer]

    # Convert sets to lists for JSON serialization
    for answer in clues_by_answer:
        clues_by_answer[answer]['clues'] = list(clues_by_answer[answer]['clues'])

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clues_by_answer, f, indent=2, sort_keys=True)

    print(f"✓ Formatted {total_clues} crossword clues. Written to {output_file}")
    print(f"   - Clues missing for {clues_missing_count} words")
    print(f"   - Scores missing for {score_missing_count} words")
    print(f"   - {score_below_threshold_count} words below score threshold of {parameters['min_score']}")
    print(f"   - {answers_with_digits} words containing digits")
    print()
    print(f"Final valid answers retained: {len(clues_by_answer)} out of {total_answers} total answers")
    print(f"Final valid clues retained: {sum(len(entry['clues']) for entry in clues_by_answer.values())} out of {total_clues} total clues")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))

    wordlist_file = os.path.join(script_dir, 'data', 'spreadthewordlist_caps.txt')
    clues_file = os.path.join(script_dir, 'data', 'clues.tsv')
    crossword_clues_file =  os.path.join(script_dir, 'data', 'crossword_clues.json')

    format_crossword_clues_dictionary(wordlist_file, clues_file, crossword_clues_file)
