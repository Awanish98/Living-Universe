"""Organism entity representing autonomous living digital lifeforms with neural brains."""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict, Any
import math
import numpy as np

from .dna import DNA
from .brain import NeuralBrain
from .memory import BoundedMemory


@dataclass
class Organism:
    id: int
    species_id: int
    x: float
    y: float
    generation: int
    dna: DNA = field(default_factory=DNA)
    brain: Optional[NeuralBrain] = None

    # Physics state
    vx: float = 0.0
    vy: float = 0.0
    ax: float = 0.0
    ay: float = 0.0
    angle: float = 0.0
    angular_velocity: float = 0.0

    # Vital metabolism
    energy: float = 85.0
    max_energy: Optional[float] = None
    health: float = 100.0
    max_health: Optional[float] = None
    age: int = 0
    max_age: Optional[int] = None
    alive: bool = True

    # Lineage & reproduction
    parent_id: Optional[int] = None
    second_parent_id: Optional[int] = None
    reproduction_cooldown: int = 120
    offspring_count: int = 0
    kills: int = 0
    food_consumed: float = 0.0

    # Social & signaling
    signal_cooldown: int = 0
    active_signal: Optional[str] = None
    bioluminescence_glow: float = 0.0
    memory: BoundedMemory = field(default_factory=lambda: BoundedMemory(16))

    # Behavioral classification & runtime metrics
    current_state: str = "foraging"
    last_reward: float = 0.0
    learned_weights: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0, 1.0])

    def __post_init__(self):
        # Scale health, energy, and lifespan based on evolved genetics
        if self.max_health is None:
            self.max_health = 80.0 + self.dna.size * 6.0 + self.dna.armor * 40.0
        if self.max_energy is None:
            self.max_energy = 100.0 + self.dna.size * 12.0
        if self.max_age is None:
            self.max_age = int(self.dna.longevity * (1.0 + self.dna.efficiency * 0.4) / max(0.4, self.dna.metabolism * 0.7))

        if self.brain is None:
            self.brain = self.dna.create_brain()

    @property
    def radius(self) -> float:
        """Physical collision & rendering radius."""
        return self.dna.size

    @property
    def mass(self) -> float:
        """Mass proportional to body volume and armor plating."""
        return (self.dna.size ** 1.8) * (1.0 + self.dna.armor * 0.6)

    @property
    def life_stage(self) -> str:
        """Biological maturity stage."""
        if not self.max_age or self.max_age == 0:
            return "adult"
        ratio = self.age / float(self.max_age)
        if ratio < 0.15:
            return "juvenile"
        elif ratio < 0.75:
            return "adult"
        else:
            return "elder"

    def is_eligible_for_reproduction(self, energy_threshold: float = 0.65) -> bool:
        """Assess whether organism has stored enough biomass to replicate."""
        return (
            self.alive
            and self.age >= 180
            and self.reproduction_cooldown <= 0
            and self.energy >= (self.max_energy * energy_threshold)
            and self.health >= (self.max_health * 0.45)
        )

    def heading_vector(self) -> Tuple[float, float]:
        """Unit direction vector."""
        return math.cos(self.angle), math.sin(self.angle)

    def calculate_thermal_stress(self, ambient_temp: float) -> float:
        """Metabolic penalty when ambient temperature deviates from optimal niche."""
        diff = abs(ambient_temp - self.dna.thermal_optimum)
        if diff <= self.dna.thermal_tolerance:
            return 0.0
        excess = diff - self.dna.thermal_tolerance
        return min(1.0, excess / 20.0)

    def take_damage(self, raw_damage: float) -> float:
        """Absorb damage with armor reduction."""
        effective_damage = raw_damage * (1.0 - min(0.80, self.dna.armor))
        self.health = max(0.0, self.health - effective_damage)
        if self.health <= 0:
            self.alive = False
        return effective_damage

    def execute_brain_decision(
        self,
        sensory_inputs: List[float],
        max_force: float = 1.2,
        turn_rate: float = 0.22,
    ) -> np.ndarray:
        """Run neural brain forward inference and translate outputs into physical forces."""
        outputs = self.brain.forward(sensory_inputs)
        thrust_urge, steer_urge, attack_urge, eat_urge, mate_urge, signal_urge = outputs

        # 1. Angular Steering Torque
        self.angle += float(steer_urge * turn_rate)
        self.angle = self.angle % (2.0 * math.pi)

        # 2. Forward Locomotive Propulsion Force
        speed_cap = self.dna.speed * (0.6 if self.life_stage == "juvenile" else (0.85 if self.life_stage == "elder" else 1.0))
        force = float(thrust_urge) * max_force * speed_cap
        self.ax += math.cos(self.angle) * force / self.mass
        self.ay += math.sin(self.angle) * force / self.mass

        # 3. Bioluminescence output
        self.bioluminescence_glow = float(signal_urge) * self.dna.bioluminescence

        # 4. State classification for UI inspector
        if attack_urge > 0.65 and self.dna.is_carnivore():
            self.current_state = "hunting"
        elif mate_urge > 0.65 and self.is_eligible_for_reproduction():
            self.current_state = "seeking_mate"
        elif eat_urge > 0.5:
            self.current_state = "grazing"
        elif thrust_urge > 0.75:
            self.current_state = "fleeing/sprinting"
        else:
            self.current_state = "wandering"

        return outputs
