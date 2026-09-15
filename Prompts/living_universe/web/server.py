"""
living_universe.web.server
~~~~~~~~~~~~~~~~~~~~~~~~~~
FastAPI + WebSocket real-time digital biosphere & human civilization streaming server.
"""

import os
import json
import random
import asyncio
from typing import Dict, Any, List
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from ..config import UniverseConfig
from ..core.engine import UniverseEngine
from ..ai.orchestrator import AIOrchestrator
from ..core.commands import WorldCommand, WorldAction
from ..systems.civilization import TECH_TREE


app = FastAPI(title="Living Universe — Digital Civilization & Biosphere Observatory")

# Global Engine & AI Orchestrator
config = UniverseConfig(width=2000, height=2000, initial_organisms=60, initial_resources=180)
engine = UniverseEngine(config)
ai = AIOrchestrator(default_provider=config.ai_provider if config.ai_enabled else "null")

static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)


@app.get("/")
async def get_index():
    index_path = os.path.join(static_dir, "index.html")
    return FileResponse(index_path)


@app.get("/api/snapshot")
async def get_snapshot():
    return engine.snapshot().to_dict()


@app.get("/api/phylogeny")
async def get_phylogeny():
    return [sp.to_dict() for sp in engine.species_registry.values()]


@app.get("/api/civilizations")
async def get_civilizations():
    return {cid: c.to_dict() for cid, c in engine.civilizations.items()}


@app.get("/api/tech_tree")
async def get_tech_tree():
    return {
        tid: {
            "name": t["name"],
            "era": t["era"].value,
            "cost": t["cost"],
            "prereqs": t["prereqs"],
            "description": t["description"],
            "bonuses": t["bonuses"],
        }
        for tid, t in TECH_TREE.items()
    }


@app.get("/api/settlements")
async def get_settlements():
    return [s.to_dict() for s in engine.settlements]


@app.get("/api/explorers")
async def get_explorers():
    return [h.to_dict() for h in engine.humans if getattr(h, "is_champion", False)]


@app.get("/api/discoveries")
async def get_discoveries():
    return [n.to_dict() for n in engine.discovery_nodes]


@app.get("/api/monuments")
async def get_monuments():
    return [m.to_dict() for m in engine.monuments]


@app.get("/api/feed")
async def get_feed():
    return list(engine.hinglish_live_feed)


def serialize_family_tree():
    return [
        {
            "id": h.id,
            "name": h.name,
            "champion_id": getattr(h, "champion_id", None),
            "is_champion": getattr(h, "is_champion", False),
            "is_progeny": getattr(h, "is_progeny", False),
            "avatar": {1: "🌿", 2: "⚔️", 3: "🔮", 4: "🌌"}.get(getattr(h, "champion_id", None), "🧬" if getattr(h, "is_progeny", False) else "👤"),
            "gender": h.gender,
            "generation": getattr(h, "generation", 0),
            "parent_ids": getattr(h, "parent_ids", []),
            "parent_names": getattr(h, "parent_names", []),
            "birth_tick": getattr(h, "birth_tick", 0),
            "intellect": round(h.intellect_score, 1),
            "inventions": list(h.inventions_unlocked) + list(getattr(h, "collaborative_inventions", [])),
            "progeny_type": getattr(h, "progeny_type", "Founder"),
            "aura_color": getattr(h, "aura_color", "#00f3ff"),
            "title": getattr(h, "avatar_title", f"Gen-{getattr(h, 'generation', 1)} Digital Citizen"),
            "lineage_title": getattr(h, "lineage_title", "Founding Grand Explorer"),
        }
        for h in engine.humans
    ]


@app.get("/api/awakening")
async def get_awakening():
    return engine.get_awakening_telemetry()


@app.post("/api/creator_message")
async def post_creator_message(payload: Dict[str, Any]):
    msg_text = payload.get("message", "")
    responses = engine.submit_creator_message(msg_text)
    return {"status": "ok", "responses": responses}


