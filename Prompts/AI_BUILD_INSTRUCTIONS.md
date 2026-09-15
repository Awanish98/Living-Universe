# MASTER BUILD INSTRUCTION FOR THE CODING AI

You are the lead engineer responsible for turning this repository into a finished, runnable project called **Living Universe**.

## Mission

Build a polished artificial-life simulation in which digital organisms ("living particles") exist in a 2D world, survive, consume resources, reproduce, mutate, learn simple behaviors, communicate, form groups, compete, and evolve over generations.

The finished application must feel like a small living digital universe, not merely a particle wallpaper.

## Hard requirements

1. The simulation must run locally on a normal laptop.
2. The core simulation must work with Gemini completely disabled.
3. Gemini must be an optional high-level intelligence layer.
4. Never call Gemini once per particle or once per render frame.
5. Keep rendering, simulation, storage, and AI integration in separate modules.
6. Use deterministic seeds for reproducible experiments.
7. Avoid blocking the simulation loop with network calls.
8. Gemini output must be validated against a strict schema before changing the world.
9. Provide graceful behavior when no API key, network, or API quota is available.
10. Add tests for core simulation rules.
11. Add a configuration file/environment variables instead of hardcoding secrets.
12. Provide clear logging and an error-safe shutdown.
13. Keep CPU/RAM usage reasonable and expose a particle-count setting.
14. Make the package importable by future projects.

## Version-controlled development

Use `VERSIONING.md` as the authoritative release-stage protocol.

Start at `Alpha 1.0`. Work through Alpha versions such as 1.1, 1.2, etc.

The owner explicitly controls stage promotion. NEVER move Alpha to Beta or Beta to Gamma automatically. When the owner says to move to the next stage, create that stage's `.0` version and update `VERSION_STATE.json`, `CHANGELOG.md`, and `TASK_STATE.json`.

At every version boundary, run tests and document changes.

## Core organism model

Each organism should have at least:

- unique id
- species id
- position and velocity
- age
- health
- energy
- reproduction cooldown
- generation
- DNA/traits
- sensors
- short-term memory
- social/communication state
- alive/dead state

Suggested traits:

- speed
- vision_range
- metabolism
- size
- fertility
- aggression
- curiosity
- sociability
- fear
- efficiency

Traits should be inherited with mutation. Use configurable mutation rate and mutation magnitude.

## Simulation lifecycle

Each tick:

1. Update environment.
2. Update spatial index/neighbor lookup.
3. Sense nearby objects.
4. Decide actions.
5. Resolve movement and collisions.
6. Consume resources.
7. Resolve predator/prey interactions.
8. Apply metabolism and environmental effects.
9. Reproduce eligible organisms.
10. Remove dead organisms.
11. Spawn resources/events.
12. Record metrics.
13. Render if the renderer is enabled.

Use a clear separation between sensing, decision, action and world-state mutation.

## Emergent behavior

Do not script every individual movement. Give organisms local rules and allow group behavior to emerge.

Examples:
- food seeking
- predator avoidance
- flocking/alignment/cohesion/separation
- following social signals
- exploration
- territory preference
- cooperation around food
- competition

## Evolution

Implement generation tracking and species statistics.

A child should inherit parent traits with mutation. Provide:
- mutation rate
- mutation strength
- fitness metrics
- species diversity
- population history
- lineage/ancestor id

Do not claim real biological evolution. This is an artificial simulation.

## Learning

Implement a lightweight optional learner first. It may be a score-based reinforcement mechanism or tiny neural policy. It must not require an LLM.

The organism can learn action preferences from rewards such as:
- finding food
- escaping danger
- surviving longer
- successful reproduction

## Memory

Implement bounded memory, not unlimited history. Example memories:
- recent food locations
- recent danger locations
- successful action
- social signal

Memory should be cheap and configurable.

## Communication

Implement local signals with limited range and cost. Example signal types:
- FOOD
- DANGER
- FOLLOW
- HELP
- TERRITORY

Communication should have energy cost and cooldown.

## Environment

Include:
- world bounds
- food/resources
- obstacles
- temperature or environmental pressure
- optional water/resource zones
- day/night visual state
- configurable hazards

Add world events such as:
- food bloom
- drought
- cold wave
- heat wave
- toxic zone
- meteor-like visual event

