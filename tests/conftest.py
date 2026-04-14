"""Pytest fixtures with mocks for MoonDict external dependencies."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_model_arch() -> MagicMock:
    """Mock ModelArch enum from moonshine-voice."""
    with patch("moondict.engine.moonshine.ModelArch") as mock:
        mock.base_es = MagicMock()
        yield mock


@pytest.fixture
def mock_transcriber() -> MagicMock:
    """Mock Transcriber class from moonshine-voice."""
    with patch("moondict.engine.moonshine.Transcriber") as mock:
        instance = MagicMock()
        mock.return_value = instance
        yield mock


@pytest.fixture
def mock_get_model_for_language() -> MagicMock:
    """Mock get_model_for_language from moonshine_voice.

    Returns a tuple of (model_path_str, model_arch_mock) matching the real API.
    """
    with patch("moondict.engine.moonshine.get_model_for_language") as mock:
        mock.return_value = ("/fake/model/path", MagicMock())
        yield mock


@pytest.fixture
def mock_sounddevice() -> MagicMock:
    """Mock sounddevice module."""
    with patch("moondict.audio.capture.sd") as mock_sd:
        mock_sd.query_devices.return_value = [
            {"name": "Default Device", "index": 0, "max_input_channels": 2},
            {"name": "USB Microphone", "index": 1, "max_input_channels": 1},
        ]
        mock_sd.default.device = (0, 0)
        yield mock_sd


@pytest.fixture
def mock_sounddevice_playback() -> MagicMock:
    """Mock sounddevice module for playback (feedback)."""
    with patch("moondict.audio.feedback.sd") as mock_sd:
        yield mock_sd


@pytest.fixture
def mock_simpleaudio() -> MagicMock:
    """Mock simpleaudio module."""
    with patch("moondict.audio.feedback.sa") as mock_sa:
        mock_instance = MagicMock()
        mock_sa.play_buffer.return_value = mock_instance
        yield mock_sa


@pytest.fixture
def mock_pynput_keyboard() -> MagicMock:
    """Mock pynput.keyboard.Listener."""
    with patch("moondict.shortcuts.handler.keyboard.Listener") as mock:
        instance = MagicMock()
        mock.return_value = instance
        yield mock


@pytest.fixture
def mock_pynput_mouse() -> MagicMock:
    """Mock pynput.mouse.Listener."""
    with patch("moondict.shortcuts.handler.mouse.Listener") as mock:
        instance = MagicMock()
        mock.return_value = instance
        yield mock


@pytest.fixture
def mock_pystray() -> MagicMock:
    """Mock pystray.Icon and MenuItem."""
    with (
        patch("moondict.tray.manager.Icon") as mock_icon,
        patch("moondict.tray.manager.MenuItem") as mock_item,
    ):
        icon_instance = MagicMock()
        mock_icon.return_value = icon_instance
        yield mock_icon, mock_item


@pytest.fixture
def sample_config():
    """Create a sample MoonDictConfig for tests."""
    from moondict.config import MoonDictConfig

    return MoonDictConfig(
        engine="moonshine",
        model="base_es",
        language="es",
        shortcut_mode="push_to_talk",
        shortcut_key="ctrl",
        audio_device=None,
        sample_rate=16000,
        audio_feedback=True,
        text_injection="xdotool",
        copy_to_clipboard=False,
    )
