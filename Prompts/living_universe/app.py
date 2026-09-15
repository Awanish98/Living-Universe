"""Interactive application runner uniting simulation, rendering, audio, and AI layers."""

import sys
import math
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def run():
    """Main application loop."""
    try:
        import pygame
    except ImportError as exc:
        raise SystemExit("Install dependencies with: pip install -r requirements.txt") from exc

    from .config import UniverseConfig
    from .core.engine import UniverseEngine
    from .rendering.pygame_renderer import PygameRenderer
    from .audio.engine import AudioEngine
    from .ai.orchestrator import AIOrchestrator

    pygame.init()
    config = UniverseConfig()
    engine = UniverseEngine(config)
    renderer = PygameRenderer(config.width, config.height)
    audio = AudioEngine(config)
    ai = AIOrchestrator(
        default_provider=config.ai_provider if config.ai_enabled else "null",
        analysis_interval_seconds=config.ai_interval_seconds,
    )

    screen = pygame.display.set_mode((config.width, config.height), pygame.RESIZABLE)
    pygame.display.set_caption("Living Universe — Artificial Life Simulation")
    clock = pygame.time.Clock()

    running = True
    is_dragging = False
    last_mouse_pos = (0, 0)
    current_fps = float(config.target_fps)

    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                renderer.width = event.w
                renderer.height = event.h
                renderer.camera.screen_width = event.w
                renderer.camera.screen_height = event.h
                renderer.hud.screen_width = event.w
                renderer.hud.screen_height = event.h
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click: select organism or drag
                    is_dragging = True
                    last_mouse_pos = event.pos
                    # Check for organism selection
                    wx, wy = renderer.camera.screen_to_world(event.pos[0], event.pos[1])
                    selected = None
                    min_d = float("inf")
                    for org in engine.organisms:
                        if org.alive:
                            dist = math.hypot(org.x - wx, org.y - wy)
                            if dist < max(12.0, org.radius * 2.0) and dist < min_d:
                                min_d = dist
                                selected = org
                    renderer.hud.selected_organism = selected

                elif event.button == 3:  # Right click: follow camera
                    wx, wy = renderer.camera.screen_to_world(event.pos[0], event.pos[1])
                    for org in engine.organisms:
                        if org.alive and math.hypot(org.x - wx, org.y - wy) < max(15.0, org.radius * 2.5):
                            renderer.camera.follow(org)
                            renderer.hud.selected_organism = org
                            break

                elif event.button == 4:  # Scroll Up: Zoom in
                    renderer.camera.zoom_at(1.15, event.pos[0], event.pos[1])
                elif event.button == 5:  # Scroll Down: Zoom out
                    renderer.camera.zoom_at(1.0 / 1.15, event.pos[0], event.pos[1])

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if is_dragging:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    renderer.camera.pan(dx, dy)
                    last_mouse_pos = event.pos

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    engine.clock.toggle_pause()
                elif event.key == pygame.K_1:
                    engine.clock.set_speed(1.0)
                elif event.key == pygame.K_2:
                    engine.clock.set_speed(2.0)
                elif event.key == pygame.K_3:
                    engine.clock.set_speed(3.0)
                elif event.key == pygame.K_4:
                    engine.clock.set_speed(5.0)
                elif event.key == pygame.K_5:
                    engine.clock.set_speed(10.0)
                elif event.key == pygame.K_f:
                    # Spawn food at mouse
                    mx, my = pygame.mouse.get_pos()
                    wx, wy = renderer.camera.screen_to_world(mx, my)
                    engine.spawn_food(count=30, x=wx, y=wy)
                    renderer.particles.spawn_eat_spark(wx, wy, count=10)
                elif event.key == pygame.K_o:
                    # Spawn organisms at mouse
                    mx, my = pygame.mouse.get_pos()
                    wx, wy = renderer.camera.screen_to_world(mx, my)
                    engine.spawn_organisms(count=15, x=wx, y=wy)
                    renderer.particles.spawn_birth_burst(wx, wy, (0, 240, 255), count=15)
                elif event.key == pygame.K_e:
                    # Trigger random event
                    engine.spawn_event(engine.random_state.choice(["FOOD_BLOOM", "DROUGHT", "HEAT_WAVE", "COLD_SNAP", "METEOR_IMPACT"]))
                elif event.key == pygame.K_s:
                    engine.save("autosave_slot")
                    ai.latest_observation = "Game state saved to autosave_slot.json"
                elif event.key == pygame.K_l:
                    try:
                        engine.load("autosave_slot")
                        ai.latest_observation = "Game state loaded from autosave_slot.json"
                    except Exception as e:
                        ai.latest_observation = f"Load failed: {str(e)}"
                elif event.key == pygame.K_m:
                    muted = audio.toggle_mute()
                    ai.latest_observation = f"Audio {'MUTED' if muted else 'UNMUTED'}"
                elif event.key == pygame.K_r:
                    engine.reset()
                    renderer.hud.selected_organism = None

        # 2. Simulation Steps based on Speed
        steps = int(engine.clock.speed_multiplier) if not engine.clock.paused else 0
        for _ in range(max(1, steps) if not engine.clock.paused else 0):
            engine.step()
            # Process emitted audio events
            if engine.emitted_audio_events:
                audio.process_events(engine.emitted_audio_events)

        # 3. AI Asynchronous Reasoning & Command Dispatch
        snapshot = engine.snapshot()
        ai.maybe_request_analysis(snapshot.to_compact_dict())
        pending_commands = ai.collect_pending_commands()
        for cmd in pending_commands:
            engine.apply_command(cmd)

        # 4. Rendering
        renderer.render(
            screen,
            engine,
            fps=current_fps,
            ai_observation=ai.latest_observation,
            audio_muted=audio.muted,
        )

        pygame.display.flip()
        clock.tick(config.target_fps)
        current_fps = clock.get_fps()

    # Cleanup
    ai.shutdown()
    audio.shutdown()
    pygame.quit()
    sys.exit(0)
