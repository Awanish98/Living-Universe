"""Unit tests for organism life cycle, metabolism, starvation, aging, and death."""

import pytest
from living_universe.config import UniverseConfig
from living_universe.core.world import World
from living_universe.entities.organism import Organism
from living_universe.entities.dna import DNA
from living_universe.systems.life import LifeSystem


def test_organism_metabolism_and_energy_depletion():
    config = UniverseConfig(base_metabolism=0.5, movement_energy_cost=0.1)
    world = World(width=1000, height=1000)
    life_sys = LifeSystem(config)

    org = Organism(
        id=1,
        species_id=1,
        x=500,
        y=500,
        generation=1,
        energy=50.0,
        health=100.0,
        dna=DNA(metabolism=1.0, size=4.0),
    )

    surviving, carcasses, births, deaths = life_sys.update([org], world, next_resource_id=1)
    assert len(surviving) == 1
    assert surviving[0].energy < 50.0
    assert surviving[0].age == 1


def test_organism_starvation_damage_and_death():
    config = UniverseConfig(starvation_damage=10.0)
    world = World(width=1000, height=1000)
    life_sys = LifeSystem(config)

    org = Organism(
        id=1,
        species_id=1,
        x=500,
        y=500,
        generation=1,
        energy=0.0,
        health=5.0,
        dna=DNA(metabolism=1.0),
    )

    surviving, carcasses, births, deaths = life_sys.update([org], world, next_resource_id=1)
    assert len(surviving) == 0
    assert deaths == 1
    assert len(carcasses) == 1
    assert carcasses[0].resource_type == "meat"


def test_organism_max_age_expiration():
    config = UniverseConfig()
    world = World(width=1000, height=1000)
    life_sys = LifeSystem(config)

    org = Organism(
        id=1,
        species_id=1,
        x=500,
        y=500,
        generation=1,
        energy=100.0,
        health=100.0,
        age=3000,  # Exceeds max_age
        max_age=2000,
    )

    surviving, carcasses, births, deaths = life_sys.update([org], world, next_resource_id=1)
    assert len(surviving) == 0
    assert deaths == 1
