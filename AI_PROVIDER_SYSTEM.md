# Multi-AI Provider System

Living Universe must use a provider-agnostic AI architecture.

## Goal

The project must be able to connect to multiple AI providers without changing the core simulation.

Initial provider adapters should be designed for:
- Google Gemini
- xAI
- OpenAI-compatible APIs
- A generic OpenAI-compatible/custom endpoint
- Null/offline provider

Do not hardcode the project around one vendor.

## Architecture

```text
                    AIProvider
                       │
       ┌───────────────┼────────────────┐
       ↓               ↓                ↓
   GeminiProvider   XAIProvider   OpenAIProvider
       │               │                │
       └───────────────┼────────────────┘
                       ↓
                AI Orchestrator
                       ↓
                Command Validator
                       ↓
                 Universe Engine
```

## Provider contract

Every provider should implement the same conceptual interface:

```python
class AIProvider:
    name: str
    async def analyze(snapshot: dict) -> AIResponse:
        ...
```

The provider returns structured data, never executable code.

## Configuration

Use environment variables or a local `.env` file. Never commit API keys.

Example variables:

```text
GEMINI_API_KEY=
GEMINI_MODEL=

XAI_API_KEY=
XAI_MODEL=

OPENAI_API_KEY=
OPENAI_MODEL=

CUSTOM_AI_BASE_URL=
CUSTOM_AI_API_KEY=
CUSTOM_AI_MODEL=
```

The exact current SDK/API syntax must be checked against each provider's official documentation when implementing the adapters. Do not invent endpoint URLs or SDK methods.

## Routing

Implement an `AIOrchestrator` with:
- selected provider
- fallback provider
- request cooldown
- timeout
- retry/backoff
- request queue
- response validation
- provider health status
- token/output limits
- logging

Example:

```python
orchestrator.set_provider("gemini")
orchestrator.set_provider("xai")
orchestrator.set_provider("openai")
```

A future provider should require adding one adapter and registering it, not rewriting the universe.

## Roles

AI providers may be used for:
- world analysis
- evolution analysis
- natural-language commands
- event suggestions
- experiment design
- narration
- high-level strategy

Do NOT send every particle to an AI model. Aggregate state into snapshots.

## Safety

- Validate every model response with Pydantic.
- Allow only a predefined set of world actions.
- Never execute model-generated code.
- Never treat prose as a command.
- Never expose API keys in logs/UI.
- Network failures must not stop the simulation.
