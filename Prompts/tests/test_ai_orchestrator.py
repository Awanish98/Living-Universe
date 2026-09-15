"""Unit tests for Multi-AI Orchestrator, GroqProvider, and offline NullProvider."""

import time
from living_universe.ai.orchestrator import AIOrchestrator
from living_universe.ai.null_provider import NullProvider
from living_universe.ai.groq_provider import GroqProvider
from living_universe.core.commands import WorldCommand


def test_null_provider_analysis():
    provider = NullProvider()
    assert provider.is_available() is True

    snapshot = {
        "tick": 100,
        "population": 150,
        "species": 3,
        "food_count": 80,
        "avg_energy": 75.0,
    }

    response = provider.analyze(snapshot)
    assert response.success is True
    assert len(response.observation) > 0


def test_groq_provider_availability():
    provider = GroqProvider()
    assert "groq" in provider.name


def test_ai_orchestrator_queue_and_fallback():
    orchestrator = AIOrchestrator(default_provider="null", analysis_interval_seconds=0.1)

    snapshot = {"population": 0, "species": 0, "food_count": 0}
    orchestrator.maybe_request_analysis(snapshot, force=True)

    # Wait briefly for worker thread to process
    time.sleep(0.2)

    commands = orchestrator.collect_pending_commands()
    assert len(commands) > 0
    assert isinstance(commands[0], WorldCommand)

    orchestrator.shutdown()
