"""Base archive handler implementation."""

import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging
import tempfile

from ..core.interfaces import ArchiveHandler
from ..config.settings import ExtractionConfig


class BaseArchiveHandler(ArchiveHandler):
    """Base implementation for archive handlers."""
    
    def __init__(self, config: ExtractionConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.timeout = config.strategy_timeout
    
    def can_handle(self, file_path: Path) -> bool:
        """Check if this handler can process the file."""
        if not file_path.exists():
            return False
        
        # Check by extension
        ext = file_path.suffix.lower().lstrip('.')
        if ext in self.supported_formats:
            return True
        
        # Check by content if extension check fails
        return self._check_by_content(file_path)
    
    def extract(self, file_path: Path, extract_to: Path) -> bool:
        """Extract the archive using multiple strategies."""
        extract_to.mkdir(parents=True, exist_ok=True)
        
        # Try each extraction command in order
        for cmd_template in self._get_extraction_commands():
            if self._try_extraction_command(cmd_template, file_path, extract_to):
                return True
        
        return False
    
    def _get_extraction_commands(self) -> List[List[str]]:
        """Get list of extraction commands to try."""
        raise NotImplementedError("Subclasses must implement _get_extraction_commands")
    
    def _check_by_content(self, file_path: Path) -> bool:
        """Check if file can be handled by examining content."""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)
            
            magic_numbers = self._get_magic_numbers()
            return any(header.startswith(magic) for magic in magic_numbers)
            
        except (IOError, OSError):
            return False
    
    def _get_magic_numbers(self) -> List[bytes]:
        """Get magic numbers for this archive type."""
        return []
    
    def _try_extraction_command(self, cmd_template: List[str], 
                              file_path: Path, extract_to: Path) -> bool:
        """Try a specific extraction command."""
        try:
            # Replace placeholders in command template
            cmd = self._build_command(cmd_template, file_path, extract_to)
            
            self.logger.debug(f"Trying command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=extract_to
            )
            
            success = result.returncode == 0
            
            if success:
                self.logger.debug(f"Extraction successful with: {cmd[0]}")
            else:
                self.logger.debug(f"Extraction failed: {result.stderr}")
            
            return success
            
        except subprocess.TimeoutExpired:
            self.logger.debug(f"Extraction timeout with: {cmd_template[0]}")
            return False
        except FileNotFoundError:
            self.logger.debug(f"Tool not found: {cmd_template[0]}")
            return False
        except Exception as e:
            self.logger.debug(f"Extraction error: {e}")
            return False
    
    def _build_command(self, cmd_template: List[str], 
                      file_path: Path, extract_to: Path) -> List[str]:
        """Build command by replacing placeholders."""
        cmd = []
        
        for part in cmd_template:
            if part == '{file}':
                cmd.append(str(file_path))
            elif part == '{output}':
                cmd.append(str(extract_to))
            elif part == '{output_flag}':
                # Some tools use different output flags
                cmd.extend(self._get_output_flag(extract_to))
            else:
                cmd.append(part)
        
        return cmd
    
    def _get_output_flag(self, extract_to: Path) -> List[str]:
        """Get output directory flag for this tool."""
        return ['-d', str(extract_to)]
    
    def test_archive(self, file_path: Path) -> bool:
        """Test if archive is valid."""
        test_commands = self._get_test_commands()
        
        for cmd_template in test_commands:
            try:
                cmd = self._build_command(cmd_template, file_path, Path('.'))
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=min(self.timeout, 10)
                )
                
                if result.returncode == 0:
                    return True
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        return False
    
    def _get_test_commands(self) -> List[List[str]]:
        """Get commands for testing archive validity."""
        return []
    
    def list_contents(self, file_path: Path) -> List[str]:
        """List archive contents."""
        list_commands = self._get_list_commands()
        
        for cmd_template in list_commands:
            try:
                cmd = self._build_command(cmd_template, file_path, Path('.'))
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=min(self.timeout, 10)
                )
                
                if result.returncode == 0:
                    return self._parse_file_list(result.stdout)
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        return []
    
    def _get_list_commands(self) -> List[List[str]]:
        """Get commands for listing archive contents."""
        return []
    
    def _parse_file_list(self, output: str) -> List[str]:
        """Parse file list from command output."""
        # Basic implementation - subclasses should override
        lines = output.strip().split('\n')
        return [line.strip() for line in lines if line.strip()]
