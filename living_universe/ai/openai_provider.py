"""OpenAI API provider adapter."""

import os
import json
from typing import Dict, Any, Optional
from .base import AIProvider, AIResponse
from .prompts import SYSTEM_ANALYSIS_PROMPT, USER_COMMAND_PROMPT
from ..core.commands import WorldCommand


class OpenAIProvider(AIProvider):
    """Integrates OpenAI GPT models for world analysis and command translation."""

    name: str = "openai"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client = None
        if self.api_key:
            self._init_client()

    def _init_client(self):
        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        except Exception:
            self._client = None

    def is_available(self) -> bool:
        return bool(self.api_key and self._client is not None)

    def analyze(self, snapshot: Dict[str, Any]) -> AIResponse:
        if not self.is_available():
            return AIResponse(provider=self.name, success=False, error="OpenAI API key not configured.")
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
            return AIResponse(provider=self.name, success=False, error="OpenAI API key not configured.")
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

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate speech or dialogue via OpenAI GPT models."""
        if not self.is_available():
            return ""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=250,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return ""

