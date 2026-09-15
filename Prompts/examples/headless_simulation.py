"""Headless simulation benchmark and telemetry exporter."""

import time
import os
import sys

# Ensure module path is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from living_universe import UniverseEngine, UniverseConfig
from living_universe.analytics.export import TelemetryExporter


def main():
    print("=" * 60)
    print("  LIVING UNIVERSE — HEADLESS SIMULATION BENCHMARK")
    print("=" * 60)

    config = UniverseConfig(
        initial_organisms=300,
        initial_resources=400,
        food_spawn_rate=0.4,
        seed=1337,
    )
    engine = UniverseEngine(config)

    ticks_to_simulate = 2000
    print(f"Starting simulation for {ticks_to_simulate} ticks...")
    start_time = time.time()

    telemetry_log = []

    for i in range(1, ticks_to_simulate + 1):
        engine.step()

        if i % 200 == 0:
            snap = engine.snapshot()
            print(
                f"Tick {snap.tick:04d} | Pop: {snap.population:03d} | "
                f"Species: {snap.species_count:02d} | Food: {snap.food_count:03d} | "
                f"Avg Energy: {snap.average_energy:4.1f} | "
                f"Herb/Carn: {snap.herbivore_count}/{snap.carnivore_count}"
            )
            telemetry_log.append({
                "tick": snap.tick,
                "population": snap.population,
                "species_count": snap.species_count,
                "food_count": snap.food_count,
                "average_energy": snap.average_energy,
                "average_health": snap.average_health,
                "herbivores": snap.herbivore_count,
                "carnivores": snap.carnivore_count,
                "births": snap.births,
                "deaths": snap.deaths,
            })

    elapsed = time.time() - start_time
    ticks_per_sec = ticks_to_simulate / max(0.001, elapsed)

    print("-" * 60)
    print(f"Completed {ticks_to_simulate} ticks in {elapsed:.2f} seconds ({ticks_per_sec:.0f} ticks/sec)")

    # Export metrics
    os.makedirs("experiments", exist_ok=True)
    TelemetryExporter.export_csv("experiments/headless_run.csv", telemetry_log)
    TelemetryExporter.export_json("experiments/final_snapshot.json", engine.snapshot().to_dict())
    print("Exported telemetry to experiments/headless_run.csv and final_snapshot.json")


if __name__ == "__main__":
    main()
