"""
living_universe.ai.pantheon
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Quad-AI Pantheon: Orchestrating 4 distinct AI personalities directing 4 human civilizations.
"""

import threading
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from .base import AIProvider, AIResponse
from .gemini import GeminiProvider
from .groq_provider import GroqProvider
from .xai import XAIProvider
from .custom_provider import CustomAIProvider
from .null_provider import NullProvider
from .prompts import (
    GEMINI_FACTION_PROMPT,
    GROQ_FACTION_PROMPT,
    XKIRO_FACTION_PROMPT,
    INCEPTION_FACTION_PROMPT,
)
from ..core.commands import WorldCommand, WorldAction


@dataclass
class FactionDirector:
    id: str  # "gemini", "groq", "xkiro", "inception"
    name: str
    civ_id: int
    civ_name: str
    species_id: int
    species_name: str
    color_rgb: List[int]
    color_hex: str
    philosophy: str
    provider: AIProvider
    system_prompt: str
    latest_thought: str = "Awaiting initial sensory telemetry..."
    active_policy: str = "Baseline Agrarian Founding"
    last_analysis_time: float = 0.0
    is_busy: bool = False
    population: int = 0
    max_generation: int = 1
    buildings_count: int = 0
    current_era: str = "Neolithic Age"
    current_tech: str = "Fire Mastery"


