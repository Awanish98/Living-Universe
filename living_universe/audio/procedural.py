"""Zero-dependency procedural sound synthesizer generating dynamic SFX and ambient audio."""

import numpy as np
from typing import Optional, Any


class ProceduralAudioSynth:
    """Synthesizes procedural audio waveforms for SFX, chirps, and ambient drones."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def create_sound(self, sound_type: str) -> Optional[Any]:
        """Generate a pygame.mixer.Sound object procedurally."""
        try:
            import pygame
            if not pygame.mixer.get_init():
                return None

            samples: np.ndarray

            if sound_type == "PARTICLE_BORN":
                # High pleasant chirp
                samples = self._generate_chirp(440.0, 880.0, duration=0.12, attack=0.01, decay=0.11)
            elif sound_type == "PARTICLE_DIED":
                # Low soft descending fade
                samples = self._generate_chirp(220.0, 110.0, duration=0.18, attack=0.01, decay=0.17)
            elif sound_type == "FOOD_CONSUMED":
                # Quick subtle blip
                samples = self._generate_tone(523.25, duration=0.06, attack=0.005, decay=0.055)
            elif sound_type == "PREDATOR_ATTACK":
                # Crisp snappy impact
                samples = self._generate_impact(duration=0.14)
            elif sound_type == "SOCIAL_SIGNAL":
                # Resonant dual ping
                samples = self._generate_chord([659.25, 987.77], duration=0.15)
            elif sound_type in ("SPECIES_EMERGED", "EVOLUTION_MILESTONE"):
                # Majestic ascending triad
                samples = self._generate_arpeggio([440.0, 554.37, 659.25, 880.0], duration=0.35)
            elif sound_type == "WORLD_EVENT_STARTED":
                # Low cosmic rumble / swell
                samples = self._generate_rumble(duration=0.6)
            elif sound_type == "WORLD_EVENT_ENDED":
                # Harmonious resolving chord
                samples = self._generate_chord([330.0, 392.0, 493.88], duration=0.4)
            else:
                samples = self._generate_tone(440.0, duration=0.1)

            # Convert to stereo 16-bit PCM
            stereo = np.column_stack((samples, samples))
            int_samples = (stereo * 32767).astype(np.int16)
            return pygame.sndarray.make_sound(int_samples)
        except Exception:
            return None

    def _generate_tone(self, freq: float, duration: float, attack: float = 0.01, decay: float = 0.09) -> np.ndarray:
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        wave = np.sin(2.0 * np.pi * freq * t)
        env = self._create_envelope(len(t), attack, decay, duration)
        return wave * env

    def _generate_chirp(self, f_start: float, f_end: float, duration: float, attack: float, decay: float) -> np.ndarray:
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        freqs = np.linspace(f_start, f_end, len(t))
        phase = 2.0 * np.pi * np.cumsum(freqs) / self.sample_rate
        wave = np.sin(phase)
        env = self._create_envelope(len(t), attack, decay, duration)
        return wave * env

    def _generate_chord(self, freqs: list[float], duration: float) -> np.ndarray:
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        combined = np.zeros_like(t)
        for f in freqs:
            combined += np.sin(2.0 * np.pi * f * t)
        combined /= len(freqs)
        env = self._create_envelope(len(t), 0.02, duration - 0.02, duration)
        return combined * env

    def _generate_arpeggio(self, freqs: list[float], duration: float) -> np.ndarray:
        samples = []
        note_dur = duration / len(freqs)
        for f in freqs:
            samples.append(self._generate_tone(f, note_dur, attack=0.01, decay=note_dur - 0.01))
        return np.concatenate(samples)

    def _generate_impact(self, duration: float) -> np.ndarray:
        num_samples = int(self.sample_rate * duration)
        noise = np.random.uniform(-1.0, 1.0, num_samples)
        t = np.linspace(0, duration, num_samples, endpoint=False)
        tone = np.sin(2.0 * np.pi * 120.0 * t)
        combined = 0.7 * noise + 0.3 * tone
        env = np.exp(-18.0 * t)
        return combined * env

    def _generate_rumble(self, duration: float) -> np.ndarray:
        num_samples = int(self.sample_rate * duration)
        noise = np.random.uniform(-0.5, 0.5, num_samples)
        t = np.linspace(0, duration, num_samples, endpoint=False)
        bass = np.sin(2.0 * np.pi * 65.0 * t)
        combined = 0.5 * noise + 0.5 * bass
        env = self._create_envelope(num_samples, 0.1, duration - 0.1, duration)
        return combined * env

    def _create_envelope(self, num_samples: int, attack: float, decay: float, duration: float) -> np.ndarray:
        att_samples = max(1, int(self.sample_rate * attack))
        dec_samples = max(1, num_samples - att_samples)
        attack_curve = np.linspace(0.0, 1.0, att_samples)
        decay_curve = np.linspace(1.0, 0.0, dec_samples)
        return np.concatenate((attack_curve, decay_curve))[:num_samples]
