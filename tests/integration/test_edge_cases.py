"""Edge case and performance tests."""

import pytest
import subprocess
from pathlib import Path

from extractall import ArchiveExtractor


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_handles_unicode_filenames(self, temp_dir):
        """Should handle Unicode and special character filenames."""
        # Create content with Unicode names
        content_dir = temp_dir / "unicode_content"
        content_dir.mkdir()
        
        unicode_files = [
            "файл_русский.txt",
            "文件中文.txt", 
            "ファイル日本語.txt",
            "file with spaces.txt",
            "file@#$%^&().txt"
        ]
        
        for filename in unicode_files:
            (content_dir / filename).write_text(f"Content: {filename}")
        
        # Create archive
        subprocess.run(["zip", "-r", str(temp_dir / "unicode.zip"), str(content_dir)], 
                      capture_output=True)
        
        # Extract
        extractor = ArchiveExtractor(str(temp_dir), mode="aggressive")
        report = extractor.run()
        
        # Should handle Unicode files
        assert report['summary']['successful'] >= 1
        
        # Check Unicode files were extracted
        output_files = list((temp_dir / "output").rglob("*"))
        unicode_output_files = [f for f in output_files if any(ord(c) > 127 for c in f.name)]
        assert len(unicode_output_files) >= 1

    def test_handles_nested_archives(self, temp_dir):
        """Should extract nested archives recursively."""
        # Create nested structure
        inner_content = temp_dir / "inner"
        inner_content.mkdir()
        (inner_content / "inner_file.txt").write_text("Inner content")
        
        # Create inner archive
        subprocess.run(["zip", "-r", str(temp_dir / "inner.zip"), str(inner_content)], 
                      capture_output=True)
        
        # Create outer content with inner archive
        outer_content = temp_dir / "outer"
        outer_content.mkdir()
        (outer_content / "outer_file.txt").write_text("Outer content")
        subprocess.run(["cp", str(temp_dir / "inner.zip"), str(outer_content / "inner.zip")], 
                      capture_output=True)
        
        # Create outer archive
        subprocess.run(["zip", "-r", str(temp_dir / "nested.zip"), str(outer_content)], 
                      capture_output=True)
        
        # Clean up intermediate files
        (temp_dir / "inner.zip").unlink()
        
        # Extract
        extractor = ArchiveExtractor(str(temp_dir), mode="aggressive")
        report = extractor.run()
        
        # Should extract nested content
        assert report['summary']['successful'] >= 1
        
        # Check both inner and outer files were extracted
        output_files = [f.name for f in (temp_dir / "output").rglob("*.txt")]
        assert "inner_file.txt" in output_files or any("inner" in name for name in output_files)
        assert "outer_file.txt" in output_files or any("outer" in name for name in output_files)

    def test_handles_duplicate_filenames(self, temp_dir):
        """Should handle duplicate filenames with incremental naming."""
        # Create multiple archives with same internal filename
        for i in range(3):
            content_dir = temp_dir / f"content_{i}"
            content_dir.mkdir()
            (content_dir / "duplicate.txt").write_text(f"Content version {i}")
            
            # Use -j flag to flatten structure and create conflicts
            subprocess.run(["zip", "-j", str(temp_dir / f"archive_{i}.zip"), 
                           str(content_dir / "duplicate.txt")], capture_output=True)
        
        # Extract
        extractor = ArchiveExtractor(str(temp_dir), mode="standard")
        report = extractor.run()
        
        # Should extract all archives
        assert report['summary']['successful'] == 3
        
        # Should create duplicate.txt, duplicate_1.txt, duplicate_2.txt
        output_files = list((temp_dir / "output").glob("duplicate*.txt"))
        assert len(output_files) == 3
        
        filenames = [f.name for f in output_files]
        assert "duplicate.txt" in filenames
        assert "duplicate_1.txt" in filenames
        assert "duplicate_2.txt" in filenames

    def test_performance_with_many_small_files(self, temp_dir):
        """Should handle many small archives efficiently."""
        import time
        
        # Create many small archives
        num_archives = 20
        for i in range(num_archives):
            content_dir = temp_dir / f"content_{i}"
            content_dir.mkdir()
            (content_dir / f"file_{i}.txt").write_text(f"Content {i}")
            
            subprocess.run(["zip", "-r", str(temp_dir / f"small_{i:03d}.zip"), str(content_dir)], 
                          capture_output=True)
        
        # Time the extraction
        start_time = time.time()
        extractor = ArchiveExtractor(str(temp_dir), mode="standard")
        report = extractor.run()
        end_time = time.time()
        
        # Should complete in reasonable time
        extraction_time = end_time - start_time
        assert extraction_time < 60  # Should complete within 1 minute
        
        # Should extract all archives
        assert report['summary']['successful'] == num_archives
        
        # Should extract all files
        output_files = list((temp_dir / "output").rglob("*.txt"))
        assert len(output_files) == num_archives

    def test_handles_empty_archives(self, temp_dir):
        """Should handle empty archives gracefully."""
        # Create empty directory
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        
        # Create empty archive
        subprocess.run(["zip", "-r", str(temp_dir / "empty.zip"), str(empty_dir)], 
                      capture_output=True)
        
        # Extract
        extractor = ArchiveExtractor(str(temp_dir))
        report = extractor.run()
        
        # Should handle empty archive without errors
        assert report['summary']['successful'] >= 1

    def test_handles_very_long_paths(self, temp_dir):
        """Should handle archives with very long internal paths."""
        # Create deep directory structure
        deep_dir = temp_dir / "content"
        current_dir = deep_dir
        
        # Create nested directories
        for i in range(10):
            current_dir = current_dir / f"very_long_directory_name_level_{i}_with_many_characters"
            current_dir.mkdir(parents=True)
        
        # Create file in deep directory
        (current_dir / "deep_file.txt").write_text("Deep file content")
        
        # Create archive
        subprocess.run(["zip", "-r", str(temp_dir / "deep_paths.zip"), str(deep_dir)], 
                      capture_output=True)
        
        # Extract
        extractor = ArchiveExtractor(str(temp_dir))
        report = extractor.run()
        
        # Should handle long paths
        assert report['summary']['successful'] >= 1
        
        # Check deep file was extracted
        deep_files = list((temp_dir / "output").rglob("deep_file.txt"))
        assert len(deep_files) >= 1
