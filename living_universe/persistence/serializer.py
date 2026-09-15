"""State serialization and deserialization for universe persistence."""

from dataclasses import asdict
from typing import Dict, Any, List
from ..entities.organism import Organism
from ..entities.dna import DNA
from ..entities.species import Species
from ..entities.resource import Resource
from ..entities.event import WorldEvent
from ..config import UniverseConfig


class UniverseSerializer:
    """Serializes and deserializes world states into versioned JSON structures."""

    SCHEMA_VERSION = 2

    @classmethod
    def serialize(
        cls,
        config: UniverseConfig,
        tick: int,
        organisms: List[Organism],
        species_registry: Dict[int, Species],
        resources: List[Resource],
        events: List[WorldEvent],
        births: int,
        deaths: int,
        next_org_id: int,
        next_species_id: int,
        next_res_id: int,
    ) -> Dict[str, Any]:
        return {
            "schema_version": cls.SCHEMA_VERSION,
            "tick": tick,
            "births": births,
            "deaths": deaths,
            "id_counters": {
                "next_org_id": next_org_id,
                "next_species_id": next_species_id,
                "next_res_id": next_res_id,
            },
            "config": config.to_dict(),
            "species": [
                {
                    "id": sp.id,
                    "name": sp.name,
                    "ancestor_species_id": sp.ancestor_species_id,
                    "representative_dna": asdict(sp.representative_dna),
                    "population": sp.population,
                    "total_born": sp.total_born,
                    "total_died": sp.total_died,
                    "max_generation": sp.max_generation,
                    "origin_tick": sp.origin_tick,
                    "extinct": sp.extinct,
                    "depth": sp.depth,
                    "innovations": sp.evolutionary_innovations,
                }
                for sp in species_registry.values()
            ],
            "resources": [
                {
                    "id": r.id,
                    "x": r.x,
                    "y": r.y,
                    "energy": r.energy,
                    "resource_type": r.resource_type,
                    "decay_timer": r.decay_timer,
                    "radius": r.radius,
                }
                for r in resources
            ],
            "events": [
                {
                    "id": e.id,
                    "type": e.type,
                    "start_tick": e.start_tick,
                    "duration": e.duration,
                    "elapsed": e.elapsed,
                    "x": e.x,
                    "y": e.y,
                    "radius": e.radius,
                    "intensity": e.intensity,
                    "metadata": e.metadata,
                }
                for e in events
            ],
            "organisms": [
                {
                    "id": o.id,
                    "species_id": o.species_id,
                    "x": o.x,
                    "y": o.y,
                    "vx": o.vx,
                    "vy": o.vy,
                    "ax": o.ax,
                    "ay": o.ay,
                    "angle": o.angle,
                    "energy": o.energy,
                    "health": o.health,
                    "age": o.age,
                    "generation": o.generation,
                    "alive": o.alive,
                    "parent_id": o.parent_id,
                    "second_parent_id": o.second_parent_id,
                    "reproduction_cooldown": o.reproduction_cooldown,
                    "kills": o.kills,
                    "offspring_count": o.offspring_count,
                    "food_consumed": o.food_consumed,
                    "dna": asdict(o.dna),
                    "learned_weights": o.learned_weights,
                }
                for o in organisms
                if o.alive
            ],
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize JSON payload into living universe domain objects."""
        species_registry = {}
        for sp_data in data.get("species", []):
            dna = DNA(**sp_data["representative_dna"])
            sp = Species(
                id=sp_data["id"],
                name=sp_data["name"],
                representative_dna=dna,
                ancestor_species_id=sp_data.get("ancestor_species_id"),
                population=sp_data.get("population", 0),
                total_born=sp_data.get("total_born", 0),
                total_died=sp_data.get("total_died", 0),
                max_generation=sp_data.get("max_generation", 0),
                origin_tick=sp_data.get("origin_tick", 0),
                extinct=sp_data.get("extinct", False),
                depth=sp_data.get("depth", 0),
                evolutionary_innovations=sp_data.get("innovations", []),
            )
            species_registry[sp.id] = sp

        resources = [
            Resource(
                id=r["id"],
                x=r["x"],
                y=r["y"],
                energy=r.get("energy", 25.0),
                resource_type=r.get("resource_type", "plant"),
                decay_timer=r.get("decay_timer", 1200),
                radius=r.get("radius", 3.0),
            )
            for r in data.get("resources", [])
        ]

        events = [
            WorldEvent(
                id=e["id"],
                type=e["type"],
                start_tick=e["start_tick"],
                duration=e["duration"],
                elapsed=e.get("elapsed", 0),
                x=e.get("x"),
                y=e.get("y"),
                radius=e.get("radius"),
                intensity=e.get("intensity", 1.0),
                metadata=e.get("metadata", {}),
            )
            for e in data.get("events", [])
        ]

        organisms = []
        for o_data in data.get("organisms", []):
            dna = DNA(**o_data["dna"])
            org = Organism(
                id=o_data["id"],
                species_id=o_data["species_id"],
                x=o_data["x"],
                y=o_data["y"],
                generation=o_data.get("generation", 0),
                dna=dna,
                vx=o_data.get("vx", 0.0),
                vy=o_data.get("vy", 0.0),
                ax=o_data.get("ax", 0.0),
                ay=o_data.get("ay", 0.0),
                angle=o_data.get("angle", 0.0),
                energy=o_data.get("energy", 80.0),
                health=o_data.get("health", 100.0),
                age=o_data.get("age", 0),
                alive=o_data.get("alive", True),
                parent_id=o_data.get("parent_id"),
                second_parent_id=o_data.get("second_parent_id"),
                reproduction_cooldown=o_data.get("reproduction_cooldown", 0),
                kills=o_data.get("kills", 0),
                offspring_count=o_data.get("offspring_count", 0),
                food_consumed=o_data.get("food_consumed", 0.0),
                learned_weights=o_data.get("learned_weights", [1.0, 1.0, 1.0, 1.0]),
            )
            organisms.append(org)

        return {
            "tick": data.get("tick", 0),
            "births": data.get("births", 0),
            "deaths": data.get("deaths", 0),
            "id_counters": data.get("id_counters", {"next_org_id": 1, "next_species_id": 1, "next_res_id": 1}),
            "config": UniverseConfig(**data.get("config", {})),
            "species_registry": species_registry,
            "resources": resources,
            "events": events,
            "organisms": organisms,
        }
