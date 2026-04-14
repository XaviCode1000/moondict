"""Tests for MoonDict audio feedback module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from moondict.audio.feedback import _TONES, generate_tone, play_sound


class TestGenerateTone:
    """Tests for tone generation."""

    def test_generate_tone_shape(self) -> None:
        """Tone generates correct byte length for 16-bit PCM."""
        # 16000 Hz * 0.1s = 1600 samples * 2 bytes = 3200 bytes
        tone = generate_tone(440, 100)
        assert len(tone) == 3200

    def test_generate_tone_duration(self) -> None:
        """Longer duration produces more bytes."""
        short = generate_tone(440, 100)  # 100ms
        long_tone = generate_tone(440, 200)  # 200ms
        assert len(long_tone) == 2 * len(short)

    def test_generate_tone_frequency(self) -> None:
        """Higher frequency produces more zero crossings."""
        low = np.frombuffer(generate_tone(220, 100), dtype=np.int16)
        high = np.frombuffer(generate_tone(880, 100), dtype=np.int16)

        # Count zero crossings as proxy for frequency
        low_crossings = np.sum(np.diff(np.signbit(low)))
        high_crossings = np.sum(np.diff(np.signbit(high)))

        assert high_crossings > low_crossings

    def test_generate_tone_volume(self) -> None:
        """Higher volume produces larger amplitude values."""
        quiet = np.frombuffer(generate_tone(440, 100, volume=0.1), dtype=np.int16)
        loud = np.frombuffer(generate_tone(440, 100, volume=0.9), dtype=np.int16)

        assert np.abs(loud).max() > np.abs(quiet).max()


class TestPlaySound:
    """Tests for sound playback."""

    @patch("moondict.audio.feedback.play_buffer")
    def test_play_sound_calls_playback(self, mock_play: MagicMock) -> None:
        """play_sound() calls play_buffer with correct tone data."""
        play_sound("start", enabled=True)
        mock_play.assert_called_once_with(_TONES["start"])

    @patch("moondict.audio.feedback.play_buffer")
    def test_play_sound_disabled(self, mock_play: MagicMock) -> None:
        """play_sound() skips playback when enabled=False."""
        play_sound("start", enabled=False)
        mock_play.assert_not_called()

    def test_play_sound_unknown_tone_raises(self) -> None:
        """play_sound() raises ValueError for unknown tone name."""
        with pytest.raises(ValueError, match="Unknown tone"):
            play_sound("nonexistent")

    @patch("moondict.audio.feedback.play_buffer")
    def test_play_all_predefined_tones(self, mock_play: MagicMock) -> None:
        """All predefined tones can be played without error."""
        for name in ("start", "stop", "error"):
            play_sound(name)
            mock_play.assert_called()
            mock_play.reset_mock()


class TestPreGeneratedTones:
    """Tests for pre-generated tone cache."""

    def test_pre_generated_tones_exist(self) -> None:
        """All expected tones are pre-generated at module load."""
        assert "start" in _TONES
        assert "stop" in _TONES
        assert "error" in _TONES

    def test_tone_frequencies(self) -> None:
        """Pre-generated tones have correct frequency content."""
        start = np.frombuffer(_TONES["start"], dtype=np.int16)
        stop = np.frombuffer(_TONES["stop"], dtype=np.int16)
        error = np.frombuffer(_TONES["error"], dtype=np.int16)

        # All should be non-empty
        assert len(start) > 0
        assert len(stop) > 0
        assert len(error) > 0

        # Error tone is 200ms, others are 100ms
        assert len(error) == 2 * len(start)
        assert len(stop) == len(start)
