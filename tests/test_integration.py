"""Integration tests for MoonDictApp with TrayIndicator."""

from __future__ import annotations

import threading
from unittest.mock import MagicMock, patch

import pytest

from moondict.config import MoonDictConfig
from moondict.main import MoonDictApp
from moondict.state import DictationState


@pytest.fixture
def sample_config() -> MoonDictConfig:
    """Create a sample MoonDictConfig for tests."""
    return MoonDictConfig(
        engine="moonshine",
        model="base_es",
        language="es",
        shortcut_mode="push_to_talk",
        shortcut_key="ctrl",
        audio_device=None,
        sample_rate=16000,
        audio_feedback=False,
        text_injection="xdotool",
        copy_to_clipboard=False,
    )


@pytest.fixture
def mock_all_external_deps() -> dict[str, MagicMock]:
    """Mock all external dependencies."""
    with (
        patch("moondict.engine.moonshine.ModelArch") as mock_model,
        patch("moondict.engine.moonshine.Transcriber") as mock_transcriber,
        patch("moondict.engine.moonshine.get_model_for_language") as mock_get_model,
        patch("moondict.engine.moonshine.sd") as mock_engine_sd,
        patch("moondict.audio.capture.sd") as mock_capture_sd,
        patch("moondict.audio.feedback.sd") as mock_feedback_sd,
        patch("moondict.shortcuts.keyboard.Listener") as mock_keyboard,
        patch("moondict.tray.indicator.Icon") as mock_icon,
        patch("moondict.tray.indicator.Menu") as mock_menu,
        patch("moondict.tray.indicator.MenuItem") as mock_menu_item,
        patch("moondict.tray.indicator.notify") as mock_notify,
        patch("moondict.tray.indicator.Image") as mock_image,
        patch("moondict.injection.xdotool.subprocess.run") as mock_subprocess_run,
    ):
        # Setup mock get_model_for_language — returns (path, arch) tuple
        mock_get_model.return_value = ("/fake/model/path", mock_model)

        # Setup mock transcriber
        mock_transcriber_instance = MagicMock()
        mock_transcriber.return_value = mock_transcriber_instance

        # Setup mock audio for capture
        mock_capture_sd.query_devices.return_value = [
            {"name": "Default Device", "index": 0, "max_input_channels": 2},
        ]
        mock_capture_sd.default.device = (0, 0)

        # Setup mock keyboard
        mock_keyboard.return_value = MagicMock()

        # Setup mock tray icon
        icon_instance = MagicMock()
        stop_event = threading.Event()
        icon_instance.run = MagicMock(side_effect=lambda: stop_event.wait())
        icon_instance.stop = MagicMock(side_effect=lambda: stop_event.set())
        mock_icon.return_value = icon_instance

        # Setup mock menu items
        menu_items = []

        def create_menu_item(*args, **kwargs):
            item = MagicMock()
            item.text = args[0] if args else kwargs.get("text", "")
            item.action = args[1] if len(args) > 1 else kwargs.get("action")
            menu_items.append(item)
            return item

        mock_menu_item.side_effect = create_menu_item
        mock_menu.return_value = menu_items

        # Setup mock image
        mock_image_instance = MagicMock()
        mock_image.new.return_value = mock_image_instance

        # Setup mock subprocess for xdotool
        mock_subprocess_run.return_value = MagicMock(returncode=0)

        yield {
            "model": mock_model,
            "transcriber": mock_transcriber,
            "get_model": mock_get_model,
            "engine_sd": mock_engine_sd,
            "capture_sd": mock_capture_sd,
            "feedback_sd": mock_feedback_sd,
            "keyboard": mock_keyboard,
            "icon": mock_icon,
            "menu": mock_menu,
            "menu_item": mock_menu_item,
            "notify": mock_notify,
            "image": mock_image,
            "subprocess_run": mock_subprocess_run,
            "icon_instance": icon_instance,
            "menu_items": menu_items,
        }


