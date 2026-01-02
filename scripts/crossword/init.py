#!/usr/bin/env python3
"""
Initialize the data files required for generating crossword game files.
"""
import sys
import urllib.request
import zipfile
import argparse
from pathlib import Path
from format_crossword_clues import format_crossword_clues_dictionary


def download_file(url, dest_path):
    """Download a file from URL to destination path."""
    print(f"Downloading {dest_path.name}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"✓ Successfully downloaded {dest_path.name}")
        return True
    except Exception as e:
        print(f"✗ Failed to download {dest_path.name}: {e}", file=sys.stderr)
        return False


def download_and_extract_zip(url, dest_path, extract_file):
    """Download a zip file and extract a specific file from it."""
    zip_path = dest_path.parent / "temp.zip"
    
    print(f"Downloading {url}...")
    try:
        urllib.request.urlretrieve(url, zip_path)
        print(f"✓ Successfully downloaded zip file")
    except Exception as e:
        print(f"✗ Failed to download zip: {e}", file=sys.stderr)
        return False
    
    print(f"Extracting {extract_file} from zip...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract the specific file
            with zip_ref.open(extract_file) as source:
                with open(dest_path, 'wb') as target:
                    target.write(source.read())
        print(f"✓ Successfully extracted {dest_path.name}")
    except Exception as e:
        print(f"✗ Failed to extract file: {e}", file=sys.stderr)
        return False
    finally:
        # Clean up zip file
        if zip_path.exists():
            zip_path.unlink()
    
    return True


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Initialize crossword data by downloading and processing files.')
    parser.add_argument('--no-cleanup', action='store_true', 
                        help='Keep intermediate wordlist and clues files after processing')
    args = parser.parse_args()
    
    # Setup paths
    script_dir = Path(__file__).parent
    data_dir = script_dir / "data"
    
    # Create data directory if it doesn't exist
    data_dir.mkdir(exist_ok=True)
    
    # Define files to download
    wordlist_url = "https://drive.google.com/uc?export=download&id=1fbGFn596W047OVOYdrKAxx3OVmwO8UyL"
    wordlist_path = data_dir / "spreadthewordlist_caps.txt"
    
    clues_zip_url = "https://xd.saul.pw/xd-clues.zip"
    clues_path = data_dir / "clues.tsv"
    clues_zip_internal_path = "xd/clues.tsv"
    
    crossword_clues_file = data_dir / "crossword_clues.json"
    
    print("=" * 60)
    print("Crossword Data Initialization")
    print("=" * 60)
    print()
    
    # Download word list
    if wordlist_path.exists():
        print(f"✓ {wordlist_path.name} already exists, skipping download")
        success1 = True
    else:
        success1 = download_file(wordlist_url, wordlist_path)
    print()
    
    # Download and extract clues
    if clues_path.exists():
        print(f"✓ {clues_path.name} already exists, skipping download")
        success2 = True
    else:
        success2 = download_and_extract_zip(clues_zip_url, clues_path, clues_zip_internal_path)
    print()
    
    # Summary
    print("=" * 60)
    if success1 and success2:
        print("✓ All files downloaded!")
        print()
        
        # Format the crossword clues dictionary
        print("=" * 60)
        print("Formatting crossword clues dictionary...")
        print("=" * 60)
        print()
        
        format_crossword_clues_dictionary(
            str(wordlist_path), 
            str(clues_path), 
            str(crossword_clues_file)
        )
        
        # Clean up intermediate files if --no-cleanup is not specified
        if not args.no_cleanup:
            print()
            print("Cleaning up intermediate files...")
            if wordlist_path.exists():
                wordlist_path.unlink()
                print(f"✓ Deleted {wordlist_path.name}")
            if clues_path.exists():
                clues_path.unlink()
                print(f"✓ Deleted {clues_path.name}")
        else:
            print()
            print(f"Keeping intermediate files (--no-cleanup specified):")
            print(f"  Word list: {wordlist_path}")
            print(f"  Clues:     {clues_path}")
        
        print()
        print("=" * 60)
        print("✓ Crossword data initialization complete!")
        print(f"  Output: {crossword_clues_file}")
    else:
        print("✗ Some downloads failed. Please check the errors above.")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
