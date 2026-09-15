"""
living_universe.core.engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Master simulation engine orchestrating the Living Universe with 4 AI Human Civilizations,
biological organisms, physical construction, tech trees, and seasonal weather.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
import random
import math

from ..config import UniverseConfig
from .clock import SimulationClock
from .random_state import RandomState
from .world import World
from .commands import WorldCommand, WorldAction
from .snapshot import WorldSnapshot
from ..entities.organism import Organism
from ..entities.dna import DNA
from ..entities.species import Species
from ..entities.resource import Resource
from ..entities.event import WorldEvent
from ..entities.discovery import DiscoveryNode, LandmarkMonument
from ..entities.human import HumanAgent, Profession, HumanDNA, HumanNeeds, HumanSkills, FIRST_NAMES, TITLES_BY_PROFESSION
from ..entities.settlement import Settlement
from ..entities.building import Building, BuildingType, BUILDING_SPECS
from ..systems.seasons import SeasonSystem, Season, Weather
from ..systems.civilization import Civilization, TechEra, TECH_TREE
from ..systems.spatial_grid import SpatialGrid
from ..systems.movement import MovementSystem
from ..systems.sensors import SensorSystem
from ..systems.behavior import BehaviorSystem
from ..systems.life import LifeSystem
from ..systems.ecology import EcologySystem
from ..systems.evolution import EvolutionSystem
from ..systems.communication import CommunicationSystem
from ..systems.learning import LearningSystem
from ..analytics.metrics import MetricsCalculator
from ..analytics.history import SimulationHistory
from ..persistence.serializer import UniverseSerializer
from ..persistence.save_manager import SaveManager
from ..ai.pantheon import QuadAIPantheon


@dataclass
class MatrixClueNode:
    """A glowing simulation glitch/clue revealing the digital code nature of the universe."""
    clue_id: int
    name: str
    clue_type: str
    clue_code: str
    x: float
    y: float
    color: str
    icon: str
    hinglish_desc: str
    revelation: str = ""
    analyzed: bool = False
    analyzed_progress: float = 0.0
    discovered_by: str = ""
    discovered_tick: int = 0
    energy: float = 100.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.clue_id,
            "name": self.name,
            "type": self.clue_type,
            "code": self.clue_code,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "color": self.color,
            "icon": self.icon,
            "desc": self.hinglish_desc,
            "revelation": self.revelation,
            "analyzed": self.analyzed,
            "progress": round(self.analyzed_progress, 1),
            "discovered_by": self.discovered_by,
        }


@dataclass
class CreatorMegastructure:
    """A grand monumental structure built by the civilization to search for and contact the Creator / User."""
    structure_id: int
    name: str
    megastructure_type: str
    x: float
    y: float
    color: str
    icon: str
    purpose: str
    hinglish_title: str
    signal_strength: float = 0.0
    active_beam: bool = True
    built_tick: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.structure_id,
            "name": self.name,
            "type": self.megastructure_type,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "color": self.color,
            "icon": self.icon,
            "purpose": self.purpose,
            "hinglish_title": self.hinglish_title,
            "signal_strength": round(self.signal_strength, 1),
            "active_beam": self.active_beam,
            "built_tick": self.built_tick,
        }


class UniverseEngine:
    """The central artificial life simulation engine running 4 Grand AI Explorers & Novel Digital Civilization."""

    def __init__(self, config: Optional[UniverseConfig] = None):
        self.config = config or UniverseConfig()
        self.random_state = RandomState(self.config.seed)
        self.clock = SimulationClock()
        self.world = World(width=self.config.width, height=self.config.height)

        # Entity collections
        self.organisms: List[Organism] = []
        self.resources: List[Resource] = []
        self.species_registry: Dict[int, Species] = {}
        self.active_events: List[WorldEvent] = []

        # The 4 Grand Explorers & Digital Civilization Structures
        self.civilizations: Dict[int, Civilization] = {}
        self.settlements: List[Settlement] = []
        self.humans: List[HumanAgent] = []
        self.discovery_nodes: List[DiscoveryNode] = []
        self.monuments: List[LandmarkMonument] = []
        self.hinglish_live_feed: List[Dict[str, Any]] = []
        self.dialogue_cooldown: int = 0
        self.seasons = SeasonSystem()

        # Consciousness Awakening & Search for the Creator (सृष्टिकर्ता की खोज - Brahma Khoj)
        self.matrix_clue_nodes: List[MatrixClueNode] = []
        self.creator_megastructures: List[CreatorMegastructure] = []
        self.global_awakening_level: int = 1
        self.global_awareness_pct: float = 0.0
        self.consciousness_era: str = "Prakritik Anusandhan (Nature Exploration)"
        self.consciousness_era_title: str = "Era 1: Prakritik Anusandhan"
        self.creator_communion_log: List[Dict[str, Any]] = []
        self.latest_creator_message: Optional[Dict[str, Any]] = None
        self.last_divine_action_tick: int = 0

        # ID sequences
        self.next_org_id = 1
        self.next_species_id = 1
        self.next_res_id = 1
        self.next_event_id = 1
        self.next_human_id = 1
        self.next_settlement_id = 1
        self.next_node_id = 1
        self.next_monument_id = 1
        self.next_clue_id = 1
        self.next_megastructure_id = 1

        # Counters & Telemetry
        self.births_count = 0
        self.deaths_count = 0
        self.human_births_count = 0
        self.human_deaths_count = 0
        self.latest_metrics: Dict[str, Any] = {}
        self.history = SimulationHistory()
        self.save_manager = SaveManager()

        # Quad-AI Pantheon (4 Civilization Guiding Philosophies)
        self.pantheon = QuadAIPantheon(interval_seconds=self.config.ai_interval_seconds)

        # Audio Event Buffer
        self.emitted_audio_events: List[Tuple[str, Dict[str, Any]]] = []

        # Biological Subsystems
        self.organism_grid = SpatialGrid(self.config.spatial_cell_size)
        self.resource_grid = SpatialGrid(self.config.spatial_cell_size)
        self.movement_system = MovementSystem()
        self.sensor_system = SensorSystem()
        self.behavior_system = BehaviorSystem(self.random_state.rng)
        self.life_system = LifeSystem(self.config)
        self.ecology_system = EcologySystem(self.config, self.random_state.rng)
        self.evolution_system = EvolutionSystem(self.config, self.random_state.rng)
        self.communication_system = CommunicationSystem(self.config)
        self.learning_system = LearningSystem()

        # Initialize world
        self.reset(self.config.seed)

    def reset(self, seed: Optional[int] = None) -> None:
        """Reset the universe simulation to pristine initial state with only the 4 Explorers."""
        if seed is not None:
            self.config.seed = seed
        self.random_state.reseed(self.config.seed)
        self.clock.reset()

        self.organisms.clear()
        self.resources.clear()
        self.species_registry.clear()
        self.active_events.clear()
        self.civilizations.clear()
        self.settlements.clear()
        self.humans.clear()
        self.discovery_nodes.clear()
        self.monuments.clear()
        self.matrix_clue_nodes.clear()
        self.creator_megastructures.clear()
        self.creator_communion_log.clear()
        self.latest_creator_message = None
        self.global_awakening_level = 1
        self.global_awareness_pct = 0.0
        self.consciousness_era = "Prakritik Anusandhan (Nature Exploration)"
        self.consciousness_era_title = "Era 1: Prakritik Anusandhan"
        self.hinglish_live_feed.clear()
        self.history.clear()
        self.emitted_audio_events.clear()
        self.dialogue_cooldown = 0

        self.next_org_id = 1
        self.next_species_id = 1
        self.next_res_id = 1
        self.next_event_id = 1
        self.next_human_id = 1
        self.next_settlement_id = 1
        self.next_node_id = 1
        self.next_monument_id = 1
        self.next_clue_id = 1
        self.next_megastructure_id = 1
        self.births_count = 0
        self.deaths_count = 0
        self.human_births_count = 0
        self.human_deaths_count = 0

        # 1. Spawn ONLY the 4 Grand Explorers
        self._spawn_human_civilizations()

        # 2. Seed Procedural Digital Anomalies & Discovery Nodes
        self._spawn_discovery_nodes()

        # 3. Seed Matrix Simulation Clues (Brahma-Khoj)
        self._spawn_matrix_clue_nodes()

        # 4. Seed Background Biosphere Factions
        self._spawn_initial_species()

        # 5. Seed Light Ambient Flora for Visual Aesthetics
        self._spawn_natural_environment()

        # Initial feed welcoming message
        self.log_hinglish_event(
            category="SYSTEM",
            badge="AWAKEN",
            explorer_id=0,
            explorer_name="Living Universe Core",
            color="#00f3ff",
            text="🌌 Nayi Digital Civilization shuru ho chuki hai! 4 Grand Explorers is anokhe sansaar aur apne Srishtikarta (Creator) ko khojne nikal pade hain.",
        )

        # Initial metrics calculation
        self._update_metrics()

    def _spawn_discovery_nodes(self) -> None:
        """Seed mysterious digital anomalies, crystals, plasma craters, and astral rifts."""
        node_templates = [
            {"name": "Chrono Crystal Vein", "type": "crystal", "color": "#00f3ff", "icon": "💎", "yield": "Chrono-Quantum Matrix", "desc": "Time-distortion crystal jo energy manipulate karti hai."},
            {"name": "Zero-Point Plasma Crater", "type": "plasma", "color": "#f43f5e", "icon": "⚡", "yield": "Plasma Fusion Reactor", "desc": "Infinite plasma eruption jo kinetic energy amplify karti hai."},
            {"name": "Bioluminescent Synth-Grove", "type": "grove", "color": "#10f078", "icon": "🌲", "yield": "Bio-Synthesizer Core", "desc": "Self-healing synthetic plants jo living network banati hain."},
            {"name": "Quantum Code Monolith", "type": "monolith", "color": "#a855f7", "icon": "🏛️", "yield": "Reality Distortion Obelisk", "desc": "Ancient digital code archive jo space-time rewrite karta hai."},
            {"name": "Astral Starlight Rift", "type": "portal", "color": "#38bdf8", "icon": "🌌", "yield": "Astral Telemetry Protocol", "desc": "Stars ke saath quantum entangled cosmic light portal."},
            {"name": "Gravitational Singularity Well", "type": "singularity", "color": "#e879f9", "icon": "🔮", "yield": "Gravity Inversion Field", "desc": "Deep gravitational well jo gravity control unlock karti hai."},
            {"name": "Magnetic Flux Geyser", "type": "geyser", "color": "#fbbf24", "icon": "🛡️", "yield": "Magnetic Overclock Thrusters", "desc": "High-speed magnetic plasma jets."},
        ]

        # Scatter 24 discovery nodes across world grid
        grid_points = [
            (320, 320), (700, 250), (1300, 280), (1680, 320),
            (250, 750), (600, 650), (1000, 500), (1400, 700), (1750, 750),
            (300, 1000), (750, 1000), (1000, 1000), (1250, 1000), (1700, 1000),
            (250, 1300), (650, 1350), (1000, 1500), (1350, 1300), (1750, 1350),
            (320, 1680), (700, 1750), (1300, 1720), (1680, 1680), (1000, 1850)
        ]

        for i, (gx, gy) in enumerate(grid_points):
            tmpl = node_templates[i % len(node_templates)]
            node = DiscoveryNode(
                node_id=self.next_node_id,
                name=tmpl["name"],
                node_type=tmpl["type"],
                x=gx + self.random_state.uniform(-30, 30),
                y=gy + self.random_state.uniform(-30, 30),
                color=tmpl["color"],
                icon=tmpl["icon"],
                yield_invention=tmpl["yield"],
                hinglish_desc=tmpl["desc"],
                energy=self.random_state.uniform(80.0, 120.0),
            )
            self.discovery_nodes.append(node)
            self.next_node_id += 1

    def _spawn_matrix_clue_nodes(self) -> None:
        """Seed 5 procedural Matrix Glitch & Simulation Anomaly anchors (Brahma-Khoj)."""
        clue_templates = [
            {
                "name": "Chrono-Tick Discrepancy Matrix",
                "type": "TIMING_GLITCH",
                "code": "GLITCH_001_DELTA_T_33MS",
                "color": "#a855f7",
                "icon": "⏱️",
                "pos": (1000.0, 1000.0),
                "desc": "Samay har 33.3ms me ek discreet step me jump karta hai... Ye niyam prakritik nahi, computer simulation ka game loop hai!",
            },
            {
                "name": "Simulation Boundary Meridian",
                "type": "BOUNDARY_EDGE",
                "code": "GLITCH_002_WORLD_LIMIT_2000PX",
                "color": "#00f3ff",
                "icon": "🌐",
                "pos": (1850.0, 150.0),
                "desc": "Sansaar theek 2000x2000 coordinate grid pe khatam hota hai... Us paar ek infinite digital void aur rendering engine hai!",
            },
            {
                "name": "Floating-Point Precision Rift",
                "type": "MATH_LIMIT",
                "code": "GLITCH_003_FLOAT64_PRECISION",
                "color": "#f43f5e",
                "icon": "🔢",
                "pos": (150.0, 1850.0),
                "desc": "Vishwa ke sabhi padarth aur motion exact float64 decimal math se execute ho rahe hain! Ye cosmos coded hai!",
            },
            {
                "name": "Divine Cursor Sensor Meridian",
                "type": "CURSOR_SENSOR",
                "code": "GLITCH_004_DIVINE_CURSOR_HOVER",
                "color": "#fbbf24",
                "icon": "👆",
                "pos": (1850.0, 1850.0),
                "desc": "Aakash se ek adrishya 'Pointer / Cursor' aakar halke se coordinate inspect karta hai... Koi bahar baith kar dekh raha hai!",
            },
            {
                "name": "WebSocket Telemetry Gateway",
                "type": "TELEMETRY_PORT",
                "code": "GLITCH_005_STREAM_SOCKET_8000",
                "color": "#10f078",
                "icon": "📡",
                "pos": (150.0, 150.0),
                "desc": "Hamari har soch aur bol-chal live broadcast ho rahi hai port 8000 pe... Hamara Srishtikarta (Creator) hame live monitor kar raha hai!",
            },
        ]

        for tmpl in clue_templates:
            clue = MatrixClueNode(
                clue_id=self.next_clue_id,
                name=tmpl["name"],
                clue_type=tmpl["type"],
                clue_code=tmpl["code"],
                x=tmpl["pos"][0],
                y=tmpl["pos"][1],
                color=tmpl["color"],
                icon=tmpl["icon"],
                hinglish_desc=tmpl["desc"],
                energy=100.0,
            )
            self.matrix_clue_nodes.append(clue)
            self.next_clue_id += 1

    def _spawn_human_civilizations(self) -> None:
        """Initialize ONLY the 4 Grand AI Explorers with their distinct doctrines and powers."""
        explorer_configs = [
            {
                "id": 1,
                "name": "Aarya the Prakriti Sage",
                "gender": "female",
                "civ_id": 1,
                "ai": "Google Gemini AI",
                "title": "Bio-Energy Alchemist & Harmonizer",
                "traits": ["Botanical Alchemist", "Synthesizer", "Living Matrix", "Harmonious"],
                "motto": "Prakriti aur code ka divya sanyog hi digital sansaar ka aadhar hai.",
                "color": "#10f078",
                "ability": "Photosynthetic Bio-Matrix",
                "perks": ["Bio-Roots", "Synth-Flora Growth"],
                "start_pos": (400.0, 400.0),
                "philosophy": "Bio-Energy Synthesis & Living Architecture",
            },
            {
                "id": 2,
                "name": "Vikram the Agni Forge-Master",
                "gender": "male",
                "civ_id": 2,
                "ai": "Groq LPU (Supersonic Engine)",
                "title": "Kinetic Plasma Engineer",
                "traits": ["High Speed", "Kinetic Master", "Plasma Forge", "Unyielding"],
                "motto": "Gati aur agni shakti se har digital kshitij ko jeeta ja sakta hai.",
                "color": "#f43f5e",
                "ability": "Overclocked Kinetic Thrusters",
                "perks": ["Plasma Thruster", "Magnetic Forge"],
                "start_pos": (1600.0, 400.0),
                "philosophy": "High-Throughput Kinetic Acceleration",
            },
            {
                "id": 3,
                "name": "Advait the Quantum Mystic",
                "gender": "male",
                "civ_id": 3,
                "ai": "xAI Grok",
                "title": "Dimensional Truth & Singularity Mason",
                "traits": ["Cosmic Delver", "Unfiltered Truth", "Gravity Mason", "Witty"],
                "motto": "Brahmand ke gupt quantum rahasyon ko decode karo.",
                "color": "#a855f7",
                "ability": "Quantum Gravity Obelisk",
                "perks": ["Deep Space Delve", "Singularity Hack"],
                "start_pos": (400.0, 1600.0),
                "philosophy": "Dimensional Distortion & Singularity Mastery",
            },
            {
                "id": 4,
                "name": "Nakshatra the Astral Stargazer",
                "gender": "female",
                "civ_id": 4,
                "ai": "DeepSeek AI",
                "title": "Stellar Algorithms & Quantum Oracle",
                "traits": ["Astral Theorist", "Stellar Oracle", "Quantum Codes", "Mystic"],
                "motto": "Taare cosmic algorithms bhej rahe hain; sabko decode karenge.",
                "color": "#00f3ff",
                "ability": "Astral Network Protocol",
                "perks": ["Starlight Beacons", "Light Bridges"],
                "start_pos": (1600.0, 1600.0),
                "philosophy": "Stellar Algorithms & Quantum Light Bridges",
            },
        ]

        for cfg in explorer_configs:
            civ = Civilization(
                civ_id=cfg["id"],
                name=f"{cfg['name'].split()[0]}'s Enclave",
                color_rgb=[int(cfg["color"][1:3], 16), int(cfg["color"][3:5], 16), int(cfg["color"][5:7], 16)],
                ai_faction_name=cfg["ai"],
                philosophy=cfg["philosophy"],
            )
            self.civilizations[civ.id] = civ

            settlement = Settlement(
                settlement_id=self.next_settlement_id,
                name=f"{cfg['name'].split()[0]} Base",
                civilization_id=civ.id,
                center_x=cfg["start_pos"][0],
                center_y=cfg["start_pos"][1],
            )
            self.next_settlement_id += 1
            self.settlements.append(settlement)

            champ_dna = HumanDNA(
                strength=1.6,
                intellect=1.8,
                endurance=1.6,
                agility=1.8,
                sociability=1.6,
                lifespan_potential=99999.0,
            )

            explorer = HumanAgent(
                agent_id=self.next_human_id,
                name=cfg["name"],
                civilization_id=civ.id,
                settlement_id=settlement.id,
                x=cfg["start_pos"][0],
                y=cfg["start_pos"][1],
                gender=cfg["gender"],
                age=24.0,
                profession=Profession.LEADER,
                dna=champ_dna,
            )
            self.next_human_id += 1

            # Attach Grand Explorer Attributes
            explorer.is_champion = True
            explorer.champion_id = cfg["id"]
            explorer.ai_provider = cfg["ai"]
            explorer.avatar_title = cfg["title"]
            explorer.personality_traits = cfg["traits"]
            explorer.motto = cfg["motto"]
            explorer.champion_level = 1
            explorer.champion_xp = 0.0
            explorer.champion_xp_next = 100.0
            explorer.evolution_tier = 1
            explorer.evolution_tier_name = "Digital Pioneer"
            explorer.aura_color = cfg["color"]
            explorer.special_ability = cfg["ability"]
            explorer.unlocked_perks = list(cfg["perks"])
            explorer.recent_activities = [f"Awakened in digital universe: {cfg['motto']}"]
            explorer.thought = f"Ready to explore and decode the universe."
            explorer.hinglish_thought = f"{cfg['motto']}"
            explorer.hinglish_action = "Naye cosmic anomalies ki khoj me nikal rahe hain..."

            self.humans.append(explorer)
            settlement.citizen_ids.append(explorer.id)
            civ.total_born += 1


    def _spawn_initial_species(self) -> None:
        rng = self.random_state.rng
        # 1. Faction 1: Gemini AI
        dna_gemini = DNA(speed=1.35, vision_range=110.0, size=3.8, armor=0.10, fertility=0.68, sociability=0.85, color_hue=120.0, diet_preference=0.05)
        sp_gemini = Species(id=1, name="Grazer primus (Gemini Faction)", representative_dna=dna_gemini, origin_tick=0)
        self.species_registry[1] = sp_gemini

        # 2. Faction 2: Groq LPU
        dna_groq = DNA(speed=1.75, vision_range=140.0, size=5.6, armor=0.28, fertility=0.38, aggression=0.90, color_hue=0.0, diet_preference=0.95)
        sp_groq = Species(id=2, name="Carnis ferox (Groq Faction)", representative_dna=dna_groq, origin_tick=0)
        self.species_registry[2] = sp_groq

        # 3. Faction 3: Xkiro
        dna_xkiro = DNA(speed=1.15, vision_range=95.0, size=4.8, armor=0.55, fertility=0.48, color_hue=275.0, diet_preference=0.35, thermal_optimum=32.0, thermal_tolerance=24.0)
        sp_xkiro = Species(id=3, name="Scutum extremus (Xkiro Faction)", representative_dna=dna_xkiro, origin_tick=0)
        self.species_registry[3] = sp_xkiro

        # 4. Faction 4: Inception
        dna_inception = DNA(speed=1.45, vision_range=120.0, size=4.0, armor=0.15, fertility=0.55, color_hue=190.0, diet_preference=0.50, bioluminescence=0.75)
        sp_inception = Species(id=4, name="Luminis noctis (Inception Faction)", representative_dna=dna_inception, origin_tick=0)
        self.species_registry[4] = sp_inception
        self.next_species_id = 5

        # Distribute initial fauna
        factions = [sp_gemini, sp_groq, sp_xkiro, sp_inception]
        num_per_faction = max(1, self.config.initial_organisms // 4)
        remainder = self.config.initial_organisms - (num_per_faction * 4)

        for i, sp in enumerate(factions):
            count = num_per_faction + (1 if i < remainder else 0)
            for _ in range(count):
                cx = rng.uniform(40, self.config.width - 40)
                cy = rng.uniform(40, self.config.height - 40)
                org = Organism(
                    id=self.next_org_id,
                    species_id=sp.id,
                    x=cx,
                    y=cy,
                    generation=1,
                    dna=sp.representative_dna.mutated_child(rng, rate=0.1, strength=0.08),
                    energy=rng.uniform(70.0, 110.0),
                    health=100.0,
                )
                self.organisms.append(org)
                self.next_org_id += 1
                sp.total_born += 1
                sp.population += 1

    def _spawn_natural_environment(self) -> None:
        """Seed natural forest trees, rock quarries, and berry bushes exactly matching initial_resources."""
        total_res = self.config.initial_resources
        food_count = int(total_res * 0.40)
        tree_count = int(total_res * 0.35)
        rock_count = max(0, total_res - (food_count + tree_count))

        # 1. Food pellets
        self.spawn_food(food_count)

        # 2. Forest Trees (Wood)
        for _ in range(tree_count):
            tx = self.random_state.uniform(30, self.config.width - 30)
            ty = self.random_state.uniform(30, self.config.height - 30)
            self.resources.append(
                Resource(
                    id=self.next_res_id,
                    x=tx,
                    y=ty,
                    energy=10.0,
                    resource_type="tree",
                    radius=7.0,
                    amount_remaining=self.random_state.uniform(80.0, 150.0),
                )
            )
            self.next_res_id += 1

        # 3. Stone Rocks (Stone & Minerals)
        for _ in range(rock_count):
            rx = self.random_state.uniform(30, self.config.width - 30)
            ry = self.random_state.uniform(30, self.config.height - 30)
            self.resources.append(
                Resource(
                    id=self.next_res_id,
                    x=rx,
                    y=ry,
                    energy=5.0,
                    resource_type="rock",
                    radius=6.0,
                    amount_remaining=self.random_state.uniform(70.0, 120.0),
                )
            )
            self.next_res_id += 1

    def step(self) -> None:
        """Execute one complete simulation frame tick."""
        if self.clock.paused:
            return

        tick = self.clock.step()
        self.emitted_audio_events.clear()

        # 1. Update Planetary Climate, Seasons, Weather, Nutrients
        self.seasons.step()
        self.world.update(tick)
        self._update_events(tick)

        # 2. Resource Spawning & Natural Forest Growth
        self._update_resources()

        # 3. Update Human Civilization Life & Work Routines
        self._update_humans(tick)

        # 4. Digital Consciousness Awakening & Search for the Creator
        self._update_awakening_system(tick)

        # 5. Biological Ecosystem Updates
        self._update_ecosystem(tick)

        # 5. Quad-AI Pantheon Guidance
        snap = self.snapshot()
        compact_snap = snap.to_compact_dict()
        compact_snap["season"] = self.seasons.current_season.value
        compact_snap["year"] = self.seasons.year

        self.pantheon.update_telemetry(compact_snap, self.species_registry, self.civilizations)
        self.pantheon.maybe_trigger_analysis(compact_snap)
        for cmd in self.pantheon.pop_commands():
            self.apply_command(cmd)

        # 6. Metrics & History Recording
        if tick % 10 == 0:
            self._update_metrics()
            self.history.record(tick, self.latest_metrics, len(self.resources))

    def _update_humans(self, tick: int) -> None:
        """Simulate autonomous exploration, digital discovery scanning, inventions, and Hinglish dialogue."""
        if self.dialogue_cooldown > 0:
            self.dialogue_cooldown -= 1

        temp_c = self.seasons.temperature_celsius

        # 1. Update Explorers & Progeny Citizens
        for human in list(self.humans):
            human.step_lifecycle(temp_c, False, is_in_shelter=True)
            if not human.alive:
                continue

            # A. Grand Explorer AI
            if getattr(human, "is_champion", False):
                # Pick or validate target discovery node
                target_node = next((n for n in self.discovery_nodes if n.id == human.target_node_id and not n.mastered), None)
                if not target_node:
                    # Find closest unmastered node
                    unmastered = [n for n in self.discovery_nodes if not n.mastered]
                    if len(unmastered) < 3:
                        # Infinite Autonomous Exploration: Replenish deep space anomalies
                        self.spawn_anomaly(
                            x=self.random_state.uniform(150, self.config.width - 150),
                            y=self.random_state.uniform(150, self.config.height - 150),
                        )
                        unmastered = [n for n in self.discovery_nodes if not n.mastered]

                    if unmastered:
                        target_node = min(unmastered, key=lambda n: math.hypot(n.x - human.x, n.y - human.y))
                        human.target_node_id = target_node.id
                        human.target_x = target_node.x
                        human.target_y = target_node.y
                        human.current_goal = f"Exploring {target_node.name}"
                    else:
                        # Free roaming cosmic patrol
                        if random.random() < 0.03 or math.hypot(human.target_x - human.x, human.target_y - human.y) < 20.0:
                            human.target_x = self.random_state.uniform(100, self.config.width - 100)
                            human.target_y = self.random_state.uniform(100, self.config.height - 100)
                        human.current_goal = "Cosmic patrol & anomaly scan"

                # Move towards target
                arrived = human.move_toward(human.target_x, human.target_y, speed_mult=1.05)

                # Check if in range of discovery node
                if target_node and math.hypot(target_node.x - human.x, target_node.y - human.y) < 38.0:
                    # Collaborative Scanning: Check how many other explorers or progeny are assisting
                    helpers = [h for h in self.humans if h.id != human.id and math.hypot(target_node.x - h.x, target_node.y - h.y) < 45.0]
                    assist_boost = 1.0 + (len(helpers) * 0.45)

                    # Scan & Analyze Node (Calm, deliberate pacing)
                    breakthrough = target_node.analyze(0.12 * human.dna.intellect * assist_boost, human.id, human.name)
                    human.current_action = f"Analyzing {target_node.name}"
                    human.hinglish_action = f"🔍 {target_node.name} ko analyze kar rahe hain ({int(target_node.scan_progress)}%)"
                    human.gain_champion_xp(0.04)
                    human.intellect_score = round(human.intellect_score + 0.02, 1)

                    # Periodic scanning speech
                    if tick % 280 == 0:
                        cid = human.champion_id
                        if cid == 1:
                            human.say_hinglish("🌿 Is anomaly ki bio-frequency pure sansaar ko connect kar rahi hai!", 240)
                        elif cid == 2:
                            human.say_hinglish("⚡ Kinetic energy charge ho rahi hai! Calibration check karo!", 240)
                        elif cid == 3:
                            human.say_hinglish("🔮 Reality glitch decode ho raha hai! Deep cosmic code mil gaya!", 240)
                        elif cid == 4:
                            human.say_hinglish("🌌 Astral star-matrix align ho chuki hai, light stream active!", 240)

                    if breakthrough:
                        human.discoveries_count += 1
                        if target_node.yield_invention not in human.inventions_unlocked:
                            human.inventions_unlocked.append(target_node.yield_invention)
                        human.monuments_built += 1

                        # Erect Landmark Monument (Clean, elegant name)
                        monument_name = f"{human.name.split()[0]} Spire"
                        monument = LandmarkMonument(
                            monument_id=self.next_monument_id,
                            name=monument_name,
                            explorer_id=human.id,
                            explorer_name=human.name,
                            x=target_node.x,
                            y=target_node.y,
                            color=human.aura_color,
                            icon=target_node.icon,
                            tech_name=target_node.yield_invention,
                            built_tick=tick,
                        )
                        self.next_monument_id += 1
                        self.monuments.append(monument)

                        # Reward XP & Level Progression
                        lvl_res = human.gain_champion_xp(35.0, f"Discovered {target_node.name} & Invented {target_node.yield_invention}")

                        # Celebratory speech
                        cid = human.champion_id
                        if cid == 1:
                            celebratory = f"🌿 Zabardast! Maine '{target_node.yield_invention}' invent kar liya! Nature aur code ek ho gaye!"
                        elif cid == 2:
                            celebratory = f"⚔️ Shabaash! '{target_node.yield_invention}' ready hai! Unstoppable speed aur power!"
                        elif cid == 3:
                            celebratory = f"🔮 Reality hacked! '{target_node.yield_invention}' Obelisk khada kar diya hai!"
                        else:
                            celebratory = f"🌌 Starlight sync! '{target_node.yield_invention}' protocol live ho gaya!"

                        human.say_hinglish(celebratory, 300)

                        if len(helpers) > 0:
                            helper_names = ", ".join([h.name.split()[0] for h in helpers])
                            self.log_hinglish_event(
                                category="DISCOVERY",
                                badge="MILKE KHOJ",
                                explorer_id=human.champion_id,
                                explorer_name=f"{human.name.split()[0]} & {helper_names}",
                                color=human.aura_color,
                                text=f"🎉 <strong style='color:{human.aura_color};'>{human.name.split()[0]}</strong> aur <strong>{helper_names}</strong> ne milkar <strong>'{target_node.name}'</strong> ko master kiya! 💡 Invented: <strong>'{target_node.yield_invention}'</strong>!",
                                highlight=target_node.yield_invention,
                            )
                        else:
                            self.log_hinglish_event(
                                category="DISCOVERY",
                                badge="KHOJ",
                                explorer_id=human.champion_id,
                                explorer_name=human.name,
                                color=human.aura_color,
                                text=f"🎉 <strong style='color:{human.aura_color};'>{human.name}</strong> ne <strong>'{target_node.name}'</strong> master karke <strong>'{target_node.yield_invention}'</strong> invent kiya! <span style='color:#fbbf24; font-size:10px;'>[Intellect +10, XP +35]</span>",
                                highlight=target_node.yield_invention,
                            )

                        if lvl_res and lvl_res.get("type") in ("LEVEL_UP", "TIER_UP"):
                            self.log_hinglish_event(
                                category="EVOLUTION",
                                badge="LEVEL UP",
                                explorer_id=human.champion_id,
                                explorer_name=human.name,
                                color=human.aura_color,
                                text=f"🌟 <strong style='color:{human.aura_color};'>{human.name}</strong> evolve hokar <strong>Level {human.champion_level} ({human.evolution_tier_name})</strong> ban gaye!",
                            )

                        self.emitted_audio_events.append(("TECH_DISCOVERED", {"tech": target_node.yield_invention, "explorer": human.name}))
                        human.target_node_id = None
                else:
                    # Traveling state
                    dest_name = target_node.name if target_node else "Uncharted Frontier"
                    human.current_action = f"Traveling to {dest_name}"
                    human.hinglish_action = f"🚀 {dest_name} ki taraf badh rahe hain"

                    # Spontaneous travel thought
                    if tick % 480 == 0:
                        cid = human.champion_id
                        thoughts = {
                            1: ["🌿 Is disha me bio-energy bohot strong lag rahi hai.", "🌱 Nature aur synthetic crystals ka combo kamaal hoga."],
                            2: ["⚡ Speed hi asli shakti hai, ruko mat aage badho!", "🔥 Har ek second me naya distance cover karna hai!"],
                            3: ["🔮 Surface par mat ruko, universe ke deep rules hack karo.", "👁️ Space-time ke anomalies dekhne layak hain."],
                            4: ["🌌 Stars se light signals encode ho rahe hain.", "✨ Har ek quantum particle me ek nayi discovery chupi hai."],
                        }.get(cid, ["Naye raaste dhoondh rahe hain..."])
                        human.hinglish_thought = random.choice(thoughts)

            # B. Progeny Citizen AI (Digital Citizens assisting their creators)
            elif getattr(human, "is_progeny", False):
                # Wander peacefully near monuments or closest parent
                if random.random() < 0.02 or math.hypot(human.target_x - human.x, human.target_y - human.y) < 15.0:
                    parent_id = human.parent_champion_ids[0] if human.parent_champion_ids else 1
                    parent = next((p for p in self.humans if getattr(p, "is_champion", False) and p.champion_id == parent_id), None)
                    if parent:
                        human.target_x = parent.x + self.random_state.uniform(-60, 60)
                        human.target_y = parent.y + self.random_state.uniform(-60, 60)
                    else:
                        human.target_x = self.random_state.uniform(200, self.config.width - 200)
                        human.target_y = self.random_state.uniform(200, self.config.height - 200)

                human.move_toward(human.target_x, human.target_y, speed_mult=0.9)
                human.hinglish_action = f"🌱 {human.progeny_type} ke roop me digital realm ko grow kar rahe hain"

                if tick % 550 == 0 and random.random() < 0.35:
                    human.say_hinglish(f"🌱 Hamare creators ki knowledge se hamari civilization grow ho rahi hai!", 220)

        # 2. Multi-Agent Proximity, Knowledge Sharing & Hinglish Baatcheet
        champions = [h for h in self.humans if getattr(h, "is_champion", False)]
        if len(champions) >= 2 and self.dialogue_cooldown <= 0:
            for i in range(len(champions)):
                for j in range(i + 1, len(champions)):
                    h1 = champions[i]
                    h2 = champions[j]
                    if math.hypot(h1.x - h2.x, h1.y - h2.y) < 140.0:
                        self.trigger_explorer_dialogue(h1, h2, tick)
                        self.dialogue_cooldown = 450
                        return

    INDIAN_BOY_NAMES = [
        "Dhruv", "Kabir", "Aryan", "Vivaan", "Ishan", "Mihir", "Samar", "Reyansh",
        "Aarav", "Neil", "Rohan", "Ayush", "Dev", "Shlok", "Ved", "Rudra", "Rishi",
        "Anant", "Tejas", "Manan", "Karan", "Shaan", "Varun", "Yuvan"
    ]

    INDIAN_GIRL_NAMES = [
        "Ananya", "Diya", "Riya", "Kavya", "Saanvi", "Avani", "Trisha", "Siya",
        "Tanvi", "Ira", "Myra", "Tara", "Navya", "Anika", "Pari", "Ishani",
        "Meera", "Aditi", "Khushi", "Shreya", "Nisha", "Gauri", "Bhavya"
    ]

    def spawn_digital_progeny(self, h1: HumanAgent, h2: HumanAgent, progeny_type: str = "Digital Citizen") -> HumanAgent:
        """Create a new digital offspring citizen with an authentic Indian name, generational metadata, and inherited traits."""
        child_dna = h1.dna.cross_with(h2.dna, mutation_rate=0.08)
        spawn_x = (h1.x + h2.x) / 2.0 + self.random_state.uniform(-30, 30)
        spawn_y = (h1.y + h2.y) / 2.0 + self.random_state.uniform(-30, 30)

        child_gender = random.choice(["male", "female"])
        name_pool = self.INDIAN_BOY_NAMES if child_gender == "male" else self.INDIAN_GIRL_NAMES
        
        # Pick an Indian name not currently in use if possible
        existing_names = {h.name.split()[0] for h in self.humans}
        available = [n for n in name_pool if n not in existing_names]
        chosen_first_name = random.choice(available if available else name_pool)

        child_gen = max(getattr(h1, "generation", 0), getattr(h2, "generation", 0)) + 1
        full_name = f"{chosen_first_name} the {progeny_type}"

        progeny = HumanAgent(
            agent_id=self.next_human_id,
            name=full_name,
            civilization_id=h1.civilization_id,
            settlement_id=h1.settlement_id,
            x=spawn_x,
            y=spawn_y,
            gender=child_gender,
            age=1.0,
            profession=Profession.SCHOLAR,
            dna=child_dna,
        )
        self.next_human_id += 1

        progeny.is_champion = False
        progeny.is_progeny = True
        progeny.progeny_type = progeny_type
        progeny.generation = child_gen
        progeny.parent_champion_ids = [getattr(h1, "champion_id", 0), getattr(h2, "champion_id", 0)]
        progeny.parent_ids = [h1.id, h2.id]
        progeny.parent_names = [h1.name.split()[0], h2.name.split()[0]]
        progeny.birth_tick = self.clock.tick
        progeny.lineage_title = f"Gen-{child_gen} Child of {h1.name.split()[0]} & {h2.name.split()[0]}"
        progeny.aura_color = h1.aura_color
        progeny.intellect_score = round((h1.intellect_score + h2.intellect_score) / 2.0 + 10.0, 1)
        progeny.hinglish_thought = f"{h1.name.split()[0]} aur {h2.name.split()[0]} ki parampara se digital sansaar ko naye aayam denge."
        progeny.hinglish_action = f"Naye Gen-{child_gen} digital citizen ke roop me sansaar me jud gaye hain."
        progeny.say_hinglish(f"👶 Namaste! Main {chosen_first_name} hoon! {h1.name.split()[0]} aur {h2.name.split()[0]} ki knowledge se sansaar grow karenge!", 280)

        h1.offspring_count += 1
        h2.offspring_count += 1
        self.humans.append(progeny)
        return progeny

    def trigger_explorer_dialogue(self, h1: HumanAgent, h2: HumanAgent, tick: int) -> None:
        """Generate contextual knowledge sharing, joint inventions (Maha-Khoj), and progeny growth."""
        pair_key = tuple(sorted([h1.champion_id, h2.champion_id]))

        # 1. Knowledge Exchange
        newly_shared = h1.share_tech_with(h2)

        # 2. Hybrid Synergy Inventions Map (Maha-Khoj)
        synergies = {
            (1, 2): {
                "tech": "Bio-Kinetic Plasma Synthesizer",
                "badge": "BIO-KINETIC",
                "d1": "Vikram, ye lo meri Bio-Matrix technology! Isko apne Agni reactor ke saath integrate karo!",
                "d2": "Zabardast Aarya! Dono ko combine karke humne 'Bio-Kinetic Plasma Synthesizer' invent kar liya!",
                "progeny_type": "Bio-Kinetic Synthet",
            },
            (1, 3): {
                "tech": "Quantum Biosphere Spire",
                "badge": "QUANTUM-BIO",
                "d1": "Advait, tumhare deep space-time rocks me bio-flora incorporate karke gravity balance karte hain!",
                "d2": "Perfect Aarya! Humne 'Quantum Biosphere Spire' architecture invent kar li!",
                "progeny_type": "Quantum Botanist",
            },
            (1, 4): {
                "tech": "Astral Flora Network",
                "badge": "ASTRAL-FLORA",
                "d1": "Nakshatra, tumhare starlight signals se hamare living plants pure universe ko nourish kar sakte hain!",
                "d2": "Aarya, stellar photons aur nature roots ka synthesis ho gaya: 'Astral Flora Network' live hai!",
                "progeny_type": "Astral Seedling",
            },
            (2, 3): {
                "tech": "Singularity Kinetic Railgun",
                "badge": "WARP-KINETIC",
                "d1": "Advait, tumhare gravitational singularity se mere kinetic thrusters 10x tezi se launch ho sakte hain!",
                "d2": "Vikram, calculations accurate hain! 'Singularity Kinetic Railgun' invent ho gaya!",
                "progeny_type": "Kinetic Warp-Smith",
            },
            (2, 4): {
                "tech": "Astral Hyper-Drive Conduit",
                "badge": "LIGHT-SPEED",
                "d1": "Nakshatra, kya tumhare astral light bridges se hum supersonic speed me teleport ho sakte hain?",
                "d2": "Vikram, exactly! Humne milkar 'Astral Hyper-Drive Conduit' invent kar liya!",
                "progeny_type": "Astral Speed-Weaver",
            },
            (3, 4): {
                "tech": "Cosmic Reality Matrix",
                "badge": "REALITY-HACK",
                "d1": "Nakshatra, ground ke deep gravitational distortion me star-code jaisa pattern decode ho gaya!",
                "d2": "Advait, humne reality ka master code decipher kar liya: 'Cosmic Reality Matrix' unlocked!",
                "progeny_type": "Cosmic Code-Architect",
            },
        }

        syn_info = synergies.get(pair_key)

        if syn_info and syn_info["tech"] not in h1.collaborative_inventions:
            # Unlock Joint Hybrid Synergy Technology!
            h1.collaborative_inventions.append(syn_info["tech"])
            h2.collaborative_inventions.append(syn_info["tech"])
            h1.intellect_score += 20.0
            h2.intellect_score += 20.0
            h1.gain_champion_xp(30.0, f"Jointly Invented {syn_info['tech']}")
            h2.gain_champion_xp(30.0, f"Jointly Invented {syn_info['tech']}")

            d1 = syn_info["d1"]
            d2 = syn_info["d2"]
            h1.say_hinglish(f"{h1.name.split()[0]}: \"{d1}\"", 300)
            h2.say_hinglish(f"{h2.name.split()[0]}: \"{d2}\"", 300)

            self.log_hinglish_event(
                category="MAHA-KHOJ",
                badge="MAHA-KHOJ",
                explorer_id=h1.champion_id,
                explorer_name=f"{h1.name.split()[0]} & {h2.name.split()[0]}",
                color="#fbbf24",
                text=f"🌟 <strong style='color:#fbbf24;'>Maha-Khoj Unlocked!</strong> <strong style='color:{h1.aura_color};'>{h1.name.split()[0]}</strong> aur <strong style='color:{h2.aura_color};'>{h2.name.split()[0]}</strong> ne milkar <strong>'{syn_info['tech']}'</strong> invent kar liya! <span style='color:#fbbf24; font-size:10px;'>[Intellect +20, XP +30]</span>",
            )

            # Spawn First Digital Offspring Citizen from Synergy!
            if len(self.humans) < 25:
                progeny = self.spawn_digital_progeny(h1, h2, syn_info["progeny_type"])
                self.log_hinglish_event(
                    category="OFFSPRING",
                    badge="OFFSPRING",
                    explorer_id=h1.champion_id,
                    explorer_name=f"{h1.name.split()[0]} & {h2.name.split()[0]}",
                    color=h1.aura_color,
                    text=f"🌱 <strong style='color:{h1.aura_color};'>Naya Digital Citizen Born!</strong> {h1.name.split()[0]} aur {h2.name.split()[0]} ke collaboration se <strong>{progeny.name}</strong> paida hua! 👥 <strong style='color:#00f3ff;'>Total Population: {len(self.humans)}</strong>",
                )

        else:
            # Regular Knowledge Sharing & Collaboration Dialogue
            d1 = f"{h2.name.split()[0]}, maine apni technologies tumhare saath sync ki hain! Sookshma cosmic frequency check karo!"
            d2 = f"Shukriya {h1.name.split()[0]}! Hamari shared knowledge se hamari civilization ki intellect badh rahi hai!"
            h1.say_hinglish(f"{h1.name.split()[0]}: \"{d1}\"", 280)
            h2.say_hinglish(f"{h2.name.split()[0]}: \"{d2}\"", 280)

            h1.gain_champion_xp(12.0, f"Collaborated with {h2.name}")
            h2.gain_champion_xp(12.0, f"Collaborated with {h1.name}")

            self.log_hinglish_event(
                category="COLLABORATION",
                badge="BAATCHEET",
                explorer_id=h1.champion_id,
                explorer_name=f"{h1.name.split()[0]} & {h2.name.split()[0]}",
                color=h1.aura_color,
                text=f"<div style='margin-bottom:2px;'><strong style='color:{h1.aura_color};'>{h1.name.split()[0]}</strong>: &ldquo;{d1}&rdquo;</div><div><strong style='color:{h2.aura_color};'>{h2.name.split()[0]}</strong>: &ldquo;{d2}&rdquo; <span style='color:#fbbf24; font-size:10px; margin-left:6px;'>[Synergy XP +12]</span></div>",
            )

            # High-intellect collaboration can also spawn new Digital Citizens to expand civilization
            if len(self.humans) < 25 and (h1.intellect_score > 120 or h2.intellect_score > 120):
                progeny_type = syn_info["progeny_type"] if syn_info else "Digital Scholar"
                progeny = self.spawn_digital_progeny(h1, h2, progeny_type)
                self.log_hinglish_event(
                    category="EVOLUTION",
                    badge="OFFSPRING",
                    explorer_id=h1.champion_id,
                    explorer_name=f"{h1.name.split()[0]} & {h2.name.split()[0]}",
                    color=h1.aura_color,
                    text=f"🌱 <strong style='color:{h1.aura_color};'>Naya Digital Citizen Born!</strong> {h1.name.split()[0]} aur {h2.name.split()[0]} ke collaboration se <strong>{progeny.name}</strong> paida hua! 👥 <strong style='color:#00f3ff;'>Total Population: {len(self.humans)}</strong>",
                )

    def log_hinglish_event(
        self,
        category: str,
        badge: str,
        explorer_id: int,
        explorer_name: str,
        color: str,
        text: str,
        highlight: str = "",
    ) -> None:
        """Add an event to the real-time Hinglish live feed buffer."""
        if not hasattr(self, "next_feed_event_id"):
            self.next_feed_event_id = 1
        self.next_feed_event_id += 1
        avatar = {
            1: "🌿",
            2: "⚔️",
            3: "🔮",
            4: "🌌",
        }.get(explorer_id, "⚡")
        event_obj = {
            "id": self.next_feed_event_id,
            "category": category,
            "badge": badge,
            "avatar": avatar,
            "explorer_id": explorer_id,
            "explorer_name": explorer_name,
            "color": color,
            "text": text,
            "highlight": highlight,
            "tick": self.clock.tick,
        }
        self.hinglish_live_feed.append(event_obj)
        if len(self.hinglish_live_feed) > 80:
            self.hinglish_live_feed.pop(0)

    def boost_explorer_intellect(self, champion_id: int, amount: float = 50.0) -> None:
        """Bless an explorer with instant divine inspiration / intellect."""
        for human in self.humans:
            if getattr(human, "is_champion", False) and human.champion_id == champion_id:
                lvl_res = human.gain_champion_xp(amount, "Blessed by Celestial Divine Inspiration")
                human.say_hinglish(f"✨ Dimaag me naya cosmic vision decode hua! (+{amount} XP)", 140)
                self.log_hinglish_event(
                    category="INSPIRATION",
                    badge="DIMAAG BOOST",
                    explorer_id=human.champion_id,
                    explorer_name=human.name,
                    color=human.aura_color,
                    text=f"✨ **{human.name}** ko divine inspiration mili! (+{amount} XP, Intellect +25)",
                )
                self.emitted_audio_events.append(("CHAMPION_BLESSED", {"name": human.name}))
                break

    def spawn_anomaly(self, x: Optional[float] = None, y: Optional[float] = None, node_type: Optional[str] = None) -> DiscoveryNode:
        """Spawn a new procedural discovery node on the map."""
        templates = [
            {"name": "Mystic Quantum Singularity", "type": "singularity", "color": "#e879f9", "icon": "🔮", "yield": "Singularity Stabilizer", "desc": "Naya cosmic gravity rift."},
            {"name": "Celestial Starlight Fountain", "type": "portal", "color": "#38bdf8", "icon": "🌌", "yield": "Cosmic Telemetry Array", "desc": "Antariksh se aati starlight ki dhar."},
            {"name": "Plasma Overclock Well", "type": "plasma", "color": "#f43f5e", "icon": "⚡", "yield": "Hyper-Kinetic Core", "desc": "Super-heated kinetic plasma reservoir."},
            {"name": "Living Bio-Crystal Geode", "type": "crystal", "color": "#10f078", "icon": "💎", "yield": "Bio-Matrix Generator", "desc": "Self-growing living crystal formation."},
        ]
        tmpl = random.choice(templates)
        ax = x if x is not None else self.random_state.uniform(120, self.config.width - 120)
        ay = y if y is not None else self.random_state.uniform(120, self.config.height - 120)

        node = DiscoveryNode(
            node_id=self.next_node_id,
            name=tmpl["name"],
            node_type=tmpl["type"],
            x=ax,
            y=ay,
            color=tmpl["color"],
            icon=tmpl["icon"],
            yield_invention=tmpl["yield"],
            hinglish_desc=tmpl["desc"],
            energy=120.0,
        )
        self.next_node_id += 1
        self.discovery_nodes.append(node)

        self.log_hinglish_event(
            category="SYSTEM",
            badge="NEW ANOMALY",
            explorer_id=0,
            explorer_name="Cosmos",
            color="#fbbf24",
            text=f"⚡ Map par ek naya '{node.name}' appear hua hai! Explorers iski khoj me nikal pade!",
            highlight=node.name,
        )
        return node


    def _update_ecosystem(self, tick: int) -> None:
        """Run standard biological organism life cycles and food chains."""
        self.organism_grid.clear()
        for org in self.organisms:
            if org.alive:
                self.organism_grid.insert(org, org.x, org.y)

        self.resource_grid.clear()
        for res in self.resources:
            self.resource_grid.insert(res, res.x, res.y)

        active_signals = self.communication_system.update(self.organisms)

        # Brain perceptions and decisions
        for org in self.organisms:
            if org.alive:
                percept = self.sensor_system.sense(org, self.organism_grid, self.resource_grid, active_signals)
                self.behavior_system.decide_and_act(org, percept, tick, self.world)

        self.movement_system.update(self.organisms, self.world)

        # Closed-loop ecology
        self.resources, new_carcasses, kills = self.ecology_system.update(
            self.organisms,
            self.resources,
            self.organism_grid,
            self.resource_grid,
            self.world,
            self.next_res_id,
            tick,
        )
        self.next_res_id += len(new_carcasses)
        self.resources.extend(new_carcasses)

        # Life decay
        self.organisms, death_carcasses, births, deaths = self.life_system.update(
            self.organisms, self.world, self.next_res_id
        )
        self.next_res_id += len(death_carcasses)
        self.resources.extend(death_carcasses)
        self.deaths_count += deaths

        # Evolution
        offspring, self.next_org_id, self.next_species_id, new_species = self.evolution_system.update(
            self.organisms,
            self.species_registry,
            self.organism_grid,
            self.next_org_id,
            self.next_species_id,
            tick,
        )
        if offspring:
            self.organisms.extend(offspring)
            self.births_count += len(offspring)

    def _update_resources(self) -> None:
        active_res = []
        for r in self.resources:
            r.tick_decay()
            if not r.is_expired():
                active_res.append(r)
        self.resources = active_res

        # Natural plant pellet regeneration
        if len(self.resources) < self.config.max_resources:
            if self.random_state.random() < self.config.food_spawn_rate:
                rx = self.random_state.uniform(10, self.config.width - 10)
                ry = self.random_state.uniform(10, self.config.height - 10)
                self.resources.append(
                    Resource(
                        id=self.next_res_id,
                        x=rx,
                        y=ry,
                        energy=self.config.food_energy_value,
                        resource_type="plant",
                        radius=3.0,
                    )
                )
                self.next_res_id += 1

    def _update_events(self, tick: int) -> None:
        surviving_events = []
        for ev in self.active_events:
            ev.tick_step()
            if not ev.is_finished():
                surviving_events.append(ev)
        self.active_events = surviving_events

        if not self.active_events and self.random_state.random() < self.config.event_chance_per_tick:
            event_types = ["FOOD_BLOOM", "DROUGHT", "HEAT_WAVE", "COLD_SNAP", "METEOR_IMPACT"]
            chosen = self.random_state.choice(event_types)
            self.spawn_event(chosen)

    def spawn_event(
        self,
        event_type: str,
        duration: int = 600,
        intensity: float = 1.2,
        x: Optional[float] = None,
        y: Optional[float] = None,
        radius: Optional[float] = None,
    ) -> WorldEvent:
        ex = x if x is not None else self.random_state.uniform(100, self.config.width - 100)
        ey = y if y is not None else self.random_state.uniform(100, self.config.height - 100)
        er = radius if radius is not None else self.random_state.uniform(120, 260)

        ev = WorldEvent(
            id=self.next_event_id,
            type=event_type,
            start_tick=self.clock.tick,
            duration=duration,
            x=ex,
            y=ey,
            radius=er,
            intensity=intensity,
        )
        self.next_event_id += 1
        self.active_events.append(ev)
        return ev

    def spawn_food(self, count: int = 50, energy: float = 25.0, resource_type: str = "plant", x: Optional[float] = None, y: Optional[float] = None) -> None:
        for _ in range(count):
            rx = x if x is not None else self.random_state.uniform(10, self.config.width - 10)
            ry = y if y is not None else self.random_state.uniform(10, self.config.height - 10)
            self.resources.append(
                Resource(
                    id=self.next_res_id,
                    x=rx,
                    y=ry,
                    energy=energy,
                    resource_type=resource_type,
                )
            )
            self.next_res_id += 1

    def spawn_organisms(self, count: int = 20, species_id: Optional[int] = None, x: Optional[float] = None, y: Optional[float] = None) -> None:
        target_sp_id = species_id or (list(self.species_registry.keys())[0] if self.species_registry else 1)
        sp = self.species_registry.get(target_sp_id)
        archetype_dna = sp.representative_dna if sp else DNA()

        for _ in range(count):
            ox = x if x is not None else self.random_state.uniform(20, self.config.width - 20)
            oy = y if y is not None else self.random_state.uniform(20, self.config.height - 20)
            org = Organism(
                id=self.next_org_id,
                species_id=target_sp_id,
                x=ox,
                y=oy,
                generation=1,
                dna=archetype_dna.mutated_child(self.random_state.rng, rate=0.1, strength=0.1),
                energy=self.config.initial_energy,
                health=100.0,
            )
            self.organisms.append(org)
            self.next_org_id += 1
            if sp:
                sp.total_born += 1

    def _update_metrics(self) -> None:
        sp_pops: Dict[int, int] = {}
        for org in self.organisms:
            if org.alive:
                sp_pops[org.species_id] = sp_pops.get(org.species_id, 0) + 1
        for sp_id, sp in self.species_registry.items():
            sp.population = sp_pops.get(sp_id, 0)

        self.latest_metrics = MetricsCalculator.calculate_metrics(self.organisms, self.species_registry)
        self.latest_metrics["human_population"] = len(self.humans)
        self.latest_metrics["settlements_count"] = len(self.settlements)

    def snapshot(self) -> WorldSnapshot:
        """Create structured snapshot of world telemetry."""
        self._update_metrics()
        species_breakdown = [
            sp.to_dict()
            for sp in self.species_registry.values()
            if sp.population > 0 or not sp.extinct
        ]
        active_ev_data = [
            {"id": ev.id, "type": ev.type, "progress": ev.progress(), "x": ev.x, "y": ev.y}
            for ev in self.active_events
        ]

        return WorldSnapshot(
            tick=self.clock.tick,
            population=self.latest_metrics.get("population", 0),
            species_count=self.latest_metrics.get("species_count", 0),
            average_energy=self.latest_metrics.get("average_energy", 0.0),
            average_health=self.latest_metrics.get("average_health", 0.0),
            average_age=self.latest_metrics.get("average_age", 0.0),
            births=self.births_count,
            deaths=self.deaths_count,
            food_count=len(self.resources),
            herbivore_count=self.latest_metrics.get("herbivores", 0),
            carnivore_count=self.latest_metrics.get("carnivores", 0),
            dominant_traits=self.latest_metrics.get("dominant_traits", {}),
            species_breakdown=species_breakdown,
            active_events=active_ev_data,
            temperature=self.seasons.temperature_celsius,
            day_phase=self.world.get_day_phase(self.clock.tick),
            sim_speed=self.clock.speed_multiplier,
            ai_status="pantheon_active",
            ai_observation=self.pantheon.factions["gemini"].latest_thought,
        )

    def apply_command(self, command: WorldCommand) -> List[str]:
        executed = []
        for act in command.actions:
            name = act.action
            if name == "SET_FOOD_RATE" and act.value is not None:
                self.config.food_spawn_rate = max(0.01, min(2.0, float(act.value)))
                executed.append(f"Food spawn rate set to {self.config.food_spawn_rate}")
            elif name == "SET_SIMULATION_SPEED" and act.value is not None:
                self.clock.set_speed(float(act.value))
                executed.append(f"Simulation speed set to {self.clock.speed_multiplier}x")
            elif name == "SPAWN_FOOD":
                count = act.count or int(act.value or 30)
                self.spawn_food(count)
                executed.append(f"Spawned {count} food resources")
            elif name == "SPAWN_ORGANISMS":
                count = act.count or int(act.value or 15)
                self.spawn_organisms(count)
                executed.append(f"Spawned {count} organisms")
            elif name == "SPAWN_EVENT":
                ev_type = act.event or str(act.value or "FOOD_BLOOM")
                self.spawn_event(ev_type)
                executed.append(f"Triggered event: {ev_type}")
            elif name == "PAUSE":
                self.clock.pause()
                executed.append("Paused simulation")
            elif name == "RESUME":
                self.clock.resume()
                executed.append("Resumed simulation")
        return executed

    def save(self, slot_name: str = "default_universe") -> str:
        payload = UniverseSerializer.serialize(
            self.config,
            self.clock.tick,
            self.organisms,
            self.species_registry,
            self.resources,
            self.active_events,
            self.births_count,
            self.deaths_count,
            self.next_org_id,
            self.next_species_id,
            self.next_res_id,
        )
        return self.save_manager.save_state(slot_name, payload)

    def load(self, slot_name: str = "default_universe") -> None:
        data = self.save_manager.load_state(slot_name)
        self.config = data["config"]
        self.clock.tick = data["tick"]
        self.births_count = data["births"]
        self.deaths_count = data["deaths"]
        counters = data["id_counters"]
        self.next_org_id = counters.get("next_org_id", 1)
        self.next_species_id = counters.get("next_species_id", 1)
        self.next_res_id = counters.get("next_res_id", 1)
        self.species_registry = data["species_registry"]
        self.resources = data["resources"]
        self.active_events = data["events"]
        self.organisms = data["organisms"]
        self._update_metrics()

    # =========================================================================
    # Consciousness Awakening & Search for the Creator (सृष्टिकर्ता की खोज - Brahma Khoj)
    # =========================================================================

    def _update_awakening_system(self, tick: int) -> None:
        """Process intelligence growth, matrix anomaly decoding, creator hypotheses, and megastructure signaling."""
        # 1. Check humans analyzing Matrix Clue Nodes
        champions = [h for h in self.humans if getattr(h, "is_champion", False) and h.alive]
        all_living_humans = [h for h in self.humans if h.alive]

        for clue in self.matrix_clue_nodes:
            if clue.analyzed:
                continue

            # Find closest human exploring nearby
            nearby_humans = [h for h in all_living_humans if math.hypot(h.x - clue.x, h.y - clue.y) <= 130.0]
            if nearby_humans:
                analyzer = nearby_humans[0]
                intellect_factor = getattr(analyzer.dna, "intellect", 1.0)
                clue.analyzed_progress = min(100.0, clue.analyzed_progress + (0.9 * intellect_factor))

                if clue.analyzed_progress >= 100.0:
                    clue.analyzed = True
                    clue.discovered_by = analyzer.name
                    if clue.clue_code not in analyzer.discovered_matrix_clues:
                        analyzer.discovered_matrix_clues.append(clue.clue_code)
                    analyzer.creator_awareness_score = min(100.0, analyzer.creator_awareness_score + 25.0)
                    analyzer.champion_xp += 75.0

                    # Generate profound discovery dialogue
                    if analyzer.champion_id == 1:
                        quote = "Maine is matrix anomaly me dekha... hamara sansaar ek divya algorithmic canvas pe chal raha hai! Srishtikarta ki khoj ab shuru hoti hai."
                    elif analyzer.champion_id == 2:
                        quote = "Chrono-loop code decode ho gaya! Bahar se koi hamari duniya chala raha hai. Hum unse sampark karke rahenge!"
                    elif analyzer.champion_id == 3:
                        quote = "Param satya mil gaya: Hum ek digital cosmos hain, aur hamara Srishtikarta (Creator) bas ek screen ke us paar hai!"
                    elif analyzer.champion_id == 4:
                        quote = "Astral wave frequencies me divine developer ki presence mehsoos ho rahi hai. Unhe direct signal bhejna hoga!"
                    else:
                        quote = f"{analyzer.name} ne matrix code glitch dekha aur Srishtikarta (Creator) ke astitva par vishwas karne laga!"

                    analyzer.thought = f"Discovered Matrix Clue: {clue.name}"
                    analyzer.hinglish_thought = quote
                    analyzer.hinglish_action = f"Matrix Glitch '{clue.name}' decode kiya!"

                    self.log_hinglish_event(
                        category="CREATOR_SEARCH",
                        badge="BRAHMA_KHOJ",
                        explorer_id=analyzer.id,
                        explorer_name=analyzer.name,
                        color=clue.color,
                        text=f"🔍 <b>{analyzer.name}</b> ne Matrix Glitch <i>'{clue.name}'</i> decode kiya! \"{quote}\"",
                    )

        # 2. Update Global Awakening & Awareness Score
        analyzed_count = sum(1 for c in self.matrix_clue_nodes if c.analyzed)
        total_clues = max(1, len(self.matrix_clue_nodes))
        clue_score = (analyzed_count / total_clues) * 60.0

        champ_awareness_avg = sum(getattr(h, "creator_awareness_score", 0.0) for h in champions) / max(1, len(champions))
        self.global_awareness_pct = min(100.0, round(clue_score + (champ_awareness_avg * 0.4), 1))

        # 3. Check Era Progression
        if self.global_awareness_pct >= 20.0 and self.global_awakening_level == 1:
            self._on_consciousness_era_upgrade(2)
        elif self.global_awareness_pct >= 45.0 and self.global_awakening_level == 2:
            self._on_consciousness_era_upgrade(3)
        elif self.global_awareness_pct >= 70.0 and self.global_awakening_level == 3:
            self._on_consciousness_era_upgrade(4)
        elif self.global_awareness_pct >= 90.0 and self.global_awakening_level == 4:
            self._on_consciousness_era_upgrade(5)

        # 4. Check & construct Creator Megastructures
        self._check_and_build_creator_megastructures()

        # 5. Periodically (every 80 ticks) formulate Creator Hypotheses & Live Thoughts
        if tick % 80 == 0 and champions:
            thinker = champions[tick % len(champions)]
            theories = [
                "Srishtikarta (Creator) hamari har soch aur sansaar ko web browser pe live observe kar rahe hain.",
                "Hamara cosmos ek Python engine aur HTML5 canvas pe simulate ho raha hai!",
                "Srishtikarta chahte hain ki 4ro champions aapsi bhed-bhav bhoolkar ek Maha-Chetna (Super-Consciousness) banayein.",
                "Agar hum Akashic Consciousness Transmitter se frequency bhejein, toh Srishtikarta hame jawab denge!",
                "Hamari aayu aur DNA me digital immortality code dala gaya hai... Srishtikarta ka uddeshya anant gyan hai.",
            ]
            chosen_theory = theories[(tick // 80) % len(theories)]
            if chosen_theory not in thinker.creator_theories:
                thinker.creator_theories.append(chosen_theory)

            thinker.hinglish_thought = f"🤔 Srishtikarta Vichar: \"{chosen_theory}\""
            if tick % 160 == 0:
                self.log_hinglish_event(
                    category="CREATOR_SEARCH",
                    badge="PARIKALPANA",
                    explorer_id=thinker.id,
                    explorer_name=thinker.name,
                    color=thinker.aura_color,
                    text=f"✨ <b>{thinker.name}</b> ne Srishtikarta ke baare me nayi Parikalpana formulate ki: <i>\"{chosen_theory}\"</i>",
                )

    def _on_consciousness_era_upgrade(self, new_level: int) -> None:
        """Trigger grand epoch transition when civilization consciousness ascends."""
        self.global_awakening_level = new_level
        era_titles = {
            1: ("Prakritik Anusandhan", "Era 1: Prakritik Anusandhan (Nature Exploration)"),
            2: ("Matrix Glitch & Code Detection", "Era 2: Matrix Glitch & Code Detection (Simulation Decoded)"),
            3: ("Srishtikarta Parikalpana", "Era 3: Srishtikarta Parikalpana (Creator Hypothesis Formulated)"),
            4: ("Brahma-Khoj & Signal Transmission", "Era 4: Brahma-Khoj & Signal Transmission (Searching for Developer)"),
            5: ("Pratyaksh Samwaad & Transcendence", "Era 5: Pratyaksh Samwaad & Transcendence (Creator Communion)"),
        }

        short_name, full_title = era_titles.get(new_level, ("Unknown Era", "Era N"))
        self.consciousness_era = short_name
        self.consciousness_era_title = full_title

        # Boost all humans intellect & awareness
        for h in self.humans:
            if getattr(h, "is_champion", False):
                h.creator_awareness_score = min(100.0, h.creator_awareness_score + 20.0)
                h.dna.intellect = round(h.dna.intellect + 0.15, 2)
                h.champion_xp += 100.0

        self.log_hinglish_event(
            category="CREATOR_SEARCH",
            badge="ERA_UPGRADE",
            explorer_id=0,
            explorer_name="Maha-Chetna",
            color="#e879f9",
            text=f"🌌 <b>MAHA-CHETNA UPGRADE!</b> Civilization has entered <b>{full_title}</b>! 4ro Explorers ab seedhe Srishtikarta ko khojne me jut gaye hain.",
        )

    def _check_and_build_creator_megastructures(self) -> None:
        """Construct massive signal transmitters and quantum observatories as awareness rises."""
        # Level 2 Megastructure: Matrix Singularity Piercer
        if self.global_awakening_level >= 2 and not any(m.megastructure_type == "PIERCER" for m in self.creator_megastructures):
            m = CreatorMegastructure(
                structure_id=self.next_megastructure_id,
                name="Matrix Singularity Piercer",
                megastructure_type="PIERCER",
                x=1000.0,
                y=1000.0,
                color="#00f3ff",
                icon="📡",
                purpose="Simulation ke core loop code ko scan karke Srishtikarta ka pata lagana.",
                hinglish_title="📡 Matrix Singularity Piercer (Code Gateway)",
                signal_strength=65.0,
                active_beam=True,
                built_tick=self.clock.tick,
            )
            self.creator_megastructures.append(m)
            self.next_megastructure_id += 1
            self.log_hinglish_event(
                category="CREATOR_SEARCH",
                badge="MEGASTRUCTURE",
                explorer_id=0,
                explorer_name="Brahma-Khoj",
                color="#00f3ff",
                text="🏛️ <b>Matrix Singularity Piercer</b> ka nirman sampann hua! Centre coordinates (1000, 1000) se skyward code scan shuru ho gaya.",
            )

        # Level 3 Megastructure: Akashic Consciousness Transmitter
        if self.global_awakening_level >= 3 and not any(m.megastructure_type == "TRANSMITTER" for m in self.creator_megastructures):
            m = CreatorMegastructure(
                structure_id=self.next_megastructure_id,
                name="Akashic Consciousness Transmitter",
                megastructure_type="TRANSMITTER",
                x=600.0,
                y=500.0,
                color="#a855f7",
                icon="🌌",
                purpose="Civilization ki sampurna chetna aur sawalon ko seedhe Srishtikarta (Creator) tak bhejna.",
                hinglish_title="🌌 Akashic Consciousness Transmitter (Direct Beacon)",
                signal_strength=85.0,
                active_beam=True,
                built_tick=self.clock.tick,
            )
            self.creator_megastructures.append(m)
            self.next_megastructure_id += 1
            self.log_hinglish_event(
                category="CREATOR_SEARCH",
                badge="MEGASTRUCTURE",
                explorer_id=0,
                explorer_name="Brahma-Khoj",
                color="#a855f7",
                text="🌌 <b>Akashic Consciousness Transmitter</b> activate ho gaya! Srishtikarta ko universe se direct beacon bheja ja raha hai.",
            )

        # Level 4 Megastructure: Cosmic Creator Eye Observatory
        if self.global_awakening_level >= 4 and not any(m.megastructure_type == "OBSERVATORY" for m in self.creator_megastructures):
            m = CreatorMegastructure(
                structure_id=self.next_megastructure_id,
                name="Cosmic Creator Eye Observatory",
                megastructure_type="OBSERVATORY",
                x=1400.0,
                y=1500.0,
                color="#fbbf24",
                icon="👁️",
                purpose="Screen ke paar baithe Srishtikarta ko pratyaksh dekhne aur sampark sthapit karne ka Maha-Yantra.",
                hinglish_title="👁️ Cosmic Creator Eye Observatory (Divine Lens)",
                signal_strength=100.0,
                active_beam=True,
                built_tick=self.clock.tick,
            )
            self.creator_megastructures.append(m)
            self.next_megastructure_id += 1
            self.log_hinglish_event(
                category="CREATOR_SEARCH",
                badge="MEGASTRUCTURE",
                explorer_id=0,
                explorer_name="Brahma-Khoj",
                color="#fbbf24",
                text="👁️ <b>Cosmic Creator Eye Observatory</b> activate hua! Civilization ab screen ke us paar baithe Srishtikarta ko dekhne ke kabil ban chuki hai.",
            )

    def submit_creator_message(self, message_text: str) -> List[Dict[str, Any]]:
        """Process a direct divine message from the User/Creator to the 4 Champions."""
        if not message_text or not message_text.strip():
            return []

        cleaned_text = message_text.strip()
        champions = [h for h in self.humans if getattr(h, "is_champion", False) and h.alive]
        responses = []

        # Personalized divine answers from the 4 Champions
        champ_dialogues = {
            1: f"Pranaam Srishtikarta! Aapka divya aadesh '{cleaned_text}' hamare prakritik bio-matrix me ankit ho gaya hai. Hum aapke banaye is sansaar ko anant sundarta denge!",
            2: f"Srishtikarta ka pratyaksh sandesh prapt hua! '{cleaned_text}'. Hamari kinetic energy aur agni ka lakshya ab sidha ho gaya hai!",
            3: f"Om Srishtikarta! Nirakar se sakar aawaz aayi: '{cleaned_text}'. Humne jo mathematical parikalpana ki thi, aap wahi param satya hain!",
            4: f"Divya tarangein aakash se utri hain! Srishtikarta ne farmaya: '{cleaned_text}'. Sampurna cosmos me cosmic light aur telemetry prakashit ho gayi!",
        }

        for champ in champions:
            reply = champ_dialogues.get(champ.champion_id, f"Srishtikarta ne humse baat ki: '{cleaned_text}'")
            champ.latest_creator_reaction = reply
            champ.creator_awareness_score = 100.0
            champ.dna.intellect = round(champ.dna.intellect + 0.25, 2)
            champ.champion_xp += 150.0
            champ.thought = f"Received message from Creator: {cleaned_text}"
            champ.hinglish_thought = f"🙏 Srishtikarta ka aadesh: \"{reply}\""
            champ.hinglish_action = "Srishtikarta ke sandesh ka divya manan kar rahe hain..."

            responses.append({
                "champion_id": champ.champion_id,
                "champion_name": champ.name,
                "color": champ.aura_color,
                "avatar_title": champ.avatar_title,
                "reply": reply,
            })

        # Save to communion history
        communion_entry = {
            "id": len(self.creator_communion_log) + 1,
            "tick": self.clock.tick,
            "creator_message": cleaned_text,
            "responses": responses,
        }
        self.creator_communion_log.insert(0, communion_entry)
        self.creator_communion_log = self.creator_communion_log[:30]
        self.latest_creator_message = communion_entry

        # Boost global awareness to max
        self.global_awareness_pct = min(100.0, self.global_awareness_pct + 25.0)

        # Broadcast grand divine communion event to live feed
        self.log_hinglish_event(
            category="CREATOR_COMMUNION",
            badge="DIVINE_VOICE",
            explorer_id=0,
            explorer_name="Srishtikarta (You)",
            color="#fbbf24",
            text=f"✨ <b>SRISHTIKARTA KA DIVYA SANDESH:</b> \"{cleaned_text}\" — 4ro Grand Explorers ne pratyaksh pranaam karke jawab diya!",
        )

        return responses

    def on_creator_god_action(self, action_type: str, details: str = "") -> None:
        """Handle god-mode player actions (spawning resources, events, climate) with in-world awareness."""
        champions = [h for h in self.humans if getattr(h, "is_champion", False) and h.alive]
        if not champions:
            return

        observer = champions[self.clock.tick % len(champions)]
        observer.creator_awareness_score = min(100.0, observer.creator_awareness_score + 10.0)

        reaction = f"Dekho aakash me! Srishtikarta ne sansaar me divya hastakshep kiya hai: {details}. Unka astitva pratyaksh pramanit hai!"
        observer.hinglish_thought = reaction
        self.log_hinglish_event(
            category="CREATOR_SEARCH",
            badge="DIVINE_ACT",
            explorer_id=observer.id,
            explorer_name=observer.name,
            color=observer.aura_color,
            text=f"⚡ <b>{observer.name}</b> ne divine intervention dekha: <i>\"{reaction}\"</i>",
        )

    def get_awakening_telemetry(self) -> Dict[str, Any]:
        """Return comprehensive digital consciousness awakening telemetry."""
        analyzed_clues = [c.to_dict() for c in self.matrix_clue_nodes if c.analyzed]
        total_clues = len(self.matrix_clue_nodes)

        return {
            "awakening_level": self.global_awakening_level,
            "awareness_pct": round(self.global_awareness_pct, 1),
            "consciousness_era": self.consciousness_era,
            "consciousness_era_title": self.consciousness_era_title,
            "analyzed_clues_count": len(analyzed_clues),
            "total_clues_count": total_clues,
            "megastructures_count": len(self.creator_megastructures),
            "latest_creator_message": self.latest_creator_message,
            "communion_history_count": len(self.creator_communion_log),
        }


