# Architecture

```text
living_universe/
├── core/          # pure simulation
├── entities/      # organisms, resources, events
├── systems/       # movement, life, ecology, evolution, social
├── ai/            # optional Gemini integration
├── rendering/     # Pygame/UI; never imported by core
├── analytics/     # metrics and experiment data
├── persistence/   # save/load
└── config/        # validated configuration
```

## Dependency direction

```text
Renderer ───────► Core
UI ─────────────► Core
Analytics ──────► Core
Persistence ────► Core
AI Adapter ─────► Core schemas / snapshots

Core MUST NOT import:
- pygame
- Gemini SDK
- UI code
- network clients
```

## Main data flow

```text
Environment
     ↓
Spatial Index
     ↓
Sensors
     ↓
Decision System
     ↓
Action Resolver
     ↓
Life/Ecology/Evolution
     ↓
Metrics + Snapshot
     ↓
Renderer
     ↘
       AI snapshot → Gemini → validated command → Command Queue
```

## Provider abstraction

Keep AI provider-neutral:

```text
AIProvider
 ├── GeminiProvider
 └── Local/NullProvider
```

This allows future models to be plugged in without rewriting the simulation.

## Performance strategy

Use a uniform spatial grid for local-neighbor queries. Keep expensive analytics on intervals rather than every frame. Run network/LLM work asynchronously and apply results at safe simulation boundaries.
