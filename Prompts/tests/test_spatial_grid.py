"""Unit tests for spatial hash grid insertion and radius queries."""

from living_universe.systems.spatial_grid import SpatialGrid
from living_universe.entities.organism import Organism


def test_spatial_grid_radius_lookup():
    grid = SpatialGrid(cell_size=64)
    org1 = Organism(id=1, species_id=1, x=100.0, y=100.0, generation=1)
    org2 = Organism(id=2, species_id=1, x=120.0, y=100.0, generation=1)
    org3 = Organism(id=3, species_id=1, x=500.0, y=500.0, generation=1)

    grid.insert(org1, org1.x, org1.y)
    grid.insert(org2, org2.x, org2.y)
    grid.insert(org3, org3.x, org3.y)

    # Search near (100, 100) with radius 50
    nearby = grid.nearby(100.0, 100.0, radius=50.0)
    nearby_ids = [o.id for o in nearby]

    assert 1 in nearby_ids
    assert 2 in nearby_ids
    assert 3 not in nearby_ids


def test_spatial_grid_clear():
    grid = SpatialGrid(cell_size=64)
    org = Organism(id=1, species_id=1, x=100.0, y=100.0, generation=1)
    grid.insert(org, org.x, org.y)
    assert len(grid.nearby(100.0, 100.0, radius=20.0)) == 1
    grid.clear()
    assert len(grid.nearby(100.0, 100.0, radius=20.0)) == 0
