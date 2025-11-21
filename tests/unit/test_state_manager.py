"""Unit tests for state manager."""

import pytest
from pathlib import Path
import json

from extractall.core.state_manager import JsonStateManager
from extractall.core.interfaces import ExtractionResult
from extractall.config.settings import create_default_config


class TestJsonStateManager:
    """Test JSON state management."""

    @pytest.fixture
    def state_manager(self, temp_dir):
        config = create_default_config(temp_dir)
        return JsonStateManager(config)

    def test_creates_initial_state(self, state_manager):
        """Should create initial state structure."""
        state = state_manager.load_state()
        
        required_keys = ['processed', 'success', 'failed', 'locked', 'statistics']
        for key in required_keys:
            assert key in state

    def test_marks_file_as_processed(self, state_manager, temp_dir):
        """Should mark files as processed with correct result."""
        test_file = temp_dir / "test.zip"
        test_file.write_text("fake")
        
        state_manager.mark_processed(test_file, ExtractionResult.SUCCESS)
        
        assert state_manager.is_processed(test_file)
        
        state = state_manager.load_state()
        assert str(test_file) in state['processed']
        assert str(test_file) in state['success']

    def test_persists_state_to_file(self, state_manager, temp_dir):
        """Should persist state to JSON file."""
        test_file = temp_dir / "test.zip"
        test_file.write_text("fake")
        
        state_manager.mark_processed(test_file, ExtractionResult.FAILED)
        
        # Check file exists and contains data
        state_file = temp_dir / "extraction_state.json"
        assert state_file.exists()
        
        with open(state_file) as f:
            data = json.load(f)
        
        assert str(test_file) in data['failed']

    def test_calculates_statistics(self, state_manager, temp_dir):
        """Should calculate extraction statistics."""
        # Process some files
        for i, result in enumerate([ExtractionResult.SUCCESS, ExtractionResult.FAILED, ExtractionResult.SUCCESS]):
            test_file = temp_dir / f"test_{i}.zip"
            test_file.write_text("fake")
            state_manager.mark_processed(test_file, result)
        
        stats = state_manager.get_statistics()
        
        assert stats['total_processed'] == 3
        assert stats['total_success'] == 2
        assert stats['total_failed'] == 1
        assert stats['success_rate'] == 66.67

    def test_loads_existing_state(self, state_manager, temp_dir):
        """Should load existing state from file."""
        # Create state file manually
        state_data = {
            'processed': ['/fake/file.zip'],
            'success': ['/fake/file.zip'],
            'failed': [],
            'locked': [],
            'statistics': {'total_processed': 1}
        }
        
        state_file = temp_dir / "extraction_state.json"
        with open(state_file, 'w') as f:
            json.dump(state_data, f)
        
        # Load state
        loaded_state = state_manager.load_state()
        assert loaded_state['processed'] == ['/fake/file.zip']
        assert loaded_state['success'] == ['/fake/file.zip']
