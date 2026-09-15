"""Configuration module for the Living Universe simulation engine."""

from dataclasses import dataclass, field
import os
from typing import Dict, Any


@dataclass
class UniverseConfig:
    # World Dimensions
    width: int = int(os.getenv("WORLD_WIDTH", "1280"))
    height: int = int(os.getenv("WORLD_HEIGHT", "720"))
    
    # Population & Resources
    initial_organisms: int = int(os.getenv("INITIAL_ORGANISMS", "200"))
    max_organisms: int = int(os.getenv("MAX_ORGANISMS", "2000"))
    initial_resources: int = int(os.getenv("INITIAL_RESOURCES", "300"))
    max_resources: int = int(os.getenv("MAX_RESOURCES", "1200"))
    food_spawn_rate: float = float(os.getenv("FOOD_SPAWN_RATE", "0.25"))
    food_energy_value: float = 25.0
    carrion_energy_ratio: float = 0.5  # Fraction of dead organism's max energy returned as meat pellet
    
    # Simulation Timing & Seed
    seed: int = int(os.getenv("UNIVERSE_SEED", "42"))
    target_fps: int = 60
    sim_speed: float = 1.0  # Multiplier for simulation steps
    
    # Organism Life Cycle & Energy
    base_metabolism: float = 0.05
    movement_energy_cost: float = 0.015
    starvation_damage: float = 0.5
    natural_healing_rate: float = 0.05
    initial_energy: float = 80.0
    max_energy: float = 200.0
    initial_health: float = 100.0
    max_health: float = 100.0
    base_lifespan: int = 1800  # in simulation ticks (~30s at 60Hz)
    reproduction_energy_cost: float = 50.0
    reproduction_cooldown_ticks: int = 180
    
    # Genetics & Mutation
    mutation_rate: float = float(os.getenv("MUTATION_RATE", "0.08"))
    mutation_strength: float = float(os.getenv("MUTATION_STRENGTH", "0.15"))
    speciation_threshold: float = 0.35  # Genetic distance to classify as new species
    
    # Spatial Partitioning
    spatial_cell_size: int = 64
    
    # Sensory & Behavior
    max_sensor_range: float = 180.0
    signal_range: float = 200.0
    signal_energy_cost: float = 2.0
    signal_cooldown_ticks: int = 40
    memory_capacity: int = 16
    
    # Combat & Ecology
    carnivore_bite_damage: float = 30.0
    predator_aggression_threshold: float = 0.6
    
    # Environmental Zones & Events
    event_chance_per_tick: float = 0.0005  # ~once every 2000 ticks
    day_night_cycle_ticks: int = 2400
    
    # AI & Multi-Provider Settings
    ai_enabled: bool = bool(os.getenv("GEMINI_API_KEY") or os.getenv("AI_ENABLED", "False").lower() in ("true", "1"))
    ai_provider: str = os.getenv("AI_PROVIDER", "null")  # "gemini", "openai", "xai", "custom", "null"
    ai_interval_seconds: float = float(os.getenv("AI_INTERVAL_SECONDS", "30.0"))
    
    # Audio Settings
    audio_enabled: bool = True
    master_volume: float = 0.7
    sfx_volume: float = 0.8
    music_volume: float = 0.4
    ambient_volume: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
