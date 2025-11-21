"""CLI entry point for ExtractAll."""

import os
import sys
from . import ArchiveExtractor


def main():
    """Main CLI function."""
    if len(sys.argv) != 2:
        print("Usage: extractall <input_directory>")
        print("       python -m extractall <input_directory>")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    if not os.path.exists(input_dir):
        print(f"Error: Directory not found: {input_dir}")
        sys.exit(1)
    
    extractor = ArchiveExtractor(input_dir)
    extractor.run()


if __name__ == "__main__":
    main()
