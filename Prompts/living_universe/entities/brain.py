"""Neural Brain controller directly driven by genome synaptic weights.

Enables autonomous emergent behavior: organisms perceive sensory cues
(food, threat, mates, internal state, light, temperature) and activate
actuators (thrust, steer, bite, eat, signal, mate) via forward propagation.
"""

from typing import List, Dict, Any, Tuple
import math
import numpy as np


class NeuralBrain:
    """Compact 2-layer Feedforward Neural Network controller.
    
    Inputs (12):
      0: Nearest Food dx (normalized to vision range)
      1: Nearest Food dy (normalized to vision range)
      2: Nearest Organism dx (normalized to vision range)
      3: Nearest Organism dy (normalized to vision range)
      4: Organism Kin / Threat affinity (-1.0 predator to +1.0 kin/mate)
      5: Relative Organism Size (other.size / self.size - 1.0)
      6: Current Energy Ratio (energy / max_energy)
      7: Current Health Ratio (health / max_health)
      8: Reproductive Urge / Maturity (0.0 to 1.0)
      9: Environmental Thermal Stress (deviation from optimum)
      10: Ambient Solar Light / Day-Night Phase (0.0 to 1.0)
      11: Constant Bias (+1.0)

    Hidden Layer: 8 neurons (tanh activation)

    Outputs (6):
      0: Forward Thrust [0.0, 1.0] (sigmoid)
      1: Steering Torque [-1.0, 1.0] (tanh)
      2: Attack / Bite Urge [0.0, 1.0] (sigmoid)
      3: Eat / Graze Urge [0.0, 1.0] (sigmoid)
      4: Mating / Pheromone Release Urge [0.0, 1.0] (sigmoid)
      5: Bioluminescence / Warning Signal [0.0, 1.0] (sigmoid)
    """

    NUM_INPUTS = 12
    NUM_HIDDEN = 8
    NUM_OUTPUTS = 6

    TOTAL_WEIGHTS = (NUM_INPUTS * NUM_HIDDEN) + (NUM_HIDDEN * NUM_OUTPUTS)
    # 12 * 8 = 96, 8 * 6 = 48 -> Total = 144 synaptic weights

    def __init__(self, weights: np.ndarray = None):
        if weights is None or len(weights) != self.TOTAL_WEIGHTS:
            # Initialize with small Gaussian random weights
            self.weights = np.random.randn(self.TOTAL_WEIGHTS).astype(np.float32) * 0.5
        else:
            self.weights = np.array(weights, dtype=np.float32)

        # Cache weight matrices
        self._w1_size = self.NUM_INPUTS * self.NUM_HIDDEN
        self.w1 = self.weights[:self._w1_size].reshape((self.NUM_INPUTS, self.NUM_HIDDEN))
        self.w2 = self.weights[self._w1_size:].reshape((self.NUM_HIDDEN, self.NUM_OUTPUTS))

        # Runtime telemetry cache for UI inspection
        self.last_inputs = np.zeros(self.NUM_INPUTS, dtype=np.float32)
        self.last_hidden = np.zeros(self.NUM_HIDDEN, dtype=np.float32)
        self.last_outputs = np.zeros(self.NUM_OUTPUTS, dtype=np.float32)

    def forward(self, inputs: List[float]) -> np.ndarray:
        """Run forward propagation and return motor outputs."""
        inp_arr = np.array(inputs, dtype=np.float32)
        if len(inp_arr) < self.NUM_INPUTS:
            padded = np.zeros(self.NUM_INPUTS, dtype=np.float32)
            padded[:len(inp_arr)] = inp_arr
            inp_arr = padded
        elif len(inp_arr) > self.NUM_INPUTS:
            inp_arr = inp_arr[:self.NUM_INPUTS]

        self.last_inputs = inp_arr

        # Hidden layer with tanh activation
        hidden = np.tanh(np.dot(inp_arr, self.w1))
        self.last_hidden = hidden

        # Output layer with specialized activations
        raw_out = np.dot(hidden, self.w2)

        # Output 0: Thrust [0, 1] via sigmoid
        thrust = float(1.0 / (1.0 + np.exp(-np.clip(raw_out[0], -10.0, 10.0))))
        # Output 1: Steer [-1, 1] via tanh
        steer = float(np.tanh(raw_out[1]))
        # Outputs 2-5: Action urges [0, 1] via sigmoid
        attack = float(1.0 / (1.0 + np.exp(-np.clip(raw_out[2], -10.0, 10.0))))
        eat = float(1.0 / (1.0 + np.exp(-np.clip(raw_out[3], -10.0, 10.0))))
        mate = float(1.0 / (1.0 + np.exp(-np.clip(raw_out[4], -10.0, 10.0))))
        signal = float(1.0 / (1.0 + np.exp(-np.clip(raw_out[5], -10.0, 10.0))))

        self.last_outputs = np.array([thrust, steer, attack, eat, mate, signal], dtype=np.float32)
        return self.last_outputs

    def mutate(self, rate: float = 0.08, strength: float = 0.25, rng=None) -> "NeuralBrain":
        """Produce a mutated offspring brain."""
        new_weights = np.copy(self.weights)
        if rng is None:
            mask = np.random.rand(self.TOTAL_WEIGHTS) < rate
            deltas = np.random.randn(self.TOTAL_WEIGHTS).astype(np.float32) * strength
        else:
            mask = np.array([rng.random() < rate for _ in range(self.TOTAL_WEIGHTS)])
            deltas = np.array([rng.gauss(0, strength) for _ in range(self.TOTAL_WEIGHTS)], dtype=np.float32)

        new_weights[mask] += deltas[mask]
        # Clip weights to prevent runaway gradients
        np.clip(new_weights, -4.0, 4.0, out=new_weights)
        return NeuralBrain(new_weights)

    def crossover(self, other: "NeuralBrain", rng=None) -> "NeuralBrain":
        """Produce a child brain by combining parent synaptic weights."""
        if rng is None:
            mask = np.random.rand(self.TOTAL_WEIGHTS) < 0.5
        else:
            mask = np.array([rng.random() < 0.5 for _ in range(self.TOTAL_WEIGHTS)])

        child_weights = np.where(mask, self.weights, other.weights)
        return NeuralBrain(child_weights)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize brain state for telemetry and persistence."""
        return {
            "weights": self.weights.tolist(),
            "last_inputs": [round(float(x), 3) for x in self.last_inputs],
            "last_hidden": [round(float(x), 3) for x in self.last_hidden],
            "last_outputs": [round(float(x), 3) for x in self.last_outputs],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NeuralBrain":
        weights = np.array(data.get("weights", []), dtype=np.float32)
        return cls(weights if len(weights) == cls.TOTAL_WEIGHTS else None)
