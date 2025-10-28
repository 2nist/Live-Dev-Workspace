"""
State manager with undo/redo functionality
"""

from typing import Any, List, Dict, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import copy


@dataclass
class HistoryEntry:
    """Single entry in state history."""
    state_snapshot: Any
    timestamp: datetime
    operation: str
    description: str = ""
    
    def __repr__(self):
        return f"<HistoryEntry op={self.operation} at {self.timestamp.isoformat()}>"


class StateManager:
    """
    Manages application state with undo/redo functionality.
    
    Uses snapshots for state preservation and supports:
    - Unlimited undo/redo (up to max_history)
    - State snapshots with deep copying
    - Operation metadata tracking
    - Change callbacks
    """
    
    def __init__(
        self,
        initial_state: Any = None,
        max_history: int = 50,
        auto_checkpoint: bool = True
    ):
        """
        Initialize state manager.
        
        Args:
            initial_state: Initial state object
            max_history: Maximum history entries to keep
            auto_checkpoint: Auto-create checkpoints on state changes
        """
        self._current_state = copy.deepcopy(initial_state) if initial_state is not None else None
        self._history: List[HistoryEntry] = []
        self._redo_stack: List[HistoryEntry] = []
        self._max_history = max_history
        self._auto_checkpoint = auto_checkpoint
        self._change_callbacks: List[Callable] = []
        
        # Create initial checkpoint
        if initial_state is not None:
            self._create_checkpoint("init", "Initial state")
    
    @property
    def current_state(self) -> Any:
        """Get current state."""
        return self._current_state
    
    @property
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._history) > 1  # Keep at least one (initial state)
    
    @property
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0
    
    @property
    def history_size(self) -> int:
        """Get history size."""
        return len(self._history)
    
    @property
    def redo_size(self) -> int:
        """Get redo stack size."""
        return len(self._redo_stack)
    
    def update_state(
        self, 
        new_state: Any,
        operation: str = "update",
        description: str = ""
    ) -> None:
        """
        Update state and create checkpoint.
        
        Args:
            new_state: New state object
            operation: Operation identifier
            description: Human-readable description
        """
        self._current_state = new_state
        
        if self._auto_checkpoint:
            self._create_checkpoint(operation, description)
        
        # Clear redo stack on new state change
        self._redo_stack.clear()
        
        # Notify listeners
        self._notify_change(operation)
    
    def _create_checkpoint(self, operation: str, description: str = "") -> None:
        """Create state checkpoint."""
        # Deep copy to prevent mutations
        snapshot = copy.deepcopy(self._current_state)
        
        entry = HistoryEntry(
            state_snapshot=snapshot,
            timestamp=datetime.now(),
            operation=operation,
            description=description
        )
        
        self._history.append(entry)
        
        # Trim history if exceeds max
        if len(self._history) > self._max_history:
            self._history.pop(0)
    
    def checkpoint(self, operation: str = "manual", description: str = "") -> None:
        """
        Manually create a checkpoint.
        
        Args:
            operation: Operation identifier
            description: Human-readable description
        """
        self._create_checkpoint(operation, description)
    
    def undo(self) -> Optional[Any]:
        """
        Undo last operation.
        
        Returns:
            Previous state or None if can't undo
        """
        if not self.can_undo:
            return None
        
        # Move current to redo stack
        current_entry = self._history.pop()
        self._redo_stack.append(current_entry)
        
        # Restore previous state
        previous_entry = self._history[-1]
        self._current_state = copy.deepcopy(previous_entry.state_snapshot)
        
        self._notify_change("undo")
        return self._current_state
    
    def redo(self) -> Optional[Any]:
        """
        Redo previously undone operation.
        
        Returns:
            Redone state or None if can't redo
        """
        if not self.can_redo:
            return None
        
        # Restore from redo stack
        entry = self._redo_stack.pop()
        self._history.append(entry)
        self._current_state = copy.deepcopy(entry.state_snapshot)
        
        self._notify_change("redo")
        return self._current_state
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent history entries.
        
        Args:
            limit: Maximum entries to return
            
        Returns:
            List of history metadata (without state snapshots)
        """
        recent = self._history[-limit:] if limit > 0 else self._history
        
        return [
            {
                "operation": entry.operation,
                "description": entry.description,
                "timestamp": entry.timestamp.isoformat()
            }
            for entry in recent
        ]
    
    def clear_history(self, keep_current: bool = True) -> None:
        """
        Clear history and redo stacks.
        
        Args:
            keep_current: Keep current state as only history entry
        """
        if keep_current and self._current_state is not None:
            self._history = []
            self._create_checkpoint("clear", "History cleared")
        else:
            self._history.clear()
        
        self._redo_stack.clear()
    
    def on_change(self, callback: Callable[[str], None]) -> None:
        """
        Register change callback.
        
        Args:
            callback: Function called on state changes (operation: str) -> None
        """
        self._change_callbacks.append(callback)
    
    def _notify_change(self, operation: str) -> None:
        """Notify all registered callbacks."""
        for callback in self._change_callbacks:
            try:
                callback(operation)
            except Exception as e:
                # Don't let callback errors crash state manager
                print(f"Callback error: {e}")
    
    def export_state(self) -> Dict[str, Any]:
        """
        Export current state and metadata.
        
        Returns:
            Dictionary with state and history info
        """
        return {
            "state": self._current_state,
            "history_size": len(self._history),
            "can_undo": self.can_undo,
            "can_redo": self.can_redo,
            "last_operation": self._history[-1].operation if self._history else None
        }
