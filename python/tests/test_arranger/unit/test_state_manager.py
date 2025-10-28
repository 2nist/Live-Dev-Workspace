"""Unit tests for StateManager."""

import pytest
from arranger.services import StateManager
from arranger.models import Arrangement, Section, SectionType


class TestStateManager:
    """Test StateManager undo/redo functionality."""
    
    def test_initialization(self):
        """Test state manager initialization."""
        initial = {"count": 0}
        sm = StateManager(initial_state=initial)
        
        assert sm.current_state == initial
        assert sm.history_size == 1
        assert not sm.can_undo  # Can't undo initial state
        assert not sm.can_redo
    
    def test_update_state(self):
        """Test state updates."""
        sm = StateManager(initial_state={"count": 0})
        
        sm.update_state({"count": 1}, operation="increment")
        assert sm.current_state["count"] == 1
        assert sm.history_size == 2
        assert sm.can_undo
    
    def test_undo(self):
        """Test undo functionality."""
        sm = StateManager(initial_state={"count": 0})
        
        sm.update_state({"count": 1}, operation="increment")
        sm.update_state({"count": 2}, operation="increment")
        
        # Undo once
        previous = sm.undo()
        assert previous["count"] == 1
        assert sm.can_redo
        
        # Undo again
        previous = sm.undo()
        assert previous["count"] == 0
        assert not sm.can_undo  # At initial state
    
    def test_redo(self):
        """Test redo functionality."""
        sm = StateManager(initial_state={"count": 0})
        
        sm.update_state({"count": 1}, operation="increment")
        sm.update_state({"count": 2}, operation="increment")
        
        # Undo twice
        sm.undo()
        sm.undo()
        
        # Redo once
        state = sm.redo()
        assert state["count"] == 1
        
        # Redo again
        state = sm.redo()
        assert state["count"] == 2
        assert not sm.can_redo
    
    def test_redo_stack_cleared_on_update(self):
        """Test redo stack cleared on new state update."""
        sm = StateManager(initial_state={"count": 0})
        
        sm.update_state({"count": 1}, operation="increment")
        sm.update_state({"count": 2}, operation="increment")
        sm.undo()
        
        assert sm.can_redo
        
        # New update should clear redo stack
        sm.update_state({"count": 10}, operation="set")
        assert not sm.can_redo
    
    def test_max_history_limit(self):
        """Test max history enforcement."""
        sm = StateManager(initial_state=0, max_history=3)
        
        for i in range(5):
            sm.update_state(i + 1, operation="increment")
        
        # Should keep only last 3 entries
        assert sm.history_size == 3
    
    def test_manual_checkpoint(self):
        """Test manual checkpoint creation."""
        sm = StateManager(initial_state={"count": 0}, auto_checkpoint=False)
        
        # Update without auto checkpoint
        sm._current_state = {"count": 5}
        assert sm.history_size == 1  # Only initial
        
        # Manual checkpoint
        sm.checkpoint(operation="manual", description="Saved state")
        assert sm.history_size == 2
    
    def test_get_history(self):
        """Test history retrieval."""
        sm = StateManager(initial_state=0)
        
        sm.update_state(1, operation="inc", description="Increment 1")
        sm.update_state(2, operation="inc", description="Increment 2")
        
        history = sm.get_history(limit=5)
        assert len(history) == 3  # init + 2 updates
        assert history[-1]["operation"] == "inc"
        assert history[-1]["description"] == "Increment 2"
    
    def test_clear_history(self):
        """Test history clearing."""
        sm = StateManager(initial_state=0)
        
        sm.update_state(1, operation="inc")
        sm.update_state(2, operation="inc")
        sm.undo()
        
        # Clear but keep current
        sm.clear_history(keep_current=True)
        assert sm.history_size == 1
        assert not sm.can_redo
        assert not sm.can_undo
    
    def test_change_callbacks(self):
        """Test change notification callbacks."""
        sm = StateManager(initial_state=0)
        
        callback_calls = []
        
        def on_change(operation: str):
            callback_calls.append(operation)
        
        sm.on_change(on_change)
        
        sm.update_state(1, operation="increment")
        sm.undo()
        sm.redo()
        
        assert callback_calls == ["increment", "undo", "redo"]
    
    def test_deep_copy_isolation(self):
        """Test that state snapshots are isolated via deep copy."""
        initial = {"data": [1, 2, 3]}
        sm = StateManager(initial_state=initial)
        
        # Modify original
        initial["data"].append(4)
        
        # State manager should have unmodified copy
        assert sm.current_state["data"] == [1, 2, 3]
    
    def test_with_arrangement_model(self):
        """Test state manager with Arrangement model."""
        arr = Arrangement(title="Test", bpm=120.0)
        sm = StateManager(initial_state=arr)
        
        # Add section
        arr.add_section(Section(label="V1", type=SectionType.VERSE, bars=8))
        sm.update_state(arr, operation="add_section", description="Added V1")
        
        assert sm.current_state.section_count == 1
        
        # Undo
        previous = sm.undo()
        assert previous.section_count == 0
        
        # Redo
        restored = sm.redo()
        assert restored.section_count == 1
    
    def test_export_state(self):
        """Test state export."""
        sm = StateManager(initial_state={"test": "data"})
        sm.update_state({"test": "updated"}, operation="update")
        
        export = sm.export_state()
        
        assert export["state"] == {"test": "updated"}
        assert export["can_undo"] is True
        assert export["can_redo"] is False
        assert export["last_operation"] == "update"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
