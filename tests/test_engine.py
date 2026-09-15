"""Unit tests for UniverseEngine lifecycle, reset, and world events."""

import pytest
from living_universe.config import UniverseConfig
from living_universe.core.engine import UniverseEngine
from living_universe.core.commands import WorldCommand, WorldAction


def test_engine_initialization():
    config = UniverseConfig(initial_organisms=50, initial_resources=100, seed=42)
    engine = UniverseEngine(config)
    
    assert len(engine.organisms) == 50
    assert len(engine.resources) == 100
    assert len(engine.species_registry) >= 3
    assert engine.clock.tick == 0


def test_engine_step_progression():
    config = UniverseConfig(initial_organisms=40, initial_resources=80, seed=42)
    engine = UniverseEngine(config)

    for _ in range(20):
        engine.step()

    snap = engine.snapshot()
    assert snap.tick == 20
    assert snap.population > 0


def test_engine_reset():
    config = UniverseConfig(initial_organisms=30, initial_resources=50, seed=99)
    engine = UniverseEngine(config)

    for _ in range(30):
        engine.step()

    assert engine.clock.tick == 30
    engine.reset(seed=99)
    assert engine.clock.tick == 0
    assert len(engine.organisms) == 30


def test_engine_apply_command():
    config = UniverseConfig(initial_organisms=20, initial_resources=20, seed=42)
    engine = UniverseEngine(config)

    cmd = WorldCommand(actions=[
        WorldAction(action="SET_FOOD_RATE", value=0.8),
        WorldAction(action="SPAWN_FOOD", count=25),
        WorldAction(action="PAUSE"),
    ])

    results = engine.apply_command(cmd)
    assert len(results) == 3
    assert engine.config.food_spawn_rate == 0.8
    assert engine.clock.paused is True
    assert len(engine.resources) >= 45
