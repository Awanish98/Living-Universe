# Sound & Audio System

The Living Universe must include a modular audio layer that can later be reused by Jarvis and other projects.

## Goals

Sound should communicate the state of the universe without overwhelming the CPU.

### Audio layers

1. Ambient layer
   - Low-volume evolving background atmosphere.
   - Optional procedural or bundled loop.
   - Changes subtly with world state.

2. SFX layer
   - Particle movement cues only for important/selected events, not every particle.
   - Food consumed
   - Birth/reproduction
   - Death
   - Predator attack
   - Communication signal
   - New species/evolution milestone
   - World events

3. Music layer
   - Optional background music.
   - Separate volume control.
   - Pause/resume with simulation.

4. Voice/narration layer
   - Optional future TTS integration.
   - Gemini-generated narration must never be treated as executable commands.
   - Keep TTS provider abstract.

## Performance rules

- Never create a sound object every frame.
- Cache loaded sounds.
- Use an event queue.
- Rate-limit repeated sounds.
- Use spatial/importance culling where useful.
- Audio must be optional and independently disableable.
- Headless simulation must work without an audio device.

## API

Create an audio abstraction similar to:

```python
audio = AudioEngine(config)
audio.play("birth")
audio.play("death", volume=0.4)
audio.set_master_volume(0.8)
audio.set_sfx_volume(0.7)
audio.set_music_volume(0.3)
audio.mute(True)
audio.update(world_snapshot)
audio.shutdown()
```

The core simulation must emit typed events rather than directly importing the audio library.

## Suggested event types

```text
PARTICLE_BORN
PARTICLE_DIED
FOOD_CONSUMED
PREDATOR_ATTACK
SOCIAL_SIGNAL
SPECIES_EMERGED
EVOLUTION_MILESTONE
WORLD_EVENT_STARTED
WORLD_EVENT_ENDED
AI_OBSERVATION
```

## Procedural audio fallback

Because the project should remain lightweight, implement a generated/procedural fallback where practical. Do not require a large sound-asset download just to run the simulation.

## Asset structure

Use:

```text
assets/
  audio/
    music/
    ambient/
    sfx/
    voice/
```

Keep audio filenames configurable. If an asset is missing, the AudioEngine should fail gracefully and continue the simulation.

## UI controls

Add:
- Master volume
- Music volume
- SFX volume
- Ambient volume
- Mute
- Audio enable/disable

Display a small audio status indicator in the HUD.

## Future reuse

The audio package should not depend on the universe. It should be possible to reuse it as:

```python
from living_universe.audio import AudioEngine
```

in a future game, Jarvis UI, visualizer, or other project.
