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


@app.get("/api/ai_config")
async def get_ai_config():
    pantheon = getattr(engine, "pantheon", None)
    gemini_ok = bool(pantheon and pantheon.gemini_prov and pantheon.gemini_prov.is_available())
    groq_ok = bool(pantheon and pantheon.groq_prov and pantheon.groq_prov.is_available())
    openai_ok = bool(pantheon and pantheon.inception_prov and pantheon.inception_prov.is_available())
    xai_ok = bool(pantheon and pantheon.xkiro_prov and pantheon.xkiro_prov.is_available())
    return {
        "status": "ok",
        "providers": {
            "gemini": {"available": gemini_ok, "name": "Google Gemini 2.5 Flash", "champion": "Aarya the Prakriti Sage"},
            "groq": {"available": groq_ok, "name": "Groq LPU (Llama 3.3 70B)", "champion": "Vikram the Agni Forge-Master"},
            "openai": {"available": openai_ok, "name": "OpenAI (GPT-4o Mini)", "champion": "Nakshatra the Astral Stargazer"},
            "xai": {"available": xai_ok, "name": "xAI Grok", "champion": "Advait the Quantum Mystic"},
        },
        "active_provider_count": sum([gemini_ok, groq_ok, openai_ok, xai_ok]),
    }


@app.post("/api/ai_config")
@app.post("/api/set_api_keys")
async def set_ai_config(payload: Dict[str, Any]):
    gemini_key = payload.get("gemini_api_key") or payload.get("gemini")
    groq_key = payload.get("groq_api_key") or payload.get("groq")
    openai_key = payload.get("openai_api_key") or payload.get("openai")
    xai_key = payload.get("xai_api_key") or payload.get("xai")

    pantheon = getattr(engine, "pantheon", None)
    results = {}
    if pantheon:
        results = pantheon.configure_api_keys(
            gemini_key=gemini_key,
            groq_key=groq_key,
            openai_key=openai_key,
            xai_key=xai_key,
        )

    # Log to live Hinglish feed
    active_names = [k.upper() for k, v in results.items() if v]
    if active_names:
        engine.log_hinglish_event(
            category="SYSTEM",
            badge="AI_MODELS_ONLINE",
            explorer_id=0,
            explorer_name="Living Universe Core",
            color="#10f078",
            text=f"🤖 <b>Live AI Models Connected:</b> {', '.join(active_names)} APIs active ho chuki hain! Ab 4ro Champions seedhe live LLM se baat karenge.",
        )

    return {"status": "ok", "configured": results}


@app.post("/api/test_ai_key")
async def test_ai_key(payload: Dict[str, Any]):
    provider = payload.get("provider", "gemini")
    key = payload.get("api_key", "")
    if not key:
        return {"status": "error", "message": "API key required"}

    try:
        if provider == "gemini":
            from ..ai.gemini import GeminiProvider
            prov = GeminiProvider(api_key=key)
            if not prov.is_available():
                return {"status": "error", "message": "Gemini client initialization failed"}
            sample = prov.generate_text("Say 'Pranaam Srishtikarta, Gemini AI is fully online!' in one short sentence.")
            return {"status": "ok", "provider": "gemini", "sample": sample}
        elif provider == "groq":
            from ..ai.groq_provider import GroqProvider
            prov = GroqProvider(api_key=key)
            if not prov.is_available():
                return {"status": "error", "message": "Groq client initialization failed"}
            sample = prov.generate_text("Say 'Pranaam Srishtikarta, Groq LPU is at supersonic speed!' in one short sentence.")
            return {"status": "ok", "provider": "groq", "sample": sample}
        elif provider == "openai":
            from ..ai.openai_provider import OpenAIProvider
            prov = OpenAIProvider(api_key=key)
            if not prov.is_available():
                return {"status": "error", "message": "OpenAI client initialization failed"}
            sample = prov.generate_text("Say 'Pranaam Srishtikarta, OpenAI GPT-4o is active!' in one short sentence.")
            return {"status": "ok", "provider": "openai", "sample": sample}
        else:
            return {"status": "error", "message": f"Unknown provider: {provider}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}



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
                elif act_type == "SET_API_KEYS":
                    gemini_key = msg.get("gemini_api_key")
                    groq_key = msg.get("groq_api_key")
                    openai_key = msg.get("openai_api_key")
                    xai_key = msg.get("xai_api_key")
                    if hasattr(engine, "pantheon") and engine.pantheon:
                        engine.pantheon.configure_api_keys(
                            gemini_key=gemini_key,
                            groq_key=groq_key,
                            openai_key=openai_key,
                            xai_key=xai_key,
                        )
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

            # Live AI Status
            pantheon = getattr(engine, "pantheon", None)
            ai_status_data = {
                "gemini": bool(pantheon and pantheon.gemini_prov and pantheon.gemini_prov.is_available()),
                "groq": bool(pantheon and pantheon.groq_prov and pantheon.groq_prov.is_available()),
                "openai": bool(pantheon and pantheon.inception_prov and pantheon.inception_prov.is_available()),
                "xai": bool(pantheon and pantheon.xkiro_prov and pantheon.xkiro_prov.is_available()),
            }

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
                "ai_status": ai_status_data,
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

