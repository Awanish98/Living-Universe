"""Multi-provider AI Orchestrator with background worker and automatic fallback."""

import threading
import time
from typing import Dict, Optional, List, Any
from .base import AIProvider, AIResponse
from .null_provider import NullProvider
from .gemini import GeminiProvider
from .openai_provider import OpenAIProvider
from .xai import XAIProvider
from .custom_provider import CustomAIProvider
from .groq_provider import GroqProvider
from .queue import AICommandQueue
from ..core.commands import WorldCommand


class AIOrchestrator:
    """Orchestrates asynchronous AI reasoning, provider routing, cooldowns, and fallbacks."""

    def __init__(
        self,
        default_provider: Optional[str] = None,
        analysis_interval_seconds: float = 30.0,
    ):
        self.analysis_interval_seconds = analysis_interval_seconds
        self.last_analysis_time = 0.0
        self.is_busy = False
        self.latest_observation: str = "AI Observer online (Idle)."
        self.provider_health: Dict[str, bool] = {}

        # Queue
        self.queue = AICommandQueue()

        # Provider Registry
        self.providers: Dict[str, AIProvider] = {
            "null": NullProvider(),
            "gemini": GeminiProvider(),
            "openai": OpenAIProvider(),
            "xai": XAIProvider(),
            "custom": CustomAIProvider(),
            "groq": GroqProvider(),
        }

        # Select provider
        if default_provider is None:
            # Auto-detect first available provider with credentials
            chosen = "null"
            for candidate in ("groq", "gemini", "openai", "xai", "custom"):
                if self.providers[candidate].is_available():
                    chosen = candidate
                    break
            self.active_provider_name = chosen
        else:
            self.active_provider_name = default_provider if default_provider in self.providers else "null"

        self.fallback_provider = self.providers["null"]

        # Background Worker Thread
        self._running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()

    def set_provider(self, name: str) -> bool:
        """Switch active AI provider."""
        if name in self.providers:
            self.active_provider_name = name
            return True
        return False

    def get_active_provider(self) -> AIProvider:
        return self.providers.get(self.active_provider_name, self.fallback_provider)

    def is_active_provider_available(self) -> bool:
        provider = self.get_active_provider()
        return provider.is_available()

    def maybe_request_analysis(self, snapshot_dict: Dict[str, Any], force: bool = False) -> bool:
        """Submit an ecosystem analysis request if interval has elapsed and worker is idle."""
        now = time.time()
        if (force or (now - self.last_analysis_time >= self.analysis_interval_seconds)) and not self.is_busy:
            self.is_busy = True
            self.last_analysis_time = now
            self.queue.submit_request("analyze", {"snapshot": snapshot_dict})
            return True
        return False

    def submit_user_command(self, user_prompt: str, snapshot_dict: Dict[str, Any]) -> None:
        """Submit a natural language user command for interpretation."""
        self.queue.submit_request("command", {"prompt": user_prompt, "snapshot": snapshot_dict})

    def collect_pending_commands(self) -> List[WorldCommand]:
        """Fetch all completed AI commands and update latest observation."""
        responses = self.queue.drain_responses()
        commands = []
        for resp in responses:
            if resp.observation:
                self.latest_observation = f"[{resp.provider.upper()}]: {resp.observation}"
            if resp.command and resp.command.actions:
                commands.append(resp.command)
        return commands

    def _worker_loop(self) -> None:
        """Background thread executing API requests asynchronously."""
        while self._running:
            req = self.queue.get_pending_request(timeout=0.1)
            if not req:
                time.sleep(0.05)
                continue

            req_type, payload = req
            provider = self.get_active_provider()

            # Execute with active provider, fallback to NullProvider on failure
            response: AIResponse
            try:
                if req_type == "analyze":
                    snapshot = payload.get("snapshot", {})
                    if provider.is_available():
                        response = provider.analyze(snapshot)
                        if not response.success:
                            # Fallback
                            response = self.fallback_provider.analyze(snapshot)
                    else:
                        response = self.fallback_provider.analyze(snapshot)

                elif req_type == "command":
                    prompt = payload.get("prompt", "")
                    snapshot = payload.get("snapshot", {})
                    if provider.is_available():
                        response = provider.command(prompt, snapshot)
                        if not response.success:
                            response = self.fallback_provider.command(prompt, snapshot)
                    else:
                        response = self.fallback_provider.command(prompt, snapshot)
                else:
                    response = AIResponse(provider="unknown", success=False, error="Unknown request type")

            except Exception as exc:
                response = AIResponse(provider=self.active_provider_name, success=False, error=str(exc))

            self.queue.post_response(response)
            self.is_busy = False

    def shutdown(self) -> None:
        self._running = False
