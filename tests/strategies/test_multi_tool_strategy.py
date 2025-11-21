"""Tests for multi-tool extraction strategy."""

import pytest
import subprocess
from pathlib import Path

from extractall.strategies.multi_tool_strategy import MultiToolStrategy
from extractall.core.detection import ArchiveInfoImpl
from extractall.core.interfaces import ExtractionResult
from extractall.config.settings import create_default_config


class TestMultiToolStrategy:
    """Test multi-tool extraction strategy."""

    @pytest.fixture
    def strategy(self, temp_dir):
        config = create_default_config(temp_dir)
        return MultiToolStrategy(config)

    @pytest.fixture
    def zip_archive(self, temp_dir):
        """Create a real ZIP archive for testing."""
        content_dir = temp_dir / "content"
        content_dir.mkdir()
        (content_dir / "test.txt").write_text("test content")
        
        zip_file = temp_dir / "test.zip"
        subprocess.run(["zip", "-r", str(zip_file), str(content_dir)], capture_output=True)
        
        return ArchiveInfoImpl(
            path=zip_file,
            type="zip",
            size=zip_file.stat().st_size,
            is_multipart=False,
            part_number=None
        )

    def test_can_handle_supported_formats(self, strategy):
        """Should handle supported archive formats."""
        supported_formats = ['zip', 'rar', '7z', 'tar']
        
        for format_type in supported_formats:
            archive_info = ArchiveInfoImpl(
                path=Path("/fake/file." + format_type),
                type=format_type,
                size=1000,
                is_multipart=False,
                part_number=None
            )
            assert strategy.can_handle(archive_info)

    def test_cannot_handle_unsupported_formats(self, strategy):
        """Should not handle unsupported formats."""
        archive_info = ArchiveInfoImpl(
            path=Path("/fake/file.unknown"),
            type="unknown",
            size=1000,
            is_multipart=False,
            part_number=None
        )
        assert not strategy.can_handle(archive_info)

    def test_extracts_zip_successfully(self, strategy, zip_archive, temp_dir):
        """Should extract ZIP files successfully."""
        extract_dir = temp_dir / "extracted"
        
        result = strategy.extract(zip_archive, extract_dir)
        
        assert result == ExtractionResult.SUCCESS
        assert extract_dir.exists()
        
        # Check extracted content
        extracted_files = list(extract_dir.rglob("*.txt"))
        assert len(extracted_files) >= 1

    def test_has_correct_priority(self, strategy):
        """Should have high priority."""
        assert strategy.priority == 10
