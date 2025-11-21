> [!WARNING]
> This project was created 100% agentically via Claude Sonnet 4.5 as an experiment, always take precaution when running software written by strangers, but even more so when written by AI.

# ExtractAll - Universal Archive Extraction Tool

A robust Python tool for extracting various archive formats with advanced features like nested archive handling, resume capability, and comprehensive error management.

## Features

- **Multi-format support**: ZIP, RAR, 7Z, TAR, GZ, BZ2, XZ and more
- **Smart detection**: Identifies archives by content when extensions are missing
- **Nested archives**: Automatically extracts archives found within archives (aggressive mode)
- **Resume capability**: Can resume interrupted extractions using state tracking
- **Duplicate handling**: Automatically renames files to avoid conflicts
- **Directory organization**: Separates extracted archives, output files, and failed extractions
- **Comprehensive logging**: Detailed logs saved to file and console output
- **Error handling**: Gracefully handles corrupted, password-protected, or incomplete archives
- **Multipart support**: Handles split archives (RAR, 7Z, ZIP parts)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd extractall

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .
```

## Usage

### Command Line Interface

```bash
# Using uv
uv run python -m extractall <input_directory>

# Using pip installation
extractall <input_directory>

# Direct execution
python -m extractall <input_directory>
```

### Python API

```python
from extractall import ArchiveExtractor

# Basic usage
extractor = ArchiveExtractor("/path/to/archives")
report = extractor.run()

# With options
extractor = ArchiveExtractor(
    input_dir="/path/to/archives",
    mode="aggressive",  # or "standard"
    enable_multipart=True
)
report = extractor.run()
```

## Extraction Modes

- **Standard**: Basic extraction with error handling
- **Aggressive**: Includes nested archive detection and recursive extraction

## Directory Structure

After running, the tool creates:
- `extracted/` - Successfully processed archive files
- `output/` - Extracted file contents (maintains original directory structure)
- `failed/` - Archives that couldn't be extracted
- `locked/` - Password-protected archives
- `extraction.log` - Detailed operation log
- `extraction_state.json` - State file for resume capability

## Supported Archive Types

| Format | Extensions | Detection Method |
|--------|------------|------------------|
| ZIP | .zip | Extension + Magic bytes |
| RAR | .rar, .r01, .r02... | Extension + Magic bytes |
| 7-Zip | .7z, .7z.001... | Extension + Magic bytes |
| TAR | .tar, .tar.gz, .tar.bz2, .tar.xz | Extension + Content |
| GZIP | .gz | Extension + Magic bytes |
| BZIP2 | .bz2 | Extension + Magic bytes |
| XZ | .xz | Extension + Magic bytes |

## Advanced Features

### Resume Capability
If extraction is interrupted, run the command again:
- Skips already processed files
- Continues from where it left off
- Maintains state in `extraction_state.json`

### Nested Archive Handling (Aggressive Mode)
- Extracts outer archives
- Scans extracted content for more archives
- Recursively processes nested archives
- Handles multiple levels of nesting

### Multipart Archive Support
- Automatically detects related parts (.r01, .7z.001, etc.)
- Groups parts together for extraction
- Handles incomplete part sets gracefully

### Error Handling
- **Password-protected**: Moved to `locked/` directory
- **Corrupted files**: Moved to `failed/` directory
- **Missing parts**: Moved to `failed/` directory
- **Unknown formats**: Logged and skipped

## Requirements

### System Tools
The tool uses system commands for extraction. Install required tools:

**Arch Linux:**
```bash
sudo pacman -S unrar unzip p7zip tar gzip bzip2 xz
```

**Ubuntu/Debian:**
```bash
sudo apt install unrar unzip p7zip-full tar gzip bzip2 xz-utils
```

**macOS:**
```bash
brew install unrar p7zip
```

### Python Requirements
- Python 3.8+
- No external Python dependencies (uses standard library only)

## Development

### Running Tests
```bash
# Run all tests
uv run pytest

# Run specific test categories
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest tests/strategies/

# Run with coverage
uv run pytest --cov=extractall
```

### Project Structure
```
extractall/
├── extractall/           # Main package
│   ├── core/            # Core extraction logic
│   ├── strategies/      # Extraction strategies
│   ├── handlers/        # Format-specific handlers
│   ├── config/          # Configuration management
│   └── utils/           # Utility functions
├── tests/               # Test suite
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── strategies/     # Strategy tests
└── docs/               # Documentation
```

## Configuration

The tool supports various configuration options through the `ExtractionConfig` class:

```python
from extractall.config.settings import ExtractionConfig, ExtractionMode

config = ExtractionConfig(
    input_dir=Path("/path/to/archives"),
    mode=ExtractionMode.AGGRESSIVE,
    enable_multipart=True,
    log_level="INFO"
)
```

## Logging

Comprehensive logging includes:
- Real-time console output
- Detailed file logging (`extraction.log`)
- Extraction statistics and success rates
- Error details and troubleshooting information

## Best Practices

1. **Test on sample data** before processing important archives
2. **Ensure sufficient disk space** for extracted content
3. **Use dedicated directories** to avoid file conflicts
4. **Review logs** for extraction issues
5. **Check failed/locked directories** for problematic archives
6. **Use aggressive mode** for nested archive scenarios

## Troubleshooting

### Common Issues

**Permission Errors:**
- Ensure write permissions in target directory
- Run with appropriate user privileges

**Missing Tools:**
- Install required system extraction tools
- Verify tools are in system PATH

**Disk Space:**
- Ensure adequate space for extraction
- Monitor disk usage during large extractions

**Special Characters:**
- Tool handles Unicode filenames automatically
- Check locale settings if issues persist

### Getting Help

Check the logs in `extraction.log` for detailed information about:
- Processing steps and decisions
- Extraction success/failure reasons
- Nested archive discoveries
- Error details and stack traces

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]
