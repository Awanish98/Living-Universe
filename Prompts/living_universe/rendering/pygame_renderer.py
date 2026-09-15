"""High-performance Pygame visual renderer with sci-fi aesthetics and particle glow."""

import math
from typing import Optional, List
import pygame
from ..core.engine import UniverseEngine
from ..core.world import World
from ..entities.organism import Organism
from ..entities.resource import Resource
from .camera import Camera2D
from .particles import ParticleEffectManager
from .hud import HUD


class PygameRenderer:
    """Master renderer for the living universe, environmental zones, and HUD."""

    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        self.width = screen_width
        self.height = screen_height
        self.camera = Camera2D(screen_width, screen_height)
        self.particles = ParticleEffectManager()
        self.hud = HUD(screen_width, screen_height)

    def render(
        self,
        surface: pygame.Surface,
        engine: UniverseEngine,
        fps: float = 60.0,
        ai_observation: str = "",
        audio_muted: bool = False,
    ) -> None:
        self.camera.update()
        self.particles.update()

        # 1. Background Universe Grid & Zones
        surface.fill((8, 10, 18))
        self._render_world_zones(surface, engine.world)
        self._render_world_boundary(surface, engine.world)

        # 2. Render Active World Events (Glowing shockwaves / blooms)
        self._render_events(surface, engine)

        # 3. Render Food & Resources
        self._render_resources(surface, engine.resources)

        # 4. Render Organisms (Body, Direction, Signals)
        self._render_organisms(surface, engine.organisms)

        # 5. Render Particle Effects
        self.particles.render(surface, self.camera)

        # 6. Render HUD Overlays
        snapshot = engine.snapshot()
        self.hud.render(
            surface,
            snapshot,
            engine.history,
            fps=fps,
            ai_observation=ai_observation,
            audio_muted=audio_muted,
        )

    def _render_world_boundary(self, surface: pygame.Surface, world: World) -> None:
        sx1, sy1 = self.camera.world_to_screen(0, 0)
        sx2, sy2 = self.camera.world_to_screen(world.width, world.height)
        rect = pygame.Rect(sx1, sy1, sx2 - sx1, sy2 - sy1)
        pygame.draw.rect(surface, (20, 35, 60), rect, 2)

    def _render_world_zones(self, surface: pygame.Surface, world: World) -> None:
        for zone in world.zones:
            if self.camera.is_visible(zone.x, zone.y, zone.radius):
                sx, sy = self.camera.world_to_screen(zone.x, zone.y)
                sr = int(zone.radius * self.camera.zoom)
                if sr > 2:
                    # Draw soft zone glow
                    zone_surf = pygame.Surface((sr * 2, sr * 2), pygame.SRCALPHA)
                    pygame.draw.circle(zone_surf, (*zone.color, 90), (sr, sr), sr)
                    pygame.draw.circle(zone_surf, (*zone.color, 140), (sr, sr), sr, 1)
                    surface.blit(zone_surf, (sx - sr, sy - sr))

    def _render_events(self, surface: pygame.Surface, engine: UniverseEngine) -> None:
        for ev in engine.active_events:
            if ev.x is not None and ev.y is not None and ev.radius is not None:
                if self.camera.is_visible(ev.x, ev.y, ev.radius):
                    sx, sy = self.camera.world_to_screen(ev.x, ev.y)
                    sr = int(ev.radius * self.camera.zoom)
                    prog = ev.progress()
                    
                    if ev.type == "FOOD_BLOOM":
                        color = (40, 220, 120)
                    elif ev.type == "METEOR_IMPACT":
                        color = (255, 90, 40)
                    else:
                        color = (0, 200, 255)

                    pulse_r = max(2, int(sr * (0.8 + 0.2 * math.sin(prog * 15.0))))
                    ev_surf = pygame.Surface((pulse_r * 2, pulse_r * 2), pygame.SRCALPHA)
                    pygame.draw.circle(ev_surf, (*color, 45), (pulse_r, pulse_r), pulse_r)
                    pygame.draw.circle(ev_surf, (*color, 160), (pulse_r, pulse_r), pulse_r, 2)
                    surface.blit(ev_surf, (sx - pulse_r, sy - pulse_r))

    def _render_resources(self, surface: pygame.Surface, resources: List[Resource]) -> None:
        zoom = self.camera.zoom
        for res in resources:
            if self.camera.is_visible(res.x, res.y, res.radius):
                sx, sy = self.camera.world_to_screen(res.x, res.y)
                r = max(1, int(res.radius * zoom))

                if res.resource_type == "plant":
                    color = (40, 230, 140)
                elif res.resource_type == "meat":
                    color = (240, 60, 80)
                else:
                    color = (200, 220, 80)

                pygame.draw.circle(surface, color, (sx, sy), r)

    def _render_organisms(self, surface: pygame.Surface, organisms: List[Organism]) -> None:
        zoom = self.camera.zoom
        selected = self.hud.selected_organism

        for org in organisms:
            if not org.alive:
                continue

            if not self.camera.is_visible(org.x, org.y, org.radius + 20.0):
                continue

            sx, sy = self.camera.world_to_screen(org.x, org.y)
            r = max(2, int(org.radius * zoom))
            color = org.dna.get_color_rgb()

            # Social signal ripple if active
            if org.active_signal:
                sig_color = (255, 60, 60) if org.active_signal == "DANGER" else (60, 240, 180)
                ripple_r = r + int(12 * zoom)
                pygame.draw.circle(surface, (*sig_color, 120), (sx, sy), ripple_r, 1)

            # Draw body circle
            pygame.draw.circle(surface, color, (sx, sy), r)

            # Heading direction marker / snout
            hx, hy = org.heading_vector()
            tip_x = sx + int(hx * (r + 3 * zoom))
            tip_y = sy + int(hy * (r + 3 * zoom))
            pygame.draw.line(surface, (240, 240, 255), (sx, sy), (tip_x, tip_y), max(1, int(1.5 * zoom)))

            # Highlight selected organism & sensory circle
            if selected and selected.id == org.id:
                # Highlight ring
                pygame.draw.circle(surface, (0, 240, 255), (sx, sy), r + 4, 2)
                # Vision field circle
                vis_r = int(org.dna.vision_range * zoom)
                vis_surf = pygame.Surface((vis_r * 2, vis_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(vis_surf, (0, 200, 255, 30), (vis_r, vis_r), vis_r)
                pygame.draw.circle(vis_surf, (0, 200, 255, 80), (vis_r, vis_r), vis_r, 1)
                surface.blit(vis_surf, (sx - vis_r, sy - vis_r))
