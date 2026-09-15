"""Rolling time-series history for telemetry visualization and graphing."""

from collections import deque
from typing import Dict, List, Any


class SimulationHistory:
    """Maintains fixed-window time-series data for analytics charts and HUD rendering."""

    def __init__(self, capacity: int = 300):
        self.capacity = capacity
        self.ticks = deque(maxlen=capacity)
        self.population = deque(maxlen=capacity)
        self.species_count = deque(maxlen=capacity)
        self.avg_energy = deque(maxlen=capacity)
        self.herbivores = deque(maxlen=capacity)
        self.carnivores = deque(maxlen=capacity)
        self.food_count = deque(maxlen=capacity)
        self.shannon_diversity = deque(maxlen=capacity)

    def record(self, tick: int, metrics: Dict[str, Any], food_count: int) -> None:
        self.ticks.append(tick)
        self.population.append(metrics.get("population", 0))
        self.species_count.append(metrics.get("species_count", 0))
        self.avg_energy.append(metrics.get("average_energy", 0.0))
        self.herbivores.append(metrics.get("herbivores", 0))
        self.carnivores.append(metrics.get("carnivores", 0))
        self.food_count.append(food_count)
        self.shannon_diversity.append(metrics.get("shannon_diversity", 0.0))

    def get_series(self, key: str) -> List[Any]:
        return list(getattr(self, key, []))

    def clear(self) -> None:
        self.ticks.clear()
        self.population.clear()
        self.species_count.clear()
        self.avg_energy.clear()
        self.herbivores.clear()
        self.carnivores.clear()
        self.food_count.clear()
        self.shannon_diversity.clear()
