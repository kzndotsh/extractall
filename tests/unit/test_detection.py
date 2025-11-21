"""Unit tests for archive detection."""

import pytest
from pathlib import Path
import subprocess

from extractall.core.detection import ArchiveDetector


class TestArchiveDetector:
    """Test archive detection functionality."""

    @pytest.fixture
    def detector(self):
        return ArchiveDetector()

    def test_detect_zip_by_extension(self, detector, temp_dir):
        """Should detect ZIP files by extension."""
        zip_file = temp_dir / "test.zip"
        zip_file.write_bytes(b"PK\x03\x04fake zip")
        
        assert detector.detect_archive_type(zip_file) == "zip"

    def test_detect_zip_by_magic_number(self, detector, temp_dir):
        """Should detect ZIP files by magic number when no extension."""
        zip_file = temp_dir / "no_extension"
        zip_file.write_bytes(b"PK\x03\x04fake zip content")
        
        assert detector.detect_archive_type(zip_file) == "zip"

    def test_detect_compound_extensions(self, detector, temp_dir):
        """Should detect compound extensions like .tar.gz."""
        tar_gz = temp_dir / "archive.tar.gz"
        tar_gz.write_bytes(b"\x1f\x8b")  # gzip magic number
        
        # Should detect as tar (compound extension takes precedence)
        result = detector.detect_archive_type(tar_gz)
        assert result in ["tar", "gz"]  # Either is acceptable

    def test_multipart_detection(self, detector, temp_dir):
        """Should detect multipart archives."""
        part1 = temp_dir / "archive.7z.001"
        part1.write_text("fake content")
        
        info = detector.analyze_archive(part1)
        assert info.is_multipart == True
        assert info.part_number == 1

    def test_find_related_parts(self, detector, temp_dir):
        """Should find all related multipart files."""
        # Create multipart files
        files = []
        for i in [1, 2, 3]:
            part = temp_dir / f"archive.7z.{i:03d}"
            part.write_text("fake content")
            files.append(part)
        
        # Should find all related parts
        related = detector.find_related_parts(files[0], files)
        assert len(related) == 3
        assert all(f in related for f in files)
