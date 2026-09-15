"""Unit tests for world state serialization, saving, and loading."""

import os
from living_universe.config import UniverseConfig
from living_universe.core.engine import UniverseEngine


def test_save_and_load_roundtrip(tmp_path):
    config = UniverseConfig(initial_organisms=40, initial_resources=60, seed=123)
    engine = UniverseEngine(config)

    # Step simulation for a bit
    for _ in range(50):
        engine.step()

    original_snap = engine.snapshot()

    # Save to temp slot
    engine.save_manager.save_dir = str(tmp_path)
    engine.save("test_save_slot")

    # Create new engine and restore
    new_engine = UniverseEngine(UniverseConfig(initial_organisms=0, initial_resources=0))
    new_engine.save_manager.save_dir = str(tmp_path)
    new_engine.load("test_save_slot")

    restored_snap = new_engine.snapshot()

    assert restored_snap.tick == original_snap.tick
    assert restored_snap.population == original_snap.population
    assert restored_snap.food_count == original_snap.food_count
    assert len(new_engine.organisms) == len(engine.organisms)
