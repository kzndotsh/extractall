"""CLI entry point for ExtractAll."""

import os
import sys
from . import ArchiveExtractor


def main():
    """Main CLI function."""
    if len(sys.argv) < 2:
        print("Usage: extractall <input_directory> [options]")
        print("Options:")
        print("  --aggressive     Enable aggressive mode (nested archives)")
        print("  --conservative   Enable conservative mode (basic extraction)")
        print("  --no-multipart   Disable multipart archive support")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    args = sys.argv[2:]
    
    # Parse mode
    mode = "standard"
    if "--aggressive" in args:
        mode = "aggressive"
    elif "--conservative" in args:
        mode = "conservative"
    
    if not os.path.exists(input_dir):
        print(f"Error: Directory not found: {input_dir}")
        sys.exit(1)
    
    extractor = ArchiveExtractor(input_dir, mode=mode)
    extractor.run()


if __name__ == "__main__":
    main()
