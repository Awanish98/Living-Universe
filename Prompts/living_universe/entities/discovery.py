"""
living_universe.entities.discovery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Mysterious digital anomalies, discovery nodes, and landmark monuments for the 4 AI Explorers.
"""

from typing import Dict, Any, Optional
import math


class DiscoveryNode:
    """An uncharted digital or cosmic anomaly on the world map waiting to be discovered and analyzed."""

    def __init__(
        self,
        node_id: int,
        name: str,
        node_type: str,
        x: float,
        y: float,
        color: str = "#00f3ff",
        icon: str = "💎",
        yield_invention: str = "Quantum Matrix",
        hinglish_desc: str = "Anokhi cosmic energy jo reality ko transform kar sakti hai.",
        energy: float = 100.0,
    ):
        self.id = node_id
        self.name = name
        self.node_type = node_type
        self.x = x
        self.y = y
        self.radius = 26.0
        self.energy = energy
        self.scan_progress = 0.0  # 0.0 to 100.0%
        self.scanned_by_id: Optional[int] = None
        self.scanned_by_name: Optional[str] = None
        self.mastered = False
        self.color = color
        self.icon = icon
        self.yield_invention = yield_invention
        self.hinglish_desc = hinglish_desc

    def analyze(self, amount: float, explorer_id: int, explorer_name: str) -> bool:
        """Scan this node. Returns True if analysis just reached 100% (Breakthrough)."""
        if self.mastered:
            return False

        self.scanned_by_id = explorer_id
        self.scanned_by_name = explorer_name
        self.scan_progress = min(100.0, self.scan_progress + amount)

        if self.scan_progress >= 100.0:
            self.mastered = True
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.node_type,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "r": self.radius,
            "energy": round(self.energy, 1),
            "progress": round(self.scan_progress, 1),
            "scanned_by_id": self.scanned_by_id,
            "scanned_by_name": self.scanned_by_name,
            "mastered": self.mastered,
            "color": self.color,
            "icon": self.icon,
            "invention": self.yield_invention,
            "hinglish_desc": self.hinglish_desc,
        }


class LandmarkMonument:
    """A glowing architectural monument erected by an explorer after mastering a digital node."""

    def __init__(
        self,
        monument_id: int,
        name: str,
        explorer_id: int,
        explorer_name: str,
        x: float,
        y: float,
        color: str,
        icon: str,
        tech_name: str,
        built_tick: int = 0,
        aura_radius: float = 65.0,
    ):
        self.id = monument_id
        self.name = name
        self.explorer_id = explorer_id
        self.explorer_name = explorer_name
        self.x = x
        self.y = y
        self.color = color
        self.icon = icon
        self.tech_name = tech_name
        self.built_tick = built_tick
        self.aura_radius = aura_radius

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "explorer_id": self.explorer_id,
            "explorer_name": self.explorer_name,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "color": self.color,
            "icon": self.icon,
            "tech_name": self.tech_name,
            "built_tick": self.built_tick,
            "aura_radius": self.aura_radius,
        }
