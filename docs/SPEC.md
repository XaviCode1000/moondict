# MoonDict — Detailed Module Specification

## Overview

MoonDict is a voice dictation application for Linux using moonshine-voice for offline ASR.
Architecture follows Clean/Hexagonal patterns with feature modules.

**Thread model:**
- **Main thread (GTK/pystray event loop)**: UI, shortcuts, tray, orchestration
- **Moonshine background thread**: Audio capture + transcription (managed by MicTranscriber)
- **Communication**: `queue.Queue[str]` for transcribed text, `threading.Event` for state signals

---

## M1: Core funcional

### 1. `src/moondict/engine/moonshine.py` — MoonshineEngine Wrapper

#### Public API

```python
"""Moonshine ASR engine wrapper."""

from __future__ import annotations

from pathlib import Path
from typing import Callable
from queue import Queue

from loguru import logger

from moondict.config import MoonDictConfig


class TranscriptionError(Exception):
    """Raised when transcription fails."""


class MoonshineEngine:
    """Wrapper around moonshine-voice MicTranscriber.

    Manages the lifecycle of the MicTranscriber and provides
    a clean interface for the rest of the application.
    """

    def __init__(
        self,
        config: MoonDictConfig,
        on_transcription: Callable[[str], None] | None = None,
    ) -> None:
        """Initialize the Moonshine engine.

        Args:
            config: Application config with model/language settings.
            on_transcription: Callback invoked on each transcription result.
                              Called on the moonshine background thread.
        """

    def load(self) -> None:
        """Load the ASR model into memory.

        Must be called before start(). Downloads model if not present.

        Raises:
            TranscriptionError: If model fails to load.
        """

    def start(self) -> None:
        """Start listening to the microphone.

        Begins audio capture and streaming transcription.
        Results are delivered via on_transcription callback.

        Raises:
            TranscriptionError: If microphone is unavailable.
            RuntimeError: If called before load() or after stop().
        """

    def stop(self) -> None:
        """Stop listening and release microphone.

        Safe to call multiple times (idempotent).
        """

    @property
    def is_listening(self) -> bool:
        """Whether the engine is currently capturing audio."""

    @property
    def is_loaded(self) -> bool:
        """Whether the model has been loaded."""

    def unload(self) -> None:
        """Release model from memory. Optional cleanup."""
```

#### Behavior

- `__init__` stores config and callback, does NOT load model yet (lazy loading).
- `load()` creates the `MicTranscriber` with `model_path=config.models_dir`, sets language/model.
- `start()` calls `MicTranscriber.start()` — this spawns moonshine's internal audio thread.
- `stop()` calls `MicTranscriber.stop()` — blocks until thread joins.
- The `on_transcription` callback receives completed transcription strings.
- Empty transcriptions (silence) are filtered out — callback not invoked.

#### Dependencies

- `moonshine_voice` — `MicTranscriber`, `Transcriber` classes
- `loguru` — logging
- `moondict.config.MoonDictConfig` — configuration
- External: model files in `~/.local/share/moondict/models/`

#### Error handling

| Scenario | Behavior |
|----------|----------|
| Model not found at path | `TranscriptionError` with message, model auto-download attempt |
| No microphone | `TranscriptionError("No audio input device available")` |
| Model load fails (corrupt) | `TranscriptionError` wrapping underlying exception |
| start() before load() | `RuntimeError("Engine not loaded. Call load() first.")` |
| Double start() | `RuntimeError("Engine already listening.")` |

#### Thread safety

- `MoonshineEngine` methods are called from **main thread**.
- `on_transcription` callback fires on **moonshine's background thread**.
- Callback MUST not block. It should push to a `queue.Queue` or use `GLib.idle_add`/`pystray` main loop.
- `is_listening` and `is_loaded` are thread-safe (backed by `threading.Event`).

#### Test strategy

| Test | Mock |
|------|------|
| `test_load_downloads_model_if_missing` | `MicTranscriber` constructor |
| `test_start_starts_listening` | `MicTranscriber.start()` |
| `test_stop_stops_listening` | `MicTranscriber.stop()` |
| `test_callback_receives_transcription` | `MicTranscriber` with fake callback |
| `test_start_before_load_raises` | — |
| `test_double_start_raises` | Mock that tracks call count |
| `test_stop_is_idempotent` | — |

---

