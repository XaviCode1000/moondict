"""Tests for keyboard shortcut listener (push-to-talk and toggle modes)."""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest
from pynput.keyboard import Key

from moondict.shortcuts.keyboard import KeyboardListener


@pytest.fixture
def mock_listener_class():
    """Mock pynput.keyboard.Listener for all tests."""
    with patch("moondict.shortcuts.keyboard.Listener") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        yield mock_cls, mock_instance


class TestKeyboardListenerPTT:
    """Push-to-talk mode tests."""

    def test_ptt_press_triggers_on_press_callback(self, mock_listener_class):
        """Pressing the key in PTT mode calls on_press callback."""
        mock_cls, _ = mock_listener_class
        on_press = MagicMock()
        on_release = MagicMock()

        listener = KeyboardListener(
            key="ctrl",
            mode="push_to_talk",
            on_press=on_press,
            on_release=on_release,
        )
        listener.start()

        constructor_kwargs = mock_cls.call_args.kwargs
        callback_on_press = constructor_kwargs["on_press"]

        callback_on_press(Key.ctrl, None)

        on_press.assert_called_once()
        on_release.assert_not_called()

    def test_ptt_release_triggers_on_release_callback(self, mock_listener_class):
        """Releasing the key in PTT mode calls on_release callback."""
        mock_cls, _ = mock_listener_class
        on_press = MagicMock()
        on_release = MagicMock()

        listener = KeyboardListener(
            key="ctrl",
            mode="push_to_talk",
            on_press=on_press,
            on_release=on_release,
        )
        listener.start()

        constructor_kwargs = mock_cls.call_args.kwargs
        callback_on_release = constructor_kwargs["on_release"]

        callback_on_release(Key.ctrl, None)

        on_release.assert_called_once()
        on_press.assert_not_called()

    def test_ptt_press_release_sequence(self, mock_listener_class):
        """Full PTT cycle: press → on_press, release → on_release."""
        mock_cls, _ = mock_listener_class
        on_press = MagicMock()
        on_release = MagicMock()

        listener = KeyboardListener(
            key="ctrl",
            mode="push_to_talk",
            on_press=on_press,
            on_release=on_release,
        )
        listener.start()

        constructor_kwargs = mock_cls.call_args.kwargs
        on_press_cb = constructor_kwargs["on_press"]
        on_release_cb = constructor_kwargs["on_release"]

        on_press_cb(Key.ctrl, None)
        on_press.assert_called_once()
        on_release.assert_not_called()

        on_release_cb(Key.ctrl, None)
        on_release.assert_called_once()


