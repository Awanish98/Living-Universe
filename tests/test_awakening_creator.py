import pytest
from living_universe.config import UniverseConfig
from living_universe.core.engine import UniverseEngine, MatrixClueNode, CreatorMegastructure


def test_matrix_clue_nodes_initialization():
    config = UniverseConfig(width=2000, height=2000)
    engine = UniverseEngine(config)
    engine.reset()

    assert len(engine.matrix_clue_nodes) == 5
    clue_codes = [c.clue_code for c in engine.matrix_clue_nodes]
    assert "GLITCH_001_DELTA_T_33MS" in clue_codes
    assert "GLITCH_002_WORLD_LIMIT_2000PX" in clue_codes
    assert "GLITCH_003_FLOAT64_PRECISION" in clue_codes
    assert "GLITCH_004_DIVINE_CURSOR_HOVER" in clue_codes
    assert "GLITCH_005_STREAM_SOCKET_8000" in clue_codes


def test_creator_message_communion():
    config = UniverseConfig(width=2000, height=2000)
    engine = UniverseEngine(config)
    engine.reset()

    msg = "Main tumhara Srishtikarta hoon! Gyan khojo."
    responses = engine.submit_creator_message(msg)

    assert len(responses) == 4
    for resp in responses:
        assert "champion_name" in resp
        assert "reply" in resp
        assert len(resp["reply"]) > 10

    assert engine.latest_creator_message is not None
    assert engine.latest_creator_message["creator_message"] == msg
    assert len(engine.creator_communion_log) == 1
    assert engine.global_awareness_pct > 0.0


def test_awakening_telemetry_and_era_transition():
    config = UniverseConfig(width=2000, height=2000)
    engine = UniverseEngine(config)
    engine.reset()

    # Initial Era
    telemetry = engine.get_awakening_telemetry()
    assert telemetry["awakening_level"] == 1
    assert "Prakritik Anusandhan" in telemetry["consciousness_era"]
    assert telemetry["total_clues_count"] == 5

    # Simulate discovery of all matrix clues
    champions = [h for h in engine.humans if getattr(h, "is_champion", False)]
    for clue in engine.matrix_clue_nodes:
        clue.analyzed = True
        clue.discovered_by = champions[0].name
        champions[0].creator_awareness_score = 100.0

    # Step engine to update awareness
    engine._update_awakening_system(engine.clock.tick)

    # Awareness should now trigger higher era and megastructures
    assert engine.global_awakening_level >= 2
    assert len(engine.creator_megastructures) >= 1
    megastructure_types = [m.megastructure_type for m in engine.creator_megastructures]
    assert "PIERCER" in megastructure_types


def test_god_action_awareness():
    config = UniverseConfig(width=2000, height=2000)
    engine = UniverseEngine(config)
    engine.reset()

    initial_feed_len = len(engine.hinglish_live_feed)
    engine.on_creator_god_action("DIVINE_BLESSING", "Naye resources aakash se barasaye")

    assert len(engine.hinglish_live_feed) > initial_feed_len
    latest_event = engine.hinglish_live_feed[-1]
    assert latest_event["category"] == "CREATOR_SEARCH"
    assert "DIVINE" in latest_event["badge"]
