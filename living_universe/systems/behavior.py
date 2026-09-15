"""Neural-driven behavior execution and sensory integration system."""

import math
import random
from typing import Tuple, List, Optional
from ..entities.organism import Organism
from ..systems.sensors import SensoryPerception
from ..core.world import World


class BehaviorSystem:
    """Evaluates sensory cues and feeds neural brains to produce autonomous decisions."""

    def __init__(self, rng: random.Random):
        self.rng = rng

    def decide_and_act(
        self,
        org: Organism,
        percept: SensoryPerception,
        current_tick: int,
        world: Optional[World] = None,
    ) -> None:
        if not org.alive:
            return

        vis = max(10.0, org.dna.vision_range)
        ambient_temp = world.get_temperature_at(org.x, org.y, current_tick) if world else 22.0
        solar = world.solar_irradiance if world else 1.0

        # Build 12-dimensional continuous sensory input vector
        # 0, 1: Nearest food vector
        if percept.nearest_food:
            food_dx = (percept.nearest_food.x - org.x) / vis
            food_dy = (percept.nearest_food.y - org.y) / vis
        else:
            food_dx, food_dy = 0.0, 0.0

        # 2, 3: Nearest organism vector
        target_org = percept.nearest_threat or percept.nearest_mate or percept.nearest_prey
        if target_org:
            org_dx = (target_org.x - org.x) / vis
            org_dy = (target_org.y - org.y) / vis
            
            # 4: Kin / Threat affinity
            if percept.nearest_threat:
                affinity = -1.0
            elif percept.nearest_mate:
                affinity = 0.8
            elif percept.nearest_prey:
                affinity = -0.4  # prey target
            elif target_org.species_id == org.species_id:
                affinity = 0.5   # flock kin
            else:
                affinity = 0.0

            # 5: Relative size
            rel_size = (target_org.dna.size / max(0.1, org.dna.size)) - 1.0
        else:
            org_dx, org_dy = 0.0, 0.0
            affinity = 0.0
            rel_size = 0.0

        # 6: Energy ratio
        energy_ratio = org.energy / max(1.0, org.max_energy)
        # 7: Health ratio
        health_ratio = org.health / max(1.0, org.max_health)
        # 8: Reproductive maturity urge
        repro_urge = 1.0 if org.is_eligible_for_reproduction() else 0.0
        # 9: Thermal stress in local biome
        thermal_stress = org.calculate_thermal_stress(ambient_temp)
        # 10: Ambient solar illumination
        light_level = solar
        # 11: Bias
        bias = 1.0

        sensory_vector = [
            food_dx,
            food_dy,
            org_dx,
            org_dy,
            affinity,
            rel_size,
            energy_ratio,
            health_ratio,
            repro_urge,
            thermal_stress,
            light_level,
            bias,
        ]

        # Execute neural brain forward pass
        org.execute_brain_decision(sensory_vector)

        # Flocking social bias if in kin group and sociability is high
        if percept.flock_neighbors and org.dna.sociability > 0.4:
            flock_ax, flock_ay = self._flock_steering(org, percept.flock_neighbors)
            org.ax += flock_ax * org.dna.sociability * 0.35
            org.ay += flock_ay * org.dna.sociability * 0.35

    def _flock_steering(self, org: Organism, neighbors: List[Organism]) -> Tuple[float, float]:
        if not neighbors:
            return 0.0, 0.0

        align_vx, align_vy = 0.0, 0.0
        center_x, center_y = 0.0, 0.0
        sep_x, sep_y = 0.0, 0.0
        count = len(neighbors)
        min_dist = org.radius * 2.2

        for other in neighbors:
            align_vx += other.vx
            align_vy += other.vy
            center_x += other.x
            center_y += other.y
            
            dx = org.x - other.x
            dy = org.y - other.y
            d = math.hypot(dx, dy)
            if 0.001 < d < min_dist:
                sep_x += (dx / d) * (min_dist - d)
                sep_y += (dy / d) * (min_dist - d)

        align_vx /= count
        align_vy /= count
        center_x /= count
        center_y /= count

        to_center_x = (center_x - org.x) * 0.05
        to_center_y = (center_y - org.y) * 0.05

        return (sep_x * 0.8 + align_vx * 0.3 + to_center_x * 0.2), (sep_y * 0.8 + align_vy * 0.3 + to_center_y * 0.2)
