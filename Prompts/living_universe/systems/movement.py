"""Movement physics and steering force integration system."""

import math
from typing import List, Tuple
from ..entities.organism import Organism
from ..core.world import World


class MovementSystem:
    """Updates organism positions, velocities, orientation, and enforces world boundaries."""

    def __init__(self, drag: float = 0.95):
        self.drag = drag

    def update(self, organisms: List[Organism], world: World, delta_time: float = 1.0) -> None:
        for org in organisms:
            if not org.alive:
                continue

            # Apply acceleration
            org.vx += org.ax * delta_time
            org.vy += org.ay * delta_time

            # Cap speed by DNA maximum velocity
            max_speed = org.dna.speed * 2.5
            speed = math.hypot(org.vx, org.vy)
            if speed > max_speed:
                scale = max_speed / speed
                org.vx *= scale
                org.vy *= scale
            elif speed > 0.05:
                # Update angle
                org.angle = math.atan2(org.vy, org.vx)

            # Apply velocity to position
            org.x += org.vx * delta_time
            org.y += org.vy * delta_time

            # Boundary repulsion / wrap
            margin = org.radius + 4.0
            if org.x < margin:
                org.x = margin
                org.vx = abs(org.vx) * 0.7
            elif org.x > world.width - margin:
                org.x = world.width - margin
                org.vx = -abs(org.vx) * 0.7

            if org.y < margin:
                org.y = margin
                org.vy = abs(org.vy) * 0.7
            elif org.y > world.height - margin:
                org.y = world.height - margin
                org.vy = -abs(org.vy) * 0.7

            # Apply drag/friction
            org.vx *= self.drag
            org.vy *= self.drag

            # Reset acceleration for next tick
            org.ax = 0.0
            org.ay = 0.0