### 2. `src/moondict/audio/capture.py` — AudioCapture

#### Public API

```python
"""Microphone audio capture abstraction."""

from __future__ import annotations

from typing import Callable, Sequence

from loguru import logger


class AudioDevice:
    """Represents an available audio input device."""

    def __init__(self, index: int, name: str, is_default: bool = False) -> None: ...

    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...


class AudioCaptureError(Exception):
    """Raised when audio capture fails."""


class AudioCapture:
    """Manages microphone audio capture.

    Delegates actual capture to moonshine's MicTranscriber,
    but provides device enumeration and selection.
    """

    def __init__(self, sample_rate: int = 16000) -> None:
        """Initialize capture with target sample rate.

        Args:
            sample_rate: Target sample rate (must match ASR engine).
        """

    def list_devices(self) -> Sequence[AudioDevice]:
        """List available audio input devices.

        Returns:
            List of AudioDevice objects, default device first.

        Raises:
            AudioCaptureError: If PortAudio cannot enumerate devices.
        """

    def get_default_device(self) -> AudioDevice | None:
        """Get the system default audio input device.

        Returns:
            AudioDevice or None if no default exists.
        """

    def select_device(self, device_index: int) -> None:
        """Select a specific device for capture.

        Args:
            device_index: The device index from sounddevice.

        Raises:
            AudioCaptureError: If device index is invalid.
        """

    @property
    def selected_device(self) -> int | None:
        """Currently selected device index, or None for default."""
```

#### Behavior

- `list_devices()` wraps `sounddevice.query_devices()`, filters to input-only devices.
- `select_device()` validates the index exists before storing.
- This module does NOT do capture itself — moonshine's MicTranscriber handles it.
- It exists as a hexagonal port so we can swap audio backends if needed.

#### Dependencies

- `sounddevice` — `query_devices()`, `default.device`
- `loguru` — logging
- No dependency on moonshine (pure audio layer)

#### Error handling

| Scenario | Behavior |
|----------|----------|
| No audio devices | Returns empty list |
| Invalid device index | `AudioCaptureError("Device 5 not found")` |
| PortAudio init fails | `AudioCaptureError` wrapping PortAudio error |

#### Thread safety

- All methods are **main thread** only.
- Pure state management, no shared mutable state.

#### Test strategy

| Test | Mock |
|------|------|
| `test_list_devices_returns_input_only` | `sounddevice.query_devices` |
| `test_get_default_device` | `sounddevice.default.device` |
| `test_select_device_valid` | `sounddevice.query_devices` |
| `test_select_device_invalid_raises` | — |
| `test_no_devices_returns_empty` | `sounddevice.query_devices` returning empty |

---

### 3. `src/moondict/audio/feedback.py` — AudioFeedback

#### Public API

```python
"""Audio feedback sounds for user confirmation."""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from moondict.config import MoonDictConfig


class FeedbackError(Exception):
    """Raised when audio feedback cannot be played."""


class AudioFeedback:
    """Plays short WAV sounds for user feedback."""

    def __init__(self, config: MoonDictConfig) -> None:
        """Initialize audio feedback.

        Args:
            config: Application config (audio_feedback toggle).
        """

    def play_start(self) -> None:
        """Play the 'recording started' sound.

        No-op if audio_feedback is disabled in config.
        """

    def play_end(self) -> None:
        """Play the 'recording ended, text injected' sound.

        No-op if audio_feedback is disabled in config.
        """

    def play_error(self) -> None:
        """Play the 'error occurred' sound.

        No-op if audio_feedback is disabled in config.
        """
```

#### Behavior

- Loads WAV files from `resources/sounds/` at init time.
- Sound files: `start.wav`, `end.wav`, `error.wav`.
- Uses `simpleaudio` or `sounddevice.play()` for playback (non-blocking).
- If `config.audio_feedback` is `False`, all play methods are no-ops.
- If sound file is missing, logs warning and skips (does NOT crash).
- Playback is fire-and-forget — does not wait for completion.

#### Dependencies

- `sounddevice` — for playback (already a dependency)
  OR `simpleaudio` — if added as optional dep
- `numpy` — for loading WAV data
- `loguru` — logging
- Resources: `resources/sounds/start.wav`, `end.wav`, `error.wav`

#### Error handling

| Scenario | Behavior |
|----------|----------|
| Sound file missing | Log warning, skip playback |
| No audio output device | Log warning, skip playback |
| Config disabled | Silent no-op |

