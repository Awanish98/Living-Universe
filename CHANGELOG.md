# Changelog

## Alpha 1.0 — Genesis
- Complete simulation engine pipeline (`UniverseEngine`) with clock, deterministic seeds, and boundary physics.
- Spatial partitioning hash grid (`SpatialGrid`) supporting 1000+ entities with O(1) cell queries.
- Environmental zones (Emerald Oasis, Solar Dunes, Frost Expanse, Acid Mire) and dynamic climate cycle.
- Complete organism lifecycle: basal metabolism, starvation, aging, healing, and carcass meat generation.
- Genetics & Evolution: 12-trait DNA vector, crossover, mutation drift, taxonomic naming, and phylogenetic speciation.
- Behavioral arbitration: hunger, fear evasion, predator hunting, foraging, and flocking cohesion.
- Ecosystem dynamics: herbivore grazing, carnivore bite combat, and dynamic world events (food bloom, meteor strike, drought).
- Social signaling and bounded spatial memory.
- Lifespan reinforcement policy adaptation.
- Multi-provider AI system: background orchestrator with Gemini (google-genai), OpenAI, xAI, Custom/Ollama, and offline NullProvider.
- Audio engine: multi-channel mixer, rate-limiting, and zero-dependency procedural sound synthesizer.
- Sci-Fi visual UI: 2D pan/zoom & organism tracking camera, particle FX, real-time telemetry HUD charts, and entity inspector card.
- Save/load state serialization (`UniverseSerializer` & `SaveManager`).
- Reusable public API and example scripts.
- Comprehensive 22-test automated verification suite.
