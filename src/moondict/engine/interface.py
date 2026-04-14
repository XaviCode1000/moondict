"""Abstract engine interface for MoonDict ASR backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol


class TranscriptionListener(Protocol):
    """Protocol for objects that receive transcription events."""

    def on_line_completed(self, text: str) -> None:
        """Called when a complete transcription line is ready.

        Args:
            text: The transcribed text.
        """
        ...


class TranscriberEngine(ABC):
    """Abstract base for speech-to-text engine implementations.

    Defines the lifecycle (load, start, stop) and event callback
    mechanism that all ASR backends must implement.
    """

    @abstractmethod
    def load(self) -> None:
        """Load the ASR model and initialize internal state.

        Raises:
            EngineLoadError: If model loading fails.
        """

    @abstractmethod
    def start(self, listener: TranscriptionListener) -> None:
        """Start listening for audio input.

        Args:
            listener: Callback receiver for transcription results.

        Raises:
            EngineStartError: If audio stream cannot be opened.
        """

    @abstractmethod
    def stop(self) -> None:
        """Stop listening and release audio resources."""

    @property
    @abstractmethod
    def is_loaded(self) -> bool:
        """Whether the model has been successfully loaded."""

    @property
    @abstractmethod
    def is_running(self) -> bool:
        """Whether the engine is currently capturing audio."""


class EngineError(Exception):
    """Base exception for engine-related errors."""


class EngineLoadError(EngineError):
    """Raised when the ASR model fails to load."""


class EngineStartError(EngineError):
    """Raised when the audio stream fails to start."""
