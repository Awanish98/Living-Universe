# PROJECT MEMORY — LIVING UNIVERSE

## Identity
Project name: Living Universe
Type: reusable artificial-life / living-particle engine
Primary goal: create a digital universe where autonomous organisms can live, interact, reproduce, mutate, learn, and evolve.

## Product vision
This is more than a particle wallpaper. The target is a small artificial-life ecosystem with:
- world/environment
- living organisms
- DNA and traits
- energy/resources
- life/death
- reproduction and mutation
- species/evolution
- behavior and sensors
- memory
- communication
- predator/prey ecology
- optional learning
- analytics
- save/load
- visual UI
- modular audio
- optional Gemini high-level intelligence

## Core engineering rule
The simulation engine must remain independent of the renderer, audio system, and Gemini/network code.

## AI role
Gemini is a high-level optional observer/controller. It must never be called per particle or per frame. It receives compact world snapshots and may return validated structured commands only.

## Audio role
Audio is event-driven and modular. It includes ambient sound, optional music, SFX for meaningful events, volume controls, mute, caching, rate limiting, and graceful headless/no-audio behavior.

## Laptop target
Initial version should run on an 8 GB RAM i5-class laptop without requiring a local LLM or dedicated high-end GPU. Optimize population, spatial lookup, rendering and analytics.

## Reuse target
The engine should be importable by future projects such as games, visualizers, Jarvis UI modules, educational simulations and other experiments.

## Source of truth
Current implementation state: `TASK_STATE.json`
Detailed requirements: `AI_BUILD_INSTRUCTIONS.md`
Sequencing: `ROADMAP.md`
Architecture: `ARCHITECTURE.md`
Audio requirements: `SOUND_AUDIO_SYSTEM.md`
Final checks: `IMPLEMENTATION_CHECKLIST.md`