class QuadAIPantheon:
    """Manages the 4 concurrent AI personalities competing and evolving in the digital universe."""

    def __init__(self, interval_seconds: float = 15.0):
        self.interval_seconds = interval_seconds
        self._running = True
        self.pending_commands: List[WorldCommand] = []
        self._lock = threading.Lock()

        # Initialize the 4 AI Providers
        self.gemini_prov = GeminiProvider()
        self.groq_prov = GroqProvider()
        self.xkiro_prov = XAIProvider()
        self.inception_prov = CustomAIProvider()
        self.null_prov = NullProvider()

        # Build Factions
        self.factions: Dict[str, FactionDirector] = {
            "gemini": FactionDirector(
                id="gemini",
                name="Aarya Prakriti Republic",
                civ_id=1,
                civ_name="Aarya Prakriti Republic",
                species_id=1,
                species_name="Prakriti Pioneers",
                color_rgb=[16, 240, 120],
                color_hex="#10f078",
                philosophy="Harmonic bio-energy synthesis, botanical architecture, communal granaries, and ecological mastery.",
                provider=self.gemini_prov if self.gemini_prov.is_available() else self.null_prov,
                system_prompt=GEMINI_FACTION_PROMPT,
                latest_thought="Sowing bio-energy flora across fertile riverside plots.",
                active_policy="+30% Crop Yields, Bio-Energy Mastery",
            ),
            "groq": FactionDirector(
                id="groq",
                name="Vikram Agni Legion",
                civ_id=2,
                civ_name="Vikram Agni Legion",
                species_id=2,
                species_name="Agni Forge Pioneers",
                color_rgb=[244, 63, 94],
                color_hex="#f43f5e",
                philosophy="Martial discipline, plasma metallurgy, supersonic kinetic power, and predator defense.",
                provider=self.groq_prov if self.groq_prov.is_available() else self.null_prov,
                system_prompt=GROQ_FACTION_PROMPT,
                latest_thought="Forging kinetic plasma matrices and fortified watchtowers against anomalies.",
                active_policy="+40% Construction Speed, Plasma Forge",
            ),
            "xkiro": FactionDirector(
                id="xkiro",
                name="Advait Quantum Empire",
                civ_id=3,
                civ_name="Advait Quantum Empire",
                species_id=3,
                species_name="Quantum Mystics",
                color_rgb=[168, 85, 247],
                color_hex="#a855f7",
                philosophy="Monumental stone architecture, singularity mining, winter survival, and stoic philosophy.",
                provider=self.xkiro_prov if self.xkiro_prov.is_available() else self.null_prov,
                system_prompt=XKIRO_FACTION_PROMPT,
                latest_thought="Probing gravitational singularities and building insulated quantum hearths.",
                active_policy="+50% Quarry Mining, Singularity Resilience",
            ),
            "inception": FactionDirector(
                id="inception",
                name="Nakshatra Astral Guild",
                civ_id=4,
                civ_name="Nakshatra Astral Guild",
                species_id=4,
                species_name="Astral Stargazers",
                color_rgb=[0, 243, 255],
                color_hex="#00f3ff",
                philosophy="Accelerated science, stellar algorithms, quantum light bridges, and nocturnal trade.",
                provider=self.inception_prov if self.inception_prov.is_available() else self.null_prov,
                system_prompt=INCEPTION_FACTION_PROMPT,
                latest_thought="Documenting celestial movements and pioneering stellar network protocols.",
                active_policy="+60% Research Speed, Astral Algorithms",
            ),
        }

        # Start multi-agent background worker thread
        self._worker_thread = threading.Thread(target=self._pantheon_worker, daemon=True)
        self._worker_thread.start()

    def update_telemetry(
        self,
        snapshot_dict: Dict[str, Any],
        species_registry: Dict[int, Any],
        civilizations: Optional[Dict[int, Any]] = None,
    ):
        """Update live faction stats from universe engine snapshot."""
        for faction in self.factions.values():
            if civilizations and faction.civ_id in civilizations:
                civ = civilizations[faction.civ_id]
                faction.current_era = civ.current_era.value
                faction.current_tech = civ.current_research or "All Completed"
                faction.buildings_count = civ.buildings_constructed
            sp = species_registry.get(faction.species_id)
            if sp:
                faction.population = sp.population
                faction.max_generation = sp.max_generation

    def maybe_trigger_analysis(self, snapshot_dict: Dict[str, Any]):
        """Check if any faction AI is due for a strategic reasoning cycle."""
        now = time.time()
        for faction in self.factions.values():
            if (now - faction.last_analysis_time >= self.interval_seconds) and not faction.is_busy:
                faction.is_busy = True
                faction.last_analysis_time = now
                threading.Thread(
                    target=self._run_faction_inference,
                    args=(faction, snapshot_dict),
                    daemon=True,
                ).start()

    def _run_faction_inference(self, faction: FactionDirector, snapshot_dict: Dict[str, Any]):
        """Execute one isolated asynchronous reasoning turn for this AI faction."""
        try:
            prompt = (
                f"WORLD & CIVILIZATION SNAPSHOT FOR {faction.name.upper()}:\n"
                f"Current Era: {faction.current_era}\n"
                f"Current Research: {faction.current_tech}\n"
                f"Population: {faction.population} citizens\n"
                f"Buildings Constructed: {faction.buildings_count}\n"
                f"Tick: {snapshot_dict.get('tick', 0)}, Year: {snapshot_dict.get('year', 1)}\n"
                f"Season: {snapshot_dict.get('season', 'Spring')}, Temp: {snapshot_dict.get('temperature', 20.0)}°C\n"
                f"Provide your 1-2 sentence civilization decree for your people."
            )

            if faction.provider and faction.provider.is_available():
                resp: AIResponse = faction.provider.analyze(
                    prompt=prompt,
                    system_prompt=faction.system_prompt,
                    temperature=0.7,
                )
                if resp and resp.text:
                    faction.latest_thought = resp.text.strip().replace('"', "").replace("{", "").replace("}", "")
                    if resp.command:
                        with self._lock:
                            self.pending_commands.append(resp.command)
            else:
                # Procedural deterministic synthesis
                self._synthesize_procedural_thought(faction, snapshot_dict)
        except Exception as e:
            self._synthesize_procedural_thought(faction, snapshot_dict)
        finally:
            faction.is_busy = False

    def _synthesize_procedural_thought(self, faction: FactionDirector, snapshot: Dict[str, Any]):
        """Rich contextual fallback thought synthesis."""
        season = snapshot.get("season", "Spring")
        pop = faction.population
        tech = faction.current_tech

        if faction.id == "gemini":
            faction.latest_thought = (
                f"Cultivating communal orchards in {season}. Prioritizing {tech} to nourish our {pop} citizens."
            )
        elif faction.id == "groq":
            faction.latest_thought = (
                f"Fortifying settlements and forging tools. Our {pop} warriors stand disciplined in {season}."
            )
        elif faction.id == "xkiro":
            faction.latest_thought = (
                f"Quarrying deep stone foundations to withstand {season}. Advancing {tech} for eternity."
            )
        elif faction.id == "inception":
            faction.latest_thought = (
                f"Charting astral constellations this {season}. Accelerating {tech} discoveries across our academies."
            )

    def _pantheon_worker(self):
        """Worker loop managing background tasks."""
        while self._running:
            time.sleep(1.0)

    def pop_commands(self) -> List[WorldCommand]:
        """Fetch and clear queued commands generated by any of the 4 AIs."""
        with self._lock:
            cmds = list(self.pending_commands)
            self.pending_commands.clear()
            return cmds

    def to_dict(self) -> Dict[str, Any]:
        """Serialize 4-AI Pantheon state for Web UI rendering."""
        return {
            fid: {
                "id": f.id,
                "name": f.name,
                "civ_name": f.civ_name,
                "species_name": f.species_name,
                "color_rgb": f.color_rgb,
                "color_hex": f.color_hex,
                "philosophy": f.philosophy,
                "thought": f.latest_thought,
                "policy": f.active_policy,
                "population": f.population,
                "era": f.current_era,
                "tech": f.current_tech,
                "buildings": f.buildings_count,
                "is_active": f.provider.is_available() if f.provider else False,
            }
            for fid, f in self.factions.items()
        }

    def shutdown(self):
        self._running = False
