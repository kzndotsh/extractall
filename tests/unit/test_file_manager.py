"""Unit tests for file manager."""

import pytest
from pathlib import Path

from extractall.core.file_manager import DefaultFileManager
from extractall.config.settings import create_default_config


class TestDefaultFileManager:
    """Test file management operations."""

    @pytest.fixture
    def file_manager(self, temp_dir):
        config = create_default_config(temp_dir)
        return DefaultFileManager(config)

    def test_creates_required_directories(self, file_manager, temp_dir):
        """Should create all required directories."""
        expected_dirs = ['extracted', 'output', 'failed', 'locked']
        
        for dir_name in expected_dirs:
            assert (temp_dir / dir_name).exists()

    def test_unique_name_generation(self, file_manager, temp_dir):
        """Should generate unique names for conflicting files."""
        # Create existing file
        existing = temp_dir / "test.txt"
        existing.write_text("existing")
        
        # Should generate unique name
        unique = file_manager.get_unique_output_path(existing)
        assert unique == temp_dir / "test_1.txt"
        
        # Create first duplicate and test again
        unique.write_text("duplicate")
        unique2 = file_manager.get_unique_output_path(existing)
        assert unique2 == temp_dir / "test_2.txt"

    def test_move_to_extracted(self, file_manager, temp_dir):
        """Should move files to extracted directory."""
        source = temp_dir / "archive.zip"
        source.write_text("fake archive")
        
        moved_path = file_manager.move_to_extracted(source)
        
        assert not source.exists()
        assert moved_path.exists()
        assert moved_path.parent.name == "extracted"

    def test_move_handles_conflicts(self, file_manager, temp_dir):
        """Should handle filename conflicts when moving."""
        # Create source files
        source1 = temp_dir / "archive.zip"
        source2 = temp_dir / "archive.zip"  # Same name, different instance
        source1.write_text("archive 1")
        
        # Move first file
        moved1 = file_manager.move_to_extracted(source1)
        
        # Create second file with same name
        source2.write_text("archive 2")
        moved2 = file_manager.move_to_extracted(source2)
        
        # Should have different names
        assert moved1.name == "archive.zip"
        assert moved2.name == "archive_1.zip"
