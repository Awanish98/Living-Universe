"""Custom / Local OpenAI-compatible provider adapter (e.g. Ollama, LM Studio, vLLM)."""

import os
import json
from typing import Dict, Any, Optional
from .base import AIProvider, AIResponse
from .prompts import SYSTEM_ANALYSIS_PROMPT, USER_COMMAND_PROMPT
from ..core.commands import WorldCommand


class CustomAIProvider(AIProvider):
    """Integrates custom local/remote OpenAI-compatible endpoints."""

    name: str = "custom"

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.base_url = base_url or os.getenv("CUSTOM_AI_BASE_URL", "http://localhost:11434/v1")
        self.api_key = api_key or os.getenv("CUSTOM_AI_API_KEY", "ollama")
        self.model = model or os.getenv("CUSTOM_AI_MODEL", "llama3")
        self._client = None
        self._init_client()

    def _init_client(self):
        try:
            from openai import OpenAI
            self._client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
            )
        except Exception:
            self._client = None

    def is_available(self) -> bool:
        return self._client is not None

    def analyze(self, snapshot: Dict[str, Any]) -> AIResponse:
        if not self.is_available():
            return AIResponse(provider=self.name, success=False, error="Custom AI client unavailable.")
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_ANALYSIS_PROMPT},
                    {"role": "user", "content": f"Snapshot:\n{json.dumps(snapshot)}"}
                ],
                response_format={"type": "json_object"}
            )
            return self._parse_json(response.choices[0].message.content)
        except Exception as exc:
            return AIResponse(provider=self.name, success=False, error=str(exc))

    def command(self, user_prompt: str, snapshot: Dict[str, Any]) -> AIResponse:
        if not self.is_available():
            return AIResponse(provider=self.name, success=False, error="Custom AI client unavailable.")
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": USER_COMMAND_PROMPT},
                    {"role": "user", "content": f"User: {user_prompt}\nSnapshot: {json.dumps(snapshot)}"}
                ],
                response_format={"type": "json_object"}
            )
            return self._parse_json(response.choices[0].message.content)
        except Exception as exc:
            return AIResponse(provider=self.name, success=False, error=str(exc))

    def _parse_json(self, text: str) -> AIResponse:
        try:
            data = json.loads(text.strip())
            obs = data.get("observation", "")
            cmd_data = data.get("command")
            cmd = WorldCommand.model_validate(cmd_data) if cmd_data else None
            return AIResponse(provider=self.name, success=True, observation=obs, command=cmd, raw_response=text)
        except Exception as exc:
            return AIResponse(provider=self.name, success=False, error=str(exc), raw_response=text)
