"""Multipart archive handling strategy."""

from pathlib import Path
from typing import Optional, List, Tuple
import logging
import re

from ..core.interfaces import ExtractionStrategy, ArchiveInfo, ExtractionResult
from ..config.settings import ExtractionConfig
from .multi_tool_strategy import MultiToolStrategy


class MultipartStrategy(ExtractionStrategy):
    """Handle multipart archives intelligently."""
    
    def __init__(self, config: ExtractionConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.multi_tool = MultiToolStrategy(config, logger)
        
        self.patterns = [
            r'^(.+)\.7z\.(\d{3})$',
            r'^(.+)\.part(\d+)\.7z$',
            r'^(.+)\.(\d{3})\.7z$',
            r'^(.+)\.r(\d{2})$',
            r'^(.+)\.rar\.(\d{3})$',
        ]
    
    def can_handle(self, archive_info: ArchiveInfo) -> bool:
        """Handle multipart archives."""
        return archive_info.is_multipart and self.multi_tool.can_handle(archive_info)
    
    def extract(self, archive_info: ArchiveInfo, extract_to: Path) -> ExtractionResult:
        """Extract multipart archive."""
        if not archive_info.is_multipart:
            return ExtractionResult.FAILED
        
        # Find all related parts
        related_parts = self._find_related_parts(archive_info)
        
        # Check completeness
        if not self._is_complete_enough(related_parts):
            self.logger.warning(f"Multipart archive incomplete: {archive_info.path.name}")
            return ExtractionResult.FAILED
        
        # Try extraction with first part
        first_part = min(related_parts, key=lambda p: p.name)
        
        # Create archive info for first part
        from ..core.detection import ArchiveInfoImpl
        first_archive_info = ArchiveInfoImpl(
            path=first_part,
            type=archive_info.type,
            size=first_part.stat().st_size,
            is_multipart=True,
            part_number=1
        )
        
        return self.multi_tool.extract(first_archive_info, extract_to)
    
    def _find_related_parts(self, archive_info: ArchiveInfo) -> List[Path]:
        """Find all parts of multipart archive."""
        parent_dir = archive_info.path.parent
        base_name = self._extract_base_name(archive_info.path)
        
        if not base_name:
            return [archive_info.path]
        
        related = []
        for file_path in parent_dir.iterdir():
            if file_path.is_file() and self._extract_base_name(file_path) == base_name:
                related.append(file_path)
        
        return related
    
    def _extract_base_name(self, file_path: Path) -> Optional[str]:
        """Extract base name from multipart filename."""
        for pattern in self.patterns:
            match = re.match(pattern, file_path.name, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _is_complete_enough(self, parts: List[Path]) -> bool:
        """Check if we have enough parts to attempt extraction."""
        if len(parts) < 2:
            return True  # Single file
        
        # Extract part numbers
        part_numbers = []
        for part in parts:
            for pattern in self.patterns:
                match = re.match(pattern, part.name, re.IGNORECASE)
                if match:
                    try:
                        part_numbers.append(int(match.group(2)))
                        break
                    except ValueError:
                        continue
        
        if not part_numbers:
            return True
        
        part_numbers.sort()
        expected_parts = part_numbers[-1] - part_numbers[0] + 1
        actual_parts = len(part_numbers)
        
        # Need at least 70% of parts
        return (actual_parts / expected_parts) >= 0.7
    
    @property
    def priority(self) -> int:
        """Medium-high priority."""
        return 20