Events must be represented as structured data and applied by the simulation engine.

## Gemini integration

Create an adapter under `living_universe/ai/`.

Gemini is NOT the physics engine and NOT the per-particle brain.

Use Gemini for:
- world analysis
- species/evolution summaries
- natural-language commands
- high-level world events
- experiment suggestions
- narrative observations

Send compact structured snapshots, for example:

{
  "tick": 12000,
  "population": 840,
  "species": 6,
  "average_energy": 67.4,
  "births": 42,
  "deaths": 31,
  "dominant_traits": {...},
  "events": [...]
}

Ask Gemini to return only validated JSON according to a Pydantic schema.

Potential command schema:
{
  "type": "WORLD_COMMAND",
  "actions": [
    {"action": "SET_FOOD_RATE", "value": 0.8},
    {"action": "SPAWN_EVENT", "event": "HEAT_WAVE", "duration": 500}
  ],
  "reason": "..."
}

Never execute arbitrary code returned by Gemini.

Use:
- cooldowns
- request queue
- background worker/thread or async task
- snapshot intervals
- token/output limits
- retries with exponential backoff
- timeout
- local fallback

## UI requirements

Create a polished dark sci-fi interface around the simulation.

Main area:
- living world viewport
- smooth particles
- species represented visually
- subtle trails/glow where affordable

HUD:
- population
- species count
- generation
- births/deaths
- average energy
- simulation speed
- Gemini status
- current event

Side panel:
- start/pause
- speed
- particle count
- spawn food
- reset
- random seed
- toggle trails
- toggle labels
- toggle AI layer

Analytics:
- population history
- species population
- average energy
- births/deaths
- diversity

Do not sacrifice simulation performance for decorative effects.

## Multi-provider AI architecture

Implement a provider-agnostic AI layer. Support adapters for Gemini, xAI, OpenAI, an OpenAI-compatible/custom endpoint, and a null/offline provider.

Use a common `AIProvider` interface and an `AIOrchestrator`. The user must be able to select the provider from configuration/UI without changing core simulation code.

Use official provider SDK/documentation for current API syntax when implementing each adapter. Never invent endpoints or SDK methods. API keys must come from environment variables and must never be committed.

All model responses must be validated against the existing Pydantic command schema. Never execute model-generated code.

## Sound and audio

Implement a modular `audio/` subsystem.

Requirements:
- ambient soundscape
- optional music
- event-driven SFX
- birth/death/food/predator/evolution/world-event cues
- master/music/SFX/ambient volume controls
- mute toggle
- cached sound assets
- event queue and rate limiting
- graceful no-audio/headless fallback
- optional future TTS provider abstraction

The core simulation must emit typed events and must not import Pygame audio directly. Audio must never run one sound event per particle per frame.

## Reusable API

Expose a clean interface similar to:

engine = UniverseEngine(config)
engine.reset(seed=42)
engine.step()
snapshot = engine.snapshot()
engine.apply_command(command)

A future project should be able to import the engine without importing Pygame.

## Persistence

Implement save/load:
- simulation configuration
- seed
- world state
- organisms
- resources
- statistics

Prefer a versioned JSON format for simple worlds and SQLite for long-running metrics if needed.

## Testing

Write tests for:
- movement
- energy consumption
- food consumption
- death
- reproduction
- inheritance
- mutation
- collision/bounds
- predator/prey
- communication range
- command validation
- save/load
- deterministic seed behavior
- Gemini-disabled fallback

## Performance

Start with 500–2,000 organisms and make the architecture capable of scaling further.

Use spatial partitioning/grid neighbor lookup rather than O(N²) all-pairs checks when population grows.

Avoid Python object churn inside the hottest update loop where practical.

## Development order

Follow the phases in `ROADMAP.md`.

Do not implement a complex neural network, 3D renderer, or massive population before the base simulation is stable.

## Definition of done

The project is done only when:

- `python -m living_universe` launches the simulation.
- It works without an API key.
- Organisms visibly live, eat, reproduce, mutate and die.
- Multiple species can emerge.
- The simulation can be paused/reset and seeded.
- Metrics are visible.
- Save/load works.
- Tests pass.
- Gemini can optionally analyze a snapshot and return a validated command.
- Documentation explains setup and extension.
- The engine can be imported independently of the renderer.
