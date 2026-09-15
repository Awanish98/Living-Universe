"""Custom world experiment: Custom zones and genetic battle."""

import os
import sys

# Ensure module path is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from living_universe import UniverseEngine, UniverseConfig, DNA, Species
from living_universe.core.world import EnvironmentalZone


def main():
    print("=" * 60)
    print("  LIVING UNIVERSE — CUSTOM WORLD EXPERIMENT")
    print("=" * 60)

    config = UniverseConfig(width=1600, height=900, initial_organisms=0, initial_resources=200, seed=777)
    engine = UniverseEngine(config)

    # 1. Add Custom Environmental Hazard Zones
    engine.world.zones.append(EnvironmentalZone(
        name="Plasma Rift",
        zone_type="toxic",
        x=800, y=450, radius=200,
        hazard_damage=0.4,
        food_multiplier=0.1,
    ))

    # 2. Register Custom Super-Predator Species
    pred_dna = DNA(
        speed=2.2,
        vision_range=180.0,
        metabolism=1.5,
        size=7.0,
        aggression=0.95,
        diet_preference=1.0,
        color_hue=0.0,  # Crimson
    )
    pred_sp = Species(id=10, name="Apex-Draconis #10", representative_dna=pred_dna)
    engine.species_registry[10] = pred_sp

    # 3. Register Custom High-Fertility Swarm Species
    swarm_dna = DNA(
        speed=1.6,
        vision_range=90.0,
        metabolism=0.7,
        size=2.8,
        fertility=0.9,
        sociability=0.9,
        aggression=0.05,
        diet_preference=0.0,
        color_hue=180.0,  # Cyan
    )
    swarm_sp = Species(id=20, name="Hyper-Swarm #20", representative_dna=swarm_dna)
    engine.species_registry[20] = swarm_sp

    # Spawn populations
    engine.spawn_organisms(count=15, species_id=10, x=300, y=300)
    engine.spawn_organisms(count=80, species_id=20, x=1200, y=600)
    engine.spawn_food(count=150)

    print("Simulating 500 ticks of Apex vs Swarm encounter...")
    for _ in range(500):
        engine.step()

    snap = engine.snapshot()
    print(f"Final Outcome:")
    print(f"  Population: {snap.population}")
    print(f"  Herbivores: {snap.herbivore_count} | Carnivores: {snap.carnivore_count}")
    print(f"  Births: +{snap.births} | Deaths: -{snap.deaths}")


if __name__ == "__main__":
    main()
