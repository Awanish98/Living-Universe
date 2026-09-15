"""xAI (Grok) provider adapter."""

import os
import json
from typing import Dict, Any, Optional
from .base import AIProvider, AIResponse
from .prompts import SYSTEM_ANALYSIS_PROMPT, USER_COMMAND_PROMPT
from ..core.commands import WorldCommand


class XAIProvider(AIProvider):
    """Integrates xAI models using the OpenAI-compatible REST interface."""

    name: str = "xai"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        self.model = model or os.getenv("XAI_MODEL", "grok-beta")
        self._client = None
        if self.api_key:
            self._init_client()

    def _init_client(self):
        try:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.x.ai/v1",
            )
        except Exception:
            self._client = None

    def is_available(self) -> bool:
        return bool(self.api_key and self._client is not None)

    def analyze(self, snapshot: Dict[str, Any]) -> AIResponse:
        if not self.is_available():
            return AIResponse(provider=self.name, success=False, error="xAI API key not configured.")
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
            return AIResponse(provider=self.name, success=False, error="xAI API key not configured.")
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
