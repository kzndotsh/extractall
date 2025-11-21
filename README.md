> [!WARNING]
> This project was created 100% agentically via Claude Sonnet 4.5 as an experiment, always take precaution when running software written by strangers, but even more so when written by AI.

# ExtractAll - Universal Archive Extraction Tool

A robust Python tool for extracting various archive formats with advanced features like repair strategies, stuck detection, resume capability, and comprehensive error management.

## Features

- **Multi-format support**: ZIP, RAR, 7Z, TAR, GZ, BZ2, XZ and more
- **Smart detection**: Identifies archives by content when extensions are missing
- **Multiple extraction modes**: Conservative, Standard, and Aggressive modes
- **Archive repair**: Attempts to repair corrupted ZIP and RAR files before extraction
- **Stuck detection**: Monitors extraction progress and handles stuck operations
- **Resume capability**: Can resume interrupted extractions using state tracking
- **Duplicate handling**: Automatically renames files to avoid conflicts
- **Directory organization**: Separates extracted archives, output files, failed extractions, and stuck operations
- **Comprehensive logging**: Detailed logs saved to file and console output
- **Error handling**: Gracefully handles corrupted, password-protected, or incomplete archives
- **Multipart support**: Handles split archives (RAR, 7Z, ZIP parts)
- **Progress monitoring**: Real-time monitoring with timeout detection

## Installation

```bash
# Clone the repository
git clone https://github.com/kzndotsh/extractall.git
cd extractall

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .
```

## Usage

### Command Line Interface

```bash
# Basic usage
extractall <input_directory>

# With extraction modes
extractall <input_directory> --aggressive    # Nested archive extraction
extractall <input_directory> --conservative  # Basic extraction only
extractall <input_directory> --no-multipart # Disable multipart support

# Using uv
uv run python -m extractall <input_directory> [options]

# Direct execution
python -m extractall <input_directory> [options]
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
    mode="aggressive"  # or "standard", "conservative"
)
report = extractor.run()

# Using new orchestrator directly
from extractall import ExtractionOrchestrator, create_aggressive_config
from pathlib import Path

config = create_aggressive_config(Path("/path/to/archives"))
orchestrator = ExtractionOrchestrator(config)
report = orchestrator.run()
```

## Extraction Modes

- **Conservative**: Basic extraction with minimal processing
- **Standard**: Basic extraction with error handling and repair attempts
- **Aggressive**: Includes nested archive detection and recursive extraction

## Directory Structure

After running, the tool creates:
- `extracted/` - Successfully processed archive files
- `output/` - Extracted file contents (maintains original directory structure)
- `failed/` - Archives that couldn't be extracted
- `locked/` - Password-protected archives
- `stuck/` - Archives that got stuck during extraction
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

### Archive Repair (Standard/Aggressive Mode)
- Attempts to repair corrupted ZIP and RAR files
- Uses system tools like `zip -F` and `rar r`
- Falls back to normal extraction if repair fails
- Configurable repair timeout

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
- **Stuck extractions**: Moved to `stuck/` directory after timeout
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
│   │   ├── orchestrator.py    # Main orchestration logic
│   │   ├── file_manager.py    # File management
│   │   ├── state_manager.py   # State tracking
│   │   ├── detection.py       # Archive detection
│   │   └── interfaces.py      # Core interfaces
│   ├── strategies/      # Extraction strategies
│   │   ├── basic_strategy.py         # Basic extraction
│   │   ├── repair_strategy.py        # Archive repair
│   │   ├── multipart_strategy.py     # Multipart handling
│   │   ├── multi_tool_strategy.py    # Multiple tool attempts
│   │   ├── partial_strategy.py       # Partial extraction
│   │   ├── encoding_strategy.py      # Encoding variants
│   │   └── alternative_format_strategy.py # Format alternatives
│   ├── handlers/        # Format-specific handlers
│   │   ├── base_handler.py    # Base handler interface
│   │   ├── zip_handler.py     # ZIP handling
│   │   ├── rar_handler.py     # RAR handling
│   │   ├── sevenz_handler.py  # 7Z handling
│   │   └── tar_handler.py     # TAR handling
│   ├── config/          # Configuration management
│   │   └── settings.py        # Configuration classes
│   └── utils/           # Utility functions
│       └── progress_monitor.py # Progress monitoring
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
    enable_repair=True,
    stuck_timeout=300,  # 5 minutes
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

**Stuck Extractions:**
- Tool automatically detects stuck operations
- Moves stuck archives to `stuck/` directory
- Configurable timeout (default: 5 minutes)

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

MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
