"""World state snapshot representation for analytics, UI, and AI reasoning."""

from dataclasses import dataclass, asdict, field
from typing import Dict, List, Any, Optional


@dataclass
class WorldSnapshot:
    tick: int
    population: int
    species_count: int
    average_energy: float
    average_health: float = 100.0
    average_age: float = 0.0
    births: int = 0
    deaths: int = 0
    food_count: int = 0
    herbivore_count: int = 0
    carnivore_count: int = 0
    dominant_traits: Dict[str, float] = field(default_factory=dict)
    species_breakdown: List[Dict[str, Any]] = field(default_factory=list)
    active_events: List[Dict[str, Any]] = field(default_factory=list)
    temperature: float = 20.0
    day_phase: float = 0.5  # 0.0 to 1.0 (0=midnight, 0.5=noon)
    sim_speed: float = 1.0
    ai_status: str = "offline"
    ai_observation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_compact_dict(self) -> Dict[str, Any]:
        """Returns a condensed dictionary suitable for LLM prompt context."""
        return {
            "tick": self.tick,
            "population": self.population,
            "species": self.species_count,
            "food_count": self.food_count,
            "avg_energy": round(self.average_energy, 1),
            "avg_health": round(self.average_health, 1),
            "births": self.births,
            "deaths": self.deaths,
            "trophic_balance": {
                "herbivores": self.herbivore_count,
                "carnivores": self.carnivore_count,
            },
            "dominant_traits": {k: round(v, 2) for k, v in self.dominant_traits.items()},
            "active_events": [e.get("type", "UNKNOWN") for e in self.active_events],
            "temperature": round(self.temperature, 1),
        }
