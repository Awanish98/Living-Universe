"""Dynamic environmental events affecting world physics, resources, and organisms."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class WorldEvent:
    id: int
    type: str  # "FOOD_BLOOM", "DROUGHT", "HEAT_WAVE", "COLD_SNAP", "TOXIC_FALLOUT", "METEOR_IMPACT"
    start_tick: int
    duration: int
    elapsed: int = 0
    x: Optional[float] = None
    y: Optional[float] = None
    radius: Optional[float] = None
    intensity: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_finished(self) -> bool:
        return self.elapsed >= self.duration

    def tick_step(self) -> None:
        self.elapsed += 1

    def progress(self) -> float:
        """Normalized 0.0 to 1.0 progress of the event."""
        if self.duration <= 0:
            return 1.0
        return min(1.0, self.elapsed / self.duration)
