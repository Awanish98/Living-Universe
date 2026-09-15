"""Pygame mixer wrapper and sound buffer cache manager."""

import os
from typing import Dict, Any, Optional
from .procedural import ProceduralAudioSynth


class AudioManager:
    """Manages audio channels, sound caching, volume levels, and headless fallback."""

    def __init__(self, asset_dir: str = "assets/audio"):
        self.asset_dir = asset_dir
        self.initialized = False
        self.sound_cache: Dict[str, Any] = {}
        self.synth = ProceduralAudioSynth()
        self._init_mixer()

    def _init_mixer(self) -> None:
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(16)
            self.initialized = True
        except Exception:
            self.initialized = False

    def get_sound(self, event_name: str) -> Optional[Any]:
        if not self.initialized:
            return None

        if event_name in self.sound_cache:
            return self.sound_cache[event_name]

        # 1. Try loading from file
        file_path = os.path.join(self.asset_dir, "sfx", f"{event_name.lower()}.wav")
        if os.path.exists(file_path):
            try:
                import pygame
                sound = pygame.mixer.Sound(file_path)
                self.sound_cache[event_name] = sound
                return sound
            except Exception:
                pass

        # 2. Procedural synthesis fallback
        sound = self.synth.create_sound(event_name)
        if sound:
            self.sound_cache[event_name] = sound
        return sound

    def shutdown(self) -> None:
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.quit()
        except Exception:
            pass
        self.initialized = False
