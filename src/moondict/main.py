"""MoonDictApp orchestrator — wires all components into a cohesive application."""

from __future__ import annotations

import queue
import threading

from loguru import logger

from moondict.audio.capture import AudioCapture
from moondict.audio.feedback import play_sound
from moondict.config import MoonDictConfig
from moondict.engine.moonshine import MoonshineEngine
from moondict.injection.xdotool import inject_text
from moondict.shortcuts.keyboard import KeyboardListener
from moondict.state import DictationState, StateMachine
from moondict.tray.indicator import TrayIndicator


class MoonDictApp:
    """Main application orchestrator for MoonDict.

    Wires together the ASR engine, audio capture, keyboard shortcuts,
    text injection, audio feedback, and system tray into a cohesive dictation system.

    Thread safety:
    - Engine events (transcriptions) arrive on pynput's internal thread.
    - They are queued via queue.Queue and processed on a background thread.
    - State transitions are protected by StateMachine's internal lock.
    """

    def __init__(self, config: MoonDictConfig, use_tray: bool = True) -> None:
        """Initialize MoonDictApp with configuration.

        Args:
            config: Application configuration (engine, audio, shortcuts, etc.).
            use_tray: Whether to enable the system tray indicator.
        """
        self._config = config
        self._feedback_enabled = config.audio_feedback

        # Core components
        self._engine = MoonshineEngine(config)
        self._capture = AudioCapture(config)
        self._state = StateMachine()

        # Event queue for engine → background thread communication
        self._event_queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self._event_thread: threading.Thread | None = None
        self._running = False

        # Keyboard listener (created with callback methods)
        self._keyboard = KeyboardListener(
            key=config.shortcut_key,
            mode=config.shortcut_mode,
            on_press=self._on_listening_start,
            on_release=self._on_listening_stop,
        )

        # Tray indicator (optional)
        self._tray: TrayIndicator | None = None
        if use_tray:
            self._tray = TrayIndicator(self)

        logger.info(
            "MoonDictApp initialized (mode={}, key={}, tray={})",
            config.shortcut_mode,
            config.shortcut_key,
            use_tray,
        )

    @property
    def state(self) -> StateMachine:
        """Access the internal state machine (for testing)."""
        return self._state

    @property
    def tray(self) -> TrayIndicator | None:
        """Access the tray indicator (for testing)."""
        return self._tray

    def start(self) -> None:
        """Start the application: load engine, start capture, start keyboard listener.

        Non-blocking: starts a background event loop thread.
        """
        logger.info("Starting MoonDict...")
        self._running = True

        # Update tray state
        if self._tray is not None:
            self._tray.set_state("loading")

        try:
            self._engine.load()
        except Exception as exc:
            logger.error("Failed to load engine: {}", exc)
            self._on_error(exc)
            return

        try:
            self._capture.start()
        except Exception as exc:
            logger.error("Failed to start audio capture: {}", exc)
            self._on_error(exc)
            return

        self._keyboard.start()

        # Attach a listener to the engine to receive transcriptions
        self._engine.start(_EngineEventBridge(self._event_queue))

        # Start background event loop thread
        self._event_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._event_thread.start()

        # Update tray state to idle
        if self._tray is not None:
            self._tray.set_state("idle")
            self._tray.start()

        logger.info("MoonDict started successfully")

    def stop(self) -> None:
        """Stop all components and cleanup."""
        logger.info("Stopping MoonDict...")
        self._running = False

        self._keyboard.stop()
        self._engine.stop()
        self._capture.stop()

        # Signal the event loop to exit
        self._event_queue.put(("shutdown", None))

        # Wait for event thread to finish
        if self._event_thread is not None:
            self._event_thread.join(timeout=3.0)

        # Stop tray
        if self._tray is not None:
            self._tray.stop()

        logger.info("MoonDict stopped")

    def _on_listening_start(self) -> None:
        """Callback: user triggered dictation start (keyboard press / double-tap).

        Plays start sound and transitions to LISTENING state.
        """
        logger.info("Dictation start triggered")
        play_sound("start", enabled=self._feedback_enabled)
        self._state.transition_to(DictationState.LISTENING)

        # Update tray state
        if self._tray is not None:
            self._tray.set_state("listening")

    def _on_listening_stop(self) -> None:
        """Callback: user triggered dictation stop (keyboard release / double-tap).

        Stops the engine's audio capture and transitions to PROCESSING state.
        """
        logger.info("Dictation stop triggered")
        self._engine.stop()
        self._state.transition_to(DictationState.PROCESSING)

        # Update tray state
        if self._tray is not None:
            self._tray.set_state("processing")

    def _on_transcription(self, text: str) -> None:
        """Process a completed transcription.

        Injects the text into the focused window, plays stop sound,
        and transitions back to IDLE.

        Args:
            text: The transcribed text to inject.
        """
        logger.info("Transcription received: {!r}", text[:80])

        success = inject_text(text)
        if not success:
            logger.warning("Failed to inject text: {!r}", text[:80])

        play_sound("stop", enabled=self._feedback_enabled)
        self._state.transition_to(DictationState.IDLE)

        # Update tray state
        if self._tray is not None:
            self._tray.set_state("idle")
            self._tray.show_notification("Transcription complete", text[:100])

    def _on_error(self, error: Exception) -> None:
        """Handle an error during dictation.

        Logs the error, plays error sound, and transitions to ERROR state.

        Args:
            error: The exception that occurred.
        """
        logger.error("Dictation error: {}", error)
        play_sound("error", enabled=self._feedback_enabled)
        self._state.transition_to(DictationState.ERROR)

        # Update tray state
        if self._tray is not None:
            self._tray.set_state("error")
            self._tray.show_notification("Dictation error", str(error)[:100])

    def _run_event_loop(self) -> None:
        """Background event loop — processes engine events.

        Runs on a daemon thread until a "shutdown" event is received.
        """
        logger.debug("Event loop started")

        while self._running:
            try:
                event_type, payload = self._event_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            if event_type == "shutdown":
                logger.debug("Shutdown event received, exiting event loop")
                break

            if event_type == "transcription":
                self._on_transcription(str(payload))
            elif event_type == "error":
                self._on_error(payload)  # type: ignore[arg-type]

        logger.debug("Event loop exited")


class _EngineEventBridge:
    """Adapter that bridges engine transcription events to the app's event queue.

    The engine runs on its own thread; this bridge puts events into a
    thread-safe queue for the background event loop to process.
    """

    def __init__(self, event_queue: queue.Queue[tuple[str, object]]) -> None:
        """Initialize bridge with the app's event queue.

        Args:
            event_queue: Queue for sending events to the event loop.
        """
        self._queue = event_queue

    def on_line_completed(self, text: str) -> None:
        """Forward a transcription result to the event queue.

        Args:
            text: The transcribed text.
        """
        self._queue.put(("transcription", text))
