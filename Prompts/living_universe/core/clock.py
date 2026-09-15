"""Simulation clock and timing control for Living Universe."""

from dataclasses import dataclass


@dataclass
class SimulationClock:
    """Tracks discrete simulation ticks, speed scaling, and pause state."""
    tick: int = 0
    speed_multiplier: float = 1.0
    paused: bool = False
    
    def step(self) -> int:
        """Advance simulation tick by 1 if not paused."""
        if not self.paused:
            self.tick += 1
        return self.tick

    def set_speed(self, multiplier: float) -> None:
        """Set simulation speed multiplier (e.g. 0.5x, 1x, 2x, 5x, 10x)."""
        self.speed_multiplier = max(0.1, min(20.0, multiplier))

    def pause(self) -> None:
        """Pause simulation execution."""
        self.paused = True

    def resume(self) -> None:
        """Resume simulation execution."""
        self.paused = False

    def toggle_pause(self) -> bool:
        """Toggle paused state and return the new state."""
        self.paused = not self.paused
        return self.paused

    def reset(self) -> None:
        """Reset the clock counter to zero."""
        self.tick = 0
