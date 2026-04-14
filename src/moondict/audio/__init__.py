"""Audio subpackage — capture and feedback."""

from moondict.audio.capture import (
    AudioCapture,
    AudioCaptureError,
    DeviceNotFoundError,
    StreamOpenError,
)
from moondict.audio.feedback import generate_tone, play_sound

__all__ = [
    "AudioCapture",
    "AudioCaptureError",
    "DeviceNotFoundError",
    "StreamOpenError",
    "generate_tone",
    "play_sound",
]
