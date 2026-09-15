"""
living_universe.systems.seasons
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Seasonal cycles (Spring, Summer, Autumn, Winter) and dynamic weather systems.
"""

from enum import Enum
from typing import Dict, Any
import math


class Season(str, Enum):
    SPRING = "Spring"
    SUMMER = "Summer"
    AUTUMN = "Autumn"
    WINTER = "Winter"


class Weather(str, Enum):
    CLEAR = "Clear"
    RAIN = "Rain"
    STORM = "Thunderstorm"
    SNOW = "Snowfall"


SEASON_PROPERTIES = {
    Season.SPRING: {
        "temperature_base": 20.0,
        "crop_multiplier": 1.2,
        "energy_drain_mod": 1.0,
        "tree_growth_rate": 1.5,
        "description": "Thawing earth, blooming flowers, and fertile soil for sowing crops.",
    },
    Season.SUMMER: {
        "temperature_base": 30.0,
        "crop_multiplier": 1.5,
        "energy_drain_mod": 1.1,
        "tree_growth_rate": 1.2,
        "description": "Long daylight, bountiful sunshine, but higher thirst and heat stress.",
    },
    Season.AUTUMN: {
        "temperature_base": 15.0,
        "crop_multiplier": 1.8,  # Peak harvest
        "energy_drain_mod": 1.0,
        "tree_growth_rate": 0.8,
        "description": "Golden foliage and bumper harvest yields to stockpile before winter.",
    },
    Season.WINTER: {
        "temperature_base": -2.0,
        "crop_multiplier": 0.1,  # Near zero farm growth
        "energy_drain_mod": 1.5,
        "tree_growth_rate": 0.1,
        "description": "Freezing blizzards and frost. Citizens need hearth fires and warm huts to survive.",
    },
}


class SeasonSystem:
    """Simulates 4-season climate cycles and atmospheric weather."""

    def __init__(self, season_length_ticks: int = 1800):
        self.season_length = season_length_ticks
        self.tick_in_year = 0
        self.year = 1
        self.current_season = Season.SPRING
        self.current_weather = Weather.CLEAR
        self.weather_timer = 300

    def step(self) -> None:
        self.tick_in_year += 1
        year_length = self.season_length * 4

        if self.tick_in_year >= year_length:
            self.tick_in_year = 0
            self.year += 1

        season_idx = (self.tick_in_year // self.season_length) % 4
        seasons = [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]
        self.current_season = seasons[season_idx]

        # Weather variation
        self.weather_timer -= 1
        if self.weather_timer <= 0:
            self.weather_timer = 400 + (hash(str(self.tick_in_year)) % 300)
            if self.current_season == Season.WINTER:
                self.current_weather = Weather.SNOW if (self.tick_in_year % 3 != 0) else Weather.CLEAR
            elif self.current_season == Season.SPRING:
                self.current_weather = Weather.RAIN if (self.tick_in_year % 2 == 0) else Weather.CLEAR
            elif self.current_season == Season.SUMMER:
                self.current_weather = Weather.STORM if (self.tick_in_year % 5 == 0) else Weather.CLEAR
            else:
                self.current_weather = Weather.RAIN if (self.tick_in_year % 4 == 0) else Weather.CLEAR

    @property
    def temperature_celsius(self) -> float:
        props = SEASON_PROPERTIES[self.current_season]
        base = props["temperature_base"]
        # Diurnal and noise modulation
        phase = math.sin((self.tick_in_year % self.season_length) / self.season_length * math.pi)
        weather_mod = -4.0 if self.current_weather in (Weather.RAIN, Weather.SNOW) else 0.0
        return base + (phase * 5.0) + weather_mod

    @property
    def crop_growth_multiplier(self) -> float:
        base_mult = SEASON_PROPERTIES[self.current_season]["crop_multiplier"]
        if self.current_weather == Weather.RAIN:
            base_mult *= 1.4
        elif self.current_weather == Weather.SNOW:
            base_mult *= 0.05
        return base_mult

    @property
    def energy_drain_multiplier(self) -> float:
        base = SEASON_PROPERTIES[self.current_season]["energy_drain_mod"]
        if self.current_season == Season.WINTER:
            return base * 1.3
        return base

    def to_dict(self) -> Dict[str, Any]:
        return {
            "year": self.year,
            "season": self.current_season.value,
            "weather": self.current_weather.value,
            "temperature_c": round(self.temperature_celsius, 1),
            "crop_multiplier": round(self.crop_growth_multiplier, 2),
            "season_progress": round((self.tick_in_year % self.season_length) / self.season_length * 100, 1),
            "description": SEASON_PROPERTIES[self.current_season]["description"],
        }
