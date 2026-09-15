"""
living_universe.entities.human
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Virtual human entity with physiological needs, professions, skills, culture, and life cycle.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import math
import random


class Profession(str, Enum):
    FARMER = "Farmer"
    LUMBERJACK = "Lumberjack"
    MINER = "Miner"
    BUILDER = "Builder"
    HUNTER = "Hunter"
    SCHOLAR = "Scholar"
    CRAFTER = "Crafter"
    LEADER = "Tribal Leader"
    CHILD = "Youth"
    ELDER = "Village Elder"


FIRST_NAMES = [
    "Aelorn", "Bram", "Cora", "Darek", "Elysia", "Finn", "Gwen", "Hadrian",
    "Isla", "Jarek", "Kaelen", "Lyra", "Milo", "Nadia", "Orion", "Pyra",
    "Quinn", "Rowan", "Silas", "Thalia", "Ulric", "Vaelen", "Wren", "Zephyr",
    "Aria", "Balthazar", "Cassian", "Dahlia", "Ezra", "Freya", "Gideon", "Helena"
]

TITLES_BY_PROFESSION = {
    Profession.FARMER: ["the Harvester", "Greenhand", "Earthtiller", "the Sower"],
    Profession.LUMBERJACK: ["Treefeller", "Oakcleaver", "Woodchopper", "Timberward"],
    Profession.MINER: ["Stonecutter", "Deepdelver", "Oreseeker", "Rockbreaker"],
    Profession.BUILDER: ["the Architect", "Hammerhand", "Stonemason", "Roofer"],
    Profession.HUNTER: ["the Tracker", "Bowmaster", "Swiftstride", "Beastbane"],
    Profession.SCHOLAR: ["the Sage", "Lorekeeper", "Stargazer", "Mindseeker"],
    Profession.CRAFTER: ["the Blacksmith", "Weaver", "Toolmaker", "Artisan"],
    Profession.LEADER: ["the Chieftain", "the Sovereign", "Peacebringer", "the Wise"],
    Profession.CHILD: ["the Little", "the Novice", "the Young"],
    Profession.ELDER: ["the Elder", "the Ancient", "the Storyteller"],
}


class HumanNeeds:
    """Tracks physiological and psychological needs (0.0 to 100.0)."""

    def __init__(self):
        self.hunger = 85.0  # 100 = fully fed, 0 = starving
        self.energy = 90.0  # 100 = well rested, 0 = exhausted
        self.warmth = 90.0  # 100 = warm & comfy, 0 = freezing hypothermia
        self.social = 75.0  # 100 = high camaraderie, 0 = lonely
        self.morale = 80.0  # 100 = inspired & joyful, 0 = depressed
        self.health = 100.0

    def decay(self, temp_celsius: float, energy_drain_mult: float = 1.0, is_in_shelter: bool = False) -> None:
        # Hunger decays slowly
        self.hunger = max(0.0, self.hunger - 0.02)

        # Energy decays while awake
        self.energy = max(0.0, self.energy - (0.02 * energy_drain_mult))

        # Warmth affected by ambient climate & shelters
        if is_in_shelter or temp_celsius >= 12.0:
            self.warmth = min(100.0, self.warmth + 0.5)
        else:
            cold_loss = max(0.0, (12.0 - temp_celsius) * 0.03)
            self.warmth = max(0.0, self.warmth - cold_loss)

        # Social decay
        self.social = max(0.0, self.social - 0.015)

        # Morale impacted by unmet needs
        need_avg = (self.hunger + self.energy + self.warmth + self.social) / 4.0
        if need_avg < 30.0:
            self.morale = max(0.0, self.morale - 0.05)
        elif need_avg > 60.0:
            self.morale = min(100.0, self.morale + 0.08)

        # Health damage only in prolonged extreme starvation/frostbite
        if self.hunger <= 0.0 or self.warmth <= 0.0:
            self.health = max(0.0, self.health - 0.08)
        else:
            self.health = min(100.0, self.health + 0.1)



class HumanSkills:
    """Skill proficiencies that increase with experience and elder teaching (0 to 100)."""

    def __init__(self):
        self.farming = random.uniform(5.0, 25.0)
        self.woodcutting = random.uniform(5.0, 25.0)
        self.mining = random.uniform(5.0, 25.0)
        self.building = random.uniform(5.0, 25.0)
        self.hunting = random.uniform(5.0, 25.0)
        self.research = random.uniform(5.0, 25.0)
        self.crafting = random.uniform(5.0, 25.0)

    def improve(self, skill_name: str, amount: float = 0.5) -> None:
        if hasattr(self, skill_name):
            current = getattr(self, skill_name)
            setattr(self, skill_name, min(100.0, current + amount))


class HumanDNA:
    """Heritable genetic traits passed down through reproduction."""

    def __init__(
        self,
        strength: float = 1.0,
        intellect: float = 1.0,
        endurance: float = 1.0,
        agility: float = 1.0,
        sociability: float = 1.0,
        lifespan_potential: float = 80.0,
    ):
        self.strength = strength
        self.intellect = intellect
        self.endurance = endurance
        self.agility = agility
        self.sociability = sociability
        self.lifespan_potential = lifespan_potential

    @classmethod
    def random_dna(cls) -> "HumanDNA":
        return cls(
            strength=random.uniform(0.7, 1.4),
            intellect=random.uniform(0.7, 1.4),
            endurance=random.uniform(0.7, 1.4),
            agility=random.uniform(0.7, 1.4),
            sociability=random.uniform(0.7, 1.4),
            lifespan_potential=random.uniform(65.0, 95.0),
        )

    def cross_with(self, partner: "HumanDNA", mutation_rate: float = 0.08) -> "HumanDNA":
        def blend(v1: float, v2: float) -> float:
            base = (v1 + v2) / 2.0
            if random.random() < mutation_rate:
                base += random.uniform(-0.15, 0.15)
            return max(0.4, round(base, 2))

        return HumanDNA(
            strength=blend(self.strength, partner.strength),
            intellect=blend(self.intellect, partner.intellect),
            endurance=blend(self.endurance, partner.endurance),
            agility=blend(self.agility, partner.agility),
            sociability=blend(self.sociability, partner.sociability),
            lifespan_potential=blend(self.lifespan_potential, partner.lifespan_potential),
        )


class HumanAgent:
    """An individual virtual human living, working, learning, and socializing."""

    def __init__(
        self,
        agent_id: int,
        name: str,
        civilization_id: int,
        settlement_id: int,
        x: float,
        y: float,
        gender: str = "female",
        age: float = 20.0,
        profession: Profession = Profession.FARMER,
        dna: Optional[HumanDNA] = None,
        generation: int = 1,
    ):
        self.id = agent_id
        self.name = name
        self.civilization_id = civilization_id
        self.settlement_id = settlement_id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.gender = gender
        self.age = age
        self.profession = profession
        self.dna = dna or HumanDNA.random_dna()
        self.needs = HumanNeeds()
        self.skills = HumanSkills()
        self.generation = generation

        # Dynamic state
        self.alive = True
        self.current_action = "Waking up"
        self.target_x = x
        self.target_y = y
        self.assigned_building_id: Optional[int] = None
        self.home_building_id: Optional[int] = None
        self.offspring_count = 0
        self.reproduction_cooldown = 0

        # Personal inventory (carrying capacity)
        self.inventory: Dict[str, float] = {
            "food": 5.0,
            "energy_cells": 10.0,
            "data_shards": 0.0,
            "crystals": 0.0,
        }
        self.max_carry_weight = 30.0 * self.dna.strength

        # Thought bubble / memory
        self.thought = f"Ready to explore the digital frontier as {self.name}."
        self.hinglish_thought = "Nayi digital duniya ko explore karne ke liye tayyar hoon!"
        self.hinglish_action = "Nayi disha me aage badh rahe hain"

        # Explorer Intelligence & Civilizations stats
        self.intellect_score = 100.0
        self.discoveries_count = 0
        self.inventions_unlocked: List[str] = []
        self.known_technologies: List[str] = []
        self.collaborative_inventions: List[str] = []
        self.monuments_built = 0
        self.current_goal = "Exploring uncharted anomalies"
        self.target_node_id: Optional[int] = None
        self.speech_bubble: Optional[str] = None
        self.speech_bubble_timer: int = 0
        self.movement_trail: List[Tuple[float, float]] = []

        # Population & Digital Progeny / Family Tree tracking
        self.is_progeny: bool = False
        self.progeny_type: str = "Pioneer"
        self.generation: int = 0
        self.parent_champion_ids: List[int] = []
        self.parent_ids: List[int] = []
        self.parent_names: List[str] = []
        self.birth_tick: int = 0
        self.lineage_title: str = "Grand Founder"
        self.aura_color: str = "#00f3ff"

        # Consciousness Awakening & Search for the Creator (सृष्टिकर्ता की खोज)
        self.awakening_level: int = 0
        self.creator_awareness_score: float = 0.0
        self.discovered_matrix_clues: List[str] = []
        self.creator_theories: List[str] = []
        self.latest_creator_reaction: Optional[str] = None

    @property
    def is_adult(self) -> bool:
        return True

    @property
    def speed(self) -> float:
        base = 0.82 * self.dna.agility
        if getattr(self, "is_champion", False):
            base *= 1.0 + (min(self.champion_level, 20) * 0.015)
        return base

    def step_lifecycle(self, temp_celsius: float, is_night: bool, is_in_shelter: bool = False) -> None:
        """Aging, metabolism, status decay, and speech bubble timers."""
        if not self.alive:
            return

        # Aging (1 year every 2400 ticks)
        self.age += 1.0 / 2400.0

        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1

        # Check age milestones for mortal citizens
        if not getattr(self, "is_champion", False):
            if self.age < 15.0:
                self.profession = Profession.CHILD
            elif self.age >= 60.0 and self.profession not in (Profession.ELDER, Profession.LEADER):
                self.profession = Profession.ELDER
            elif self.profession == Profession.CHILD and self.age >= 15.0:
                adult_roles = [Profession.FARMER, Profession.BUILDER, Profession.LUMBERJACK, Profession.MINER, Profession.SCHOLAR, Profession.HUNTER]
                self.profession = random.choice(adult_roles)

        # Needs decay
        self.needs.decay(temp_celsius, is_in_shelter=is_in_shelter)

        # Explorer self-sustenance: Grand Explorers regenerate energy & vitals
        if getattr(self, "is_champion", False):
            self.needs.energy = min(100.0, self.needs.energy + 0.15)
            self.needs.health = 100.0
            self.needs.morale = 100.0

        # Check death conditions for mortal citizens
        if not getattr(self, "is_champion", False):
            if self.needs.health <= 0.0 or self.age >= self.dna.lifespan_potential:
                self.alive = False
                self.thought = "Passed peacefully into ancestral memory."

        if self.speech_bubble_timer > 0:
            self.speech_bubble_timer -= 1
            if self.speech_bubble_timer <= 0:
                self.speech_bubble = None

        # Record movement trail (max 10 points)
        if len(self.movement_trail) == 0 or math.hypot(self.movement_trail[-1][0] - self.x, self.movement_trail[-1][1] - self.y) > 15.0:
            self.movement_trail.append((round(self.x, 1), round(self.y, 1)))
            if len(self.movement_trail) > 10:
                self.movement_trail.pop(0)

    def move_toward(self, tx: float, ty: float, speed_mult: float = 1.0) -> bool:
        """Move toward target coordinate. Returns True if arrived within proximity."""
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist < 12.0:
            self.vx = 0.0
            self.vy = 0.0
            return True

        sp = self.speed * speed_mult
        self.vx = (dx / dist) * sp
        self.vy = (dy / dist) * sp
        self.x += self.vx
        self.y += self.vy
        return False

    def say_hinglish(self, text: str, duration_ticks: int = 260) -> None:
        """Set floating speech bubble and update thought."""
        self.speech_bubble = text
        self.speech_bubble_timer = duration_ticks
        self.hinglish_thought = text
        self.thought = text

    def gain_champion_xp(self, amount: float, reason: str = "") -> Optional[Dict[str, Any]]:
        """Add XP to champion and check for Level / Evolution Tier promotions."""
        if not getattr(self, "is_champion", False):
            return None

        self.champion_xp += amount
        self.intellect_score = round(self.intellect_score + (amount * 0.45), 1)
        leveled_up = False
        evolved_tier = False

        while self.champion_xp >= self.champion_xp_next:
            self.champion_xp -= self.champion_xp_next
            self.champion_level += 1
            self.champion_xp_next = round(100.0 * (1.28 ** (self.champion_level - 1)), 1)
            leveled_up = True
            self.intellect_score += 25.0

            # Digital Civilization Evolution Tiers (No Bronze/Iron Age, purely Futuristic/Digital)
            old_tier = self.evolution_tier
            if self.champion_level >= 25:
                self.evolution_tier = 5
                self.evolution_tier_name = "Transcendent Cosmic Deity"
            elif self.champion_level >= 16:
                self.evolution_tier = 4
                self.evolution_tier_name = "Cosmic Archon"
            elif self.champion_level >= 9:
                self.evolution_tier = 3
                self.evolution_tier_name = "Reality Hacker & Architect"
            elif self.champion_level >= 4:
                self.evolution_tier = 2
                self.evolution_tier_name = "Quantum Artificer"
            else:
                self.evolution_tier = 1
                self.evolution_tier_name = "Digital Pioneer"

            if self.evolution_tier > old_tier:
                evolved_tier = True
                new_perk = f"Tier {self.evolution_tier}: {self.evolution_tier_name}"
                if new_perk not in self.unlocked_perks:
                    self.unlocked_perks.append(new_perk)

            # Stat growth
            self.dna.intellect = round(self.dna.intellect + 0.12, 2)
            self.dna.agility = round(self.dna.agility + 0.05, 2)

        if reason:
            self.log_champion_activity(reason)

        if evolved_tier:
            return {"type": "TIER_UP", "level": self.champion_level, "tier": self.evolution_tier, "tier_name": self.evolution_tier_name}
        elif leveled_up:
            return {"type": "LEVEL_UP", "level": self.champion_level}
        return None

    def log_champion_activity(self, text: str) -> None:
        """Log recent activity to explorer's live chronicle."""
        if not hasattr(self, "recent_activities"):
            self.recent_activities = []
        self.recent_activities.append(text)
        if len(self.recent_activities) > 8:
            self.recent_activities.pop(0)

    def share_tech_with(self, other: "HumanAgent") -> List[str]:
        """Exchange unlocked technologies with another explorer. Returns newly shared techs."""
        newly_learned = []
        for tech in self.inventions_unlocked:
            if tech not in other.inventions_unlocked and tech not in other.known_technologies:
                other.known_technologies.append(tech)
                newly_learned.append(tech)
        for tech in other.inventions_unlocked:
            if tech not in self.inventions_unlocked and tech not in self.known_technologies:
                self.known_technologies.append(tech)
                newly_learned.append(tech)
        return newly_learned

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "name": self.name,
            "civilization_id": self.civilization_id,
            "settlement_id": self.settlement_id,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "vx": round(self.vx, 2),
            "vy": round(self.vy, 2),
            "gender": self.gender,
            "age": round(self.age, 1),
            "profession": "Progeny Citizen" if self.is_progeny else "Explorer",
            "alive": self.alive,
            "current_action": self.current_action,
            "thought": self.thought,
            "hinglish_thought": self.hinglish_thought,
            "hinglish_action": self.hinglish_action,
            "speech_bubble": self.speech_bubble,
            "speech_timer": self.speech_bubble_timer,
            "intellect": round(self.intellect_score, 1),
            "discoveries_count": self.discoveries_count,
            "inventions": list(self.inventions_unlocked),
            "known_technologies": list(self.known_technologies),
            "collaborative_inventions": list(self.collaborative_inventions),
            "offspring_count": self.offspring_count,
            "is_progeny": self.is_progeny,
            "progeny_type": self.progeny_type,
            "generation": getattr(self, "generation", 0),
            "parent_ids": list(getattr(self, "parent_ids", [])),
            "parent_names": list(self.parent_names),
            "birth_tick": getattr(self, "birth_tick", 0),
            "lineage_title": getattr(self, "lineage_title", "Grand Founder"),
            "aura_color": getattr(self, "aura_color", "#00f3ff"),
            "awakening_level": getattr(self, "awakening_level", 0),
            "creator_awareness": round(getattr(self, "creator_awareness_score", 0.0), 1),
            "matrix_clues": list(getattr(self, "discovered_matrix_clues", [])),
            "creator_theories": list(getattr(self, "creator_theories", [])),
            "monuments_built": self.monuments_built,
            "current_goal": self.current_goal,
            "trail": list(self.movement_trail),
            "inventory": {k: round(v, 1) for k, v in self.inventory.items()},
        }

        # If Champion Explorer, attach full persona & evolution telemetry
        if getattr(self, "is_champion", False):
            data["champion"] = {
                "champion_id": self.champion_id,
                "ai_provider": self.ai_provider,
                "avatar_title": self.avatar_title,
                "personality_traits": self.personality_traits,
                "motto": self.motto,
                "level": self.champion_level,
                "xp": round(self.champion_xp, 1),
                "xp_next": round(self.champion_xp_next, 1),
                "tier": self.evolution_tier,
                "tier_name": self.evolution_tier_name,
                "aura_color": self.aura_color,
                "special_ability": self.special_ability,
                "unlocked_perks": self.unlocked_perks,
                "collaborative_inventions": list(self.collaborative_inventions),
                "recent_activities": getattr(self, "recent_activities", []),
            }

        return data


