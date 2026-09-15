from living_universe.config import UniverseConfig
from living_universe.core.engine import UniverseEngine

def test_seed_is_reproducible():
    a = UniverseEngine(UniverseConfig(seed=123))
    b = UniverseEngine(UniverseConfig(seed=123))
    for _ in range(10):
        a.step()
        b.step()
    assert a.snapshot() == b.snapshot()
