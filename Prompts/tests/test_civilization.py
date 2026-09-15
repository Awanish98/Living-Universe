"""Unit tests for Virtual Human Civilizations, settlements, buildings, and technology tree."""

import pytest
from living_universe.entities.human import HumanAgent, Profession, HumanDNA, HumanNeeds
from living_universe.entities.building import Building, BuildingType
from living_universe.entities.settlement import Settlement
from living_universe.systems.civilization import Civilization, TechEra, TECH_TREE
from living_universe.systems.seasons import SeasonSystem, Season
from living_universe.core.engine import UniverseEngine
from living_universe.config import UniverseConfig


def test_human_lifecycle_and_needs():
    dna = HumanDNA(strength=1.2, intellect=1.3, lifespan_potential=80.0)
    human = HumanAgent(
        agent_id=1,
        name="Elysia Greenhand",
        civilization_id=1,
        settlement_id=1,
        x=100.0,
        y=100.0,
        age=20.0,
        profession=Profession.FARMER,
        dna=dna,
    )

    assert human.alive
    assert human.is_adult
    assert human.profession == Profession.FARMER

    # Step lifecycle under warm spring climate
    human.step_lifecycle(temp_celsius=20.0, is_night=False)
    assert human.age > 20.0
    assert human.needs.hunger < 85.0  # Decayed hunger


def test_building_construction_and_farming():
    building = Building(
        building_id=1,
        building_type=BuildingType.HUT,
        x=150.0,
        y=150.0,
        settlement_id=1,
        civilization_id=1,
        completed=False,
    )

    assert not building.completed
    assert not building.is_materials_ready

    # Deliver materials
    building.add_materials(wood=building.wood_cost, stone=building.stone_cost)
    assert building.is_materials_ready

    # Apply construction work
    finished = building.work_on_construction(building.build_work)
    assert finished
    assert building.completed


def test_civilization_tech_tree_and_research():
    civ = Civilization(
        civ_id=1,
        name="Verdantia",
        color_rgb=[16, 240, 120],
        ai_faction_name="Gemini",
        philosophy="Agrarian",
        founder_traits={},
    )

    assert civ.has_tech("fire_making")
    assert civ.current_era == TechEra.NEOLITHIC

    # Add research points to discover agriculture
    discovered = civ.add_research_points(100.0)
    assert discovered == "agriculture"
    assert civ.has_tech("agriculture")
    assert civ.get_bonus("farm_yield") > 1.0


def test_engine_human_civilization_simulation():
    config = UniverseConfig(width=1000, height=1000, initial_organisms=20, initial_resources=40)
    engine = UniverseEngine(config)

    assert len(engine.civilizations) == 4
    assert len(engine.settlements) == 4
    assert len(engine.humans) == 4  # The 4 Grand AI Explorers

    # Step engine 15 times
    for _ in range(15):
        engine.step()

    snap = engine.snapshot()
    assert snap.population >= 20
    assert len(engine.humans) == 4
    assert engine.seasons.current_season in (Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER)
