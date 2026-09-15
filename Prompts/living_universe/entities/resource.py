"""
living_universe.entities.resource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Resource entity representing food, carrion, harvestable trees, and stone rocks.
"""

from dataclasses import dataclass
from typing import Literal, Optional, Dict, Any


ResourceType = Literal["plant", "meat", "mineral", "tree", "rock"]


@dataclass
class Resource:
    id: int
    x: float
    y: float
    energy: float = 25.0
    resource_type: ResourceType = "plant"
    decay_timer: Optional[int] = 1200  # Ticks until decay (None = permanent until harvested)
    radius: float = 3.0
    amount_remaining: float = 100.0  # For trees (wood) and rocks (stone)

    def is_expired(self) -> bool:
        if self.resource_type == "meat":
            return self.decay_timer is not None and self.decay_timer <= 0
        return self.amount_remaining <= 0.0

    def tick_decay(self) -> None:
        if self.decay_timer is not None and self.decay_timer > 0 and self.resource_type == "meat":
            self.decay_timer -= 1

    def harvest(self, amount: float) -> float:
        """Harvest material from tree or stone rock."""
        taken = min(self.amount_remaining, amount)
        self.amount_remaining -= taken
        return taken

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "type": self.resource_type,
            "energy": round(self.energy, 1),
            "amount": round(self.amount_remaining, 1),
            "radius": self.radius,
        }
