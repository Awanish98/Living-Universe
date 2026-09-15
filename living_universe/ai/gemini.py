"""Google Gemini AI integration using the official google-genai SDK."""

import os
import json
from typing import Dict, Any, Optional
from .base import AIProvider, AIResponse
from .prompts import SYSTEM_ANALYSIS_PROMPT, USER_COMMAND_PROMPT
from ..core.commands import WorldCommand


class GeminiProvider(AIProvider):
    """Integrates Google Gemini models for high-level ecological analysis and narration."""

    name: str = "gemini"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self._client = None
        if self.api_key:
            self._init_client()

    def _init_client(self):
        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        except Exception as exc:
            self._client = None

    def is_available(self) -> bool:
        return bool(self.api_key and self._client is not None)

    def analyze(self, snapshot: Dict[str, Any]) -> AIResponse:
        if not self.is_available():
            return AIResponse(
                provider=self.name,
                success=False,
                error="Gemini API key not configured or client unavailable.",
            )

        try:
            from google.genai import types
            prompt = f"Current Universe Snapshot:\n{json.dumps(snapshot, indent=2)}"
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_ANALYSIS_PROMPT,
                    response_mime_type="application/json",
                ),
            )
            return self._parse_json_response(response.text)
        except Exception as exc:
            return AIResponse(
                provider=self.name,
                success=False,
                error=f"Gemini API call failed: {str(exc)}",
            )

    def command(self, user_prompt: str, snapshot: Dict[str, Any]) -> AIResponse:
        if not self.is_available():
            return AIResponse(
                provider=self.name,
                success=False,
                error="Gemini API key not configured.",
            )

        try:
            from google.genai import types
            content = f"User Request: {user_prompt}\n\nWorld State Context:\n{json.dumps(snapshot, indent=2)}"
            response = self._client.models.generate_content(
                model=self.model,
                contents=content,
                config=types.GenerateContentConfig(
                    system_instruction=USER_COMMAND_PROMPT,
                    response_mime_type="application/json",
                ),
            )
            return self._parse_json_response(response.text)
        except Exception as exc:
            return AIResponse(
                provider=self.name,
                success=False,
                error=f"Gemini command translation failed: {str(exc)}",
            )

    def _parse_json_response(self, text: str) -> AIResponse:
        try:
            data = json.loads(text.strip())
            obs = data.get("observation", "")
            cmd_data = data.get("command")
            cmd = None
            if cmd_data:
                cmd = WorldCommand.model_validate(cmd_data)
            return AIResponse(
                provider=self.name,
                success=True,
                observation=obs,
                command=cmd,
                raw_response=text,
            )
        except Exception as exc:
            return AIResponse(
                provider=self.name,
                success=False,
                error=f"JSON validation failed: {str(exc)}",
                raw_response=text,
            )

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate open-ended natural speech or philosophical dialogue from Gemini."""
        if not self.is_available():
            return ""
        try:
            from google.genai import types
            cfg = types.GenerateContentConfig(system_instruction=system_prompt) if system_prompt else None
            resp = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=cfg,
            )
            return resp.text.strip() if resp and resp.text else ""
        except Exception as exc:
            return ""

