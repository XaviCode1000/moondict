"""Acceptance E2E tests for MoonDict.

Tests the complete user flow with all external dependencies mocked:
start app → press key → speak → transcribe → inject → stop

These tests verify critical paths only — state transitions, text flow
through the pipeline, and notification delivery.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from moondict.main import MoonDictApp
from moondict.state import DictationState

# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def fully_mocked_app():
    """Create MoonDictApp with ALL external dependencies mocked.

    This fixture mocks:
    - Engine (MoonshineEngine)
    - Audio capture
    - Audio feedback (play_sound)
    - Keyboard listener
    - Tray indicator
    - Text injection (xdotool)
    """
    import numpy as np

    config = MagicMock()
    config.audio_feedback = True
    config.shortcut_key = "ctrl"
    config.shortcut_mode = "push_to_talk"
    config.sample_rate = 16000

    engine = MagicMock()
    engine.transcribe.return_value = "transcribed text from engine"

    # Audio capture returns fake audio data
    capture = MagicMock()
    fake_audio = MagicMock()
    fake_audio.audio_data = np.zeros(16000, dtype=np.float32)  # 1 sec silence
    fake_audio.sample_rate = 16000
    capture.record.return_value = fake_audio

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
        app = MoonDictApp(config)
        yield {
            "app": app,
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


# ─── E2E Flow Tests ─────────────────────────────────────────────────────────


class TestFullDictationFlow:
    """E2E tests for the complete dictation workflow."""

    def test_e2e_full_cycle_idle_to_idle(self, fully_mocked_app):
        """Full E2E: IDLE → start → press key → LISTENING → release → PROCESSING → transcribe → IDLE."""
        ctx = fully_mocked_app
        app = ctx["app"]

        # Verify initial state
        assert app.state.current_state == DictationState.IDLE

        # Simulate user pressing key (start listening)
        app._on_listening_start()
        assert app.state.current_state == DictationState.LISTENING
        ctx["play_sound"].assert_called_with("start", enabled=True)

        # Simulate user releasing key (stop listening, start processing)
        app._on_listening_stop()
        assert app.state.current_state == DictationState.PROCESSING
        # Engine keeps running to finish processing buffered audio

        # Simulate transcription result
        test_text = "Hola, esto es una prueba de dictado"
        ctx["inject"].return_value = True
        app._on_transcription(test_text)
        assert app.state.current_state == DictationState.IDLE

        # Verify text was injected
        ctx["inject"].assert_called_once_with(test_text)

        # Verify stop sound played
        ctx["play_sound"].assert_any_call("stop", enabled=True)

    def test_e2e_text_flows_through_pipeline(self, fully_mocked_app):
        """Verify transcribed text flows: engine → app → injection."""
        ctx = fully_mocked_app
        app = ctx["app"]

        # Simulate dictation cycle
        app._on_listening_start()
        app._on_listening_stop()

        # Text from "engine" to injection
        expected_text = "El veloz murciélago hindú comía feliz cardillo y kiwi"
        ctx["inject"].return_value = True
        app._on_transcription(expected_text)

        ctx["inject"].assert_called_once_with(expected_text)

    def test_e2e_notifications_sent(self, fully_mocked_app):
        """Verify notification sounds are sent at each state transition."""
        ctx = fully_mocked_app
        app = ctx["app"]

        # Start listening → start sound
        app._on_listening_start()
        ctx["play_sound"].assert_called_with("start", enabled=True)

        # Transcription complete → stop sound
        ctx["inject"].return_value = True
        app._on_transcription("test")
        ctx["play_sound"].assert_any_call("stop", enabled=True)

    def test_e2e_error_recovery(self, fully_mocked_app):
        """E2E: error during dictation should transition to ERROR, then recover to IDLE."""
        ctx = fully_mocked_app
        app = ctx["app"]

        # Start listening
        app._on_listening_start()
        assert app.state.current_state == DictationState.LISTENING

        # Simulate error
        app._on_error(RuntimeError("mic disconnected"))
        assert app.state.current_state == DictationState.ERROR
        ctx["play_sound"].assert_called_with("error", enabled=True)

        # Recovery
        app.state.transition_to(DictationState.IDLE)
        assert app.state.current_state == DictationState.IDLE

    def test_e2e_injection_failure_doesnt_crash(self, fully_mocked_app):
        """E2E: if text injection fails, app should still return to IDLE."""
        ctx = fully_mocked_app
        app = ctx["app"]

        app._on_listening_start()
        app._on_listening_stop()

        # Injection fails
        ctx["inject"].return_value = False
        app._on_transcription("this text will fail to inject")

        # Should still be IDLE
        assert app.state.current_state == DictationState.IDLE

    def test_e2e_app_start_stop_lifecycle(self, fully_mocked_app):
        """E2E: full app start/stop lifecycle."""
        ctx = fully_mocked_app
        app = ctx["app"]

        # Start app
        app.start()
        ctx["engine"].load.assert_called_once()
        ctx["capture"].start.assert_called_once()
        ctx["keyboard"].start.assert_called_once()

        # Stop app
        app.stop()
        ctx["engine"].stop.assert_called_once()
        ctx["capture"].stop.assert_called_once()
        ctx["keyboard"].stop.assert_called_once()
        ctx["tray"].stop.assert_called_once()

    def test_e2e_dictation_while_running(self, fully_mocked_app):
        """E2E: perform dictation cycle while app is running."""
        ctx = fully_mocked_app
        app = ctx["app"]

        # Start the app
        app.start()

        # Perform dictation
        app._on_listening_start()
        assert app.state.current_state == DictationState.LISTENING

        app._on_listening_stop()
        assert app.state.current_state == DictationState.PROCESSING

        ctx["inject"].return_value = True
        app._on_transcription("dictated while running")
        assert app.state.current_state == DictationState.IDLE

        # Stop the app
        app.stop()

    def test_e2e_state_transitions_are_valid(self, fully_mocked_app):
        """Verify all state transitions in a full cycle follow the state machine rules."""
        ctx = fully_mocked_app
        app = ctx["app"]

        expected_sequence = [
            DictationState.IDLE,
            DictationState.LISTENING,
            DictationState.PROCESSING,
            DictationState.IDLE,
        ]

        actual_sequence: list[DictationState] = [app.state.current_state]

        app._on_listening_start()
        actual_sequence.append(app.state.current_state)

        app._on_listening_stop()
        actual_sequence.append(app.state.current_state)

        ctx["inject"].return_value = True
        app._on_transcription("test")
        actual_sequence.append(app.state.current_state)

        assert actual_sequence == expected_sequence

    def test_e2e_multiple_consecutive_dictations(self, fully_mocked_app):
        """E2E: perform multiple dictation cycles in a row."""
        ctx = fully_mocked_app
        app = ctx["app"]
        ctx["inject"].return_value = True

        for i in range(3):
            app._on_listening_start()
            assert app.state.current_state == DictationState.LISTENING

            app._on_listening_stop()
            assert app.state.current_state == DictationState.PROCESSING

            app._on_transcription(f"dictation number {i + 1}")
            assert app.state.current_state == DictationState.IDLE

        assert ctx["inject"].call_count == 3

    def test_e2e_empty_transcription_handled(self, fully_mocked_app):
        """E2E: empty transcription result should still complete the cycle."""
        ctx = fully_mocked_app
        app = ctx["app"]

        app._on_listening_start()
        app._on_listening_stop()

        ctx["inject"].return_value = True
        app._on_transcription("")

        assert app.state.current_state == DictationState.IDLE
        ctx["inject"].assert_called_once_with("")
