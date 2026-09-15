"""Ecosystem analytics and population genetics metric calculations."""

from typing import List, Dict, Any
import math
from ..entities.organism import Organism
from ..entities.species import Species


class MetricsCalculator:
    """Calculates diversity metrics, trophic distributions, and genetic trait averages."""

    @staticmethod
    def calculate_metrics(
        organisms: List[Organism],
        species_registry: Dict[int, Species],
    ) -> Dict[str, Any]:
        living = [o for o in organisms if o.alive]
        total = len(living)

        if total == 0:
            return {
                "population": 0,
                "species_count": 0,
                "shannon_diversity": 0.0,
                "average_energy": 0.0,
                "average_health": 0.0,
                "average_age": 0.0,
                "herbivores": 0,
                "carnivores": 0,
                "omnivores": 0,
                "dominant_traits": {},
            }

        # 1. Species Distribution & Shannon Entropy
        species_counts: Dict[int, int] = {}
        for o in living:
            species_counts[o.species_id] = species_counts.get(o.species_id, 0) + 1

        shannon_entropy = 0.0
        for count in species_counts.values():
            p = count / total
            if p > 0:
                shannon_entropy -= p * math.log(p)

        # 2. Trophic Classification & Averages
        herbivores = 0
        carnivores = 0
        omnivores = 0

        sum_energy = 0.0
        sum_health = 0.0
        sum_age = 0.0
        sum_speed = 0.0
        sum_vision = 0.0
        sum_size = 0.0
        sum_aggression = 0.0
        sum_fertility = 0.0
        sum_metabolism = 0.0
        sum_sociability = 0.0

        for o in living:
            sum_energy += o.energy
            sum_health += o.health
            sum_age += o.age
            sum_speed += o.dna.speed
            sum_vision += o.dna.vision_range
            sum_size += o.dna.size
            sum_aggression += o.dna.aggression
            sum_fertility += o.dna.fertility
            sum_metabolism += o.dna.metabolism
            sum_sociability += o.dna.sociability

            if o.dna.is_carnivore():
                carnivores += 1
            elif o.dna.is_herbivore():
                herbivores += 1
            else:
                omnivores += 1

        return {
            "population": total,
            "species_count": len(species_counts),
            "shannon_diversity": round(shannon_entropy, 3),
            "average_energy": round(sum_energy / total, 2),
            "average_health": round(sum_health / total, 2),
            "average_age": round(sum_age / total, 1),
            "herbivores": herbivores,
            "carnivores": carnivores,
            "omnivores": omnivores,
            "dominant_traits": {
                "speed": round(sum_speed / total, 2),
                "vision": round(sum_vision / total, 1),
                "size": round(sum_size / total, 2),
                "aggression": round(sum_aggression / total, 2),
                "fertility": round(sum_fertility / total, 2),
                "metabolism": round(sum_metabolism / total, 2),
                "sociability": round(sum_sociability / total, 2),
            },
        }
