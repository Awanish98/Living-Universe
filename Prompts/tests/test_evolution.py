"""Unit tests for genetics, mutation, reproduction, and speciation."""

import random
from living_universe.config import UniverseConfig
from living_universe.entities.dna import DNA
from living_universe.entities.species import Species
from living_universe.entities.organism import Organism
from living_universe.systems.spatial_grid import SpatialGrid
from living_universe.systems.evolution import EvolutionSystem


def test_dna_mutation():
    rng = random.Random(42)
    parent_dna = DNA(speed=1.5, vision_range=100.0, metabolism=1.0)
    child_dna = parent_dna.mutated_child(rng, rate=1.0, strength=0.2)
    
    assert child_dna.speed != parent_dna.speed or child_dna.vision_range != parent_dna.vision_range
    assert child_dna.speed >= 0.3
    assert child_dna.vision_range >= 30.0


def test_genetic_distance():
    dna1 = DNA(speed=1.0, aggression=0.1, size=4.0)
    dna2 = DNA(speed=1.0, aggression=0.1, size=4.0)
    dna3 = DNA(speed=3.0, aggression=0.9, size=9.0)

    assert dna1.genetic_distance(dna2) == 0.0
    assert dna1.genetic_distance(dna3) > 0.5


def test_evolution_system_reproduction_and_speciation():
    config = UniverseConfig(speciation_threshold=0.2, mutation_rate=0.5, mutation_strength=0.3)
    rng = random.Random(42)
    evo_sys = EvolutionSystem(config, rng)
    grid = SpatialGrid(64)

    species_registry = {
        1: Species(id=1, name="Proto-Species #1", representative_dna=DNA())
    }

    # High energy, mature organism eligible for reproduction
    parent = Organism(
        id=1,
        species_id=1,
        x=200,
        y=200,
        generation=1,
        energy=150.0,
        health=100.0,
        age=300,
        reproduction_cooldown=0,
        dna=DNA(),
    )

    offspring, next_org_id, next_sp_id, new_species = evo_sys.update(
        [parent], species_registry, grid, next_organism_id=2, next_species_id=2, current_tick=100
    )

    assert len(offspring) == 1
    assert offspring[0].parent_id == 1
    assert offspring[0].generation == 2
    assert parent.energy < 150.0
    assert parent.reproduction_cooldown > 0
