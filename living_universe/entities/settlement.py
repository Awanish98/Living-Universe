"""
living_universe.entities.settlement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Human settlements, villages, towns, zoning, and communal resource distribution.
"""

from typing import Dict, List, Optional, Any, Tuple
import math
from living_universe.entities.building import Building, BuildingType


class Settlement:
    """Represents a human settlement, village, or town with territorial structures."""

    def __init__(
        self,
        settlement_id: int,
        name: str,
        civilization_id: int,
        center_x: float,
        center_y: float,
        radius: float = 140.0,
    ):
        self.id = settlement_id
        self.name = name
        self.civilization_id = civilization_id
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius

        self.buildings: List[Building] = []
        self.citizen_ids: List[int] = []
        self.next_building_id = 1

        # Initial core structures
        self._init_foundation_camp()

    def _init_foundation_camp(self) -> None:
        """Create central campfire and starting shelters."""
        # Central Campfire
        campfire = Building(
            building_id=self._get_next_building_id(),
            building_type=BuildingType.CAMPFIRE,
            x=self.center_x,
            y=self.center_y,
            settlement_id=self.id,
            civilization_id=self.civilization_id,
            completed=True,
        )
        self.buildings.append(campfire)

        # 2 Initial Thatch Huts
        hut1 = Building(
            building_id=self._get_next_building_id(),
            building_type=BuildingType.HUT,
            x=self.center_x - 35,
            y=self.center_y - 25,
            settlement_id=self.id,
            civilization_id=self.civilization_id,
            completed=True,
        )
        hut2 = Building(
            building_id=self._get_next_building_id(),
            building_type=BuildingType.HUT,
            x=self.center_x + 35,
            y=self.center_y - 25,
            settlement_id=self.id,
            civilization_id=self.civilization_id,
            completed=True,
        )
        # 1 Initial Farm Plot
        farm = Building(
            building_id=self._get_next_building_id(),
            building_type=BuildingType.FARM_PLOT,
            x=self.center_x,
            y=self.center_y + 45,
            settlement_id=self.id,
            civilization_id=self.civilization_id,
            completed=True,
        )
        self.buildings.extend([hut1, hut2, farm])

    def _get_next_building_id(self) -> int:
        bid = self.next_building_id
        self.next_building_id += 1
        return bid

    def plan_new_construction(
        self, building_type: BuildingType, current_wood: float, current_stone: float
    ) -> Optional[Building]:
        """Auto-zone and place a new planned building in the settlement perimeter."""
        # Check if we already have too many unbuilt sites
        unbuilt = [b for b in self.buildings if not b.completed]
        if len(unbuilt) >= 2:
            return None

        # Determine optimal coordinates via spiral distribution
        count = len(self.buildings)
        angle = count * 1.4  # Golden angle approx
        dist = 35.0 + math.sqrt(count) * 22.0
        bx = self.center_x + math.cos(angle) * dist
        by = self.center_y + math.sin(angle) * dist

        new_b = Building(
            building_id=self._get_next_building_id(),
            building_type=building_type,
            x=bx,
            y=by,
            settlement_id=self.id,
            civilization_id=self.civilization_id,
            completed=False,
        )
        self.buildings.append(new_b)
        self.radius = max(self.radius, dist + 40.0)
        return new_b

    def get_completed_buildings(self, b_type: Optional[BuildingType] = None) -> List[Building]:
        if b_type:
            return [b for b in self.buildings if b.completed and b.type == b_type]
        return [b for b in self.buildings if b.completed]

    def get_unbuilt_buildings(self) -> List[Building]:
        return [b for b in self.buildings if not b.completed]

    def get_nearest_building(
        self, x: float, y: float, b_type: Optional[BuildingType] = None, completed_only: bool = True
    ) -> Optional[Building]:
        best_b = None
        min_d = float("inf")
        for b in self.buildings:
            if completed_only and not b.completed:
                continue
            if b_type and b.type != b_type:
                continue
            d = math.hypot(b.x - x, b.y - y)
            if d < min_d:
                min_d = d
                best_b = b
        return best_b

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "civilization_id": self.civilization_id,
            "center_x": round(self.center_x, 1),
            "center_y": round(self.center_y, 1),
            "radius": round(self.radius, 1),
            "citizen_count": len(self.citizen_ids),
            "building_count": len(self.buildings),
            "buildings": [b.to_dict() for b in self.buildings],
        }
