"""Ecosystem interactions: closed-loop nutrient cycling, autotrophic plant growth, and predation."""

from typing import List, Tuple, Set, Optional, Any
import math
import random
from ..entities.organism import Organism
from ..entities.resource import Resource
from ..systems.spatial_grid import SpatialGrid
from ..core.world import World
from ..config import UniverseConfig


class EcologySystem:
    """Manages biogeochemical nutrient cycling, plant photosynthesis, foraging, and predation."""

    def __init__(self, config: UniverseConfig, rng: Optional[random.Random] = None):
        self.config = config
        self.rng = rng or random.Random(config.seed)

    def update(
        self,
        organisms: List[Organism],
        resources: List[Resource],
        organism_grid: SpatialGrid,
        resource_grid: SpatialGrid,
        world_or_next_id: Any = None,
        next_resource_id: Optional[int] = None,
        tick: int = 0,
    ) -> Tuple[List[Resource], List[Resource], int]:
        """
        Execute closed nutrient-energy loop:
        1. Organic foraging & digestion
        2. Armor-mitigated predation combat
        3. Carcass decay recycling nutrients back into soil
        4. Autotrophic plant emergence powered by soil nutrients & sunlight
        """
        if isinstance(world_or_next_id, int):
            # Called via legacy signature: (organisms, resources, org_grid, res_grid, next_resource_id)
            res_id = world_or_next_id
            world: Optional[World] = None
        else:
            world = world_or_next_id
            res_id = next_resource_id if next_resource_id is not None else 1

        eaten_resource_ids: Set[int] = set()
        new_resources: List[Resource] = []
        kills_count = 0

        # 1. Resource Consumption (Foraging & Scavenging)
        for org in organisms:
            if not org.alive or org.energy >= org.max_energy:
                continue

            nearby_res = resource_grid.nearby(org.x, org.y, org.radius + 8.0)
            for res in nearby_res:
                if res.id in eaten_resource_ids:
                    continue

                dx = res.x - org.x
                dy = res.y - org.y
                dist = math.hypot(dx, dy)
                if dist <= (org.radius + res.radius):
                    # Check digestive enzyme diet compatibility
                    can_eat = False
                    if res.resource_type == "plant" and (org.dna.is_herbivore() or not org.dna.is_carnivore()):
                        can_eat = True
                    elif res.resource_type == "meat" and (org.dna.is_carnivore() or not org.dna.is_herbivore()):
                        can_eat = True

                    if can_eat:
                        extracted_energy = res.energy * org.dna.efficiency
                        org.energy = min(org.max_energy, org.energy + extracted_energy)
                        org.food_consumed += res.energy
                        org.last_reward += 1.2
                        eaten_resource_ids.add(res.id)

                        # Excrete metabolic waste returning minerals to soil
                        if world and hasattr(world, "nutrients") and world.nutrients:
                            waste_minerals = res.energy * (1.0 - org.dna.efficiency) * 0.5
                            world.nutrients.add_nutrients(org.x, org.y, waste_minerals)
                        break

        # 2. Carcass Decay & Soil Mineralization
        remaining_resources: List[Resource] = []
        for r in resources:
            if r.id in eaten_resource_ids:
                continue

            # Decay carcasses over time into soil nutrients
            if r.decay_timer is not None:
                r.decay_timer -= 1
                if r.decay_timer <= 0:
                    if world and hasattr(world, "nutrients") and world.nutrients:
                        world.nutrients.add_nutrients(r.x, r.y, r.energy * 0.8)
                    continue

            remaining_resources.append(r)

        # 3. Predation & Combat
        for org in organisms:
            if not org.alive or not (org.dna.is_carnivore() or org.dna.aggression > 0.45):
                continue

            nearby_targets = organism_grid.nearby(org.x, org.y, org.radius + 10.0)
            for prey in nearby_targets:
                if prey.id == org.id or not prey.alive or prey.species_id == org.species_id:
                    continue

                dx = prey.x - org.x
                dy = prey.y - org.y
                dist = math.hypot(dx, dy)
                if dist <= (org.radius + prey.radius + 3.0):
                    raw_damage = (
                        self.config.carnivore_bite_damage
                        * org.dna.aggression
                        * (org.dna.size / max(1.0, prey.dna.size))
                    )
                    
                    actual_damage = prey.take_damage(raw_damage)
                    org.energy = min(org.max_energy, org.energy + actual_damage * 0.3 * org.dna.efficiency)
                    prey.last_reward -= 0.8

                    if not prey.alive:
                        kills_count += 1
                        org.kills += 1
                        org.last_reward += 3.0

                        meat_value = prey.max_energy * 0.65
                        org.energy = min(org.max_energy, org.energy + meat_value * 0.5 * org.dna.efficiency)

                        new_resources.append(Resource(
                            id=res_id,
                            x=prey.x,
                            y=prey.y,
                            energy=meat_value * 0.5,
                            resource_type="meat",
                            decay_timer=900,
                            radius=max(3.0, prey.dna.size * 0.8),
                        ))
                        res_id += 1
                    break

        # 4. Photosynthetic Autotrophic Plant Emergence
        if world and hasattr(world, "nutrients") and world.nutrients:
            if tick % 6 == 0 and len(remaining_resources) < self.config.max_resources:
                spawn_attempts = 4
                for _ in range(spawn_attempts):
                    rx = self.rng.uniform(20.0, world.width - 20.0)
                    ry = self.rng.uniform(20.0, world.height - 20.0)
                    
                    zone = world.get_zone_at(rx, ry)
                    moisture = zone.moisture if zone else 0.5
                    multiplier = zone.food_multiplier if zone else 1.0
                    
                    local_nutrient = world.nutrients.get_at(rx, ry)
                    growth_chance = (local_nutrient / 100.0) * world.solar_irradiance * moisture * multiplier
                    
                    if self.rng.random() < growth_chance * 0.4:
                        extracted = world.nutrients.extract_nutrients(rx, ry, self.config.food_energy_value * 0.6)
                        plant_energy = max(10.0, extracted + 15.0)
                        new_resources.append(Resource(
                            id=res_id,
                            x=rx,
                            y=ry,
                            energy=plant_energy,
                            resource_type="plant",
                            decay_timer=None,
                            radius=self.rng.uniform(2.5, 4.5),
                        ))
                        res_id += 1

        return remaining_resources, new_resources, kills_count
