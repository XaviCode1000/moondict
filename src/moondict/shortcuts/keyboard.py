"""Keyboard shortcut listener for MoonDict — push-to-talk and toggle modes."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from loguru import logger
from pynput.keyboard import Key, Listener

from moondict.config import ShortcutMode

if TYPE_CHECKING:
    from collections.abc import Callable

# Map config key strings to pynput Key enum values
# Each key maps to a tuple of all matching variants (left, right, generic)
_KEY_MAP: dict[str, tuple[Key, ...]] = {
    "ctrl": (Key.ctrl, Key.ctrl_l, Key.ctrl_r),
    "alt": (Key.alt, Key.alt_l, Key.alt_r),
    "shift": (Key.shift, Key.shift_l, Key.shift_r),
}

# Double-tap window in seconds
_DOUBLE_TAP_WINDOW = 0.5


class KeyboardListener:
    """Listens for keyboard shortcuts to control dictation.

    Supports two modes:
    - push_to_talk: hold key → start listening, release → stop
    - toggle: double-tap within 500ms → start/stop listening

    Callbacks run on pynput's internal listener thread.
    """

    def __init__(
        self,
        key: str,
        mode: ShortcutMode,
        on_press: Callable[[], None],
        on_release: Callable[[], None],
    ) -> None:
        """Initialize keyboard listener.

        Args:
            key: Config key name ("ctrl", "alt", "shift").
            mode: Shortcut mode ("push_to_talk" or "toggle").
            on_press: Callback invoked when dictation should start.
            on_release: Callback invoked when dictation should stop.
        """
        self._pynput_keys = _KEY_MAP[key]
        self._mode = mode
        self._on_press = on_press
        self._on_release = on_release
        self._listener: Listener | None = None
        self._last_tap_time: float = 0.0
        self._is_active: bool = False  # For toggle mode: are we currently "listening"?

    def start(self) -> None:
        """Start the keyboard listener in a background thread."""
        self._listener = Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self._listener.start()
        logger.info(
            "Keyboard listener started (key={}, mode={})", self._mode, self._pynput_keys
        )

    def stop(self) -> None:
        """Stop the keyboard listener."""
        if self._listener is None:
            logger.debug("Keyboard listener not running, nothing to stop")
            return

        self._listener.stop()
        self._listener = None
        logger.info("Keyboard listener stopped")

    def _on_key_press(self, key: Key, *_args: object) -> None:
        """Internal pynput callback for key press events.

        Args:
            key: The pynput Key that was pressed.
            *_args: Additional pynput event data (unused).
        """
        if key not in self._pynput_keys:
            return

        if self._mode == "push_to_talk":
            logger.debug("PTT key pressed")
            self._on_press()

        elif self._mode == "toggle":
            self._handle_toggle_press()

    def _on_key_release(self, key: Key, *_args: object) -> None:
        """Internal pynput callback for key release events.

        Args:
            key: The pynput Key that was released.
            *_args: Additional pynput event data (unused).
        """
        if key not in self._pynput_keys:
            return

        if self._mode == "push_to_talk":
            logger.debug("PTT key released")
            self._on_release()

        elif self._mode == "toggle":
            self._handle_toggle_release()

    def _handle_toggle_press(self) -> None:
        """Handle key press in toggle mode — no action on press alone."""
        # In toggle mode, we only act on release (to detect complete taps)
        pass

    def _handle_toggle_release(self) -> None:
        """Handle key release in toggle mode — detect double-tap."""
        now = time.time()
        elapsed = now - self._last_tap_time

        if elapsed <= _DOUBLE_TAP_WINDOW:
            # Double-tap detected
            if not self._is_active:
                logger.info("Toggle: double-tap detected → START listening")
                self._on_press()
                self._is_active = True
            else:
                logger.info("Toggle: double-tap detected → STOP listening")
                self._on_release()
                self._is_active = False
            # Reset tap time so next tap starts a new sequence
            self._last_tap_time = 0.0
        else:
            # First tap or too-slow second tap
            self._last_tap_time = now
