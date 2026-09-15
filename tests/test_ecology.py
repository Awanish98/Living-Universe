"""Unit tests for foraging, predator attacks, and carrion generation."""

from living_universe.config import UniverseConfig
from living_universe.entities.organism import Organism
from living_universe.entities.resource import Resource
from living_universe.entities.dna import DNA
from living_universe.systems.spatial_grid import SpatialGrid
from living_universe.systems.ecology import EcologySystem


def test_herbivore_foraging():
    config = UniverseConfig()
    eco_sys = EcologySystem(config)
    org_grid = SpatialGrid(64)
    res_grid = SpatialGrid(64)

    # Hungry herbivore
    herb = Organism(
        id=1,
        species_id=1,
        x=100.0,
        y=100.0,
        generation=1,
        energy=20.0,
        dna=DNA(diet_preference=0.0, size=4.0),
    )
    # Plant food right at same location
    food = Resource(id=1, x=100.0, y=100.0, energy=30.0, resource_type="plant")

    org_grid.insert(herb, herb.x, herb.y)
    res_grid.insert(food, food.x, food.y)

    remaining, carcasses, kills = eco_sys.update(
        [herb], [food], org_grid, res_grid, next_resource_id=2
    )

    assert len(remaining) == 0  # Food was consumed
    assert herb.energy > 20.0  # Energy gained


def test_carnivore_predation_and_kill():
    config = UniverseConfig(carnivore_bite_damage=50.0)
    eco_sys = EcologySystem(config)
    org_grid = SpatialGrid(64)
    res_grid = SpatialGrid(64)

    carn = Organism(
        id=1,
        species_id=1,
        x=200.0,
        y=200.0,
        generation=1,
        energy=50.0,
        dna=DNA(diet_preference=1.0, aggression=0.9, size=6.0),
    )
    prey = Organism(
        id=2,
        species_id=2,  # Different species
        x=202.0,
        y=200.0,
        generation=1,
        health=20.0,  # Low health will die from one bite
        dna=DNA(diet_preference=0.0, aggression=0.1, size=3.0),
    )

    org_grid.insert(carn, carn.x, carn.y)
    org_grid.insert(prey, prey.x, prey.y)

    remaining, carcasses, kills = eco_sys.update(
        [carn, prey], [], org_grid, res_grid, next_resource_id=1
    )

    assert prey.alive is False
    assert kills == 1
    assert carn.kills == 1
    assert len(carcasses) >= 1
    assert carcasses[0].resource_type == "meat"