#### Thread safety

- Play methods can be called from **any thread**.
- Playback runs on sounddevice's internal thread.
- No shared mutable state.

#### Test strategy

| Test | Mock |
|------|------|
| `test_play_start_plays_sound` | `sounddevice.play` |
| `test_play_start_noop_when_disabled` | Config with `audio_feedback=False` |
| `test_play_missing_file_logs_warning` | Missing WAV file path |
| `test_play_error_sound` | `sounddevice.play` |

---

### 4. `src/moondict/main.py` — MoonDictApp (Orchestrator)

#### Public API

```python
"""Main application orchestrator."""

from __future__ import annotations

import threading
from enum import Enum, auto
from queue import Queue

from loguru import logger

from moondict.config import MoonDictConfig
from moondict.engine.moonshine import MoonshineEngine
from moondict.audio.feedback import AudioFeedback
from moondict.injection.xdotool import TextInjector
from moondict.shortcuts.keyboard import ShortcutListener


class AppState(Enum):
    """Application state machine."""
    IDLE = auto()
    LISTENING = auto()
    PROCESSING = auto()
    ERROR = auto()


class MoonDictApp:
    """Main application controller.

    Orchestrates engine, shortcuts, injection, and feedback.
    Runs on the main thread. State transitions are event-driven.
    """

    def __init__(self, config: MoonDictConfig) -> None:
        """Initialize all components.

        Does NOT start anything. Call run() to begin.
        """

    def run(self) -> None:
        """Start the application.

        Loads engine, registers shortcuts, starts event loop.
        Blocks until quit() is called.
        """

    def quit(self) -> None:
        """Gracefully shut down the application.

        Stops engine, unregisters shortcuts, exits event loop.
        """

    def on_shortcut_pressed(self) -> None:
        """Handle shortcut press (push-to-talk start).

        Called by ShortcutListener on the main thread.
        """

    def on_shortcut_released(self) -> None:
        """Handle shortcut release (push-to-talk stop).

        Triggers transcription and text injection.
        Called by ShortcutListener on the main thread.
        """

    def on_toggle_activated(self) -> None:
        """Handle toggle shortcut (toggle mode).

        Starts if idle, stops if listening.
        """

    def _on_transcription(self, text: str) -> None:
        """Handle transcription result from engine.

        Called on moonshine's background thread.
        Pushes text to main thread via queue.
        """

    def _process_transcription(self, text: str) -> None:
        """Inject transcribed text into the focused field.

        Runs on main thread. Plays feedback, injects text.
        """

    @property
    def state(self) -> AppState:
        """Current application state."""
```

#### Behavior

**State machine:**
```
IDLE ──[shortcut pressed]──▶ LISTENING ──[shortcut released]──▶ PROCESSING
       [toggle]                                                    │
                                                                   ▼
IDLE ◀──[injection complete]───────────────────────────────────────┘
  │
  └──[error]──▶ ERROR ──[recovery]──▶ IDLE
```

**Startup sequence in `run()`:**
1. Configure loguru with `config.log_level`
2. Create `AudioCapture`, `MoonshineEngine`, `AudioFeedback`, `TextInjector`, `ShortcutListener`
3. Call `engine.load()`
4. Register shortcut callbacks
5. Start shortcut listener (blocking event loop for pystray/pynput)

**Push-to-talk flow:**
1. User presses Ctrl → `on_shortcut_pressed()` → `engine.start()` + `feedback.play_start()` → state=LISTENING
2. User speaks → moonshine streams transcription → `_on_transcription(text)` queues result
3. User releases Ctrl → `engine.stop()` → state=PROCESSING
4. `_process_transcription(text)` → `feedback.play_end()` → `injector.inject(text)` → state=IDLE

**Toggle mode flow:**
1. User double-taps Ctrl → `on_toggle_activated()` → start listening
2. User double-taps again → stop listening, process result

#### Dependencies

- All feature modules (engine, audio, injection, shortcuts)
- `queue.Queue` — cross-thread communication
- `threading.Event` — state signaling
- `loguru` — logging

#### Error handling

| Scenario | Behavior |
|----------|----------|
| Engine load fails | Log error, set state=ERROR, show notification, quit |
| Transcription empty | Skip injection, return to IDLE |
| Injection fails | Log error, copy to clipboard as fallback, `feedback.play_error()` |
| Shortcut registration fails | Log error, continue without shortcuts (tray only) |

