"""DNA and genetic trait model with morphological, physiological, and neural brain encoding."""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Tuple, ClassVar, Optional, List
import random
import math
import numpy as np

from .brain import NeuralBrain


@dataclass
class DNA:
    # Morphological Traits
    speed: float = 1.3
    vision_range: float = 95.0
    vision_fov: float = 140.0  # Field of view cone in degrees
    size: float = 4.2
    armor: float = 0.1         # Damage reduction (0.0 to 0.8)
    color_hue: float = 120.0   # Hue in degrees (0 = red, 120 = green, 240 = blue)
    bioluminescence: float = 0.0  # Night glow & warning color intensity (0.0 to 1.0)

    # Physiological & Metabolic Traits
    metabolism: float = 1.0    # Basal calorie consumption rate
    diet_preference: float = 0.1  # 0.0=pure herbivore, 0.5=omnivore, 1.0=pure carnivore
    thermal_optimum: float = 22.0  # Optimal temperature in Celsius (10 to 40)
    thermal_tolerance: float = 15.0  # Temperature variance buffer (5 to 30)
    efficiency: float = 0.75   # Digestive energy extraction efficiency

    # Life History & Reproductive Strategy
    fertility: float = 0.55    # Reproduction trigger threshold
    clutch_size: int = 1       # Number of offspring per reproductive cycle (1 to 4)
    longevity: float = 1200.0  # Maximum natural lifespan ticks before senescence
    asexual_affinity: float = 0.4  # Propensity for asexual fission vs sexual mating

    # Behavioral & Social Disposition Weights
    aggression: float = 0.2
    curiosity: float = 0.5
    sociability: float = 0.5
    fear: float = 0.6

    # Neural Brain Genome (Synaptic Weights Matrix)
    brain_weights: Optional[List[float]] = None

    TRAIT_BOUNDS: ClassVar[Dict[str, Tuple[float, float]]] = {
        "speed": (0.3, 3.8),
        "vision_range": (30.0, 260.0),
        "vision_fov": (45.0, 360.0),
        "size": (1.8, 12.0),
        "armor": (0.0, 0.8),
        "color_hue": (0.0, 360.0),
        "bioluminescence": (0.0, 1.0),
        "metabolism": (0.3, 3.0),
        "diet_preference": (0.0, 1.0),
        "thermal_optimum": (5.0, 45.0),
        "thermal_tolerance": (4.0, 30.0),
        "efficiency": (0.25, 0.95),
        "fertility": (0.1, 1.0),
        "longevity": (400.0, 3000.0),
        "asexual_affinity": (0.0, 1.0),
        "aggression": (0.0, 1.0),
        "curiosity": (0.05, 1.0),
        "sociability": (0.0, 1.0),
        "fear": (0.05, 1.0),
    }

    def __post_init__(self):
        self._ensure_bounds()
        if self.brain_weights is None or len(self.brain_weights) != NeuralBrain.TOTAL_WEIGHTS:
            # Deterministic default baseline weights
            self.brain_weights = [0.0] * NeuralBrain.TOTAL_WEIGHTS

    def _ensure_bounds(self):
        for trait, (min_v, max_v) in self.TRAIT_BOUNDS.items():
            val = getattr(self, trait)
            if trait == "color_hue":
                setattr(self, trait, float(val) % 360.0)
            else:
                setattr(self, trait, max(min_v, min(max_v, float(val))))
        self.clutch_size = max(1, min(4, int(round(self.clutch_size))))

    def create_brain(self) -> NeuralBrain:
        """Instantiate a runtime NeuralBrain from this DNA's synaptic weights."""
        return NeuralBrain(np.array(self.brain_weights, dtype=np.float32))

    def mutated_child(self, rng: random.Random, rate: float = 0.08, strength: float = 0.18) -> "DNA":
        """Produce a child DNA with stochastic mutations applied to traits and neural weights."""
        data = asdict(self)
        for key in list(data.keys()):
            if key in self.TRAIT_BOUNDS and rng.random() < rate:
                val = data[key]
                if key == "color_hue":
                    drift = rng.gauss(0, 25.0 * strength)
                    data[key] = (val + drift) % 360.0
                elif key == "clutch_size":
                    data[key] = max(1, min(4, val + rng.choice([-1, 0, 1])))
                else:
                    delta = rng.uniform(-strength, strength) * max(0.1, abs(val))
                    data[key] = val + delta

        # Mutate neural brain weights
        parent_brain = NeuralBrain(np.array(self.brain_weights, dtype=np.float32))
        child_brain = parent_brain.mutate(rate=rate, strength=strength * 1.5, rng=rng)
        data["brain_weights"] = child_brain.weights.tolist()

        child = DNA(**data)
        child._ensure_bounds()
        return child

    def crossover(self, other: "DNA", rng: random.Random) -> "DNA":
        """Produce child DNA via genetic crossover from two parents."""
        data = {}
        self_dict = asdict(self)
        other_dict = asdict(other)

        for key in self_dict.keys():
            if key == "brain_weights":
                parent_a_brain = NeuralBrain(np.array(self.brain_weights, dtype=np.float32))
                parent_b_brain = NeuralBrain(np.array(other.brain_weights, dtype=np.float32))
                child_brain = parent_a_brain.crossover(parent_b_brain, rng=rng)
                data["brain_weights"] = child_brain.weights.tolist()
            elif key in self.TRAIT_BOUNDS:
                data[key] = self_dict[key] if rng.random() < 0.5 else other_dict[key]

        child = DNA(**data)
        child._ensure_bounds()
        return child

    def genetic_distance(self, other: "DNA") -> float:
        """Calculate normalized Euclidean distance between two DNA vectors including brain weights."""
        weights = {
            "speed": 1.0 / 3.0,
            "vision_range": 1.0 / 200.0,
            "size": 1.0 / 8.0,
            "armor": 2.0,
            "diet_preference": 2.5,
            "metabolism": 1.0 / 2.0,
            "fertility": 1.2,
            "aggression": 1.5,
            "thermal_optimum": 1.0 / 20.0,
        }
        dist_sq = 0.0
        for trait, weight in weights.items():
            diff = (getattr(self, trait) - getattr(other, trait)) * weight
            dist_sq += diff * diff

        # Add neural brain weight distance component
        if self.brain_weights and other.brain_weights:
            bw1 = np.array(self.brain_weights[:32], dtype=np.float32)
            bw2 = np.array(other.brain_weights[:32], dtype=np.float32)
            brain_diff = np.mean(np.abs(bw1 - bw2)) * 0.5
            dist_sq += float(brain_diff * brain_diff)

        return math.sqrt(dist_sq)

    def is_carnivore(self) -> bool:
        return self.diet_preference >= 0.65 or self.aggression >= 0.7

    def is_herbivore(self) -> bool:
        return self.diet_preference <= 0.35 and self.aggression < 0.45

    def get_color_rgb(self) -> Tuple[int, int, int]:
        """Convert HSV color hue to RGB (0-255)."""
        h = self.color_hue / 60.0
        c = 0.88
        x = c * (1.0 - abs((h % 2.0) - 1.0))
        m = 0.12

        if 0 <= h < 1:
            r, g, b = c, x, 0
        elif 1 <= h < 2:
            r, g, b = x, c, 0
        elif 2 <= h < 3:
            r, g, b = 0, c, x
        elif 3 <= h < 4:
            r, g, b = 0, x, c
        elif 4 <= h < 5:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)
