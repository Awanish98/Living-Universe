# Living Universe — AI Build Package

A reusable Artificial-Life / Living-Particle engine designed to run on a laptop first, while remaining extensible for future Jarvis projects.

## Goal

Build a digital universe containing autonomous particles/organisms with:

- Physics and movement
- Energy, food, health, aging and death
- DNA, traits and mutation
- Reproduction and natural selection
- Predator/prey relationships
- Sensors, goals and decisions
- Memory and communication
- Optional learning/neural behavior
- Dynamic environments and world events
- Species tracking and evolution statistics
- Gemini API as a high-level optional intelligence/controller layer
- Reusable Python package/API so the engine can be embedded in future projects
- A polished 2D desktop visualization first; 3D can be a later renderer
- A modular audio layer with ambient sound, music, event SFX and optional future TTS

## Laptop-first constraint

Target the initial build for a modest laptop: 8 GB RAM, i5-class CPU and entry-level NVIDIA GPU. Do not require a local LLM or GPU for the core simulation. Gemini is an optional cloud API integration.

## Non-goals for v1

Do not make an API request for every particle or every frame. The simulation must work fully offline without Gemini. Gemini should receive summarized world state and return validated high-level actions/rules/events.

## Recommended stack

- Python 3.11+
- NumPy
- Pygame for the first renderer
- Pydantic for schemas/validation
- Optional Numba for CPU optimization
- Optional NetworkX for analysis
- Google Gemini API SDK only in the optional AI layer
- pytest for tests
- JSON/SQLite for lightweight persistence
- Pygame mixer / modular audio abstraction for ambient, music and event-driven SFX

## Start

1. Create a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Run `python -m living_universe`.
4. The first screen should show a functioning world with particles, food, energy, reproduction and death.
5. Add features in the roadmap order rather than attempting all advanced systems at once.

## Design principle

Separate the simulation engine from the renderer and AI integration. A particle must never depend directly on Pygame or Gemini. This makes the engine reusable in games, websites, Jarvis UI, data visualization and other future projects.

## Multi-AI and versioning

The AI layer is provider-neutral and designed for Gemini, xAI, OpenAI, OpenAI-compatible/custom providers, and offline mode. Development is owner-controlled through Alpha/Beta/Gamma stages; see `VERSIONING.md`.
