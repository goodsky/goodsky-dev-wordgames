#!/usr/bin/env python3
"""
Apply suggestions from suggestions.json to the dictionary.
Usage: python apply_suggestions.py [--whatif]

Reads suggestions.json, adds/removes words from dict.txt, and keeps the result alphabetically sorted.
Use --whatif for a dry run that shows what would change without modifying files.
"""

import json
import sys
import os

def load_suggestions(suggestions_file):
    """Load suggestions from JSON file."""
    try:
        with open(suggestions_file, 'r') as f:
            data = json.load(f)
            return {
                'add': set(word.upper() for word in data.get('add', [])),
                'remove': set(word.upper() for word in data.get('remove', []))
            }
    except FileNotFoundError:
        print(f"Error: Suggestions file '{suggestions_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{suggestions_file}': {e}")
        sys.exit(1)

def load_dictionary(dict_file):
    """Load dictionary words from file."""
    try:
        with open(dict_file, 'r') as f:
            return set(line.strip().upper() for line in f if line.strip())
    except FileNotFoundError:
        print(f"Error: Dictionary file '{dict_file}' not found.")
        sys.exit(1)

def apply_suggestions(dict_file, suggestions_file, whatif=False):
    """Apply suggestions to dictionary and save result."""
    # Load data
    suggestions = load_suggestions(suggestions_file)
    words = load_dictionary(dict_file)
    
    print(f"Loaded {len(words)} words from dictionary")
    print(f"Suggestions: {len(suggestions['add'])} to add, {len(suggestions['remove'])} to remove")
    
    if whatif:
        print("\nRunning in WHATIF mode - no changes will be made\n")
    
    # Track changes
    added = []
    removed = []
    already_exists = []
    not_found = []
    
    # Process additions
    for word in suggestions['add']:
        if word in words:
            already_exists.append(word)
        else:
            added.append(word)
            if not whatif:
                words.add(word)
    
    # Process removals
    for word in suggestions['remove']:
        if word in words:
            removed.append(word)
            if not whatif:
                words.remove(word)
        else:
            not_found.append(word)
    
    # Report changes
    if added:
        print(f"\nWords to ADD ({len(added)}):")
        for word in sorted(added):
            print(f"  + {word}")
    
    if already_exists:
        print(f"\nWords already in dictionary ({len(already_exists)}):")
        for word in sorted(already_exists):
            print(f"  = {word}")
    
    if removed:
        print(f"\nWords to REMOVE ({len(removed)}):")
        for word in sorted(removed):
            print(f"  - {word}")
    
    if not_found:
        print(f"\nWords not found in dictionary ({len(not_found)}):")
        for word in sorted(not_found):
            print(f"  ? {word}")
    
    # Save updated dictionary
    if not whatif:
        # Sort alphabetically and write back
        sorted_words = sorted(words)
        with open(dict_file, 'w') as f:
            for word in sorted_words:
                f.write(word + '\n')
        
        print(f"\n✓ Dictionary updated: {len(words)} words (was {len(words) - len(added) + len(removed)})")
        
        # Clear suggestions file
        with open(suggestions_file, 'w') as f:
            json.dump({"add": [], "remove": []}, f, indent=2)
        
        print(f"✓ Suggestions file cleared")
    else:
        print(f"\nWould result in {len(words) + len(added) - len(removed)} words (currently {len(words)})")
        print("Run without --whatif to apply changes")

if __name__ == '__main__':
    # Determine script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data', 'dictionary')
    
    dict_file = os.path.join(data_dir, 'dict.txt')
    suggestions_file = os.path.join(data_dir, 'suggestions.json')
    
    # Check for whatif flag
    whatif = '--whatif' in sys.argv
    
    print(f"Dictionary: {dict_file}")
    print(f"Suggestions: {suggestions_file}\n")
    
    apply_suggestions(dict_file, suggestions_file, whatif)
