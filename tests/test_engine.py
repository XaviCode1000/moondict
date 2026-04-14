"""Tests for MoonDict engine implementations."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from moondict.config import MoonDictConfig
from moondict.engine.interface import EngineLoadError, TranscriptionListener
from moondict.engine.moonshine import MoonshineEngine, TranscriptEventListener


class TestMoonshineEngineLoad:
    """Tests for MoonshineEngine.load()."""

    def test_load_success(
        self,
        sample_config: MoonDictConfig,
        mock_get_model_for_language: MagicMock,
        mock_transcriber: MagicMock,
        mock_model_arch: MagicMock,
    ) -> None:
        """Engine loads model and creates transcriber successfully."""
        engine = MoonshineEngine(sample_config)
        engine.load()

        mock_get_model_for_language.assert_called_once_with("es")
        mock_transcriber.assert_called_once()
        assert engine.is_loaded is True
        assert engine.is_running is False

    def test_load_model_failure(
        self,
        sample_config: MoonDictConfig,
        mock_get_model_for_language: MagicMock,
    ) -> None:
        """Engine raises EngineLoadError when model download fails."""
        mock_get_model_for_language.side_effect = RuntimeError("Model not found")

        engine = MoonshineEngine(sample_config)

        with pytest.raises(EngineLoadError):
            engine.load()

        assert engine.is_loaded is False

    def test_load_transcriber_failure(
        self,
        sample_config: MoonDictConfig,
        mock_get_model_for_language: MagicMock,
        mock_transcriber: MagicMock,
        mock_model_arch: MagicMock,
    ) -> None:
        """Engine raises EngineLoadError when transcriber init fails."""
        mock_transcriber.side_effect = RuntimeError("Transcriber error")

        engine = MoonshineEngine(sample_config)

        with pytest.raises(EngineLoadError):
            engine.load()

        assert engine.is_loaded is False


class TestMoonshineEngineLifecycle:
    """Tests for MoonshineEngine start/stop lifecycle."""

    def test_start_creates_stream(
        self,
        sample_config: MoonDictConfig,
        mock_get_model_for_language: MagicMock,
        mock_transcriber: MagicMock,
        mock_model_arch: MagicMock,
    ) -> None:
        """Engine starts audio stream after loading."""
        engine = MoonshineEngine(sample_config)
        engine.load()

        listener: TranscriptionListener = MagicMock()

        with patch("moondict.engine.moonshine.sd") as mock_sd:
            mock_stream = MagicMock()
            mock_sd.InputStream.return_value = mock_stream
            engine.start(listener)

            mock_sd.InputStream.assert_called_once()
            assert engine.is_running is True

    def test_stop_cleans_up(
        self,
        sample_config: MoonDictConfig,
        mock_get_model_for_language: MagicMock,
        mock_transcriber: MagicMock,
        mock_model_arch: MagicMock,
    ) -> None:
        """Engine stops stream and resets running state."""
        engine = MoonshineEngine(sample_config)
        engine.load()

        listener: TranscriptionListener = MagicMock()

        with patch("moondict.engine.moonshine.sd") as mock_sd:
            mock_stream = MagicMock()
            mock_sd.InputStream.return_value = mock_stream
            engine.start(listener)

            engine.stop()

            mock_stream.stop.assert_called_once()
            mock_stream.close.assert_called_once()
            assert engine.is_running is False

    def test_start_without_load_raises(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Engine raises EngineLoadError if start() called before load()."""
        engine = MoonshineEngine(sample_config)
        listener: TranscriptionListener = MagicMock()

        with (
            pytest.raises(EngineLoadError),
            patch("moondict.engine.moonshine.sd"),
        ):
            engine.start(listener)


class TestMoonshineEngineStateTransitions:
    """Tests for is_loaded / is_running state transitions."""

    def test_initial_state(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Engine starts with is_loaded=False and is_running=False."""
        engine = MoonshineEngine(sample_config)
        assert engine.is_loaded is False
        assert engine.is_running is False

    def test_state_after_load(
        self,
        sample_config: MoonDictConfig,
        mock_get_model_for_language: MagicMock,
        mock_transcriber: MagicMock,
        mock_model_arch: MagicMock,
    ) -> None:
        """After load: is_loaded=True, is_running=False."""
        engine = MoonshineEngine(sample_config)
        engine.load()
        assert engine.is_loaded is True
        assert engine.is_running is False

    def test_state_after_start_stop(
        self,
        sample_config: MoonDictConfig,
        mock_get_model_for_language: MagicMock,
        mock_transcriber: MagicMock,
        mock_model_arch: MagicMock,
    ) -> None:
        """After start: is_running=True. After stop: is_running=False."""
        engine = MoonshineEngine(sample_config)
        engine.load()

        listener: TranscriptionListener = MagicMock()
        with patch("moondict.engine.moonshine.sd") as mock_sd:
            mock_sd.InputStream.return_value = MagicMock()
            engine.start(listener)
            assert engine.is_running is True

            engine.stop()
            assert engine.is_running is False

        assert engine.is_loaded is True  # load state preserved


class TestTranscriptEventListener:
    """Tests for TranscriptEventListener inner class."""

    def test_on_transcript_event_forwards_to_listener(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Listener forwards completed text to engine._listener."""
        engine = MoonshineEngine(sample_config)
        engine._listener = MagicMock()  # Simulate app's event bridge
        listener = TranscriptEventListener(engine)

        mock_line = MagicMock()
        mock_line.text = "hello world"
        mock_line.is_complete = True
        mock_event = MagicMock()
        mock_event.line = mock_line

        listener(mock_event)

        engine._listener.on_line_completed.assert_called_once_with("hello world")

    def test_on_transcript_event_ignores_incomplete(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Listener does NOT forward incomplete text."""
        engine = MoonshineEngine(sample_config)
        engine._listener = MagicMock()
        listener = TranscriptEventListener(engine)

        mock_line = MagicMock()
        mock_line.text = "partial"
        mock_line.is_complete = False
        mock_event = MagicMock()
        mock_event.line = mock_line

        listener(mock_event)

        engine._listener.on_line_completed.assert_not_called()

    def test_on_transcript_event_ignores_when_no_listener(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Listener does nothing when engine._listener is None."""
        engine = MoonshineEngine(sample_config)
        listener = TranscriptEventListener(engine)

        mock_line = MagicMock()
        mock_line.text = "hello"
        mock_line.is_complete = True
        mock_event = MagicMock()
        mock_event.line = mock_line

        # Should not raise
        listener(mock_event)
