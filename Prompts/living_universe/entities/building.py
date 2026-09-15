"""
living_universe.entities.building
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Constructible structures, infrastructure, and facilities in human settlements.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
import math


class BuildingType(str, Enum):
    CAMPFIRE = "campfire"
    HUT = "hut"
    HOUSE = "house"
    FARM_PLOT = "farm_plot"
    GRANARY = "granary"
    WORKSHOP = "workshop"
    LIBRARY = "library"
    WELL = "well"
    WATCHTOWER = "watchtower"
    PALISADE = "palisade"


BUILDING_SPECS: Dict[BuildingType, Dict[str, Any]] = {
    BuildingType.CAMPFIRE: {
        "name": "Campfire",
        "wood_cost": 15,
        "stone_cost": 5,
        "build_work": 30,
        "radius": 18,
        "warmth_radius": 120,
        "max_occupants": 8,
        "description": "Provides warmth, cooked meals, and evening social storytelling.",
    },
    BuildingType.HUT: {
        "name": "Thatch Hut",
        "wood_cost": 30,
        "stone_cost": 10,
        "build_work": 60,
        "radius": 22,
        "max_occupants": 4,
        "description": "Basic shelter protecting humans from rain, snow, and night cold.",
    },
    BuildingType.HOUSE: {
        "name": "Timber House",
        "wood_cost": 60,
        "stone_cost": 35,
        "build_work": 120,
        "radius": 28,
        "max_occupants": 6,
        "description": "Sturdy residential home boosting health recovery and family birth rates.",
    },
    BuildingType.FARM_PLOT: {
        "name": "Cultivated Farm",
        "wood_cost": 20,
        "stone_cost": 5,
        "build_work": 45,
        "radius": 32,
        "max_occupants": 4,
        "description": "Tilled agrarian plot producing recurring crops of wheat, corn, and herbs.",
    },
    BuildingType.GRANARY: {
        "name": "Granary & Storage",
        "wood_cost": 50,
        "stone_cost": 25,
        "build_work": 90,
        "radius": 26,
        "storage_capacity": 500,
        "description": "Communal storage for food, timber, stone, and crafted tools.",
    },
    BuildingType.WORKSHOP: {
        "name": "Tool Workshop",
        "wood_cost": 45,
        "stone_cost": 40,
        "build_work": 100,
        "radius": 25,
        "description": "Crafting bench producing stone axes, pickaxes, hoes, and protective garments.",
    },
    BuildingType.LIBRARY: {
        "name": "Academy & Library",
        "wood_cost": 70,
        "stone_cost": 60,
        "build_work": 150,
        "radius": 30,
        "description": "Scholarly sanctuary where sages generate research points and teach citizens.",
    },
    BuildingType.WELL: {
        "name": "Freshwater Well",
        "wood_cost": 15,
        "stone_cost": 30,
        "build_work": 50,
        "radius": 16,
        "description": "Provides clean drinking water, boosting settlement hygiene and health.",
    },
    BuildingType.WATCHTOWER: {
        "name": "Watchtower",
        "wood_cost": 40,
        "stone_cost": 30,
        "build_work": 80,
        "radius": 20,
        "defense_radius": 180,
        "description": "Early detection outpost defending villagers from predators and rival raids.",
    },
    BuildingType.PALISADE: {
        "name": "Defensive Palisade",
        "wood_cost": 25,
        "stone_cost": 10,
        "build_work": 40,
        "radius": 14,
        "description": "Wooden perimeter wall securing the settlement borders.",
    },
}


class Building:
    """Represents a physical structure built by humans inside a settlement."""

    def __init__(
        self,
        building_id: int,
        building_type: BuildingType,
        x: float,
        y: float,
        settlement_id: int,
        civilization_id: int,
        completed: bool = False,
    ):
        self.id = building_id
        self.type = building_type
        self.x = x
        self.y = y
        self.settlement_id = settlement_id
        self.civilization_id = civilization_id

        specs = BUILDING_SPECS.get(building_type, BUILDING_SPECS[BuildingType.HUT])
        self.name = specs["name"]
        self.wood_cost = specs["wood_cost"]
        self.stone_cost = specs["stone_cost"]
        self.build_work = specs["build_work"]
        self.radius = float(specs.get("radius", 20.0))
        self.max_occupants = specs.get("max_occupants", 4)
        self.warmth_radius = float(specs.get("warmth_radius", 0.0))

        self.wood_delivered = self.wood_cost if completed else 0
        self.stone_delivered = self.stone_cost if completed else 0
        self.construction_progress = float(self.build_work) if completed else 0.0
        self.completed = completed
        self.health = 100.0
        self.max_health = 100.0
        self.level = 1

        # Specialized state
        self.crop_growth = 0.0  # For farm plots (0.0 to 100.0)
        self.occupants: List[int] = []  # List of Human agent IDs
        self.stored_resources: Dict[str, float] = {
            "food": 0.0,
            "wood": 0.0,
            "stone": 0.0,
            "tools": 0.0,
        }

    @property
    def is_materials_ready(self) -> bool:
        return (
            self.wood_delivered >= self.wood_cost
            and self.stone_delivered >= self.stone_cost
        )

    def add_materials(self, wood: int = 0, stone: int = 0) -> None:
        self.wood_delivered = min(self.wood_cost, self.wood_delivered + wood)
        self.stone_delivered = min(self.stone_cost, self.stone_delivered + stone)

    def work_on_construction(self, work_amount: float) -> bool:
        """Apply builder labor. Returns True if building just finished."""
        if self.completed:
            return False
        if not self.is_materials_ready:
            return False

        self.construction_progress += work_amount
        if self.construction_progress >= self.build_work:
            self.construction_progress = float(self.build_work)
            self.completed = True
            return True
        return False

    def update_farm(self, growth_delta: float) -> float:
        """Update farm plot growth and return harvested food if ready."""
        if not self.completed or self.type != BuildingType.FARM_PLOT:
            return 0.0

        self.crop_growth += growth_delta
        if self.crop_growth >= 100.0:
            self.crop_growth = 0.0
            return 45.0  # Harvest yield
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "settlement_id": self.settlement_id,
            "civilization_id": self.civilization_id,
            "completed": self.completed,
            "progress": round((self.construction_progress / max(1.0, float(self.build_work))) * 100, 1),
            "health": round(self.health, 1),
            "level": self.level,
            "occupant_count": len(self.occupants),
            "crop_growth": round(self.crop_growth, 1) if self.type == BuildingType.FARM_PLOT else None,
            "radius": self.radius,
            "wood_delivered": self.wood_delivered,
            "wood_cost": self.wood_cost,
            "stone_delivered": self.stone_delivered,
            "stone_cost": self.stone_cost,
        }
