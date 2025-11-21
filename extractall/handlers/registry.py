"""Archive handler registry and factory."""

from typing import Dict, List, Optional, Type
from pathlib import Path
import logging

from ..core.interfaces import ArchiveHandler, ArchiveInfo
from ..config.settings import ExtractionConfig


class HandlerRegistry:
    """Registry for archive handlers."""
    
    def __init__(self, config: ExtractionConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self._handlers: Dict[str, Type[ArchiveHandler]] = {}
        self._handler_instances: Dict[str, ArchiveHandler] = {}
    
    def register_handler(self, format_type: str, handler_class: Type[ArchiveHandler]) -> None:
        """Register a handler for a specific format."""
        self._handlers[format_type] = handler_class
        self.logger.debug(f"Registered handler for {format_type}: {handler_class.__name__}")
    
    def get_handler(self, format_type: str) -> Optional[ArchiveHandler]:
        """Get handler instance for format type."""
        if format_type not in self._handlers:
            return None
        
        # Use cached instance if available
        if format_type in self._handler_instances:
            return self._handler_instances[format_type]
        
        # Create new instance
        handler_class = self._handlers[format_type]
        handler_instance = handler_class(self.config, self.logger)
        self._handler_instances[format_type] = handler_instance
        
        return handler_instance
    
    def get_compatible_handlers(self, archive_info: ArchiveInfo) -> List[ArchiveHandler]:
        """Get all handlers that can handle the archive."""
        compatible_handlers = []
        
        for format_type, handler_class in self._handlers.items():
            handler = self.get_handler(format_type)
            if handler and handler.can_handle(archive_info.path):
                compatible_handlers.append(handler)
        
        return compatible_handlers
    
    def get_all_supported_formats(self) -> List[str]:
        """Get all supported archive formats."""
        formats = set()
        for handler_class in self._handlers.values():
            # Create temporary instance to get supported formats
            temp_handler = handler_class(self.config, self.logger)
            formats.update(temp_handler.supported_formats)
        
        return sorted(list(formats))
    
    def auto_register_handlers(self) -> None:
        """Auto-register all available handlers."""
        from .zip_handler import ZipHandler
        from .rar_handler import RarHandler
        from .sevenz_handler import SevenZHandler
        from .tar_handler import TarHandler
        
        handlers = [
            ('zip', ZipHandler),
            ('rar', RarHandler),
            ('7z', SevenZHandler),
            ('tar', TarHandler),
        ]
        
        for format_type, handler_class in handlers:
            try:
                self.register_handler(format_type, handler_class)
            except ImportError as e:
                self.logger.warning(f"Could not register {format_type} handler: {e}")


def create_handler_registry(config: ExtractionConfig, 
                          logger: Optional[logging.Logger] = None) -> HandlerRegistry:
    """Create and configure handler registry."""
    registry = HandlerRegistry(config, logger)
    registry.auto_register_handlers()
    return registry
