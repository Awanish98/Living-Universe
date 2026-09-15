"""Deterministic random number generator state management."""

import random
from random import Random
from typing import Tuple


class RandomState:
    """Encapsulates deterministic PRNG streams for reproducibility."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = Random(seed)

    def reseed(self, seed: int) -> None:
        self.seed = seed
        self.rng.seed(seed)

    def uniform(self, a: float, b: float) -> float:
        return self.rng.uniform(a, b)

    def random(self) -> float:
        return self.rng.random()

    def randint(self, a: int, b: int) -> int:
        return self.rng.randint(a, b)

    def choice(self, seq):
        return self.rng.choice(seq)

    def sample(self, population, k):
        return self.rng.sample(population, k)

    def gauss(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        return self.rng.gauss(mu, sigma)

    def get_child_rng(self) -> Random:
        """Create a deterministic child RNG instance."""
        child_seed = self.rng.randint(0, 2**31 - 1)
        return Random(child_seed)

    def get_state(self) -> Tuple:
        return self.rng.getstate()

    def set_state(self, state: Tuple) -> None:
        self.rng.setstate(state)
