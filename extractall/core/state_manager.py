"""State management for extraction tracking."""

import json
from pathlib import Path
from typing import Dict, Set, Optional
import logging
from datetime import datetime

from .interfaces import StateManager, ExtractionResult
from ..config.settings import ExtractionConfig


class JsonStateManager(StateManager):
    """JSON-based state management."""
    
    def __init__(self, config: ExtractionConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.state_file = config.input_dir / config.state_file
        self._state_cache: Optional[Dict] = None
    
    def save_state(self, state: Dict) -> None:
        """Save extraction state to JSON file."""
        try:
            # Add metadata
            state['metadata'] = {
                'last_updated': datetime.now().isoformat(),
                'version': '1.0',
            }
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            self._state_cache = state
            self.logger.debug(f"State saved to {self.state_file}")
            
        except (OSError, json.JSONEncodeError) as e:
            self.logger.error(f"Failed to save state: {e}")
            raise
    
    def load_state(self) -> Dict:
        """Load extraction state from JSON file."""
        # Don't use cache for different directories
        if not self.state_file.exists():
            return self._create_initial_state()
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Validate and migrate if necessary
            state = self._validate_and_migrate_state(state)
            
            self.logger.debug(f"State loaded from {self.state_file}")
            return state
            
        except (OSError, json.JSONDecodeError) as e:
            self.logger.warning(f"Failed to load state, creating new: {e}")
            return self._create_initial_state()
    
    def is_processed(self, file_path: Path) -> bool:
        """Check if file was already processed."""
        state = self.load_state()
        file_str = str(file_path)
        
        return file_str in state.get('processed', [])
    
    def mark_processed(self, file_path: Path, result: ExtractionResult) -> None:
        """Mark file as processed with result."""
        state = self.load_state()
        file_str = str(file_path)
        
        # Add to processed list
        if file_str not in state['processed']:
            state['processed'].append(file_str)
        
        # Add to specific result category
        result_key = result.value
        if result_key not in state:
            state[result_key] = []
        
        if file_str not in state[result_key]:
            state[result_key].append(file_str)
        
        # Update statistics
        self._update_statistics(state)
        
        self.save_state(state)
    
    def get_statistics(self) -> Dict:
        """Get extraction statistics."""
        state = self.load_state()
        return state.get('statistics', {})
    
    def _create_initial_state(self) -> Dict:
        """Create initial state structure."""
        return {
            'processed': [],
            'success': [],
            'failed': [],
            'locked': [],
            'partial': [],
            'statistics': {
                'total_processed': 0,
                'success_rate': 0.0,
                'last_run': None,
            },
            'metadata': {
                'created': datetime.now().isoformat(),
                'version': '1.0',
            }
        }
    
    def _validate_and_migrate_state(self, state: Dict) -> Dict:
        """Validate and migrate state if necessary."""
        # Ensure required keys exist
        required_keys = ['processed', 'success', 'failed', 'locked']
        for key in required_keys:
            if key not in state:
                state[key] = []
        
        # Ensure statistics exist
        if 'statistics' not in state:
            state['statistics'] = {
                'total_processed': len(state.get('processed', [])),
                'success_rate': 0.0,
                'last_run': None,
            }
        
        # Migrate old format if needed
        if 'extracted' in state and 'success' not in state:
            state['success'] = state.pop('extracted', [])
        
        return state
    
    def _update_statistics(self, state: Dict) -> None:
        """Update statistics in state."""
        total_processed = len(state.get('processed', []))
        total_success = len(state.get('success', []))
        
        success_rate = (total_success / total_processed * 100) if total_processed > 0 else 0.0
        
        state['statistics'] = {
            'total_processed': total_processed,
            'total_success': total_success,
            'total_failed': len(state.get('failed', [])),
            'total_locked': len(state.get('locked', [])),
            'total_partial': len(state.get('partial', [])),
            'success_rate': round(success_rate, 2),
            'last_run': datetime.now().isoformat(),
        }
    
    def reset_state(self) -> None:
        """Reset state to initial state."""
        self._state_cache = None
        if self.state_file.exists():
            self.state_file.unlink()
        self.logger.info("State reset")
    
    def export_report(self) -> Dict:
        """Export detailed report."""
        state = self.load_state()
        
        return {
            'summary': state.get('statistics', {}),
            'details': {
                'successful_files': state.get('success', []),
                'failed_files': state.get('failed', []),
                'locked_files': state.get('locked', []),
                'partial_files': state.get('partial', []),
            },
            'metadata': state.get('metadata', {}),
        }
