"""Social communication, acoustic signals, and collective alerts system."""

from typing import List, Tuple, Optional
from ..entities.organism import Organism
from ..config import UniverseConfig


class CommunicationSystem:
    """Processes organism social signaling and maintains active acoustic/chemical broadcast fields."""

    def __init__(self, config: UniverseConfig):
        self.config = config
        self.active_signals: List[Tuple[str, float, float, float]] = []  # (type, x, y, radius)

    def update(self, organisms: List[Organism]) -> List[Tuple[str, float, float, float]]:
        """
        Evaluate signal emissions from organisms.
        Returns:
            active_signals: list of (signal_type, x, y, radius)
        """
        self.active_signals.clear()

        for org in organisms:
            if not org.alive or org.signal_cooldown > 0 or org.energy < self.config.signal_energy_cost:
                org.active_signal = None
                continue

            chosen_signal: Optional[str] = None

            # Emit DANGER signal if actively fleeing with high fear/sociability
            if org.current_state == "fleeing" and org.dna.sociability > 0.35:
                chosen_signal = "DANGER"
            # Emit FOOD signal if full/feeding with high sociability
            elif org.current_state == "seeking_food" and org.energy > (org.max_energy * 0.75) and org.dna.sociability > 0.6:
                chosen_signal = "FOOD"
            # Emit MATE signal if eligible and searching
            elif org.is_eligible_for_reproduction() and org.current_state == "mating":
                chosen_signal = "MATE"

            if chosen_signal:
                org.active_signal = chosen_signal
                org.signal_cooldown = self.config.signal_cooldown_ticks
                org.energy -= self.config.signal_energy_cost
                self.active_signals.append((
                    chosen_signal,
                    org.x,
                    org.y,
                    self.config.signal_range * (org.dna.size / 4.0)
                ))
            else:
                org.active_signal = None

        return self.active_signals