class TestKeyboardListenerToggle:
    """Toggle mode tests (double-tap detection)."""

    def test_toggle_single_tap_no_callback(self, mock_listener_class):
        """A single tap in toggle mode should NOT trigger any callback."""
        mock_cls, _ = mock_listener_class
        on_press = MagicMock()
        on_release = MagicMock()

        listener = KeyboardListener(
            key="ctrl",
            mode="toggle",
            on_press=on_press,
            on_release=on_release,
        )
        listener.start()

        constructor_kwargs = mock_cls.call_args.kwargs
        on_press_cb = constructor_kwargs["on_press"]
        on_release_cb = constructor_kwargs["on_release"]

        on_press_cb(Key.ctrl, None)
        on_release_cb(Key.ctrl, None)

        on_press.assert_not_called()
        on_release.assert_not_called()

    def _do_double_tap(self, on_press_cb, on_release_cb):
        """Simulate a double-tap: two quick press+release cycles."""
        on_press_cb(Key.ctrl, None)
        on_release_cb(Key.ctrl, None)
        on_press_cb(Key.ctrl, None)
        on_release_cb(Key.ctrl, None)

    def test_toggle_double_tap_triggers_callbacks(self, mock_listener_class):
        """Double tap within 500ms triggers on_press (start listening)."""
        mock_cls, _ = mock_listener_class
        on_press = MagicMock()
        on_release = MagicMock()

        listener = KeyboardListener(
            key="ctrl",
            mode="toggle",
            on_press=on_press,
            on_release=on_release,
        )
        listener.start()

        constructor_kwargs = mock_cls.call_args.kwargs
        on_press_cb = constructor_kwargs["on_press"]
        on_release_cb = constructor_kwargs["on_release"]

        self._do_double_tap(on_press_cb, on_release_cb)

        on_press.assert_called_once()
        on_release.assert_not_called()

    def test_toggle_double_tap_to_stop(self, mock_listener_class):
        """Second double-tap triggers on_release (stop listening)."""
        mock_cls, _ = mock_listener_class
        on_press = MagicMock()
        on_release = MagicMock()

        listener = KeyboardListener(
            key="ctrl",
            mode="toggle",
            on_press=on_press,
            on_release=on_release,
        )
        listener.start()

        constructor_kwargs = mock_cls.call_args.kwargs
        on_press_cb = constructor_kwargs["on_press"]
        on_release_cb = constructor_kwargs["on_release"]

        self._do_double_tap(on_press_cb, on_release_cb)
        on_press.assert_called_once()
        on_release.assert_not_called()

        self._do_double_tap(on_press_cb, on_release_cb)
        assert on_press.call_count == 1
        on_release.assert_called_once()

    def test_toggle_double_tap_too_slow_no_trigger(self, mock_listener_class):
        """Two taps separated by >500ms should NOT trigger."""
        mock_cls, _ = mock_listener_class
        on_press = MagicMock()
        on_release = MagicMock()

        listener = KeyboardListener(
            key="ctrl",
            mode="toggle",
            on_press=on_press,
            on_release=on_release,
        )
        listener.start()

        constructor_kwargs = mock_cls.call_args.kwargs
        on_press_cb = constructor_kwargs["on_press"]
        on_release_cb = constructor_kwargs["on_release"]

        on_press_cb(Key.ctrl, None)
        on_release_cb(Key.ctrl, None)

        listener._last_tap_time = time.time() - 1.0

        on_press_cb(Key.ctrl, None)
        on_release_cb(Key.ctrl, None)

        on_press.assert_not_called()
        on_release.assert_not_called()


class TestKeyboardListenerLifecycle:
    """Start/stop lifecycle tests."""

    def test_start_creates_pynput_listener(self, mock_listener_class):
        """start() creates a pynput Listener instance."""
        mock_cls, mock_instance = mock_listener_class
        listener = KeyboardListener(
            key="ctrl",
            mode="push_to_talk",
            on_press=MagicMock(),
            on_release=MagicMock(),
        )
        listener.start()

        mock_cls.assert_called_once()
        mock_instance.start.assert_called_once()

    def test_stop_stops_listener(self, mock_listener_class):
        """stop() stops the pynput Listener."""
        _, mock_instance = mock_listener_class
        listener = KeyboardListener(
            key="ctrl",
            mode="push_to_talk",
            on_press=MagicMock(),
            on_release=MagicMock(),
        )
        listener.start()
        listener.stop()

        mock_instance.stop.assert_called_once()

    def test_stop_when_not_running_is_safe(self, mock_listener_class):
        """stop() on a non-started listener does not raise."""
        _, mock_instance = mock_listener_class
        listener = KeyboardListener(
            key="ctrl",
            mode="push_to_talk",
            on_press=MagicMock(),
            on_release=MagicMock(),
        )
        listener.stop()
        mock_instance.stop.assert_not_called()

    def test_key_mapping_ctrl(self, mock_listener_class):
        """Key 'ctrl' maps to pynput Key.ctrl."""
        mock_cls, _ = mock_listener_class
        listener = KeyboardListener(
            key="ctrl",
            mode="push_to_talk",
            on_press=MagicMock(),
            on_release=MagicMock(),
        )
        listener.start()

        assert mock_cls.call_args.kwargs["on_press"] is not None
        assert mock_cls.call_args.kwargs["on_release"] is not None

    def test_key_mapping_alt(self, mock_listener_class):
        """Key 'alt' maps to pynput Key.alt."""
        mock_cls, _ = mock_listener_class
        listener = KeyboardListener(
            key="alt",
            mode="push_to_talk",
            on_press=MagicMock(),
            on_release=MagicMock(),
        )
        listener.start()

        mock_cls.assert_called_once()

    def test_key_mapping_shift(self, mock_listener_class):
        """Key 'shift' maps to pynput Key.shift."""
        mock_cls, _ = mock_listener_class
        listener = KeyboardListener(
            key="shift",
            mode="push_to_talk",
            on_press=MagicMock(),
            on_release=MagicMock(),
        )
        listener.start()

        mock_cls.assert_called_once()
