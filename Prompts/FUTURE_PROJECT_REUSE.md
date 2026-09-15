# Reuse in Future Projects

The long-term goal is to make the simulation engine a reusable package.

Example:

```python
from living_universe.core.engine import UniverseEngine
from living_universe.config import UniverseConfig

engine = UniverseEngine(UniverseConfig())
engine.reset(seed=99)

for _ in range(1000):
    engine.step()

print(engine.snapshot())
```

Future adapters can render the same engine in:
- Jarvis UI backgrounds
- games/NPC ecosystems
- music visualizers
- data visualizations
- educational simulations
- web applications
- experimental artificial-life worlds

Keep the engine's public API stable and keep renderer-specific code out of `core/`.
