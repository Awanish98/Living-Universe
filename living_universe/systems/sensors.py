"""Sensory perception system for biological vision and spatial awareness."""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import math
from ..entities.organism import Organism
from ..entities.resource import Resource
from ..systems.spatial_grid import SpatialGrid


@dataclass
class SensoryPerception:
    nearest_food: Optional[Resource] = None
    food_dist: float = float("inf")
    nearest_threat: Optional[Organism] = None
    threat_dist: float = float("inf")
    nearest_prey: Optional[Organism] = None
    prey_dist: float = float("inf")
    nearest_mate: Optional[Organism] = None
    mate_dist: float = float("inf")
    flock_neighbors: List[Organism] = field(default_factory=list)
    sensed_signals: List[Tuple[str, float, float]] = field(default_factory=list)  # (type, x, y)


class SensorSystem:
    """Computes sensory percepts for each organism using spatial hash grids."""

    def sense(
        self,
        org: Organism,
        organism_grid: SpatialGrid,
        resource_grid: SpatialGrid,
        active_signals: Optional[List[Tuple[str, float, float, int]]] = None,
    ) -> SensoryPerception:
        percept = SensoryPerception()
        vision = org.dna.vision_range

        # 1. Sense Resources
        nearby_resources = resource_grid.nearby(org.x, org.y, vision)
        for res in nearby_resources:
            # Check diet compatibility (carnivores prioritize meat or skip plants)
            if org.dna.is_carnivore() and res.resource_type == "plant":
                continue
            dx = res.x - org.x
            dy = res.y - org.y
            dist = math.hypot(dx, dy)
            if dist < percept.food_dist:
                percept.food_dist = dist
                percept.nearest_food = res

        # 2. Sense other organisms
        nearby_orgs = organism_grid.nearby(org.x, org.y, vision)
        for other in nearby_orgs:
            if other.id == org.id or not other.alive:
                continue

            dx = other.x - org.x
            dy = other.y - org.y
            dist = math.hypot(dx, dy)
            if dist > vision:
                continue

            # Threat detection: other is more aggressive and larger or is carnivore
            is_predator = (
                (other.dna.is_carnivore() or other.dna.aggression > 0.6)
                and (other.dna.size >= org.dna.size * 0.9)
                and other.species_id != org.species_id
            )
            if is_predator and dist < percept.threat_dist:
                percept.threat_dist = dist
                percept.nearest_threat = other

            # Prey detection: self is carnivore/aggressive, other is smaller/weaker
            is_prey = (
                (org.dna.is_carnivore() or org.dna.aggression > 0.5)
                and (org.dna.size > other.dna.size * 0.95 or org.dna.aggression > other.dna.aggression + 0.3)
                and other.species_id != org.species_id
            )
            if is_prey and dist < percept.prey_dist:
                percept.prey_dist = dist
                percept.nearest_prey = other

            # Mate detection: same species, both eligible
            if (
                other.species_id == org.species_id
                and org.is_eligible_for_reproduction()
                and other.is_eligible_for_reproduction()
            ):
                if dist < percept.mate_dist:
                    percept.mate_dist = dist
                    percept.nearest_mate = other

            # Flocking neighbors: same species within social perception
            if other.species_id == org.species_id and dist < vision * 0.7:
                percept.flock_neighbors.append(other)

        # 3. Sense nearby communication signals
        if active_signals:
            for sig_type, sx, sy, radius in active_signals:
                dx = sx - org.x
                dy = sy - org.y
                if math.hypot(dx, dy) <= radius:
                    percept.sensed_signals.append((sig_type, sx, sy))

        return percept
