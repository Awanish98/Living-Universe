"""Visual particle effects system for births, deaths, eating, attacks, and events."""

from dataclasses import dataclass
from typing import List, Tuple
import random
import pygame
from .camera import Camera2D


@dataclass
class VisualParticle:
    x: float
    y: float
    vx: float
    vy: float
    color: Tuple[int, int, int]
    radius: float
    alpha: float = 255.0
    decay: float = 8.0

    def update(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.alpha -= self.decay
        self.radius = max(0.5, self.radius * 0.95)
        return self.alpha > 0.0


class ParticleEffectManager:
    """Manages visual flare particles, shockwaves, and environmental trails."""

    def __init__(self):
        self.particles: List[VisualParticle] = []
        self.rng = random.Random()

    def spawn_birth_burst(self, x: float, y: float, color: Tuple[int, int, int], count: int = 12) -> None:
        for _ in range(count):
            angle = self.rng.uniform(0, 6.28)
            spd = self.rng.uniform(0.5, 2.5)
            self.particles.append(VisualParticle(
                x=x, y=y,
                vx=spd * self.rng.uniform(0.8, 1.2) * self.rng.choice([-1, 1]),
                vy=spd * self.rng.uniform(0.8, 1.2) * self.rng.choice([-1, 1]),
                color=(min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50)),
                radius=self.rng.uniform(2.0, 4.0),
                decay=self.rng.uniform(6.0, 12.0)
            ))

    def spawn_death_fade(self, x: float, y: float, color: Tuple[int, int, int], count: int = 8) -> None:
        for _ in range(count):
            self.particles.append(VisualParticle(
                x=x + self.rng.uniform(-3, 3),
                y=y + self.rng.uniform(-3, 3),
                vx=self.rng.uniform(-0.5, 0.5),
                vy=self.rng.uniform(-0.8, -0.1),
                color=(150, 150, 160),
                radius=self.rng.uniform(1.5, 3.0),
                decay=self.rng.uniform(4.0, 8.0)
            ))

    def spawn_eat_spark(self, x: float, y: float, count: int = 4) -> None:
        for _ in range(count):
            self.particles.append(VisualParticle(
                x=x, y=y,
                vx=self.rng.uniform(-1.0, 1.0),
                vy=self.rng.uniform(-1.0, 1.0),
                color=(120, 255, 180),
                radius=2.0,
                decay=15.0
            ))

    def spawn_attack_flash(self, x: float, y: float, count: int = 6) -> None:
        for _ in range(count):
            self.particles.append(VisualParticle(
                x=x, y=y,
                vx=self.rng.uniform(-2.0, 2.0),
                vy=self.rng.uniform(-2.0, 2.0),
                color=(255, 60, 60),
                radius=self.rng.uniform(2.5, 4.5),
                decay=16.0
            ))

    def update(self) -> None:
        self.particles = [p for p in self.particles if p.update()]

    def render(self, surface: pygame.Surface, camera: Camera2D) -> None:
        for p in self.particles:
            if camera.is_visible(p.x, p.y, p.radius):
                sx, sy = camera.world_to_screen(p.x, p.y)
                r = max(1, int(p.radius * camera.zoom))
                alpha = int(max(0, min(255, p.alpha)))
                # Fast circle draw
                color = (*p.color, alpha)
                pygame.draw.circle(surface, p.color, (sx, sy), r)