#### Thread safety

- `MoonDictApp` runs on **main thread** (pystray/pynput event loop).
- `_on_transcription` is called on **moonshine's background thread** — it MUST NOT call engine/injection directly. Instead, it puts text in a `Queue` and signals the main loop.
- Main loop processes queue via periodic check or callback marshaling.
- State transitions use `threading.Lock` for safety.

#### Test strategy

| Test | Mock |
|------|------|
| `test_run_initializes_all_components` | All component constructors |
| `test_shortcut_press_starts_listening` | `MoonshineEngine.start` |
| `test_shortcut_release_stops_and_injects` | `MoonshineEngine.stop`, `TextInjector.inject` |
| `test_toggle_mode_starts_and_stops` | Engine start/stop |
| `test_empty_transcription_skips_injection` | Engine returning empty string |
| `test_injection_fallback_to_clipboard` | `TextInjector` raising error |
| `test_quit_stops_everything` | All stop methods |
| `test_state_transitions` | State machine |

---

### 5. `src/moondict/__main__.py` — CLI Entry Point

#### Public API

```python
"""CLI entry point for MoonDict."""

from __future__ import annotations

import sys


def main() -> None:
    """Entry point for the `moondict` command.

    Parses CLI arguments, loads config, creates MoonDictApp, runs it.
    Handles top-level exceptions.
    """
```

#### Behavior

1. Parse CLI args with `argparse`:
   - `--config PATH` — override config file location
   - `--version` — print version and exit
   - `--no-tray` — run without system tray (CLI-only mode)
   - `--verbose` — set log level to DEBUG
2. Load `MoonDictConfig` from `~/.config/moondict/config.json`
3. Create `MoonDictApp(config)`
4. Call `app.run()`
5. Catch `KeyboardInterrupt` → clean exit
6. Catch `Exception` → log critical, exit code 1

#### Dependencies

- `argparse` (stdlib)
- `moondict.config.MoonDictConfig`
- `moondict.main.MoonDictApp`
- `moondict.__version__`
- `loguru` — for top-level error logging

#### Error handling

| Scenario | Behavior |
|----------|----------|
| Config file invalid JSON | Log error, create default config, continue |
| Config file missing | Create default config at `~/.config/moondict/config.json` |
| Unhandled exception | Log critical with traceback, exit 1 |
| KeyboardInterrupt | Exit 0 silently |

#### Thread safety

- Runs entirely on **main thread**.
- No shared state.

#### Test strategy

| Test | Mock |
|------|------|
| `test_main_runs_app` | `MoonDictApp.run` |
| `test_main_handles_keyboard_interrupt` | `MoonDictApp.run` raising KeyboardInterrupt |
| `test_main_handles_exception` | `MoonDictApp.run` raising Exception |
| `test_main_version_flag` | `sys.argv` with `--version` |
| `test_main_creates_config_if_missing` | Missing config file |

---

## M2: Dictation completo

### 6. `src/moondict/shortcuts/keyboard.py` — ShortcutListener

#### Public API

```python
"""Global keyboard shortcut listener."""

from __future__ import annotations

from typing import Callable

from loguru import logger

from moondict.config import MoonDictConfig, ShortcutMode


class ShortcutError(Exception):
    """Raised when shortcut registration fails."""


class ShortcutListener:
    """Listens for global keyboard shortcuts.

    Supports push-to-talk (hold key) and toggle (double-tap) modes.
    Uses pynput for cross-desktop global hotkey detection.
    """

    def __init__(
        self,
        config: MoonDictConfig,
        on_press: Callable[[], None],
        on_release: Callable[[], None],
        on_toggle: Callable[[], None],
    ) -> None:
        """Initialize shortcut listener.

        Args:
            config: Application config with shortcut_key and shortcut_mode.
            on_press: Called when shortcut key is pressed (push-to-talk).
            on_release: Called when shortcut key is released (push-to-talk).
            on_toggle: Called on each toggle activation (toggle mode).
        """

    def start(self) -> None:
        """Start listening for global shortcuts.

        Blocks until stop() is called. Should be run in a thread
        or as part of the main event loop.

        Raises:
            ShortcutError: If global shortcut cannot be registered.
        """

    def stop(self) -> None:
        """Stop listening for shortcuts.

        Safe to call multiple times (idempotent).
        """

    @property
    def is_running(self) -> bool:
        """Whether the listener is currently active."""
```

