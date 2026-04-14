"""Tests for MoonDict entry point (__main__)."""

from __future__ import annotations

import signal
from unittest.mock import MagicMock, patch

import pytest

from moondict.__main__ import _create_signal_handler, main


@pytest.fixture
def mock_app():
    """Create a mocked MoonDictApp for entry point tests."""
    with (
        patch("moondict.__main__.MoonDictConfig") as mock_config_cls,
        patch("moondict.__main__.MoonDictApp") as mock_app_cls,
        patch("moondict.__main__.signal.signal"),
    ):
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app
        mock_config = mock_config_cls.return_value

        yield {
            "config": mock_config,
            "app": mock_app,
            "config_cls": mock_config_cls,
            "app_cls": mock_app_cls,
        }


class TestMainEntryPoint:
    """Tests for the main() entry point function."""

    def test_main_creates_config(self, mock_app):
        """main() should create a MoonDictConfig instance."""
        with patch("sys.argv", ["moondict"]):
            main()

        mock_app["config_cls"].assert_called_once()

    def test_main_creates_app(self, mock_app):
        """main() should create a MoonDictApp with config and use_tray=True."""
        with patch("sys.argv", ["moondict"]):
            main()

        mock_app["app_cls"].assert_called_once_with(mock_app["config"], use_tray=True)

    def test_main_starts_app(self, mock_app):
        """main() should call app.start()."""
        with patch("sys.argv", ["moondict"]):
            main()

        mock_app["app"].start.assert_called_once()

    def test_main_registers_signal_handlers(self, mock_app):
        """main() should register SIGINT and SIGTERM handlers."""
        with patch("moondict.__main__.signal.signal") as mock_signal:
            with patch("sys.argv", ["moondict"]):
                main()

            assert mock_signal.call_count == 2
            mock_signal.assert_any_call(
                signal.SIGINT, mock_signal.call_args_list[0][0][1]
            )
            mock_signal.assert_any_call(
                signal.SIGTERM, mock_signal.call_args_list[1][0][1]
            )


class TestMainCliFlags:
    """Tests for CLI argument handling."""

    def test_push_to_talk_flag(self, mock_app):
        """--push-to-talk should set shortcut_mode to push_to_talk."""
        with patch("sys.argv", ["moondict", "--push-to-talk"]):
            main()

        assert mock_app["config"].shortcut_mode == "push_to_talk"

    def test_toggle_flag(self, mock_app):
        """--toggle should set shortcut_mode to toggle."""
        with patch("sys.argv", ["moondict", "--toggle"]):
            main()

        assert mock_app["config"].shortcut_mode == "toggle"

    def test_device_flag(self, mock_app):
        """--device should set audio_device."""
        with patch("sys.argv", ["moondict", "--device", "2"]):
            main()

        assert mock_app["config"].audio_device == 2

    def test_model_flag(self, mock_app):
        """--model should set model."""
        with patch("sys.argv", ["moondict", "--model", "base_es"]):
            main()

        assert mock_app["config"].model == "base_es"

    def test_no_tray_flag(self, mock_app):
        """--no-tray should set use_tray=False."""
        with patch("sys.argv", ["moondict", "--no-tray"]):
            main()

        mock_app["app_cls"].assert_called_once_with(mock_app["config"], use_tray=False)

    def test_no_flags_uses_defaults(self, mock_app):
        """No flags should use config defaults."""
        with patch("sys.argv", ["moondict"]):
            main()

        mock_app["config_cls"].assert_called_once()


class TestSignalHandler:
    """Tests for signal handler behavior."""

    def test_signal_handler_calls_stop(self):
        """SIGINT handler should call app.stop()."""
        app = MagicMock()
        handler = _create_signal_handler(app)

        with patch("moondict.__main__.sys.exit"):
            handler(signal.SIGINT, None)

        app.stop.assert_called_once()

    def test_signal_handler_calls_exit(self):
        """SIGINT handler should call sys.exit(0)."""
        app = MagicMock()
        handler = _create_signal_handler(app)

        with patch("moondict.__main__.sys.exit") as mock_exit:
            handler(signal.SIGTERM, None)

            mock_exit.assert_called_once_with(0)
