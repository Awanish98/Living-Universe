"""Unit tests for the modular AudioEngine and procedural synth fallback."""

from living_universe.audio.engine import AudioEngine
from living_universe.audio.procedural import ProceduralAudioSynth


def test_audio_engine_headless_safety():
    audio = AudioEngine()
    # Should not raise any error even if sound card/audio device is missing or uninitialized
    audio.play("PARTICLE_BORN")
    audio.play("FOOD_CONSUMED")
    audio.set_master_volume(0.5)
    assert audio.master_volume == 0.5
    audio.mute(True)
    assert audio.muted is True
    audio.shutdown()


def test_procedural_synth_generation():
    synth = ProceduralAudioSynth(sample_rate=22050)
    samples = synth._generate_tone(440.0, duration=0.05)
    assert len(samples) > 0
    assert max(abs(samples)) <= 1.0
