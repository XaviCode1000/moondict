"""Tests for MoonDict audio capture module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import sounddevice as sd
from sounddevice import PortAudioError

from moondict.audio.capture import (
    AudioCapture,
    DeviceNotFoundError,
    StreamOpenError,
    find_android_mic,
)
from moondict.config import MoonDictConfig


class TestAudioCaptureLifecycle:
    """Tests for AudioCapture start/stop lifecycle."""

    def test_start_opens_stream(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """AudioCapture opens a sounddevice InputStream on start()."""
        capture = AudioCapture(sample_config)

        with patch("moondict.audio.capture.sd") as mock_sd:
            mock_stream = MagicMock()
            mock_sd.InputStream.return_value = mock_stream
            capture.start()

            mock_sd.InputStream.assert_called_once()
            mock_stream.start.assert_called_once()

    def test_stop_closes_stream(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """AudioCapture stops and closes the stream on stop()."""
        capture = AudioCapture(sample_config)

        with patch("moondict.audio.capture.sd") as mock_sd:
            mock_stream = MagicMock()
            mock_sd.InputStream.return_value = mock_stream
            capture.start()
            capture.stop()

            mock_stream.stop.assert_called_once()
            mock_stream.close.assert_called_once()

    def test_stop_when_not_running_is_safe(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Calling stop() before start() does not raise."""
        capture = AudioCapture(sample_config)
        capture.stop()  # Should not raise

    def test_start_with_device_not_found(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Raises DeviceNotFoundError when configured device index is invalid."""
        config = MoonDictConfig(audio_device=9999)
        capture = AudioCapture(config)

        with patch("moondict.audio.capture.sd") as mock_sd:
            mock_sd.query_devices.return_value = [
                {"name": "Device 0", "max_input_channels": 1}
            ]

            with pytest.raises(DeviceNotFoundError, match="9999"):
                capture.start()

    def test_start_stream_open_error(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Raises StreamOpenError when PortAudio fails to open stream."""
        capture = AudioCapture(sample_config)

        with patch("moondict.audio.capture.sd") as mock_sd:
            mock_sd.InputStream.side_effect = PortAudioError("Permission denied")

            with pytest.raises(StreamOpenError, match="Permission denied"):
                capture.start()


class TestAudioCaptureCallback:
    """Tests for the audio callback mechanism."""

    def test_callback_puts_data_in_queue(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Callback puts a copy of audio data into the queue."""
        capture = AudioCapture(sample_config)
        audio_data = np.array([0.1, 0.2, 0.3], dtype=np.float32)

        capture._callback(audio_data, 3, {}, sd.CallbackFlags(0))

        result = capture.queue.get_nowait()
        np.testing.assert_array_equal(result, audio_data)

    def test_callback_copies_data(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Callback copies data to prevent mutation by consumer."""
        capture = AudioCapture(sample_config)
        audio_data = np.array([0.5], dtype=np.float32)

        capture._callback(audio_data, 1, {}, sd.CallbackFlags(0))

        result = capture.queue.get_nowait()
        result[0] = 0.0  # Mutate the copy
        assert audio_data[0] == 0.5  # Original unchanged


class TestAudioCaptureListDevices:
    """Tests for AudioCapture.list_devices()."""

    def test_list_devices_returns_input_only(
        self,
    ) -> None:
        """Only devices with input channels are returned."""
        with patch("moondict.audio.capture.sd") as mock_sd:
            mock_sd.query_devices.return_value = [
                {"name": "Mic", "max_input_channels": 2},
                {"name": "Speaker", "max_input_channels": 0},
                {"name": "Headset", "max_input_channels": 1},
            ]

            devices = AudioCapture.list_devices()

            assert len(devices) == 2
            assert devices[0] == (0, "Mic")
            assert devices[1] == (2, "Headset")

    def test_list_devices_empty(self) -> None:
        """Returns empty list when no devices available."""
        with patch("moondict.audio.capture.sd") as mock_sd:
            mock_sd.query_devices.return_value = []

            devices = AudioCapture.list_devices()

            assert devices == []


class TestFindAndroidMic:
    """Tests for find_android_mic() auto-detection."""

    def test_find_android_mic_returns_index_when_found(self) -> None:
        """Should return the index of the first device matching 'android-'."""
        with patch("moondict.audio.capture.sd") as mock_sd:
            mock_sd.query_devices.return_value = [
                {"name": "Built-in Mic", "max_input_channels": 1},
                {"name": "android-R58W30HJ23K.monitor", "max_input_channels": 2},
                {"name": "USB Headset", "max_input_channels": 1},
            ]

            result = find_android_mic()

            assert result == 1

    def test_find_android_mic_returns_first_match(self) -> None:
        """Should return the index of the first matching android device."""
        with patch("moondict.audio.capture.sd") as mock_sd:
            mock_sd.query_devices.return_value = [
                {"name": "android-ABC.monitor", "max_input_channels": 1},
                {"name": "android-XYZ.monitor", "max_input_channels": 1},
            ]

            result = find_android_mic()

            assert result == 0

    def test_find_android_mic_returns_none_when_not_found(self) -> None:
        """Should return None when no android device exists."""
        with patch("moondict.audio.capture.sd") as mock_sd:
            mock_sd.query_devices.return_value = [
                {"name": "Built-in Mic", "max_input_channels": 1},
                {"name": "USB Microphone", "max_input_channels": 2},
            ]

            result = find_android_mic()

            assert result is None

    def test_find_android_mic_returns_none_when_empty(self) -> None:
        """Should return None when no devices are available."""
        with patch("moondict.audio.capture.sd") as mock_sd:
            mock_sd.query_devices.return_value = []

            result = find_android_mic()

            assert result is None


class TestAudioCaptureAutoDetect:
    """Tests for AudioCapture auto_detect_android parameter."""

    def test_auto_detect_uses_find_android_mic_when_device_none(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Should call find_android_mic() when audio_device is None and auto_detect is True."""
        config = MoonDictConfig(audio_device=None)

        with (
            patch("moondict.audio.capture.sd") as mock_sd,
            patch("moondict.audio.capture.find_android_mic") as mock_find,
        ):
            mock_stream = MagicMock()
            mock_sd.InputStream.return_value = mock_stream
            mock_sd.query_devices.return_value = [
                {"name": "android-mic", "max_input_channels": 1}
            ] * 50
            mock_find.return_value = 42

            capture = AudioCapture(config, auto_detect_android=True)
            capture.start()

            mock_find.assert_called_once()
            # Verify the found device was used
            call_kwargs = mock_sd.InputStream.call_args
            assert call_kwargs.kwargs["device"] == 42

    def test_auto_detect_skips_when_device_set(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Should NOT call find_android_mic() when audio_device is explicitly set."""
        config = MoonDictConfig(audio_device=0)

        with (
            patch("moondict.audio.capture.sd") as mock_sd,
            patch("moondict.audio.capture.find_android_mic") as mock_find,
        ):
            mock_stream = MagicMock()
            mock_sd.InputStream.return_value = mock_stream
            mock_sd.query_devices.return_value = [
                {"name": "Default Mic", "max_input_channels": 1}
            ]

            capture = AudioCapture(config, auto_detect_android=True)
            capture.start()

            mock_find.assert_not_called()
            call_kwargs = mock_sd.InputStream.call_args
            assert call_kwargs.kwargs["device"] == 0

    def test_auto_detect_false_does_not_autodetect(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Should NOT call find_android_mic() when auto_detect_android is False."""
        config = MoonDictConfig(audio_device=None)

        with (
            patch("moondict.audio.capture.sd") as mock_sd,
            patch("moondict.audio.capture.find_android_mic") as mock_find,
        ):
            mock_stream = MagicMock()
            mock_sd.InputStream.return_value = mock_stream

            capture = AudioCapture(config, auto_detect_android=False)
            capture.start()

            mock_find.assert_not_called()

    def test_auto_detect_uses_none_when_no_android_found(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Should pass device=None to stream when find_android_mic returns None."""
        config = MoonDictConfig(audio_device=None)

        with (
            patch("moondict.audio.capture.sd") as mock_sd,
            patch("moondict.audio.capture.find_android_mic") as mock_find,
        ):
            mock_stream = MagicMock()
            mock_sd.InputStream.return_value = mock_stream
            mock_find.return_value = None

            capture = AudioCapture(config, auto_detect_android=True)
            capture.start()

            call_kwargs = mock_sd.InputStream.call_args
            assert call_kwargs.kwargs["device"] is None
