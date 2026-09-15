"""Bounded spatial and episodic memory for living organisms."""

from collections import deque
from dataclasses import dataclass
from typing import List, Tuple, Optional, Any


@dataclass
class MemoryItem:
    memory_type: str  # "food", "danger", "mate", "signal"
    x: float
    y: float
    timestamp: int
    value: float = 1.0


class BoundedMemory:
    """Fixed-capacity memory buffer preserving recent salient environmental experiences."""

    def __init__(self, max_items: int = 16):
        self.max_items = max_items
        self.items: deque[MemoryItem] = deque(maxlen=max_items)

    def remember(self, memory_type: str, x: float, y: float, timestamp: int, value: float = 1.0) -> None:
        self.items.append(MemoryItem(memory_type, x, y, timestamp, value))

    def get_recent_by_type(self, memory_type: str, max_age: int = 600, current_tick: int = 0) -> List[MemoryItem]:
        """Retrieve recent unexpired memories of a specific type."""
        results = []
        for mem in self.items:
            if mem.memory_type == memory_type and (current_tick - mem.timestamp <= max_age):
                results.append(mem)
        return results

    def get_latest(self, memory_type: str) -> Optional[MemoryItem]:
        """Get most recent memory matching type."""
        for mem in reversed(self.items):
            if mem.memory_type == memory_type:
                return mem
        return None

    def recent(self) -> List[MemoryItem]:
        return list(self.items)

    def clear(self) -> None:
        self.items.clear()