#### Behavior

**Push-to-talk mode (`shortcut_mode = "push_to_talk"`):**
- Uses `pynput.keyboard.Listener` with `on_press` and `on_release`.
- Detects when `config.shortcut_key` (ctrl/alt/shift) is held down.
- `on_press` fires immediately on key down.
- `on_release` fires on key up.
- Does NOT suppress the key (user can still use Ctrl+C etc.).

**Toggle mode (`shortcut_mode = "toggle"`):**
- Uses `pynput.keyboard.GlobalHotKeys` for a combo like `<ctrl>+<ctrl>` or `<ctrl>+d`.
- Each activation fires `on_toggle`.
- The app toggles between listening and idle.

**Key mapping:**
```python
_KEY_MAP: dict[str, pynput.keyboard.Key] = {
    "ctrl": pynput.keyboard.Key.ctrl,
    "alt": pynput.keyboard.Key.alt,
    "shift": pynput.keyboard.Key.shift,
}
```

#### Dependencies

- `pynput.keyboard` — `Listener`, `Key`, `GlobalHotKeys`, `KeyCode`
- `loguru` — logging
- `moondict.config` — `MoonDictConfig`, `ShortcutMode`

#### Error handling

| Scenario | Behavior |
|----------|----------|
| No X11 display (Wayland) | `ShortcutError("pynput requires X11 for global hotkeys")` |
| Key already grabbed by WM | `ShortcutError("Shortcut already in use")` |
| Double start | `RuntimeError("Listener already running")` |

#### Thread safety

- `start()` blocks — should be called from a **dedicated thread** or the main event loop.
- Callbacks (`on_press`, `on_release`, `on_toggle`) fire on **pynput's listener thread**.
- Callbacks MUST be thread-safe (push to queue or use main-loop marshaling).
- `stop()` is thread-safe — can be called from any thread.

#### Test strategy

| Test | Mock |
|------|------|
| `test_push_to_talk_press_calls_on_press` | `pynput.keyboard.Listener` with fake press |
| `test_push_to_talk_release_calls_on_release` | `pynput.keyboard.Listener` with fake release |
| `test_toggle_mode_calls_on_toggle` | `pynput.keyboard.GlobalHotKeys` |
| `test_stop_is_idempotent` | — |
| `test_start_without_x11_raises` | Mock pynput raising Display error |
| `test_listener_ignores_other_keys` | Fake events for non-shortcut keys |

---

### 7. `src/moondict/injection/xdotool.py` — TextInjector

#### Public API

```python
"""Text injection into the focused application."""

from __future__ import annotations

import subprocess
from pathlib import Path

from loguru import logger


class InjectionError(Exception):
    """Raised when text injection fails."""


class TextInjector:
    """Injects text at the current cursor position.

    Primary backend: xdotool (X11 only).
    Fallback: clipboard (copy to clipboard, notify user).
    """

    def __init__(
        self,
        use_clipboard_fallback: bool = True,
        xdotool_path: str = "xdotool",
    ) -> None:
        """Initialize text injector.

        Args:
            use_clipboard_fallback: If True, copies to clipboard on xdotool failure.
            xdotool_path: Path to xdotool binary.
        """

    def inject(self, text: str) -> None:
        """Inject text at the current cursor position.

        Uses xdotool type for ASCII, Unicode clipboard paste for special chars.

        Args:
            text: The text to inject.

        Raises:
            InjectionError: If injection fails and clipboard fallback also fails.
        """

    def copy_to_clipboard(self, text: str) -> None:
        """Copy text to the system clipboard.

        Uses xclip or wl-clipboard.

        Args:
            text: The text to copy.

        Raises:
            InjectionError: If no clipboard utility is available.
        """
```

#### Behavior

**Injection strategy:**
1. Check if text contains non-ASCII characters (tildes, ñ, etc.)
2. If ASCII-only → `xdotool type --delay 1 --clearmodifiers 'text'`
3. If Unicode → copy to clipboard via `xclip -selection clipboard`, then `xdotool key ctrl+v`
4. If xdotool fails → try clipboard fallback (copy + notify)

