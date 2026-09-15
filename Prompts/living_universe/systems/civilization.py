"""
living_universe.systems.civilization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Human civilizations, technology tree progression, shared warehouses, and culture.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
import time


class TechEra(str, Enum):
    NEOLITHIC = "Neolithic Age"
    BRONZE = "Bronze Age"
    IRON = "Iron Age"
    CLASSICAL = "Classical Age"


TECH_TREE: Dict[str, Dict[str, Any]] = {
    # Neolithic Age
    "fire_making": {
        "name": "Fire Mastery",
        "era": TechEra.NEOLITHIC,
        "cost": 50,
        "prereqs": [],
        "description": "Enables campfires, cooked nourishment, and night warmth.",
        "bonuses": {"warmth_mult": 1.5, "cooking_efficiency": 1.3},
    },
    "agriculture": {
        "name": "Crop Domestication",
        "era": TechEra.NEOLITHIC,
        "cost": 80,
        "prereqs": ["fire_making"],
        "description": "Unlocks farm plots for cultivating wheat, corn, and medicinal herbs.",
        "bonuses": {"farm_yield": 1.4},
    },
    "thatch_masonry": {
        "name": "Shelter Construction",
        "era": TechEra.NEOLITHIC,
        "cost": 70,
        "prereqs": ["fire_making"],
        "description": "Enables building huts and wooden communal granaries.",
        "bonuses": {"build_speed": 1.25, "shelter_capacity": 1.5},
    },
    "flint_knapping": {
        "name": "Stone Tools",
        "era": TechEra.NEOLITHIC,
        "cost": 60,
        "prereqs": [],
        "description": "Flint axes and pickaxes double woodcutting and stone quarrying yields.",
        "bonuses": {"harvest_speed": 1.5},
    },

    # Bronze Age
    "bronze_metallurgy": {
        "name": "Bronze Smelting",
        "era": TechEra.BRONZE,
        "cost": 150,
        "prereqs": ["flint_knapping", "agriculture"],
        "description": "Forging copper-tin alloys for heavy-duty tools and workshops.",
        "bonuses": {"harvest_speed": 2.0, "tool_durability": 2.0},
    },
    "irrigation": {
        "name": "Canals & Irrigation",
        "era": TechEra.BRONZE,
        "cost": 140,
        "prereqs": ["agriculture"],
        "description": "Advanced aqueducts boost farm harvests and drought resistance.",
        "bonuses": {"farm_yield": 1.8},
    },
    "timber_architecture": {
        "name": "Timber Framed Houses",
        "era": TechEra.BRONZE,
        "cost": 160,
        "prereqs": ["thatch_masonry"],
        "description": "Construct large timber residences and defensive palisade walls.",
        "bonuses": {"health_regen": 1.4, "defense": 1.5},
    },
    "written_lore": {
        "name": "Written Script & Lore",
        "era": TechEra.BRONZE,
        "cost": 180,
        "prereqs": ["fire_making"],
        "description": "Enables libraries and academy research desks to rapidly generate science.",
        "bonuses": {"research_speed": 1.6, "skill_learning_rate": 1.5},
    },

    # Iron Age
    "iron_forging": {
        "name": "Master Ironworking",
        "era": TechEra.IRON,
        "cost": 300,
        "prereqs": ["bronze_metallurgy"],
        "description": "Superior iron axes, plows, and armor protecting citizens.",
        "bonuses": {"harvest_speed": 2.5, "defense": 2.0},
    },
    "stone_fortifications": {
        "name": "Stone Masonry & Towers",
        "era": TechEra.IRON,
        "cost": 280,
        "prereqs": ["timber_architecture"],
        "description": "Erect stone watchtowers and reinforced granaries.",
        "bonuses": {"build_speed": 1.5, "defense": 2.2},
    },
    "herbal_apothecary": {
        "name": "Apothecary & Medicine",
        "era": TechEra.IRON,
        "cost": 260,
        "prereqs": ["agriculture", "written_lore"],
        "description": "Medicinal concoctions cure disease and extend elder human lifespans.",
        "bonuses": {"lifespan_bonus": 1.3, "health_regen": 2.0},
    },

    # Classical Age
    "monumental_architecture": {
        "name": "Monumental Wonders",
        "era": TechEra.CLASSICAL,
        "cost": 500,
        "prereqs": ["stone_fortifications", "written_lore"],
        "description": "Grand wonders inspiring societal morale, arts, and cultural supremacy.",
        "bonuses": {"morale_boost": 2.0, "culture_generation": 2.5},
    },
    "philosophical_academy": {
        "name": "Philosophical Enlightenment",
        "era": TechEra.CLASSICAL,
        "cost": 480,
        "prereqs": ["herbal_apothecary", "written_lore"],
        "description": "Scholarly mastery accelerating scientific breakthroughs and diplomacy.",
        "bonuses": {"research_speed": 2.5, "innovation_rate": 2.0},
    },
}


class Civilization:
    """Represents a human civilization with shared technology, culture, and warehouse."""

    def __init__(
        self,
        civ_id: int,
        name: str,
        color_rgb: List[int],
        ai_faction_name: str,
        philosophy: str,
        founder_traits: Optional[Dict[str, Any]] = None,
    ):
        self.id = civ_id
        self.name = name
        self.color_rgb = color_rgb
        self.ai_faction_name = ai_faction_name
        self.philosophy = philosophy
        self.founder_traits = founder_traits or {}

        # Resources & Economy
        self.warehouse: Dict[str, float] = {
            "food": 120.0,
            "wood": 80.0,
            "stone": 40.0,
            "ore": 0.0,
            "tools": 15.0,
            "research_points": 0.0,
        }

        # Technology Progression
        self.unlocked_techs: List[str] = ["fire_making"]
        self.current_research: Optional[str] = "agriculture"
        self.research_progress: float = 0.0
        self.culture_points: float = 0.0

        # Demographics & Statistics
        self.total_born: int = 0
        self.total_died: int = 0
        self.buildings_constructed: int = 0
        self.chronicle_events: List[str] = [
            f"Year 1: The {self.name} settled upon fertile lands under the guidance of {self.ai_faction_name}."
        ]

    @property
    def current_era(self) -> TechEra:
        unlocked_count = len(self.unlocked_techs)
        if unlocked_count >= 10:
            return TechEra.CLASSICAL
        elif unlocked_count >= 7:
            return TechEra.IRON
        elif unlocked_count >= 4:
            return TechEra.BRONZE
        return TechEra.NEOLITHIC

    def add_research_points(self, points: float) -> Optional[str]:
        """Contribute research labor from scholars. Returns tech name if newly discovered."""
        if not self.current_research or self.current_research not in TECH_TREE:
            # Pick next available tech
            self._select_next_research()
            if not self.current_research:
                return None

        tech = TECH_TREE[self.current_research]
        cost = tech["cost"]
        self.research_progress += points
        self.warehouse["research_points"] += points

        if self.research_progress >= cost:
            discovered = self.current_research
            self.unlocked_techs.append(discovered)
            self.chronicle_events.append(
                f"Discovered {tech['name']} ({tech['era'].value}): {tech['description']}"
            )
            self.research_progress = 0.0
            self._select_next_research()
            return discovered
        return None

    def _select_next_research(self) -> None:
        """Automatically or AI-directed select next valid research candidate."""
        candidates = []
        for tech_id, tech_data in TECH_TREE.items():
            if tech_id not in self.unlocked_techs:
                # Check prereqs
                if all(p in self.unlocked_techs for p in tech_data["prereqs"]):
                    candidates.append(tech_id)
        if candidates:
            # Bias selection based on civilization philosophy
            if "Agrarian" in self.philosophy and "agriculture" in candidates:
                self.current_research = "agriculture"
            elif "Industry" in self.philosophy and "bronze_metallurgy" in candidates:
                self.current_research = "bronze_metallurgy"
            elif "Stone" in self.philosophy and "stone_fortifications" in candidates:
                self.current_research = "stone_fortifications"
            elif "Science" in self.philosophy and "written_lore" in candidates:
                self.current_research = "written_lore"
            else:
                self.current_research = candidates[0]
        else:
            self.current_research = None

    def has_tech(self, tech_name: str) -> bool:
        return tech_name in self.unlocked_techs

    def get_bonus(self, bonus_key: str, default: float = 1.0) -> float:
        val = default
        for tech_id in self.unlocked_techs:
            tech_data = TECH_TREE.get(tech_id, {})
            bonuses = tech_data.get("bonuses", {})
            if bonus_key in bonuses:
                val *= bonuses[bonus_key]
        return val

    def log_event(self, event: str) -> None:
        self.chronicle_events.append(event)
        if len(self.chronicle_events) > 50:
            self.chronicle_events.pop(0)

    def to_dict(self) -> Dict[str, Any]:
        curr_tech = TECH_TREE.get(self.current_research) if self.current_research else None
        return {
            "id": self.id,
            "name": self.name,
            "color_rgb": self.color_rgb,
            "ai_faction": self.ai_faction_name,
            "philosophy": self.philosophy,
            "era": self.current_era.value,
            "warehouse": {k: round(v, 1) for k, v in self.warehouse.items()},
            "unlocked_techs": [
                {"id": t, "name": TECH_TREE[t]["name"], "era": TECH_TREE[t]["era"].value}
                for t in self.unlocked_techs
                if t in TECH_TREE
            ],
            "current_research": {
                "id": self.current_research,
                "name": curr_tech["name"] if curr_tech else "Completed All",
                "progress": round(self.research_progress, 1),
                "cost": curr_tech["cost"] if curr_tech else 100,
                "percent": round((self.research_progress / curr_tech["cost"]) * 100, 1) if curr_tech else 100.0,
            } if self.current_research else None,
            "total_born": self.total_born,
            "total_died": self.total_died,
            "buildings_constructed": self.buildings_constructed,
            "chronicle": self.chronicle_events[-8:],
        }
