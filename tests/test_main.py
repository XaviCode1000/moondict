"""Tests for MoonDictApp orchestrator."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from moondict.main import MoonDictApp
from moondict.state import DictationState


@pytest.fixture
def mocked_app():
    """Create MoonDictApp with all dependencies mocked."""
    config = MagicMock()
    config.audio_feedback = True
    config.shortcut_key = "ctrl"
    config.shortcut_mode = "push_to_talk"

    engine = MagicMock()
    capture = MagicMock()
    keyboard = MagicMock()
    tray = MagicMock()

    with (
        patch("moondict.main.MoonshineEngine", return_value=engine) as mock_engine_cls,
        patch("moondict.main.AudioCapture", return_value=capture) as mock_capture_cls,
        patch(
            "moondict.main.KeyboardListener", return_value=keyboard
        ) as mock_keyboard_cls,
        patch("moondict.main.TrayIndicator", return_value=tray) as mock_tray_cls,
        patch("moondict.main.inject_text") as mock_inject,
        patch("moondict.main.play_sound") as mock_play,
    ):
        yield {
            "config": config,
            "engine": engine,
            "capture": capture,
            "keyboard": keyboard,
            "tray": tray,
            "inject": mock_inject,
            "play_sound": mock_play,
            "engine_cls": mock_engine_cls,
            "capture_cls": mock_capture_cls,
            "keyboard_cls": mock_keyboard_cls,
            "tray_cls": mock_tray_cls,
        }


class TestMoonDictAppLifecycle:
    """Tests for MoonDictApp start/stop lifecycle."""

    def test_app_creation(self, mocked_app):
        """App should initialize all components."""
        app = MoonDictApp(mocked_app["config"])
        assert app is not None

    def test_start_loads_engine(self, mocked_app):
        """start() should load the engine."""
        app = MoonDictApp(mocked_app["config"])
        app.start()

        mocked_app["engine"].load.assert_called_once()

    def test_start_starts_capture(self, mocked_app):
        """start() should start audio capture."""
        app = MoonDictApp(mocked_app["config"])
        app.start()

        mocked_app["capture"].start.assert_called_once()

    def test_start_starts_keyboard_listener(self, mocked_app):
        """start() should start the keyboard listener."""
        app = MoonDictApp(mocked_app["config"])
        app.start()

        mocked_app["keyboard"].start.assert_called_once()

    def test_stop_stops_all_components(self, mocked_app):
        """stop() should stop engine, capture, and keyboard."""
        app = MoonDictApp(mocked_app["config"])
        app.start()
        app.stop()

        mocked_app["engine"].stop.assert_called_once()
        mocked_app["capture"].stop.assert_called_once()
        mocked_app["keyboard"].stop.assert_called_once()
        mocked_app["tray"].stop.assert_called_once()

    def test_stop_without_start_is_safe(self, mocked_app):
        """stop() without start() should not raise."""
        app = MoonDictApp(mocked_app["config"])
        app.stop()

    def test_initial_state_is_idle(self, mocked_app):
        """App should start in IDLE state."""
        app = MoonDictApp(mocked_app["config"])
        assert app.state.current_state == DictationState.IDLE

    def test_on_listening_start_transitions_to_listening(self, mocked_app):
        """_on_listening_start should transition to LISTENING and play sound."""
        app = MoonDictApp(mocked_app["config"])
        app._on_listening_start()

        assert app.state.current_state == DictationState.LISTENING
        mocked_app["play_sound"].assert_called_once_with("start", enabled=True)

    def test_on_listening_stop_transitions_to_processing(self, mocked_app):
        """_on_listening_stop should transition to PROCESSING (engine keeps running)."""
        app = MoonDictApp(mocked_app["config"])
        app._on_listening_start()
        app._on_listening_stop()

        # Engine should NOT be stopped — it needs to finish processing buffered audio
        mocked_app["engine"].stop.assert_not_called()
        assert app.state.current_state == DictationState.PROCESSING

    def test_full_dictation_cycle(self, mocked_app):
        """Full cycle: IDLE → LISTENING → PROCESSING → IDLE."""
        app = MoonDictApp(mocked_app["config"])
        mocked_app["inject"].return_value = True

        app._on_listening_start()
        assert app.state.current_state == DictationState.LISTENING

        app._on_listening_stop()
        assert app.state.current_state == DictationState.PROCESSING

        app._on_transcription("hello world")
        assert app.state.current_state == DictationState.IDLE

        mocked_app["play_sound"].assert_any_call("start", enabled=True)
        mocked_app["play_sound"].assert_any_call("stop", enabled=True)
        mocked_app["inject"].assert_called_once_with("hello world")

    def test_on_transcription_injects_and_recovers(self, mocked_app):
        """_on_transcription should inject text, play stop sound, recover to IDLE."""
        app = MoonDictApp(mocked_app["config"])
        mocked_app["inject"].return_value = True

        app._on_transcription("hello world")

        mocked_app["inject"].assert_called_once_with("hello world")
        mocked_app["play_sound"].assert_called_with("stop", enabled=True)
        assert app.state.current_state == DictationState.IDLE

    def test_on_error_transitions_to_error(self, mocked_app):
        """_on_error should log and transition to ERROR."""
        app = MoonDictApp(mocked_app["config"])
        error = RuntimeError("test error")

        app._on_error(error)

        assert app.state.current_state == DictationState.ERROR
        mocked_app["play_sound"].assert_called_with("error", enabled=True)


class TestMoonDictAppErrorRecovery:
    """Tests for error handling and recovery."""

    def test_error_recovery_returns_to_idle(self, mocked_app):
        """After error, app should be able to recover to IDLE."""
        app = MoonDictApp(mocked_app["config"])
        app._on_error(RuntimeError("test"))
        assert app.state.current_state == DictationState.ERROR

        app.state.transition_to(DictationState.IDLE)
        assert app.state.current_state == DictationState.IDLE

    def test_transcription_failure_doesnt_crash(self, mocked_app):
        """If injection fails, app should still transition to IDLE."""
        app = MoonDictApp(mocked_app["config"])
        mocked_app["inject"].return_value = False

        app._on_transcription("hello")

        assert app.state.current_state == DictationState.IDLE


class TestMoonDictAppWiring:
    """Tests for correct dependency wiring."""

    def test_keyboard_listener_receives_correct_callbacks(self, mocked_app):
        """KeyboardListener should be created with app's callback methods."""
        app = MoonDictApp(mocked_app["config"])

        mocked_app["keyboard_cls"].assert_called_once()
        call_kwargs = mocked_app["keyboard_cls"].call_args.kwargs
        assert call_kwargs["key"] == mocked_app["config"].shortcut_key
        assert call_kwargs["mode"] == mocked_app["config"].shortcut_mode
        assert call_kwargs["on_press"] == app._on_listening_start
        assert call_kwargs["on_release"] == app._on_listening_stop
