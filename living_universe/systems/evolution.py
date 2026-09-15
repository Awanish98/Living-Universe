"""Evolution, reproduction, genetic mutation, and phylogenetic cladogenesis system."""

from typing import List, Dict, Tuple, Optional
import random
import math
from ..entities.organism import Organism
from ..entities.dna import DNA
from ..entities.species import Species
from ..systems.spatial_grid import SpatialGrid
from ..config import UniverseConfig


class EvolutionSystem:
    """Handles Darwinian reproduction, genetic crossover, neural mutation, and phylogenetic speciation."""

    def __init__(self, config: UniverseConfig, rng: random.Random):
        self.config = config
        self.rng = rng

    def update(
        self,
        organisms: List[Organism],
        species_registry: Dict[int, Species],
        organism_grid: SpatialGrid,
        next_organism_id: int,
        next_species_id: int,
        current_tick: int,
    ) -> Tuple[List[Organism], int, int, List[Species]]:
        """
        Evaluate reproduction and generate offspring with mutation/speciation.
        Returns:
            new_offspring: list of newly born Organisms
            next_org_id: updated organism ID sequence
            next_sp_id: updated species ID sequence
            newly_emerged_species: list of newly created Species
        """
        new_offspring: List[Organism] = []
        newly_emerged: List[Species] = []
        curr_org_id = next_organism_id
        curr_sp_id = next_species_id

        if len(organisms) >= self.config.max_organisms:
            return new_offspring, curr_org_id, curr_sp_id, newly_emerged

        for org in organisms:
            if not org.is_eligible_for_reproduction():
                continue

            if len(organisms) + len(new_offspring) >= self.config.max_organisms:
                break

            # Search for eligible sexual mate nearby
            mate: Optional[Organism] = None
            if org.dna.asexual_affinity < 0.8:
                nearby_candidates = organism_grid.nearby(org.x, org.y, org.radius * 4.0)
                for other in nearby_candidates:
                    if (
                        other.id != org.id
                        and other.alive
                        and other.is_eligible_for_reproduction()
                        and (other.species_id == org.species_id or other.dna.genetic_distance(org.dna) < 0.6)
                    ):
                        mate = other
                        break

            clutch_size = max(1, min(3, org.dna.clutch_size))

            for _ in range(clutch_size):
                if len(organisms) + len(new_offspring) >= self.config.max_organisms:
                    break

                # Generate child DNA
                if mate:
                    combined_dna = org.dna.crossover(mate.dna, self.rng)
                    child_dna = combined_dna.mutated_child(
                        self.rng,
                        rate=self.config.mutation_rate,
                        strength=self.config.mutation_strength,
                    )
                else:
                    child_dna = org.dna.mutated_child(
                        self.rng,
                        rate=self.config.mutation_rate,
                        strength=self.config.mutation_strength,
                    )

                # Speciation Check: Compare genetic drift from species archetype
                parent_species = species_registry.get(org.species_id)
                target_species_id = org.species_id

                if parent_species:
                    dist = child_dna.genetic_distance(parent_species.representative_dna)
                    if dist >= self.config.speciation_threshold:
                        # New species cladogenesis!
                        innovations = []
                        if child_dna.is_carnivore() and not parent_species.representative_dna.is_carnivore():
                            innovations.append("Evolved Carnivorous Jaws")
                        if child_dna.armor > parent_species.representative_dna.armor + 0.2:
                            innovations.append("Evolved Armored Carapace")
                        if child_dna.speed > parent_species.representative_dna.speed + 0.6:
                            innovations.append("Evolved High-Speed Propulsion")
                        if child_dna.bioluminescence > 0.4 and parent_species.representative_dna.bioluminescence <= 0.2:
                            innovations.append("Evolved Bioluminescent Gland")
                        if abs(child_dna.thermal_optimum - parent_species.representative_dna.thermal_optimum) > 10.0:
                            innovations.append(f"Adapted to {child_dna.thermal_optimum:.0f}°C Climate")

                        new_sp = Species(
                            id=curr_sp_id,
                            name=Species.generate_name(child_dna, curr_sp_id),
                            representative_dna=child_dna,
                            ancestor_species_id=org.species_id,
                            origin_tick=current_tick,
                            depth=parent_species.depth + 1,
                            evolutionary_innovations=innovations,
                        )
                        species_registry[curr_sp_id] = new_sp
                        newly_emerged.append(new_sp)
                        target_species_id = curr_sp_id
                        curr_sp_id += 1

                # Spawn offspring near parents
                offset_angle = self.rng.uniform(0, 2 * math.pi)
                offset_dist = org.radius + child_dna.size + self.rng.uniform(2.0, 8.0)
                cx = org.x + math.cos(offset_angle) * offset_dist
                cy = org.y + math.sin(offset_angle) * offset_dist

                child = Organism(
                    id=curr_org_id,
                    species_id=target_species_id,
                    x=cx,
                    y=cy,
                    generation=org.generation + 1,
                    dna=child_dna,
                    energy=self.config.initial_energy * 0.9,
                    health=100.0,
                    parent_id=org.id,
                    second_parent_id=mate.id if mate else None,
                    reproduction_cooldown=self.config.reproduction_cooldown_ticks // 2,
                )
                child.learned_weights = [
                    max(0.2, min(3.0, w + self.rng.gauss(0, 0.04))) for w in org.learned_weights
                ]
                new_offspring.append(child)
                curr_org_id += 1

                sp = species_registry.get(target_species_id)
                if sp:
                    sp.total_born += 1
                    sp.max_generation = max(sp.max_generation, child.generation)

            # Deduct metabolic energy from parents
            org.energy -= self.config.reproduction_energy_cost
            org.reproduction_cooldown = self.config.reproduction_cooldown_ticks
            org.offspring_count += clutch_size
            org.last_reward += 2.0

            if mate:
                mate.energy -= self.config.reproduction_energy_cost * 0.4
                mate.reproduction_cooldown = self.config.reproduction_cooldown_ticks
                mate.offspring_count += clutch_size
                mate.last_reward += 1.5

        # Check for species extinction
        living_species_ids = {o.species_id for o in organisms if o.alive}
        for sp_id, sp in species_registry.items():
            if sp_id not in living_species_ids and not sp.extinct and sp.total_born > 0:
                sp.extinct = True
                sp.extinction_tick = current_tick

        return new_offspring, curr_org_id, curr_sp_id, newly_emerged
