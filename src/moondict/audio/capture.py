"""Audio capture module for MoonDict."""

from __future__ import annotations

import queue
import subprocess

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


def find_android_mic() -> str | None:
    """Find the PipeWire source name matching 'android-'.

    Uses pactl to query PipeWire sources directly, which correctly
    sees android-* sources created by audiosource.

    Returns:
        The source name (e.g., 'android-c8ab597'), or None if not found.
    """
    try:
        result = subprocess.run(
            ["pactl", "list", "sources", "short"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        for line in result.stdout.strip().splitlines():
            parts = line.split("\t")
            if len(parts) >= 2 and "android-" in parts[1]:
                source_name = parts[1]
                logger.debug("Found android mic: {}", source_name)
                return source_name
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
        logger.debug("Failed to query PipeWire sources: {}", exc)

    logger.debug("No android mic found in PipeWire sources")
    return None


class AndroidMicManager:
    """Manages PipeWire default source switching for android mic capture.

    PortAudio/sounddevice cannot select individual PipeWire sources by name.
    The solution is to temporarily set the android source as the PipeWire
    default, capture from the default device, then restore the original.

    This mirrors the approach used in the fish `dictation` function.
    """

    def __init__(self, source_name: str) -> None:
        self._source_name = source_name
        self._original_default: str | None = None

    @staticmethod
    def _get_default_source() -> str | None:
        """Get the current default PipeWire source name."""
        try:
            result = subprocess.run(
                ["pactl", "get-default-source"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            return result.stdout.strip() or None
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return None

    @staticmethod
    def _set_default_source(name: str) -> None:
        """Set the default PipeWire source."""
        subprocess.run(
            ["pactl", "set-default-source", name],
            capture_output=True,
            text=True,
            timeout=3,
            check=True,
        )

    def activate(self) -> None:
        """Save current default and switch to android source."""
        self._original_default = self._get_default_source()
        logger.info(
            "Switching PipeWire default source: {} → {}",
            self._original_default or "(unknown)",
            self._source_name,
        )
        self._set_default_source(self._source_name)

    def restore(self) -> None:
        """Restore the original default source."""
        if self._original_default:
            logger.info("Restoring PipeWire default source: {}", self._original_default)
            try:
                self._set_default_source(self._original_default)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                logger.warning("Failed to restore default source: {}", exc)
        self._original_default = None


class AudioCapture:
    """Manages raw audio input capture via sounddevice.

    Opens an InputStream at 16kHz, mono, float32 and delivers
    audio blocks through a thread-safe queue.Queue.
    """

    SAMPLE_RATE = 16000
    CHANNELS = 1
    DTYPE = "float32"
    BLOCKSIZE = 1024

    def __init__(
        self,
        config: MoonDictConfig,
        *,
        auto_detect_android: bool = False,
    ) -> None:
        """Initialize audio capture with configuration.

        Args:
            config: MoonDictConfig with audio device and sample rate settings.
            auto_detect_android: When True and config.audio_device is None,
                auto-detect an Android microphone via PipeWire source switching.
        """
        self._config = config
        self._auto_detect_android = auto_detect_android
        self._queue: queue.Queue[np.ndarray] = queue.Queue()
        self._stream: sd.InputStream | None = None
        self._android_mic: AndroidMicManager | None = None

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

        # Auto-detect android mic: find source, switch default, capture from default
        if self._auto_detect_android and device is None:
            source_name = find_android_mic()
            if source_name is not None:
                self._android_mic = AndroidMicManager(source_name)
                self._android_mic.activate()
                logger.info("Android mic active via PipeWire default source switch")

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
            # Restore android default on failure
            if self._android_mic:
                self._android_mic.restore()
                self._android_mic = None
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

        # Restore original PipeWire default source if we switched it
        if self._android_mic:
            self._android_mic.restore()
            self._android_mic = None

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
