"""Real-time HUD sparkline and telemetry graphing components for Pygame surfaces."""

from typing import List, Tuple
import pygame
from ..analytics.history import SimulationHistory


class MiniChart:
    """Renders real-time telemetry graphs on Pygame surfaces."""

    def __init__(self, width: int = 240, height: int = 90):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)

    def draw_history(
        self,
        history: SimulationHistory,
        title: str = "POPULATION DYNAMICS",
    ) -> pygame.Surface:
        self.surface.fill((12, 16, 26, 200))
        pygame.draw.rect(self.surface, (30, 42, 64), (0, 0, self.width, self.height), 1)

        pop_data = history.get_series("population")
        food_data = history.get_series("food_count")
        carn_data = history.get_series("carnivores")

        if len(pop_data) < 2:
            return self.surface

        max_val = max(10, max(pop_data), max(food_data) if food_data else 10)

        # Plot Food line (Greenish)
        self._plot_line(food_data, max_val, (60, 200, 100), 1)
        # Plot Population line (Cyan)
        self._plot_line(pop_data, max_val, (0, 220, 255), 2)
        # Plot Carnivore line (Red)
        if carn_data:
            self._plot_line(carn_data, max_val, (255, 70, 70), 1)

        return self.surface

    def _plot_line(self, data: List[float | int], max_val: float, color: Tuple[int, int, int], width: int):
        n = len(data)
        if n < 2:
            return

        points = []
        step_x = (self.width - 10) / max(1, n - 1)

        for i, val in enumerate(data):
            px = 5 + int(i * step_x)
            norm = min(1.0, max(0.0, val / max_val))
            py = int((self.height - 10) - (norm * (self.height - 20))) + 5
            points.append((px, py))

        if len(points) >= 2:
            pygame.draw.lines(self.surface, color, False, points, width)
