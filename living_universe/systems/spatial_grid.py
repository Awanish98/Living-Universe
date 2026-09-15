"""High-performance 2D Uniform Spatial Hash Grid for fast proximity queries."""

from typing import Dict, List, Tuple, Set, Any
import math


class SpatialGrid:
    """A 2D spatial hash grid supporting fast O(1) insertions and local proximity lookups."""

    def __init__(self, cell_size: int = 64):
        self.cell_size = max(16, cell_size)
        self.cells: Dict[Tuple[int, int], List[Any]] = {}

    def clear(self) -> None:
        """Clear all grid cells."""
        self.cells.clear()

    def insert(self, item: Any, x: float, y: float) -> None:
        """Insert an item into the spatial grid at (x, y)."""
        cx = int(x // self.cell_size)
        cy = int(y // self.cell_size)
        key = (cx, cy)
        if key not in self.cells:
            self.cells[key] = [item]
        else:
            self.cells[key].append(item)

    def nearby(self, x: float, y: float, radius: float) -> List[Any]:
        """Find all items within radius of (x, y)."""
        if radius <= 0:
            return []
        
        min_cx = int((x - radius) // self.cell_size)
        max_cx = int((x + radius) // self.cell_size)
        min_cy = int((y - radius) // self.cell_size)
        max_cy = int((y + radius) // self.cell_size)

        radius_sq = radius * radius
        results = []
        
        for cx in range(min_cx, max_cx + 1):
            for cy in range(min_cy, max_cy + 1):
                cell = self.cells.get((cx, cy))
                if cell:
                    for item in cell:
                        # If item has x, y attributes, check Euclidean distance
                        if hasattr(item, 'x') and hasattr(item, 'y'):
                            dx = item.x - x
                            dy = item.y - y
                            if dx * dx + dy * dy <= radius_sq:
                                results.append(item)
                        else:
                            results.append(item)
        return results

    def nearby_in_box(self, min_x: float, min_y: float, max_x: float, max_y: float) -> List[Any]:
        """Find all items within an axis-aligned bounding box."""
        min_cx = int(min_x // self.cell_size)
        max_cx = int(max_x // self.cell_size)
        min_cy = int(min_y // self.cell_size)
        max_cy = int(max_y // self.cell_size)

        results = []
        for cx in range(min_cx, max_cx + 1):
            for cy in range(min_cy, max_cy + 1):
                cell = self.cells.get((cx, cy))
                if cell:
                    for item in cell:
                        if hasattr(item, 'x') and hasattr(item, 'y'):
                            if min_x <= item.x <= max_x and min_y <= item.y <= max_y:
                                results.append(item)
                        else:
                            results.append(item)
        return results
