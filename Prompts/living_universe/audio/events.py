"""Typed audio event definitions."""

from typing import Tuple

EVENTS: Tuple[str, ...] = (
    "PARTICLE_BORN",
    "PARTICLE_DIED",
    "FOOD_CONSUMED",
    "PREDATOR_ATTACK",
    "SOCIAL_SIGNAL",
    "SPECIES_EMERGED",
    "EVOLUTION_MILESTONE",
    "WORLD_EVENT_STARTED",
    "WORLD_EVENT_ENDED",
    "AI_OBSERVATION",
)
