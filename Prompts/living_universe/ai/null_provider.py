"""Offline / Heuristic AI provider providing automated observations without external network calls."""

from typing import Dict, Any
from .base import AIProvider, AIResponse
from ..core.commands import WorldCommand, WorldAction


class NullProvider(AIProvider):
    """Offline heuristic observer that monitors ecosystem health deterministically."""

    name: str = "null_offline"

    def is_available(self) -> bool:
        return True

    def analyze(self, snapshot: Dict[str, Any]) -> AIResponse:
        pop = snapshot.get("population", 0)
        species = snapshot.get("species", snapshot.get("species_count", 0))
        food = snapshot.get("food_count", 0)
        avg_energy = snapshot.get("avg_energy", snapshot.get("average_energy", 0.0))
        trophic = snapshot.get("trophic_balance", {})
        carnivores = trophic.get("carnivores", snapshot.get("carnivore_count", 0))
        herbivores = trophic.get("herbivores", snapshot.get("herbivore_count", 0))

        actions = []
        reason = ""
        observation = ""

        if pop == 0:
            observation = "Extinction event detected. Cosmic seeding required to restart ecosystem."
            actions.append(WorldAction(action="SPAWN_ORGANISMS", count=30))
            actions.append(WorldAction(action="SPAWN_FOOD", count=100))
            reason = "Rescue seeding after population collapse."
        elif pop < 30 and food < 40:
            observation = f"Population critically low ({pop}). Inducing resource bloom to support recovery."
            actions.append(WorldAction(action="SPAWN_EVENT", event="FOOD_BLOOM", duration=500))
            reason = "Preventing population starvation."
        elif pop > 800:
            observation = f"Ecosystem density high ({pop} organisms). Carrying capacity stabilizing naturally."
        elif carnivores > 0 and herbivores == 0:
            observation = f"Apex predators dominating without primary grazers. Spawning prey species."
            actions.append(WorldAction(action="SPAWN_ORGANISMS", count=25))
            reason = "Restoring trophic balance."
        else:
            observation = f"Ecosystem flourishing with {pop} organisms across {species} active species (avg energy: {avg_energy:.1f})."

        cmd = WorldCommand(actions=actions, reason=reason) if actions else None

        return AIResponse(
            provider=self.name,
            success=True,
            observation=observation,
            command=cmd,
        )

    def command(self, user_prompt: str, snapshot: Dict[str, Any]) -> AIResponse:
        prompt_lower = user_prompt.lower()
        actions = []
        obs = f"Processed command: '{user_prompt}'"

        if "food" in prompt_lower or "feed" in prompt_lower or "spawn food" in prompt_lower:
            actions.append(WorldAction(action="SPAWN_FOOD", count=60))
        elif "organism" in prompt_lower or "spawn" in prompt_lower or "life" in prompt_lower:
            actions.append(WorldAction(action="SPAWN_ORGANISMS", count=20))
        elif "bloom" in prompt_lower:
            actions.append(WorldAction(action="SPAWN_EVENT", event="FOOD_BLOOM", duration=600))
        elif "meteor" in prompt_lower or "disaster" in prompt_lower or "strike" in prompt_lower:
            actions.append(WorldAction(action="SPAWN_EVENT", event="METEOR_IMPACT", duration=300))
        elif "pause" in prompt_lower:
            actions.append(WorldAction(action="PAUSE"))
        elif "resume" in prompt_lower or "play" in prompt_lower:
            actions.append(WorldAction(action="RESUME"))
        elif "mutate" in prompt_lower or "evolve" in prompt_lower:
            actions.append(WorldAction(action="MUTATION_BOOST", value=1.5))
        else:
            obs = f"Unrecognized prompt '{user_prompt}', applying standard food replenish."
            actions.append(WorldAction(action="SPAWN_FOOD", count=30))

        return AIResponse(
            provider=self.name,
            success=True,
            observation=obs,
            command=WorldCommand(actions=actions, reason=f"User prompt: {user_prompt}"),
        )