**Command construction:**
```bash
# ASCII injection
xdotool type --delay 1 --clearmodifiers 'Hello world'

# Unicode injection (two-step)
echo -n 'María tomó café' | xclip -selection clipboard
xdotool key ctrl+v
```

**Unicode detection:**
```python
def _has_unicode(text: str) -> bool:
    return any(ord(c) > 127 for c in text)
```

#### Dependencies

- `subprocess` (stdlib) — `run()`, `CalledProcessError`
- `shutil` (stdlib) — `which()`
- `loguru` — logging
- External: `xdotool`, `xclip` (system packages, not Python deps)

#### Error handling

| Scenario | Behavior |
|----------|----------|
| xdotool not installed | `InjectionError("xdotool not found. Install it: sudo apt install xdotool")` |
| No X11 display | `InjectionError("No X11 display available")` |
| xdotool type fails | Try clipboard fallback |
| Clipboard fallback also fails | `InjectionError` with both errors |
| Empty text | No-op (does not run xdotool) |
| Text with newlines | Replace with spaces (xdotool can't type newlines) |

#### Thread safety

- All methods are **main thread** only.
- `subprocess.run` is blocking but fast (< 100ms).
- No shared mutable state.

#### Test strategy

| Test | Mock |
|------|------|
| `test_inject_ascii_calls_xdotool` | `subprocess.run` |
| `test_inject_unicode_uses_clipboard` | `subprocess.run` |
| `test_inject_empty_text_noop` | — |
| `test_inject_newlines_replaced_with_spaces` | `subprocess.run` |
| `test_xdotool_not_found_raises` | `shutil.which` returning None |
| `test_clipboard_fallback_on_failure` | `subprocess.run` side_effect=CalledProcessError |
| `test_copy_to_clipboard_uses_xclip` | `subprocess.run` |

---

## M3: UX completa

### 8. `src/moondict/tray/indicator.py` — TrayIndicator

#### Public API

```python
"""System tray icon and menu."""

from __future__ import annotations

from typing import Callable

import pystray
from PIL import Image
from loguru import logger

from moondict.main import AppState


class TrayIndicator:
    """System tray icon with context menu.

    Displays different icons based on app state.
    Provides menu items for common actions.
    """

    def __init__(
        self,
        on_quit: Callable[[], None],
        on_toggle_mode: Callable[[], None] | None = None,
        on_settings: Callable[[], None] | None = None,
    ) -> None:
        """Initialize tray indicator.

        Args:
            on_quit: Called when user selects 'Quit' from menu.
            on_toggle_mode: Called when user toggles push-to-talk/toggle mode.
            on_settings: Called when user opens settings.
        """

    def run(self) -> None:
        """Show the tray icon and start the event loop.

        Blocks until stop() is called.
        """

    def stop(self) -> None:
        """Hide the tray icon and stop the event loop."""

    def update_state(self, state: AppState) -> None:
        """Update the tray icon to reflect the current app state.

        Args:
            state: The current AppState (IDLE, LISTENING, PROCESSING, ERROR).
        """

    def update_tooltip(self, text: str) -> None:
        """Update the tray icon tooltip text.

        Args:
            text: The tooltip text.
        """

    def notify(self, title: str, message: str) -> None:
        """Show a system notification.

        Args:
            title: Notification title.
            message: Notification body.
        """
```

#### Behavior

**Icons per state:**
- `IDLE` → gray microphone icon (`resources/icons/mic-idle.png`)
- `LISTENING` → red microphone icon (`resources/icons/mic-listening.png`)
- `PROCESSING` → spinning/loading icon (`resources/icons/mic-processing.png`)
- `ERROR` → error icon (`resources/icons/mic-error.png`)

**Context menu:**
```
MoonDict v0.1.0          (disabled, title)
─────────────────
Toggle Mode: Push-to-Talk  (clickable, toggles to "Toggle")
Settings                   (clickable, opens settings — future)
─────────────────
Quit                       (clickable, exits app)
```

**Notifications:**
- Uses `pystray`'s built-in `notify()` method (maps to libnotify on Linux).
- `notify(title, message)` → shows desktop notification.
- If notify not supported (e.g., no notification daemon), logs warning.

**Event loop:**
- `pystray.Icon.run()` blocks and processes menu events.
- State updates use `icon.update_menu()` to refresh.

#### Dependencies

- `pystray` — `Icon`, `Menu`, `MenuItem`
- `PIL.Image` — loading icon images
- `loguru` — logging
- `moondict.main.AppState` — state enum
- Resources: `resources/icons/mic-*.png` (32x32 PNG)

#### Error handling

| Scenario | Behavior |
|----------|----------|
| No system tray available | Log warning, continue without tray (CLI mode) |
| Icon file missing | Use fallback (create simple colored square via PIL) |
| Notification daemon unavailable | Log warning, skip notification |
| Menu action fails | Log error, continue |

#### Thread safety

- `pystray.Icon.run()` runs on its **own thread** (separate from main).
- `update_state()` and `update_tooltip()` must be called via `icon.update_menu()` which is thread-safe in pystray.
- Use `pystray`'s thread-safe `update_menu()` pattern:
  ```python
  self._icon.update_menu()
  ```

#### Test strategy

| Test | Mock |
|------|------|
| `test_run_creates_icon` | `pystray.Icon` |
| `test_update_state_changes_icon` | Mock icon with state tracking |
| `test_quit_menu_item_calls_callback` | Mock menu action |
| `test_notify_shows_notification` | `pystray.Icon.notify` |
| `test_missing_icon_uses_fallback` | Missing PNG file |
| `test_stop_removes_icon` | `pystray.Icon.remove` |

---

## Tests

### `tests/test_config.py`

```python
"""Tests for moondict.config.MoonDictConfig."""
```

| Test | What it verifies |
|------|-----------------|
| `test_default_config` | Default values are correct (language=es, mode=push_to_talk, etc.) |
| `test_config_from_env` | Environment variables override defaults (`MOONDICT_LANGUAGE=en`) |
| `test_config_from_file` | JSON config file is loaded correctly |
| `test_config_file_not_found_uses_defaults` | Missing config file → defaults |
| `test_config_invalid_json_raises` | Malformed JSON raises ValidationError |
| `test_config_models_dir_default` | `models_dir` points to `~/.local/share/moondict/models` |
| `test_config_serializable` | `config.model_dump_json()` produces valid JSON |

---

### `tests/test_engine.py`

```python
"""Tests for moondict.engine.moonshine.MoonshineEngine."""
```

| Test | What it verifies |
|------|-----------------|
| `test_load_initializes_transcriber` | `MicTranscriber` is created with correct model path |
| `test_load_model_not_found_downloads` | Missing model triggers download |
| `test_start_starts_listening` | `MicTranscriber.start()` called, `is_listening=True` |
| `test_stop_stops_listening` | `MicTranscriber.stop()` called, `is_listening=False` |
| `test_start_before_load_raises` | `RuntimeError` raised |
| `test_double_start_raises` | `RuntimeError` raised |
| `test_stop_is_idempotent` | Multiple stops don't raise |
| `test_callback_receives_text` | `on_transcription` called with transcribed string |
| `test_callback_ignores_empty` | Empty string does not trigger callback |
| `test_unload_releases_model` | `is_loaded=False` after unload |

---

### `tests/test_capture.py`

```python
"""Tests for moondict.audio.capture.AudioCapture."""
```

| Test | What it verifies |
|------|-----------------|
| `test_list_devices_returns_input_only` | Output devices filtered out |
| `test_list_devices_empty` | No devices → empty list |
| `test_get_default_device` | Returns default or None |
| `test_select_device_valid` | Device index stored correctly |
| `test_select_device_invalid_raises` | `AudioCaptureError` raised |
| `test_selected_device_none_by_default` | No device selected initially |

---

### `tests/test_feedback.py`

```python
"""Tests for moondict.audio.feedback.AudioFeedback."""
```

| Test | What it verifies |
|------|-----------------|
| `test_play_start_when_enabled` | `sounddevice.play` called with start.wav data |
| `test_play_start_when_disabled` | No sounddevice call |
| `test_play_end` | `sounddevice.play` called with end.wav data |
| `test_play_error` | `sounddevice.play` called with error.wav data |
| `test_missing_sound_file_logs_warning` | Warning logged, no exception |
| `test_play_does_not_block` | Returns immediately (fire-and-forget) |

---

### `tests/test_keyboard.py`

```python
"""Tests for moondict.shortcuts.keyboard.ShortcutListener."""
```

| Test | What it verifies |
|------|-----------------|
| `test_push_to_talk_press` | `on_press` called when shortcut key pressed |
| `test_push_to_talk_release` | `on