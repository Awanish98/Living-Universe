# Living Universe — End-to-End Development Roadmap

## Phase 0 — Foundation
- Project structure
- Configuration
- logging
- dependency management
- deterministic random seed
- basic application entry point

## Phase 1 — Particle World
- 2D coordinates
- velocity/acceleration
- bounds
- basic forces
- food objects
- renderer

Milestone: moving particles and food are visible.

## Phase 2 — Life
- energy
- metabolism
- food consumption
- health
- aging
- death
- spawning

Milestone: particles have a complete life cycle.

## Phase 3 — DNA & Evolution
- traits
- inheritance
- mutation
- generations
- fitness
- species identity

Milestone: offspring differ from parents and population changes over generations.

## Phase 4 — Behavior
- sensors
- food seeking
- danger avoidance
- exploration
- flocking
- simple decision system

Milestone: organisms make local decisions instead of random movement.

## Phase 5 — Ecosystem
- predators/prey
- resource scarcity
- environmental zones
- hazards
- dynamic events

Milestone: population dynamics emerge.

## Phase 6 — Memory & Communication
- bounded memory
- local signals
- social groups
- cooperation
- competition

Milestone: collective behavior emerges.

## Phase 7 — Learning
- reward system
- lightweight policy learner
- behavior adaptation
- learning statistics

Milestone: behavior can improve from experience without an LLM.

## Phase 8 — Gemini Intelligence Layer
- Gemini adapter
- snapshot summarizer
- JSON command schema
- command validator
- background request queue
- natural-language world commands
- AI observations/narrator
- graceful offline fallback

Milestone: Gemini can observe and influence the universe safely without becoming the per-particle loop.

## Phase 9 — Analytics
- population graph
- species graph
- energy graph
- generation statistics
- lineage
- experiment comparison
- export CSV/JSON

## Phase 10 — Persistence
- save/load
- experiment files
- replay seed
- snapshot checkpoints

## Phase 11 — Polish
- modern UI
- controls
- visual effects
- performance profiling
- accessibility
- documentation

## Phase 12 — Reusable Engine
- stable public API
- examples/
- plugin hooks
- renderer abstraction
- AI provider abstraction

## Phase 13 — Future
- WebGL renderer
- 3D renderer
- distributed simulation
- GPU acceleration
- advanced neural evolution
- civilization layer
- multi-world experiments
- Jarvis integration
