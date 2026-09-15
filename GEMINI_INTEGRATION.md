# Gemini Integration Contract

## Principle

Gemini is an optional external reasoning layer. The universe must remain fully functional if Gemini is unavailable.

## Recommended cadence

Do not call Gemini every frame. Start with one analysis request every 30–120 seconds of real time or every configurable number of simulation ticks.

## Input

Send a compact JSON snapshot, not the entire organism list.

## Output

Only accept a Pydantic-validated `WorldCommand`.

Allowed actions:
- SET_FOOD_RATE
- SET_SIMULATION_SPEED
- SPAWN_EVENT
- SPAWN_FOOD
- PAUSE
- RESUME

Do not execute natural-language output as code.

## Future expansion

A second endpoint/provider can provide narrative observations. Keep narration separate from commands so a prose response can never accidentally mutate the world.
