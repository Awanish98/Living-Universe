# Target Project Structure

living-universe/
├── README.md
├── AGENT_RULES.md
├── PROJECT_MEMORY.md
├── TASK_STATE.json
├── SESSION_RECOVERY.md
├── AI_BUILD_INSTRUCTIONS.md
├── ROADMAP.md
├── ARCHITECTURE.md
├── PROJECT_STRUCTURE.md
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── pyproject.toml
├── run.py
├── living_universe/
│   ├── __init__.py
│   ├── __main__.py
│   ├── app.py
│   ├── config.py
│   ├── core/
│   │   ├── engine.py
│   │   ├── world.py
│   │   ├── clock.py
│   │   ├── commands.py
│   │   ├── snapshot.py
│   │   └── random_state.py
│   ├── entities/
│   │   ├── organism.py
│   │   ├── dna.py
│   │   ├── species.py
│   │   ├── resource.py
│   │   ├── event.py
│   │   └── memory.py
│   ├── systems/
│   │   ├── movement.py
│   │   ├── sensors.py
│   │   ├── behavior.py
│   │   ├── life.py
│   │   ├── ecology.py
│   │   ├── evolution.py
│   │   ├── communication.py
│   │   ├── learning.py
│   │   └── spatial_grid.py
│   ├── ai/
│   │   ├── base.py
│   │   ├── orchestrator.py
│   │   ├── gemini.py
│   │   ├── xai.py
│   │   ├── openai_provider.py
│   │   ├── custom_provider.py
│   │   ├── null_provider.py
│   │   ├── prompts.py
│   │   └── queue.py
│   ├── analytics/
│   │   ├── metrics.py
│   │   ├── history.py
│   │   └── export.py
│   ├── persistence/
│   │   ├── serializer.py
│   │   └── save_manager.py
│   └── rendering/
│       ├── pygame_renderer.py
│       ├── camera.py
│       ├── particles.py
│       ├── hud.py
│       └── charts.py
├── tests/
│   ├── test_engine.py
│   ├── test_life.py
│   ├── test_evolution.py
│   ├── test_commands.py
│   ├── test_persistence.py
│   └── test_determinism.py
├── examples/
│   ├── headless_simulation.py
│   └── custom_world.py
├── assets/
│   └── README.md
├── saves/
├── experiments/
└── logs/
