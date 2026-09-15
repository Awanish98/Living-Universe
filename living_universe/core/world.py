"""World environment container with biogeochemical nutrient fields, dynamic biomes, and solar cycles."""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Any, Optional
import math
import numpy as np


@dataclass
class EnvironmentalZone:
    name: str
    zone_type: str  # "lush", "desert", "tundra", "volcanic", "abyss", "toxic"
    x: float
    y: float
    radius: float
    temperature_offset: float = 0.0
    moisture: float = 0.5  # 0.0 (arid) to 1.0 (marsh/rainforest)
    mineral_wealth: float = 1.0
    food_multiplier: float = 1.0
    hazard_damage: float = 0.0
    color: Tuple[int, int, int] = (40, 60, 40)

    def contains(self, px: float, py: float) -> bool:
        dx = px - self.x
        dy = py - self.y
        return (dx * dx + dy * dy) <= (self.radius * self.radius)


class NutrientField:
    """2D grid modeling soil and aquatic nutrient concentrations with diffusion."""

    def __init__(self, width: int, height: int, cols: int = 64, rows: int = 36):
        self.world_width = width
        self.world_height = height
        self.cols = cols
        self.rows = rows
        self.cell_w = width / float(cols)
        self.cell_h = height / float(rows)
        # Initialize nutrient concentration field (0.0 to 100.0)
        self.grid = np.full((rows, cols), 35.0, dtype=np.float32)

    def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        c = max(0, min(self.cols - 1, int(x / self.cell_w)))
        r = max(0, min(self.rows - 1, int(y / self.cell_h)))
        return r, c

    def add_nutrients(self, x: float, y: float, amount: float):
        r, c = self.world_to_grid(x, y)
        self.grid[r, c] = min(100.0, self.grid[r, c] + amount)

    def extract_nutrients(self, x: float, y: float, amount: float) -> float:
        r, c = self.world_to_grid(x, y)
        extracted = min(float(self.grid[r, c]), amount)
        self.grid[r, c] -= extracted
        return extracted

    def get_at(self, x: float, y: float) -> float:
        r, c = self.world_to_grid(x, y)
        return float(self.grid[r, c])

    def diffuse_and_cycle(self, diffusion_rate: float = 0.04):
        """Simulate physical diffusion across neighboring cells."""
        kernel = np.array([[0.05, 0.1, 0.05],
                           [0.1,  0.4, 0.1 ],
                           [0.05, 0.1, 0.05]], dtype=np.float32)
        
        # Simple fast pad-based 2D diffusion
        padded = np.pad(self.grid, 1, mode='edge')
        diffused = np.zeros_like(self.grid)
        for dr in range(3):
            for dc in range(3):
                diffused += padded[dr:dr+self.rows, dc:dc+self.cols] * kernel[dr, dc]
        
        self.grid = np.clip(self.grid * (1.0 - diffusion_rate) + diffused * diffusion_rate, 5.0, 100.0)


@dataclass
class World:
    width: int
    height: int
    base_temperature: float = 22.0  # Celsius
    temperature: float = 22.0
    day_length_ticks: int = 2400
    solar_irradiance: float = 1.0
    zones: List[EnvironmentalZone] = field(default_factory=list)
    nutrients: Optional[NutrientField] = None

    def __post_init__(self):
        if self.nutrients is None:
            self.nutrients = NutrientField(self.width, self.height)
        if not self.zones:
            self._create_rich_biomes()

    def _create_rich_biomes(self):
        cx, cy = self.width / 2.0, self.height / 2.0
        
        # 1. Verdant Marsh & Forest (Central)
        self.zones.append(EnvironmentalZone(
            name="Verdant Canopy",
            zone_type="lush",
            x=cx,
            y=cy,
            radius=min(self.width, self.height) * 0.30,
            temperature_offset=0.0,
            moisture=0.9,
            mineral_wealth=1.5,
            food_multiplier=2.2,
            color=(18, 52, 32)
        ))
        
        # 2. Arid Dunes & Savanna (Top-Right)
        self.zones.append(EnvironmentalZone(
            name="Solar Dunes",
            zone_type="desert",
            x=self.width * 0.82,
            y=self.height * 0.22,
            radius=min(self.width, self.height) * 0.24,
            temperature_offset=14.0,
            moisture=0.1,
            mineral_wealth=0.8,
            food_multiplier=0.4,
            color=(56, 42, 18)
        ))
        
        # 3. Glacial Abyss & Tundra (Bottom-Left)
        self.zones.append(EnvironmentalZone(
            name="Frost Expanse",
            zone_type="tundra",
            x=self.width * 0.18,
            y=self.height * 0.78,
            radius=min(self.width, self.height) * 0.24,
            temperature_offset=-16.0,
            moisture=0.6,
            mineral_wealth=1.0,
            food_multiplier=0.5,
            color=(18, 36, 56)
        ))

        # 4. Volcanic Ridge & Vents (Bottom-Right)
        self.zones.append(EnvironmentalZone(
            name="Hydrothermal Ridge",
            zone_type="volcanic",
            x=self.width * 0.80,
            y=self.height * 0.80,
            radius=min(self.width, self.height) * 0.18,
            temperature_offset=18.0,
            moisture=0.3,
            mineral_wealth=2.8,
            food_multiplier=1.2,
            color=(52, 20, 18)
        ))

        # 5. Acid Mire & Bioluminescent Trench (Top-Left)
        self.zones.append(EnvironmentalZone(
            name="Bioluminescent Mire",
            zone_type="toxic",
            x=self.width * 0.20,
            y=self.height * 0.20,
            radius=min(self.width, self.height) * 0.16,
            temperature_offset=4.0,
            moisture=0.95,
            mineral_wealth=1.8,
            food_multiplier=0.3,
            hazard_damage=0.25,
            color=(36, 16, 46)
        ))

    def update(self, tick: int) -> None:
        """Update planetary climate, solar irradiance, and nutrient diffusion."""
        phase = (tick % self.day_length_ticks) / float(self.day_length_ticks)
        
        # Diurnal solar cycle
        solar_angle = phase * 2.0 * math.pi
        self.solar_irradiance = max(0.08, float(math.sin(solar_angle) * 0.5 + 0.5))
        
        # Global temperature fluctuation
        diurnal_temp = math.sin(solar_angle - math.pi / 4.0) * 9.0
        self.temperature = self.base_temperature + diurnal_temp

        # Diffuse biogeochemical nutrients every 5 ticks
        if tick % 5 == 0:
            self.nutrients.diffuse_and_cycle()

    def get_day_phase(self, tick: int) -> float:
        return (tick % self.day_length_ticks) / float(self.day_length_ticks)

    def get_temperature_at(self, x: float, y: float, tick: int) -> float:
        zone = self.get_zone_at(x, y)
        offset = zone.temperature_offset if zone else 0.0
        return self.temperature + offset

    def get_zone_at(self, x: float, y: float) -> Optional[EnvironmentalZone]:
        for zone in reversed(self.zones):
            if zone.contains(x, y):
                return zone
        return None

    def clamp_or_wrap(self, x: float, y: float, margin: float = 0.0) -> Tuple[float, float]:
        nx = max(margin, min(self.width - margin, x))
        ny = max(margin, min(self.height - margin, y))
        return nx, ny
