"""Living Universe — Reusable artificial-life and living-particle simulation engine."""

from .config import UniverseConfig
from .core.engine import UniverseEngine
from .core.world import World
from .core.commands import WorldCommand, WorldAction
from .core.snapshot import WorldSnapshot
from .entities.organism import Organism
from .entities.dna import DNA
from .entities.species import Species
from .entities.resource import Resource
from .entities.event import WorldEvent
from .audio.engine import AudioEngine
from .ai.orchestrator import AIOrchestrator
from .app import run

__version__ = "0.1.0"
__all__ = [
    "UniverseConfig",
    "UniverseEngine",
    "World",
    "WorldCommand",
    "WorldAction",
    "WorldSnapshot",
    "Organism",
    "DNA",
    "Species",
    "Resource",
    "WorldEvent",
    "AudioEngine",
    "AIOrchestrator",
    "run",
]
