"""2D Pan, Zoom, and Entity-Tracking Camera System."""

from typing import Tuple, Optional
from ..entities.organism import Organism


class Camera2D:
    """Controls the viewport coordinate transformation, zoom scaling, and organism tracking."""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        self.zoom: float = 1.0
        self.min_zoom: float = 0.25
        self.max_zoom: float = 4.0
        self.target: Optional[Organism] = None

    def update(self) -> None:
        """Smoothly track target organism if locked."""
        if self.target and self.target.alive:
            target_offset_x = self.screen_width / 2.0 - self.target.x * self.zoom
            target_offset_y = self.screen_height / 2.0 - self.target.y * self.zoom
            # Smooth lerp
            self.offset_x += (target_offset_x - self.offset_x) * 0.1
            self.offset_y += (target_offset_y - self.offset_y) * 0.1
        elif self.target and not self.target.alive:
            self.target = None

    def pan(self, dx: float, dy: float) -> None:
        """Pan viewport by delta screen pixels."""
        self.target = None  # Detach target on manual pan
        self.offset_x += dx
        self.offset_y += dy

    def zoom_at(self, factor: float, screen_x: float, screen_y: float) -> None:
        """Zoom focused on a specific screen point."""
        old_zoom = self.zoom
        new_zoom = max(self.min_zoom, min(self.max_zoom, self.zoom * factor))
        if old_zoom == new_zoom:
            return

        # Adjust offsets so screen_x, screen_y remains fixed in world space
        world_x = (screen_x - self.offset_x) / old_zoom
        world_y = (screen_y - self.offset_y) / old_zoom

        self.zoom = new_zoom
        self.offset_x = screen_x - world_x * self.zoom
        self.offset_y = screen_y - world_y * self.zoom

    def world_to_screen(self, wx: float, wy: float) -> Tuple[int, int]:
        sx = int(wx * self.zoom + self.offset_x)
        sy = int(wy * self.zoom + self.offset_y)
        return sx, sy

    def screen_to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        wx = (sx - self.offset_x) / self.zoom
        wy = (sy - self.offset_y) / self.zoom
        return wx, wy

    def is_visible(self, wx: float, wy: float, radius: float = 10.0) -> bool:
        sx, sy = self.world_to_screen(wx, wy)
        margin = radius * self.zoom + 20.0
        return (
            -margin <= sx <= self.screen_width + margin
            and -margin <= sy <= self.screen_height + margin
        )

    def follow(self, organism: Optional[Organism]) -> None:
        self.target = organism
