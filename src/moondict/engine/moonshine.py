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

    Receives line-by-line transcription results from the Moonshine transcriber
    and puts them into a thread-safe queue for the application to consume.
    """

    def __init__(self, engine: MoonshineEngine) -> None:
        self._engine = engine

    def on_line_completed(self, text: str) -> None:
        """Put transcribed text into the engine's queue.

        Args:
            text: The transcribed text line.
        """
        logger.debug("Transcription received: {}", text)
        self._engine._queue.put(text)


class MoonshineEngine(TranscriberEngine):
    """Moonshine-based speech-to-text engine.

    Manages the lifecycle of the Moonshine ASR model and audio capture:
    - Loads the Spanish model via get_model_for_language("es")
    - Creates a Transcriber instance for real-time transcription
    - Opens a sounddevice InputStream for audio capture
    - Uses a thread-safe queue.Queue for event delivery
    - Uses threading.Event for state management
    """

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
            self._model = get_model_for_language(self._config.language)
        except Exception as exc:
            logger.error("Failed to load model: {}", exc)
            raise EngineLoadError(f"Model load failed: {exc}") from exc

        try:
            self._transcriber = Transcriber(self._model)
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
            raise EngineStartError(f"Stream open failed: {exc}") from exc

        # Attach listener to transcriber
        if self._transcriber:
            self._transcriber.add_listener(callback_handler)

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
        """Process incoming audio data through the transcriber.

        Args:
            indata: Audio buffer as numpy array.
            frames: Number of frames in the buffer.
            time_info: Timing information from sounddevice.
            status: Stream status flags.
        """
        if status:
            logger.debug("Audio stream status: {}", status)

        if self._transcriber is not None:
            try:
                self._transcriber.process(indata)
            except Exception as exc:
                logger.error("Transcription error: {}", exc)
