"""Modular Text-to-Speech (TTS) provider abstraction for AI narration."""

from abc import ABC, abstractmethod
from typing import Optional


class TTSProvider(ABC):
    @abstractmethod
    def speak(self, text: str) -> None:
        pass


class NullTTS(TTSProvider):
    def speak(self, text: str) -> None:
        pass


class LocalTTS(TTSProvider):
    def __init__(self):
        self._engine = None
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
        except Exception:
            self._engine = None

    def speak(self, text: str) -> None:
        if self._engine:
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception:
                pass
