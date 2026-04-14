"""Moonshine ASR engine implementation."""

from __future__ import annotations

import queue
import threading
from typing import TYPE_CHECKING

import numpy as np  # Runtime usage in callback
import sounddevice as sd
from loguru import logger
from moonshine_voice import ModelArch, Transcriber, get_model_for_language

from moondict.engine.interface import (
    EngineLoadError,
    EngineStartError,
    TranscriberEngine,
    TranscriptionListener,
)

if TYPE_CHECKING:
    from moondict.config import MoonDictConfig


class TranscriptEventListener:
    """Callback adapter that bridges Moonshine events to the engine queue.

    Receives TranscriptEvent callbacks from the Moonshine transcriber stream
    and puts the transcribed text into a thread-safe queue for the application.
    Implements __call__ to be used as a callable listener.
    """

    def __init__(self, engine: MoonshineEngine) -> None:
        self._engine = engine

    def __call__(self, event: object) -> None:
        """Handle a transcription event from the Moonshine transcriber.

        Args:
            event: TranscriptEvent with line, stream_handle fields.
        """
        text = getattr(getattr(event, "line", None), "text", "")
        if text:
            is_complete = getattr(getattr(event, "line", None), "is_complete", False)
            logger.debug("Transcription event: '{}' (complete={})", text, is_complete)
            if is_complete and self._engine._listener is not None:
                # Forward directly to the app's event bridge
                self._engine._listener.on_line_completed(text)


class MoonshineEngine(TranscriberEngine):
    """Moonshine-based speech-to-text engine.

    Manages the lifecycle of the Moonshine ASR model and audio capture:
    - Loads the Spanish model via get_model_for_language("es")
    - Creates a Transcriber with a custom stream for sounddevice integration
    - Opens a sounddevice InputStream for audio capture
    - Uses a thread-safe queue.Queue for event delivery
    - Uses threading.Event for state management
    """

    UPDATE_INTERVAL = 0.5  # seconds between transcription updates

    def __init__(self, config: MoonDictConfig) -> None:
        """Initialize engine with configuration.

        Args:
            config: MoonDictConfig with language, model, and audio settings.
        """
        self._config = config
        self._queue: queue.Queue[str] = queue.Queue()
        self._loaded_event = threading.Event()
        self._running_event = threading.Event()
        self._stream: sd.InputStream | None = None
        self._transcriber: Transcriber | None = None
        self._mic_stream: object | None = None  # moonshine_voice Stream
        self._model: ModelArch | None = None
        self._listener: TranscriptionListener | None = None

    def load(self) -> None:
        """Load the Moonshine Spanish model and create the transcriber.

        Raises:
            EngineLoadError: If model download or transcriber init fails.
        """
        if self._loaded_event.is_set():
            logger.debug("Model already loaded, skipping")
            return

        logger.info("Loading Moonshine model for language: {}", self._config.language)

        try:
            model_path, model_arch = get_model_for_language(self._config.language)
            self._model_path = model_path
            self._model_arch = model_arch
        except Exception as exc:
            logger.error("Failed to load model: {}", exc)
            raise EngineLoadError(f"Model load failed: {exc}") from exc

        try:
            self._transcriber = Transcriber(self._model_path, self._model_arch)
        except Exception as exc:
            logger.error("Failed to initialize transcriber: {}", exc)
            raise EngineLoadError(f"Transcriber init failed: {exc}") from exc

        self._loaded_event.set()
        logger.info("Moonshine model loaded successfully")

    def start(self, listener: TranscriptionListener) -> None:
        """Start audio capture and attach the transcription listener.

        Args:
            listener: Callback receiver for transcription results.

        Raises:
            EngineLoadError: If start() is called before load().
            EngineStartError: If the audio stream cannot be opened.
        """
        if not self._loaded_event.is_set():
            raise EngineLoadError("Engine must be loaded before starting")

        if self._running_event.is_set():
            logger.debug("Engine already running, skipping")
            return

        self._listener = listener
        callback_handler = TranscriptEventListener(self)

        if self._transcriber is None:
            raise EngineLoadError("Transcriber not initialized")

        # Create a custom stream for sounddevice integration
        # (not the default stream — that's for mic_transcriber only)
        self._mic_stream = self._transcriber.create_stream(
            update_interval=self.UPDATE_INTERVAL
        )
        self._mic_stream.add_listener(callback_handler)
        self._mic_stream.start()

        try:
            self._stream = sd.InputStream(
                samplerate=self._config.sample_rate,
                channels=1,
                dtype="float32",
                blocksize=1024,
                callback=self._audio_callback,
            )
            self._stream.start()
        except Exception as exc:
            logger.error("Failed to start audio stream: {}", exc)
            # Cleanup mic stream on failure
            try:
                self._mic_stream.stop()
                self._mic_stream = None
            except Exception:
                pass
            raise EngineStartError(f"Stream open failed: {exc}") from exc

        self._running_event.set()
        logger.info("Audio capture started")

    def stop(self) -> None:
        """Stop audio capture and release resources."""
        if not self._running_event.is_set():
            logger.debug("Engine not running, nothing to stop")
            return

        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception as exc:
                logger.warning("Error closing stream: {}", exc)
            self._stream = None

        if self._mic_stream:
            try:
                self._mic_stream.stop()
            except Exception as exc:
                logger.warning("Error stopping mic stream: {}", exc)
            self._mic_stream = None

        self._running_event.clear()
        logger.info("Audio capture stopped")

    @property
    def is_loaded(self) -> bool:
        """Whether the model has been successfully loaded."""
        return self._loaded_event.is_set()

    @property
    def is_running(self) -> bool:
        """Whether the engine is currently capturing audio."""
        return self._running_event.is_set()

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info: dict[str, object],
        status: sd.CallbackFlags,
    ) -> None:
        """Process incoming audio data through the transcriber stream.

        Args:
            indata: Audio buffer as numpy array.
            frames: Number of frames in the buffer.
            time_info: Timing information from sounddevice.
            status: Stream status flags.
        """
        if status:
            logger.debug("Audio stream status: {}", status)

        if self._mic_stream is not None:
            try:
                audio_list = indata.flatten().tolist()
                self._mic_stream.add_audio(audio_list, sample_rate=16000)
            except Exception as exc:
                logger.error("Transcription error: {}", exc)
