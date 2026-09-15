"""Modular AudioEngine coordinating SFX, ambient sound, rate limiting, and volume controls."""

import time
from typing import Dict, List, Tuple, Optional, Any
from .mixer import AudioManager
from .tts import TTSProvider, NullTTS, LocalTTS


class AudioEngine:
    """Event-driven audio engine with sound caching, volume levels, mute, and rate limiting."""

    def __init__(self, config=None):
        self.config = config
        self.muted = False
        self.master_volume = 0.7
        self.sfx_volume = 0.8
        self.music_volume = 0.4
        self.ambient_volume = 0.5

        self.audio_manager = AudioManager()
        self.tts: TTSProvider = LocalTTS()

        # Rate limiting: event_name -> last_played_timestamp
        self.last_played: Dict[str, float] = {}
        self.min_interval: Dict[str, float] = {
            "FOOD_CONSUMED": 0.08,
            "PARTICLE_BORN": 0.12,
            "PARTICLE_DIED": 0.15,
            "PREDATOR_ATTACK": 0.1,
            "SOCIAL_SIGNAL": 0.2,
            "SPECIES_EMERGED": 0.5,
            "EVOLUTION_MILESTONE": 0.8,
            "WORLD_EVENT_STARTED": 1.0,
            "WORLD_EVENT_ENDED": 1.0,
        }

    def play(self, event_name: str, volume: float = 1.0) -> None:
        if self.muted or not self.audio_manager.initialized:
            return

        now = time.time()
        interval = self.min_interval.get(event_name, 0.05)
        if now - self.last_played.get(event_name, 0.0) < interval:
            return  # Rate limited

        sound = self.audio_manager.get_sound(event_name)
        if sound:
            try:
                calc_vol = max(0.0, min(1.0, self.master_volume * self.sfx_volume * volume))
                sound.set_volume(calc_vol)
                sound.play()
                self.last_played[event_name] = now
            except Exception:
                pass

    def process_events(self, events: List[Tuple[str, Dict[str, Any]]]) -> None:
        """Process simulation-emitted audio events."""
        for ev_type, _ in events:
            self.play(ev_type)

    def speak(self, text: str) -> None:
        if not self.muted:
            self.tts.speak(text)

    def set_master_volume(self, value: float) -> None:
        self.master_volume = max(0.0, min(1.0, value))

    def set_sfx_volume(self, value: float) -> None:
        self.sfx_volume = max(0.0, min(1.0, value))

    def set_music_volume(self, value: float) -> None:
        self.music_volume = max(0.0, min(1.0, value))

    def set_ambient_volume(self, value: float) -> None:
        self.ambient_volume = max(0.0, min(1.0, value))

    def mute(self, enabled: bool = True) -> None:
        self.muted = enabled

    def toggle_mute(self) -> bool:
        self.muted = not self.muted
        return self.muted

    def shutdown(self) -> None:
        self.audio_manager.shutdown()
