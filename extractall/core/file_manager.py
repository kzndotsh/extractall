"""File management operations."""

import shutil
from pathlib import Path
from typing import Dict, Optional
import logging

from .interfaces import FileManager
from ..config.settings import ExtractionConfig


class DefaultFileManager(FileManager):
    """Default implementation of file management."""
    
    def __init__(self, config: ExtractionConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.directories = config.get_directory_paths()
        
        # Ensure directories exist
        self._create_directories()
    
    def _create_directories(self) -> None:
        """Create necessary directories."""
        for dir_name, dir_path in self.directories.items():
            if dir_name != 'input':  # Don't create input directory
                dir_path.mkdir(exist_ok=True)
                self.logger.debug(f"Ensured directory exists: {dir_path}")
    
    def move_to_extracted(self, file_path: Path) -> Path:
        """Move file to extracted directory."""
        return self._move_file_safely(file_path, self.directories['extracted'])
    
    def move_to_failed(self, file_path: Path) -> Path:
        """Move file to failed directory."""
        return self._move_file_safely(file_path, self.directories['failed'])
    
    def move_to_locked(self, file_path: Path) -> Path:
        """Move file to locked directory."""
        return self._move_file_safely(file_path, self.directories['locked'])
    
    def get_unique_output_path(self, base_path: Path) -> Path:
        """Get unique path for output file to avoid conflicts."""
        if not base_path.exists():
            return base_path
        
        counter = 1
        while True:
            stem = base_path.stem
            suffix = base_path.suffix
            new_name = f"{stem}_{counter}{suffix}"
            new_path = base_path.parent / new_name
            
            if not new_path.exists():
                return new_path
            
            counter += 1
    
    def _move_file_safely(self, source: Path, destination_dir: Path) -> Path:
        """Move file safely with conflict resolution."""
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")
        
        destination_path = destination_dir / source.name
        final_path = self.get_unique_output_path(destination_path)
        
        try:
            shutil.move(str(source), str(final_path))
            self.logger.debug(f"Moved {source.name} to {final_path}")
            return final_path
        except (OSError, shutil.Error) as e:
            self.logger.error(f"Failed to move {source.name}: {e}")
            raise
    
    def copy_extracted_files(self, temp_dir: Path, preserve_structure: bool = True) -> int:
        """Copy extracted files to output directory."""
        files_copied = 0
        
        for item in temp_dir.rglob('*'):
            if item.is_file():
                if preserve_structure:
                    # Maintain directory structure
                    relative_path = item.relative_to(temp_dir)
                    output_path = self.directories['output'] / relative_path
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    # Flatten structure
                    output_path = self.directories['output'] / item.name
                
                final_path = self.get_unique_output_path(output_path)
                
                try:
                    shutil.copy2(str(item), str(final_path))
                    files_copied += 1
                    self.logger.debug(f"Copied {item.name} to {final_path}")
                except (OSError, shutil.Error) as e:
                    self.logger.warning(f"Failed to copy {item.name}: {e}")
        
        return files_copied
    
    def cleanup_temp_directory(self, temp_dir: Path) -> None:
        """Clean up temporary directory."""
        if temp_dir.exists() and temp_dir.is_dir():
            try:
                shutil.rmtree(temp_dir)
                self.logger.debug(f"Cleaned up temp directory: {temp_dir}")
            except (OSError, shutil.Error) as e:
                self.logger.warning(f"Failed to cleanup {temp_dir}: {e}")
    
    def get_temp_directory(self, base_name: str) -> Path:
        """Create a temporary directory for extraction."""
        temp_dir = self.directories['output'] / f"temp_{base_name}"
        temp_dir.mkdir(exist_ok=True)
        return temp_dir
