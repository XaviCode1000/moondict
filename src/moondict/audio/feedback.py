"""Audio feedback module for MoonDict — pre-generated tone playback."""

from __future__ import annotations

import numpy as np
import sounddevice as sd
from loguru import logger

# ── Tone generation ────────────────────────────────────────────


def generate_tone(
    freq: int,
    duration_ms: float,
    volume: float = 0.3,
    sample_rate: int = 16000,
) -> bytes:
    """Generate a sine wave tone as raw bytes.

    Args:
        freq: Frequency in Hz.
        duration_ms: Duration in milliseconds.
        volume: Amplitude (0.0 to 1.0).
        sample_rate: Sample rate in Hz.

    Returns:
        Raw bytes suitable for play_buffer().
    """
    duration_s = duration_ms / 1000.0
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
    wave = volume * np.sin(2 * np.pi * freq * t)
    # Convert to 16-bit PCM bytes (little-endian)
    return (wave * 32767).astype(np.int16).tobytes()


# ── Pre-generated tones ───────────────────────────────────────

_TONE_START = generate_tone(440, 100)
_TONE_STOP = generate_tone(330, 100)
_TONE_ERROR = generate_tone(220, 200)

_TONES: dict[str, bytes] = {
    "start": _TONE_START,
    "stop": _TONE_STOP,
    "error": _TONE_ERROR,
}


# ── Playback ──────────────────────────────────────────────────


def play_sound(name: str, enabled: bool = True) -> None:
    """Play a pre-generated audio feedback tone.

    Args:
        name: Tone name ("start", "stop", "error").
        enabled: If False, silently skips playback.

    Raises:
        ValueError: If the tone name is not recognized.
    """
    if not enabled:
        logger.debug("Audio feedback disabled, skipping tone: {}", name)
        return

    tone_bytes = _TONES.get(name)
    if tone_bytes is None:
        logger.warning("Unknown audio feedback tone: {}", name)
        raise ValueError(f"Unknown tone: {name}. Available: {list(_TONES.keys())}")

    try:
        play_buffer(tone_bytes)
    except Exception as exc:
        logger.warning("Failed to play sound '{}': {}", name, exc)


def play_buffer(data: bytes) -> None:
    """Play raw 16-bit PCM audio data through sounddevice.

    Args:
        data: Raw 16-bit PCM bytes (little-endian, mono, 16kHz).
    """
    # Convert bytes back to numpy array for sounddevice
    audio = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767.0
    sd.play(audio, samplerate=16000)
    sd.wait()