class TestTrayIntegration:
    """Test tray integration with MoonDictApp."""

    def test_app_creates_tray_by_default(
        self, sample_config: MoonDictConfig, mock_all_external_deps: dict
    ) -> None:
        """MoonDictApp creates TrayIndicator when use_tray=True (default)."""
        app = MoonDictApp(sample_config)
        assert app.tray is not None
        app.stop()

    def test_app_skips_tray_when_disabled(
        self, sample_config: MoonDictConfig, mock_all_external_deps: dict
    ) -> None:
        """MoonDictApp does not create TrayIndicator when use_tray=False."""
        app = MoonDictApp(sample_config, use_tray=False)
        assert app.tray is None
        app.stop()

    def test_tray_start_called_on_app_start(
        self, sample_config: MoonDictConfig, mock_all_external_deps: dict
    ) -> None:
        """TrayIndicator.start() is called when app starts."""
        app = MoonDictApp(sample_config)
        app.start()

        mock_all_external_deps["icon"].assert_called()
        app.stop()

    def test_tray_state_matches_app_state_idle(
        self, sample_config: MoonDictConfig, mock_all_external_deps: dict
    ) -> None:
        """Tray state reflects app state (idle after start)."""
        app = MoonDictApp(sample_config)
        app.start()

        # After start, tray should be in idle state
        assert app.tray is not None
        assert app.tray._state == "idle"

        app.stop()

    def test_tray_state_matches_app_state_listening(
        self, sample_config: MoonDictConfig, mock_all_external_deps: dict
    ) -> None:
        """Tray state reflects app state (listening on key press)."""
        app = MoonDictApp(sample_config)
        app.start()

        # Simulate key press
        app._on_listening_start()

        assert app.tray is not None
        assert app.tray._state == "listening"
        assert app.state.is_state(DictationState.LISTENING)

        app.stop()

    def test_tray_state_matches_app_state_processing(
        self, sample_config: MoonDictConfig, mock_all_external_deps: dict
    ) -> None:
        """Tray state reflects app state (processing on key release)."""
        app = MoonDictApp(sample_config)
        app.start()

        # Simulate key press then release
        app._on_listening_start()
        app._on_listening_stop()

        assert app.tray is not None
        assert app.tray._state == "processing"
        assert app.state.is_state(DictationState.PROCESSING)

        app.stop()

    def test_notification_on_transcription_complete(
        self, sample_config: MoonDictConfig, mock_all_external_deps: dict
    ) -> None:
        """Notification is shown when transcription completes."""
        app = MoonDictApp(sample_config)
        app.start()

        # Simulate transcription
        app._on_transcription("Hello world")

        mock_all_external_deps["notify"].assert_called()
        app.stop()

    def test_notification_on_error(
        self, sample_config: MoonDictConfig, mock_all_external_deps: dict
    ) -> None:
        """Notification is shown when an error occurs."""
        app = MoonDictApp(sample_config)
        app.start()

        # Simulate error
        error = RuntimeError("Test error")
        app._on_error(error)

        mock_all_external_deps["notify"].assert_called()
        app.stop()

    def test_tray_stops_on_app_stop(
        self, sample_config: MoonDictConfig, mock_all_external_deps: dict
    ) -> None:
        """TrayIndicator.stop() is called when app stops."""
        app = MoonDictApp(sample_config)
        app.start()
        app.stop()

        mock_all_external_deps["icon_instance"].stop.assert_called()

    def test_no_tray_no_state_updates(
        self, sample_config: MoonDictConfig, mock_all_external_deps: dict
    ) -> None:
        """When tray is disabled, no state updates are attempted."""
        app = MoonDictApp(sample_config, use_tray=False)
        app.start()

        # Simulate state transitions
        app._on_listening_start()
        app._on_listening_stop()
        app._on_transcription("Test")

        # No icon should have been created
        mock_all_external_deps["icon"].assert_not_called()
        app.stop()
