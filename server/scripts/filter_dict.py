#!/usr/bin/env python3
"""
Filter dictionary by removing words from a filter list.
Usage: python filter_dict.py <dict_file> <filter_file> [--whatif]

The dict_file will be read and overwritten with the filtered version.
Use --whatif for a dry run that shows what would be removed without modifying the file.
"""

import sys

def load_filter_words(filter_file):
    """Load words to filter from a file."""
    try:
        with open(filter_file, 'r') as f:
            return set(line.strip().lower() for line in f if line.strip() and not line.startswith('#'))
    except FileNotFoundError:
        print(f"Error: Filter file '{filter_file}' not found.")
        sys.exit(1)

def filter_dictionary(dict_file, filter_file, whatif=False):
    """Filter dictionary file using a filter list and overwrite."""
    # Load filter words
    filter_words = load_filter_words(filter_file)
    print(f"Loaded {len(filter_words)} words from filter list")

    if whatif:
        print("Running in WHATIF mode - no changes will be made\n")

    # Load dictionary
    with open(dict_file, 'r') as f:
        words = [line.strip().lower() for line in f if line.strip()]

    original_count = len(words)

    # Filter words
    kept_words = []
    removed_words = []

    for word in words:
        if word in filter_words:
            removed_words.append(word)
        else:
            kept_words.append(word)

    # Remove duplicates and sort
    kept_words = sorted(set(kept_words))

    # Overwrite dictionary file (unless in whatif mode)
    if not whatif:
        with open(dict_file, 'w') as f:
            for word in kept_words:
                f.write(word.upper() + '\n')

    # Print report
    print(f"\n=== Dictionary Filtering Report ===")
    print(f"Original word count: {original_count}")
    print(f"Words kept: {len(kept_words)}")
    print(f"Words removed: {len(removed_words)}")

    if whatif:
        print(f"\nWHATIF: Dictionary would be updated: {dict_file}")
    else:
        print(f"\nDictionary updated: {dict_file}")

    if removed_words:
        print(f"\n=== Removed Words ===")
        for word in sorted(removed_words):
            print(word)

if __name__ == '__main__':
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python filter_dict.py <dict_file> <filter_file> [--whatif]")
        print("\nExample:")
        print("  python filter_dict.py dict.txt profanity.txt")
        print("  python filter_dict.py dict.txt profanity.txt --whatif")
        sys.exit(1)

    dict_file = sys.argv[1]
    filter_file = sys.argv[2]
    whatif = len(sys.argv) == 4 and sys.argv[3] == '--whatif'

    filter_dictionary(dict_file, filter_file, whatif)