@app.get("/api/family_tree")
async def get_family_tree():
    return serialize_family_tree()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    async def client_listener():
        try:
            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)
                act_type = msg.get("action")

                if act_type == "PAUSE":
                    engine.clock.pause()
                elif act_type == "RESUME":
                    engine.clock.resume()
                elif act_type == "TOGGLE_PAUSE":
                    engine.clock.toggle_pause()
                elif act_type == "SET_SPEED":
                    engine.clock.set_speed(float(msg.get("value", 1.0)))
                elif act_type in ("BOOST_INTELLECT", "BOOST_CHAMPION"):
                    champ_id = int(msg.get("champion_id", 1))
                    engine.boost_explorer_intellect(champ_id, amount=float(msg.get("amount", 50.0)))
                elif act_type == "CREATOR_MESSAGE":
                    text = msg.get("text", "")
                    engine.submit_creator_message(text)
                elif act_type == "GOD_ACTION":
                    engine.on_creator_god_action(msg.get("action_type", "BLESSING"), msg.get("details", ""))
                elif act_type == "SPAWN_ANOMALY":
                    engine.spawn_anomaly(
                        x=msg.get("x"),
                        y=msg.get("y"),
                        node_type=msg.get("type"),
                    )
                elif act_type in ("TRIGGER_DIALOGUE", "TRIGGER_COLLABORATION"):
                    champs = [h for h in engine.humans if getattr(h, "is_champion", False)]
                    if len(champs) >= 2:
                        c1, c2 = random.sample(champs, 2)
                        engine.trigger_explorer_dialogue(c1, c2, engine.clock.tick)
                elif act_type == "RESET":
                    engine.reset()
                elif act_type == "AI_PROMPT":
                    prompt = msg.get("prompt", "")
                    ai.submit_user_command(prompt, engine.snapshot().to_compact_dict())
        except (WebSocketDisconnect, asyncio.CancelledError):
            pass

    listener_task = asyncio.create_task(client_listener())

    try:
        frame_counter = 0
        step_accumulator = 0.0
        while True:
            frame_counter += 1
            if not engine.clock.paused:
                step_accumulator += float(engine.clock.speed_multiplier)
                while step_accumulator >= 1.0:
                    engine.step()
                    step_accumulator -= 1.0

            snap = engine.snapshot()

            # The 4 Grand Explorers
            explorers_data = [h.to_dict() for h in engine.humans if getattr(h, "is_champion", False)]

            # Discovery Nodes & Anomalies
            nodes_data = [n.to_dict() for n in engine.discovery_nodes]

            # Matrix Clue Nodes (Brahma-Khoj)
            matrix_clues_data = [c.to_dict() for c in engine.matrix_clue_nodes]

            # Built Landmark Monuments & Creator Megastructures
            monuments_data = [m.to_dict() for m in engine.monuments]
            creator_megastructures_data = [m.to_dict() for m in engine.creator_megastructures]

            # Progeny Digital Citizens
            progeny_data = [h.to_dict() for h in engine.humans if getattr(h, "is_progeny", False)]

            # Live Hinglish Feed
            feed_data = list(engine.hinglish_live_feed)

            # Live Family Tree
            family_tree_data = serialize_family_tree()

            # Awakening Telemetry
            awakening_telemetry = engine.get_awakening_telemetry()

            payload = {
                "tick": snap.tick,
                "paused": engine.clock.paused,
                "speed": engine.clock.speed_multiplier,
                "explorers": explorers_data,
                "progeny": progeny_data,
                "population": len(engine.humans),
                "family_tree": family_tree_data,
                "discovery_nodes": nodes_data,
                "matrix_clues": matrix_clues_data,
                "monuments": monuments_data,
                "creator_megastructures": creator_megastructures_data,
                "awakening": awakening_telemetry,
                "creator_communion_log": engine.creator_communion_log,
                "hinglish_live_feed": feed_data,
                "nodes_count": len(engine.discovery_nodes),
                "mastered_nodes_count": sum(1 for n in engine.discovery_nodes if n.mastered),
                "monuments_count": len(engine.monuments),
                "collaborative_inventions": list({tech for h in engine.humans for tech in getattr(h, "collaborative_inventions", [])}),
                "temp": round(snap.temperature, 1),
                "day_phase": round(engine.world.get_day_phase(snap.tick), 3),
                "audio_events": [ev[0] for ev in engine.emitted_audio_events],
                "seasons": engine.seasons.to_dict(),
                "world": {
                    "w": engine.world.width,
                    "h": engine.world.height,
                    "zones": [
                        {
                            "name": z.name,
                            "type": z.zone_type,
                            "x": z.x,
                            "y": z.y,
                            "r": z.radius,
                            "c": z.color,
                        }
                        for z in engine.world.zones
                    ],
                },
                # Backward compatibility keys for frontend components
                "champions": explorers_data,
                "humans": explorers_data,
                "resources": [],
                "organisms": [],
                "settlements": [s.to_dict() for s in engine.settlements],
                "civilizations": {cid: c.to_dict() for cid, c in engine.civilizations.items()},
            }

            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(0.033)  # ~30 FPS network stream

    except (WebSocketDisconnect, Exception):
        pass
    finally:
        listener_task.cancel()


app.mount("/static", StaticFiles(directory=static_dir), name="static")

