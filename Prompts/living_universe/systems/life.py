"""Life cycle system: metabolism, thermal stress, aging, healing, and mortality."""

from typing import List, Tuple, Optional
import math
from ..entities.organism import Organism
from ..entities.resource import Resource
from ..core.world import World
from ..config import UniverseConfig


class LifeSystem:
    """Calculates metabolic energy expenditure, thermal stress adaptation, senescence, and lifecycle transitions."""

    def __init__(self, config: UniverseConfig):
        self.config = config

    def update(
        self,
        organisms: List[Organism],
        world: World,
        next_resource_id: int,
    ) -> Tuple[List[Organism], List[Resource], int, int]:
        """
        Update lifecycles.
        Returns:
            surviving_organisms: list of organisms still alive
            new_carcasses: list of Resource meat pellets created from dying organisms
            births_count: 0 (tracked in evolution)
            deaths_count: number of organisms died this tick
        """
        surviving = []
        new_carcasses = []
        deaths_count = 0
        res_id = next_resource_id

        for org in organisms:
            if not org.alive:
                continue

            org.age += 1
            if org.reproduction_cooldown > 0:
                org.reproduction_cooldown -= 1
            if org.signal_cooldown > 0:
                org.signal_cooldown -= 1

            # 1. Base Metabolism Calculation
            speed_sq = org.vx * org.vx + org.vy * org.vy
            speed_factor = math.sqrt(speed_sq)
            
            # Base metabolic burn scaled by DNA traits (size, vision, speed capability, armor weight)
            metabolic_burn = (
                self.config.base_metabolism
                * org.dna.metabolism
                * (0.55 + 0.08 * org.dna.size + 0.05 * (org.dna.vision_range / 60.0) + org.dna.armor * 0.15)
            )
            movement_burn = self.config.movement_energy_cost * speed_factor * (org.mass / 12.0)
            total_burn = metabolic_burn + movement_burn

            # 2. Environmental Zone & Thermal Stress Adaptation
            local_temp = world.get_temperature_at(org.x, org.y, org.age)
            thermal_stress = org.calculate_thermal_stress(local_temp)
            if thermal_stress > 0.0:
                # Poorly adapted organisms burn extra energy attempting thermoregulation
                total_burn += thermal_stress * 0.35
                if thermal_stress > 0.6:
                    org.health -= thermal_stress * 0.15  # Thermal damage

            zone = world.get_zone_at(org.x, org.y)
            if zone and zone.hazard_damage > 0:
                org.take_damage(zone.hazard_damage)

            org.energy -= total_burn

            # 3. Starvation and Healing
            if org.energy <= 0.0:
                org.energy = 0.0
                org.health -= self.config.starvation_damage
            elif org.energy > (org.max_energy * 0.7) and org.health < org.max_health:
                heal_amount = min(self.config.natural_healing_rate, org.max_health - org.health)
                org.health += heal_amount
                org.energy -= heal_amount * 0.45

            # 4. Check Mortality (Senescence or fatal trauma)
            is_dead = (org.health <= 0.0) or (org.age >= org.max_age)
            if is_dead:
                org.alive = False
                deaths_count += 1

                # Spawn meat carcass and enrich soil with organic minerals
                carcass_energy = (org.max_energy * self.config.carrion_energy_ratio) * (org.dna.size / 4.0)
                if carcass_energy > 5.0:
                    new_carcasses.append(Resource(
                        id=res_id,
                        x=org.x,
                        y=org.y,
                        energy=carcass_energy,
                        resource_type="meat",
                        decay_timer=900,
                        radius=max(2.5, org.dna.size * 0.75),
                    ))
                    res_id += 1
                
                # Direct mineral return to nutrient grid
                world.nutrients.add_nutrients(org.x, org.y, carcass_energy * 0.4)
            else:
                surviving.append(org)

        return surviving, new_carcasses, 0, deaths_count
