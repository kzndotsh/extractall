"""Multi-tool extraction strategy."""

from pathlib import Path
from typing import Optional, List, Dict
import logging
import subprocess

from ..core.interfaces import ExtractionStrategy, ArchiveInfo, ExtractionResult
from ..config.settings import ExtractionConfig


class MultiToolStrategy(ExtractionStrategy):
    """Try multiple tools for the same archive type."""
    
    def __init__(self, config: ExtractionConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        self.tool_chains = {
            'zip': [
                (['unzip', '-q', '-o', '{file}', '-d', '{output}'], "unzip"),
                (['7z', 'x', '{file}', '-o{output}', '-y'], "7z"),
                (['python3', '-m', 'zipfile', '-e', '{file}', '{output}'], "python"),
            ],
            'rar': [
                (['unrar', 'x', '-y', '{file}', '{output}'], "unrar"),
                (['7z', 'x', '{file}', '-o{output}', '-y'], "7z"),
            ],
            '7z': [
                (['7z', 'x', '{file}', '-o{output}', '-y'], "7z"),
                (['7z', 'x', '-tzip', '{file}', '-o{output}', '-y'], "7z-as-zip"),
            ],
            'tar': [
                (['tar', '-xf', '{file}', '-C', '{output}'], "tar"),
                (['7z', 'x', '{file}', '-o{output}', '-y'], "7z"),
            ]
        }
    
    def can_handle(self, archive_info: ArchiveInfo) -> bool:
        """Check if we have tool chains for this type."""
        return archive_info.type in self.tool_chains
    
    def extract(self, archive_info: ArchiveInfo, extract_to: Path) -> ExtractionResult:
        """Try multiple tools in sequence."""
        extract_to.mkdir(parents=True, exist_ok=True)
        
        tools = self.tool_chains.get(archive_info.type, [])
        
        for cmd_template, tool_name in tools:
            try:
                cmd = self._build_command(cmd_template, archive_info.path, extract_to)
                self.logger.debug(f"Trying {tool_name} for {archive_info.path.name}")
                
                result = subprocess.run(
                    cmd, capture_output=True, text=True, 
                    timeout=self.config.strategy_timeout
                )
                
                if result.returncode == 0:
                    self.logger.info(f"Success with {tool_name}")
                    return ExtractionResult.SUCCESS
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        return ExtractionResult.FAILED
    
    def _build_command(self, template: List[str], file_path: Path, output: Path) -> List[str]:
        """Build command from template."""
        return [part.format(file=str(file_path), output=str(output)) 
                for part in template]
    
    @property
    def priority(self) -> int:
        """High priority strategy."""
        return 10
