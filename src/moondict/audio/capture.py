"""Audio capture module for MoonDict."""

from __future__ import annotations

import queue

import numpy as np  # Runtime usage in callback
import sounddevice as sd
from loguru import logger
from sounddevice import PortAudioError

from moondict.config import MoonDictConfig


class AudioCaptureError(Exception):
    """Base exception for audio capture errors."""


class DeviceNotFoundError(AudioCaptureError):
    """Raised when the requested audio device is not found."""


class StreamOpenError(AudioCaptureError):
    """Raised when the audio stream cannot be opened."""


class AudioCapture:
    """Manages raw audio input capture via sounddevice.

    Opens an InputStream at 16kHz, mono, float32 and delivers
    audio blocks through a thread-safe queue.Queue.
    """

    SAMPLE_RATE = 16000
    CHANNELS = 1
    DTYPE = "float32"
    BLOCKSIZE = 1024

    def __init__(self, config: MoonDictConfig) -> None:
        """Initialize audio capture with configuration.

        Args:
            config: MoonDictConfig with audio device and sample rate settings.
        """
        self._config = config
        self._queue: queue.Queue[np.ndarray] = queue.Queue()
        self._stream: sd.InputStream | None = None

    @property
    def queue(self) -> queue.Queue[np.ndarray]:
        """Thread-safe queue for consuming captured audio blocks."""
        return self._queue

    def start(self) -> None:
        """Open and start the audio input stream.

        Raises:
            DeviceNotFoundError: If the configured device doesn't exist.
            StreamOpenError: If the stream fails to open.
        """
        device = self._config.audio_device

        # Validate device exists if specified
        if device is not None:
            devices = sd.query_devices()
            if device >= len(devices):
                raise DeviceNotFoundError(f"Device index {device} not found")

        try:
            self._stream = sd.InputStream(
                device=device,
                samplerate=self._config.sample_rate or self.SAMPLE_RATE,
                channels=self.CHANNELS,
                dtype=self.DTYPE,
                blocksize=self.BLOCKSIZE,
                callback=self._callback,
            )
            self._stream.start()
        except PortAudioError as exc:
            logger.error("Failed to open audio stream: {}", exc)
            raise StreamOpenError(f"Stream open failed: {exc}") from exc

        logger.info(
            "Audio capture started (device={}, sample_rate={})",
            device,
            self._config.sample_rate,
        )

    def stop(self) -> None:
        """Stop and close the audio input stream."""
        if self._stream is None:
            logger.debug("Audio capture not running, nothing to stop")
            return

        try:
            self._stream.stop()
            self._stream.close()
        except Exception as exc:
            logger.warning("Error closing audio stream: {}", exc)

        self._stream = None
        logger.info("Audio capture stopped")

    @staticmethod
    def list_devices() -> list[tuple[int, str]]:
        """List available audio input devices.

        Returns:
            List of (index, name) tuples for devices with input channels.
        """
        devices = sd.query_devices()
        input_devices: list[tuple[int, str]] = []

        for idx, dev in enumerate(devices):
            max_input = dev.get("max_input_channels", 0)
            if max_input > 0:
                input_devices.append((idx, dev["name"]))

        return input_devices

    def _callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info: dict[str, object],
        status: sd.CallbackFlags,
    ) -> None:
        """Sounddevice callback — puts audio data into the queue.

        Args:
            indata: Audio buffer as numpy array.
            frames: Number of frames captured.
            time_info: Timing metadata from sounddevice.
            status: Stream status flags.
        """
        if status:
            logger.debug("Audio capture status: {}", status)

        self._queue.put(indata.copy())
