"""Tests for neural brain controller, genetic cladistics, and biogeochemical nutrient systems."""

import pytest
import numpy as np
import random

from living_universe.config import UniverseConfig
from living_universe.entities.brain import NeuralBrain
from living_universe.entities.dna import DNA
from living_universe.entities.organism import Organism
from living_universe.entities.species import Species
from living_universe.core.world import World, NutrientField
from living_universe.core.engine import UniverseEngine
from living_universe.systems.ecology import EcologySystem
from living_universe.systems.evolution import EvolutionSystem


def test_neural_brain_forward_pass():
    brain = NeuralBrain()
    inputs = [0.5, -0.2, 0.8, 0.1, 0.5, 0.0, 0.9, 1.0, 0.0, 0.1, 1.0, 1.0]
    outputs = brain.forward(inputs)
    
    assert len(outputs) == 6
    thrust, steer, attack, eat, mate, signal = outputs
    assert 0.0 <= thrust <= 1.0
    assert -1.0 <= steer <= 1.0
    assert 0.0 <= attack <= 1.0
    assert 0.0 <= eat <= 1.0
    assert 0.0 <= mate <= 1.0
    assert 0.0 <= signal <= 1.0


def test_neural_brain_mutation_and_crossover():
    rng = random.Random(42)
    b1 = NeuralBrain()
    b2 = NeuralBrain()
    
    child_brain = b1.crossover(b2, rng=rng)
    assert len(child_brain.weights) == NeuralBrain.TOTAL_WEIGHTS
    
    mutated = child_brain.mutate(rate=0.2, strength=0.3, rng=rng)
    assert len(mutated.weights) == NeuralBrain.TOTAL_WEIGHTS
    assert not np.array_equal(child_brain.weights, mutated.weights)


def test_dna_with_brain_and_traits():
    rng = random.Random(42)
    dna = DNA(speed=2.0, armor=0.4, thermal_optimum=28.0)
    assert dna.brain_weights is not None
    assert len(dna.brain_weights) == NeuralBrain.TOTAL_WEIGHTS

    child_dna = dna.mutated_child(rng, rate=0.1, strength=0.1)
    assert child_dna.brain_weights is not None
    assert len(child_dna.brain_weights) == NeuralBrain.TOTAL_WEIGHTS
    assert child_dna.armor >= 0.0


def test_biogeochemical_nutrient_field():
    nutrients = NutrientField(width=1000, height=800, cols=20, rows=16)
    initial_val = nutrients.get_at(500, 400)
    assert initial_val > 0.0

    nutrients.add_nutrients(500, 400, 30.0)
    assert nutrients.get_at(500, 400) > initial_val

    extracted = nutrients.extract_nutrients(500, 400, 15.0)
    assert extracted == 15.0

    nutrients.diffuse_and_cycle(diffusion_rate=0.1)
    assert nutrients.get_at(500, 400) > 0.0


def test_organism_armor_and_thermal_mechanics():
    dna = DNA(armor=0.5, thermal_optimum=20.0, thermal_tolerance=10.0)
    org = Organism(id=1, species_id=1, x=100, y=100, generation=1, dna=dna)

    # Damage absorption with armor
    damage_taken = org.take_damage(50.0)
    assert damage_taken == 25.0  # 50% armor reduction
    assert org.health == 75.0

    # Thermal stress
    stress_normal = org.calculate_thermal_stress(25.0)  # within 10-30°C buffer
    assert stress_normal == 0.0

    stress_extreme = org.calculate_thermal_stress(45.0)  # 25°C diff > 10°C buffer
    assert stress_extreme > 0.0


def test_speciation_cladogenesis():
    config = UniverseConfig()
    rng = random.Random(42)
    evo = EvolutionSystem(config, rng)
    
    parent_dna = DNA(speed=1.0, diet_preference=0.0, aggression=0.1)
    parent_sp = Species(id=1, name="Grazer primus", representative_dna=parent_dna, depth=0)
    registry = {1: parent_sp}

    parent_org = Organism(
        id=1,
        species_id=1,
        x=200,
        y=200,
        generation=1,
        dna=parent_dna,
        energy=150.0,
        max_energy=150.0,
        age=200,
        reproduction_cooldown=0,
    )
    from living_universe.systems.spatial_grid import SpatialGrid
    grid = SpatialGrid(50.0)
    grid.insert(parent_org, 200, 200)

    # Force drastic mutation to trigger speciation
    config.mutation_rate = 1.0
    config.mutation_strength = 2.5
    config.speciation_threshold = 0.3

    offspring, next_oid, next_sid, new_sp = evo.update(
        [parent_org], registry, grid, next_organism_id=2, next_species_id=2, current_tick=100
    )

    assert len(offspring) > 0
    assert len(new_sp) > 0
    assert new_sp[0].depth == 1
    assert new_sp[0].ancestor_species_id == 1


def test_universe_engine_neural_biosphere_loop():
    config = UniverseConfig(initial_organisms=40, initial_resources=60)
    engine = UniverseEngine(config)

    assert len(engine.organisms) == 40
    assert len(engine.resources) == 60
    assert len(engine.species_registry) >= 3

    # Step simulation for 50 ticks
    for _ in range(50):
        engine.step()

    snap = engine.snapshot()
    assert snap.tick == 50
    assert snap.population > 0
    assert snap.species_count >= 3

