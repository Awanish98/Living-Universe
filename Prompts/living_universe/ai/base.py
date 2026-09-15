"""Abstract base interface and structured response contracts for AI providers."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from ..core.commands import WorldCommand


class AIResponse(BaseModel):
    """Structured response returned by any AI provider."""
    provider: str
    success: bool = True
    observation: str = ""
    command: Optional[WorldCommand] = None
    raw_response: Optional[str] = None
    error: Optional[str] = None


class AIProvider(ABC):
    """Abstract interface for high-level universe intelligence providers."""

    name: str = "base"

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and available."""
        pass

    @abstractmethod
    def analyze(self, snapshot: Dict[str, Any]) -> AIResponse:
        """Analyze a world snapshot and generate observations and/or validated commands."""
        pass

    @abstractmethod
    def command(self, user_prompt: str, snapshot: Dict[str, Any]) -> AIResponse:
        """Process a natural language user command into a validated WorldCommand."""
        pass
