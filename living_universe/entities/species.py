"""Species identity, phylogenetic lineage, and taxonomic cladistics."""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, Any, List
from .dna import DNA


@dataclass
class Species:
    id: int
    name: str
    representative_dna: DNA
    ancestor_species_id: Optional[int] = None
    population: int = 0
    total_born: int = 0
    total_died: int = 0
    max_generation: int = 0
    color_rgb: Tuple[int, int, int] = (120, 220, 140)
    origin_tick: int = 0
    extinct: bool = False
    extinction_tick: Optional[int] = None
    depth: int = 0
    evolutionary_innovations: List[str] = field(default_factory=list)
    trait_summary: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.representative_dna:
            self.color_rgb = self.representative_dna.get_color_rgb()
            self._update_trait_summary()

    def _update_trait_summary(self):
        dna = self.representative_dna
        diet = "Carnivore" if dna.is_carnivore() else ("Herbivore" if dna.is_herbivore() else "Omnivore")
        self.trait_summary = {
            "speed": round(dna.speed, 2),
            "vision": round(dna.vision_range, 1),
            "size": round(dna.size, 1),
            "armor": round(dna.armor, 2),
            "diet": diet,
            "thermal_optimum": round(dna.thermal_optimum, 1),
            "aggression": round(dna.aggression, 2),
            "sociability": round(dna.sociability, 2),
            "fertility": round(dna.fertility, 2),
            "bioluminescence": round(dna.bioluminescence, 2),
        }

    @staticmethod
    def generate_name(dna: DNA, species_id: int) -> str:
        """Generate a Linnaean binomial taxonomic name based on phenotypic traits."""
        # Genus (capitalized)
        if dna.is_carnivore():
            genera = ["Carnis", "Vorax", "Stalkus", "Raptoria", "Dentata", "Apex"]
        elif dna.speed > 2.0:
            genera = ["Velox", "Cursorius", "Drifto", "Pteron", "Agilis"]
        elif dna.size > 6.0:
            genera = ["Titanus", "Colossus", "Gigas", "Grandis", "Macro"]
        elif dna.armor > 0.4:
            genera = ["Scutum", "Testudo", "Loricata", "Armatus"]
        elif dna.bioluminescence > 0.4:
            genera = ["Luminis", "Lucifer", "Pharos", "Aura"]
        elif dna.thermal_optimum < 15.0:
            genera = ["Cryo", "Glacies", "Borealis", "Frigus"]
        elif dna.thermal_optimum > 32.0:
            genera = ["Thermo", "Pyros", "Calor", "Sol"]
        else:
            genera = ["Grazer", "Herbis", "Phyto", "Vermis", "Motes"]

        # Specific Epithet (lowercase)
        epithets = [
            "primus", "secundus", "adaptus", "communis", "vulgaris",
            "ferox", "elegans", "simplex", "robustus", "micro",
            "silvestris", "marinus", "australis", "noctis", "vitalis",
        ]

        genus = genera[species_id % len(genera)]
        epithet = epithets[(species_id * 7 + 3) % len(epithets)]
        return f"{genus} {epithet} (#{species_id})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "ancestor_id": self.ancestor_species_id,
            "population": self.population,
            "total_born": self.total_born,
            "total_died": self.total_died,
            "max_generation": self.max_generation,
            "origin_tick": self.origin_tick,
            "extinct": self.extinct,
            "depth": self.depth,
            "color_rgb": list(self.color_rgb),
            "innovations": self.evolutionary_innovations,
            "traits": self.trait_summary,
        }
