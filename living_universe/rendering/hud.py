"""Futuristic sci-fi HUD, entity inspector, control panels, and AI observation banner."""

from typing import Optional, Dict, Any, List
import pygame
from ..core.snapshot import WorldSnapshot
from ..entities.organism import Organism
from ..entities.species import Species
from ..analytics.history import SimulationHistory
from .charts import MiniChart


class HUD:
    """Renders the futuristic interface, telemetry overlays, and organism inspector."""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_main = pygame.font.SysFont("Consolas, Courier, monospace", 13)
        self.font_title = pygame.font.SysFont("Consolas, Courier, monospace", 16, bold=True)
        self.font_small = pygame.font.SysFont("Consolas, Courier, monospace", 11)
        self.chart = MiniChart(width=230, height=80)
        self.selected_organism: Optional[Organism] = None

    def render(
        self,
        surface: pygame.Surface,
        snapshot: WorldSnapshot,
        history: SimulationHistory,
        fps: float,
        ai_observation: str,
        audio_muted: bool,
        show_controls: bool = True,
    ) -> None:
        # 1. Top Telemetry Bar
        self._render_top_bar(surface, snapshot, fps, audio_muted)

        # 2. Active Event Banner (if any)
        self._render_event_banner(surface, snapshot)

        # 3. Bottom AI Narration Ticker
        self._render_ai_ticker(surface, ai_observation, snapshot.ai_status)

        # 4. Right Side Telemetry & Graph Panel
        self._render_right_panel(surface, snapshot, history)

        # 5. Left Controls Overlay
        if show_controls:
            self._render_controls_overlay(surface)

        # 6. Organism Inspector Card
        if self.selected_organism and self.selected_organism.alive:
            self._render_inspector(surface, snapshot)

    def _render_top_bar(self, surface: pygame.Surface, s: WorldSnapshot, fps: float, audio_muted: bool) -> None:
        bar = pygame.Surface((self.screen_width, 34), pygame.SRCALPHA)
        bar.fill((8, 12, 20, 230))
        pygame.draw.line(bar, (0, 180, 255), (0, 33), (self.screen_width, 33), 1)

        txt_left = (
            f"TICK: {s.tick:06d} | POP: {s.population:04d} | "
            f"SPECIES: {s.species_count:02d} | FOOD: {s.food_count:04d} | "
            f"ENERGY: {s.average_energy:4.1f} | HEALTH: {s.average_health:4.1f}%"
        )
        rendered_l = self.font_main.render(txt_left, True, (0, 240, 255))
        bar.blit(rendered_l, (14, 9))

        audio_str = "MUTED" if audio_muted else "AUDIO ON"
        txt_right = f"SPEED: {s.sim_speed:.1f}x | FPS: {fps:4.1f} | {audio_str}"
        rendered_r = self.font_main.render(txt_right, True, (150, 200, 255))
        bar.blit(rendered_r, (self.screen_width - rendered_r.get_width() - 14, 9))

        surface.blit(bar, (0, 0))

    def _render_event_banner(self, surface: pygame.Surface, s: WorldSnapshot) -> None:
        if not s.active_events:
            return
        ev = s.active_events[0]
        ev_type = ev.get("type", "EVENT")
        prog = ev.get("progress", 0.0)

        banner_w, banner_h = 280, 28
        bx = (self.screen_width - banner_w) // 2
        by = 40

        box = pygame.Surface((banner_w, banner_h), pygame.SRCALPHA)
        box.fill((45, 15, 20, 220))
        pygame.draw.rect(box, (255, 80, 80), (0, 0, banner_w, banner_h), 1)

        # Progress bar
        pw = int((banner_w - 4) * prog)
        pygame.draw.rect(box, (180, 40, 40), (2, 2, pw, banner_h - 4))

        txt = self.font_small.render(f"ACTIVE EVENT: {ev_type} [{int(prog*100)}%]", True, (255, 220, 220))
        box.blit(txt, ((banner_w - txt.get_width()) // 2, 6))

        surface.blit(box, (bx, by))

    def _render_ai_ticker(self, surface: pygame.Surface, observation: str, ai_status: str) -> None:
        bar_h = 28
        bar = pygame.Surface((self.screen_width, bar_h), pygame.SRCALPHA)
        bar.fill((8, 12, 20, 230))
        pygame.draw.line(bar, (0, 180, 255), (0, 0), (self.screen_width, 0), 1)

        obs_text = observation if observation else "AI Observer monitoring ecosystem..."
        txt = self.font_main.render(obs_text, True, (120, 255, 200))
        bar.blit(txt, (14, 6))

        surface.blit(bar, (0, self.screen_height - bar_h))

    def _render_right_panel(self, surface: pygame.Surface, s: WorldSnapshot, history: SimulationHistory) -> None:
        pw, ph = 250, 260
        px = self.screen_width - pw - 12
        py = 44

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((8, 12, 22, 210))
        pygame.draw.rect(panel, (30, 45, 75), (0, 0, pw, ph), 1)

        # Title
        t = self.font_title.render("ECOSYSTEM TELEMETRY", True, (0, 220, 255))
        panel.blit(t, (10, 8))

        # Chart
        chart_surf = self.chart.draw_history(history)
        panel.blit(chart_surf, (10, 32))

        # Legend
        leg_pop = self.font_small.render("■ Population", True, (0, 220, 255))
        leg_food = self.font_small.render("■ Food", True, (60, 200, 100))
        leg_carn = self.font_small.render("■ Predators", True, (255, 70, 70))
        panel.blit(leg_pop, (12, 116))
        panel.blit(leg_food, (100, 116))
        panel.blit(leg_carn, (165, 116))

        # Trophic Distribution Breakdown
        y = 136
        trophic_txt = f"Trophic: {s.herbivore_count} Herb / {s.carnivore_count} Carn"
        panel.blit(self.font_main.render(trophic_txt, True, (200, 220, 240)), (10, y))

        y += 18
        birth_death_txt = f"Births: +{s.births} | Deaths: -{s.deaths}"
        panel.blit(self.font_main.render(birth_death_txt, True, (160, 200, 220)), (10, y))

        # Dominant Traits
        y += 22
        panel.blit(self.font_small.render("DOMINANT GENETICS:", True, (0, 180, 220)), (10, y))
        y += 16
        dt = s.dominant_traits
        if dt:
            traits_line1 = f"Spd:{dt.get('speed',0)} Vis:{int(dt.get('vision',0))} Siz:{dt.get('size',0)}"
            traits_line2 = f"Agg:{dt.get('aggression',0)} Fer:{dt.get('fertility',0)} Soc:{dt.get('sociability',0)}"
            panel.blit(self.font_small.render(traits_line1, True, (170, 190, 210)), (10, y))
            panel.blit(self.font_small.render(traits_line2, True, (170, 190, 210)), (10, y + 14))

        surface.blit(panel, (px, py))

    def _render_controls_overlay(self, surface: pygame.Surface) -> None:
        cw, ch = 200, 175
        cx = 12
        cy = 44

        box = pygame.Surface((cw, ch), pygame.SRCALPHA)
        box.fill((8, 12, 22, 190))
        pygame.draw.rect(box, (30, 45, 75), (0, 0, cw, ch), 1)

        title = self.font_title.render("CONTROLS", True, (0, 220, 255))
        box.blit(title, (10, 8))

        shortcuts = [
            ("SPACE", "Pause / Play"),
            ("1 - 5", "Speed (1x to 10x)"),
            ("F", "Spawn Food"),
            ("O", "Spawn Organisms"),
            ("E", "Trigger Event"),
            ("S / L", "Save / Load"),
            ("M", "Mute Audio"),
            ("CLICK", "Inspect Organism"),
            ("DRAG", "Pan Viewport"),
        ]

        y = 30
        for key, desc in shortcuts:
            k_surf = self.font_small.render(key, True, (255, 200, 80))
            d_surf = self.font_small.render(desc, True, (180, 200, 220))
            box.blit(k_surf, (10, y))
            box.blit(d_surf, (70, y))
            y += 15

        surface.blit(box, (cx, cy))

    def _render_inspector(self, surface: pygame.Surface, snapshot: WorldSnapshot) -> None:
        org = self.selected_organism
        if not org or not org.alive:
            return

        iw, ih = 250, 240
        ix = 12
        iy = self.screen_height - ih - 38

        card = pygame.Surface((iw, ih), pygame.SRCALPHA)
        card.fill((10, 16, 28, 230))
        pygame.draw.rect(card, (0, 220, 255), (0, 0, iw, ih), 1)

        # Header with organism color
        sp_color = org.dna.get_color_rgb()
        pygame.draw.circle(card, sp_color, (20, 20), 8)
        
        title_txt = f"ORGANISM #{org.id} (G{org.generation})"
        card.blit(self.font_title.render(title_txt, True, (0, 240, 255)), (36, 12))

        # State & Species
        diet_str = "Carnivore" if org.dna.is_carnivore() else ("Herbivore" if org.dna.is_herbivore() else "Omnivore")
        card.blit(self.font_small.render(f"Species: #{org.species_id} [{diet_str}]", True, (160, 200, 230)), (14, 38))
        card.blit(self.font_small.render(f"State: {org.current_state.upper()}", True, (255, 220, 100)), (14, 54))

        # Energy & Health Bars
        y = 74
        self._draw_bar(card, "ENERGY", org.energy, org.max_energy, (40, 220, 120), y)
        y += 24
        self._draw_bar(card, "HEALTH", org.health, org.max_health, (255, 70, 70), y)

        # DNA Trait Grid
        y += 26
        card.blit(self.font_small.render("GENOMIC PROFILE:", True, (0, 180, 220)), (14, y))
        y += 14
        t1 = f"Spd: {org.dna.speed:.1f} | Vis: {int(org.dna.vision_range)} | Siz: {org.dna.size:.1f}"
        t2 = f"Agg: {org.dna.aggression:.2f} | Fer: {org.dna.fertility:.2f} | Soc: {org.dna.sociability:.2f}"
        card.blit(self.font_small.render(t1, True, (180, 200, 220)), (14, y))
        card.blit(self.font_small.render(t2, True, (180, 200, 220)), (14, y + 14))

        # Stats
        y += 32
        stats_txt = f"Age: {org.age} | Kills: {org.kills} | Offspring: {org.offspring_count}"
        card.blit(self.font_small.render(stats_txt, True, (140, 180, 220)), (14, y))

        surface.blit(card, (ix, iy))

    def _draw_bar(self, surf: pygame.Surface, label: str, current: float, max_v: float, color: tuple, y: int):
        ratio = max(0.0, min(1.0, current / max(1.0, max_v)))
        bar_w = 140
        bar_h = 10
        x = 94

        surf.blit(self.font_small.render(f"{label}:", True, (180, 200, 220)), (14, y - 1))
        pygame.draw.rect(surf, (20, 30, 45), (x, y, bar_w, bar_h))
        pygame.draw.rect(surf, color, (x, y, int(bar_w * ratio), bar_h))
        pygame.draw.rect(surf, (40, 60, 90), (x, y, bar_w, bar_h), 1)
