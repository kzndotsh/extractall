"""Partial extraction strategy for damaged archives."""

from pathlib import Path
from typing import Optional, List
import logging
import subprocess

from ..core.interfaces import ExtractionStrategy, ArchiveInfo, ExtractionResult
from ..config.settings import ExtractionConfig


class PartialExtractionStrategy(ExtractionStrategy):
    """Extract what's possible from damaged archives."""
    
    def __init__(self, config: ExtractionConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
    
    def can_handle(self, archive_info: ArchiveInfo) -> bool:
        """Can attempt partial extraction if enabled."""
        return (self.config.enable_partial_extraction and 
                archive_info.type in ['zip', 'rar', '7z'])
    
    def extract(self, archive_info: ArchiveInfo, extract_to: Path) -> ExtractionResult:
        """Extract individual files even if archive is partially corrupted."""
        extract_to.mkdir(parents=True, exist_ok=True)
        
        if archive_info.type == 'zip':
            return self._partial_extract_zip(archive_info, extract_to)
        elif archive_info.type == 'rar':
            return self._partial_extract_rar(archive_info, extract_to)
        elif archive_info.type == '7z':
            return self._partial_extract_7z(archive_info, extract_to)
        
        return ExtractionResult.FAILED
    
    def _partial_extract_zip(self, archive_info: ArchiveInfo, extract_to: Path) -> ExtractionResult:
        """Extract individual files from ZIP."""
        try:
            # List contents first
            result = subprocess.run(
                ['unzip', '-l', str(archive_info.path)], 
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return ExtractionResult.FAILED
            
            # Extract files one by one
            extracted_any = False
            for line in result.stdout.split('\n'):
                if '/' in line and not line.strip().endswith('/'):
                    parts = line.split()
                    if len(parts) >= 4:
                        filename = parts[-1]
                        try:
                            subprocess.run(
                                ['unzip', '-j', str(archive_info.path), filename, '-d', str(extract_to)], 
                                capture_output=True, timeout=5
                            )
                            extracted_any = True
                        except:
                            continue
            
            return ExtractionResult.PARTIAL if extracted_any else ExtractionResult.FAILED
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return ExtractionResult.FAILED
    
    def _partial_extract_rar(self, archive_info: ArchiveInfo, extract_to: Path) -> ExtractionResult:
        """Extract with error recovery for RAR."""
        try:
            result = subprocess.run(
                ['unrar', 'x', '-kb', '-y', str(archive_info.path), str(extract_to)], 
                capture_output=True, text=True, timeout=30
            )
            
            # Check if any files were extracted
            if any(extract_to.iterdir()):
                return ExtractionResult.PARTIAL
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return ExtractionResult.FAILED
    
    def _partial_extract_7z(self, archive_info: ArchiveInfo, extract_to: Path) -> ExtractionResult:
        """Extract with continue-on-error for 7z."""
        try:
            result = subprocess.run(
                ['7z', 'x', str(archive_info.path), f'-o{extract_to}', '-y', '-aos'], 
                capture_output=True, text=True, timeout=30
            )
            
            # Check if any files were extracted
            if any(extract_to.iterdir()):
                return ExtractionResult.PARTIAL
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return ExtractionResult.FAILED
    
    @property
    def priority(self) -> int:
        """Low priority - try after other methods."""
        return 80
