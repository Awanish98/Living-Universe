"""Lightweight lifespan reinforcement learning and policy adaptation system."""

from typing import List
from ..entities.organism import Organism


class LearningSystem:
    """Adapts organism behavioral weights based on experiential reward feedback."""

    def __init__(self, learning_rate: float = 0.05, discount_factor: float = 0.9):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

    def update(self, organisms: List[Organism]) -> None:
        for org in organisms:
            if not org.alive or abs(org.last_reward) < 0.001:
                continue

            # State to weight index map: [0: food, 1: flee, 2: hunt, 3: social]
            state_index = None
            if org.current_state in ("seeking_food", "foraging"):
                state_index = 0
            elif org.current_state in ("fleeing", "evading"):
                state_index = 1
            elif org.current_state in ("hunting", "attacking"):
                state_index = 2
            elif org.current_state in ("socializing", "mating"):
                state_index = 3

            if state_index is not None and len(org.learned_weights) == 4:
                # Update policy weight
                delta = self.learning_rate * org.last_reward
                org.learned_weights[state_index] = max(
                    0.2, min(3.5, org.learned_weights[state_index] + delta)
                )

            # Decay and reset reward buffer
            org.last_reward = 0.0
