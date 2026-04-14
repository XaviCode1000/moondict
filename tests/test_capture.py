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

    def test_find_android_mic_returns_source_name_when_found(self) -> None:
        """Should return the source name matching 'android-'."""
        with patch("moondict.audio.capture.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="56\talsa_input.pci.monitor\tPipeWire\ts32le 2ch 48000Hz\tSUSPENDED\n2276\tandroid-c8ab597\tPipeWire\ts16le 1ch 44100Hz\tSUSPENDED\n"
            )

            result = find_android_mic()

            assert result == "android-c8ab597"

    def test_find_android_mic_returns_first_match(self) -> None:
        """Should return the first android source name found."""
        with patch("moondict.audio.capture.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="10\tandroid-ABC\tPipeWire\ts16le 1ch 44100Hz\tSUSPENDED\n20\tandroid-XYZ\tPipeWire\ts16le 1ch 44100Hz\tSUSPENDED\n"
            )

            result = find_android_mic()

            assert result == "android-ABC"

    def test_find_android_mic_returns_none_when_not_found(self) -> None:
        """Should return None when no android source exists."""
        with patch("moondict.audio.capture.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="56\talsa_input.pci.monitor\tPipeWire\ts32le 2ch 48000Hz\tSUSPENDED\n"
            )

            result = find_android_mic()

            assert result is None

    def test_find_android_mic_returns_none_when_empty(self) -> None:
        """Should return None when no sources are available."""
        with patch("moondict.audio.capture.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="")

            result = find_android_mic()

            assert result is None

    def test_find_android_mic_returns_none_on_error(self) -> None:
        """Should return None when pactl fails."""
        with patch("moondict.audio.capture.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("pactl not found")

            result = find_android_mic()

            assert result is None


class TestAndroidMicManager:
    """Tests for AndroidMicManager PipeWire source switching."""

    @patch("moondict.audio.capture.subprocess.run")
    def test_activate_saves_original_and_switches(self, mock_run: MagicMock) -> None:
        """Should save original default and switch to android source."""
        from moondict.audio.capture import AndroidMicManager

        mock_run.return_value = MagicMock(
            stdout="alsa_input.pci-0000_00_1b.0.analog-stereo\n"
        )
        mgr = AndroidMicManager("android-c8ab597")
        mgr.activate()

        # Should have called get-default-source once and set-default-source once
        assert mock_run.call_count == 2

    @patch("moondict.audio.capture.subprocess.run")
    def test_restore_switches_back(self, mock_run: MagicMock) -> None:
        """Should restore the original default source."""
        from moondict.audio.capture import AndroidMicManager

        mock_run.return_value = MagicMock(
            stdout="alsa_input.pci-0000_00_1b.0.analog-stereo\n"
        )
        mgr = AndroidMicManager("android-c8ab597")
        mgr.activate()
        mgr.restore()

        # Should have called set-default-source for restore
        assert mock_run.call_count == 3

    @patch("moondict.audio.capture.subprocess.run")
    def test_restore_is_safe_without_activate(self, mock_run: MagicMock) -> None:
        """Should not raise when restore called without activate."""
        from moondict.audio.capture import AndroidMicManager

        mgr = AndroidMicManager("android-c8ab597")
        mgr.restore()  # Should not raise

        mock_run.assert_not_called()


class TestAudioCaptureAutoDetect:
    """Tests for AudioCapture auto_detect_android parameter."""

    def test_auto_detect_activates_android_mic_when_device_none(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Should activate AndroidMicManager when audio_device is None and auto_detect is True."""
        config = MoonDictConfig(audio_device=None)

        with (
            patch("moondict.audio.capture.sd") as mock_sd,
            patch("moondict.audio.capture.find_android_mic") as mock_find,
            patch("moondict.audio.capture.AndroidMicManager") as mock_mgr_cls,
        ):
            mock_stream = MagicMock()
            mock_sd.InputStream.return_value = mock_stream
            mock_find.return_value = "android-c8ab597"
            mock_mgr = MagicMock()
            mock_mgr_cls.return_value = mock_mgr

            capture = AudioCapture(config, auto_detect_android=True)
            capture.start()

            mock_find.assert_called_once()
            mock_mgr_cls.assert_called_once_with("android-c8ab597")
            mock_mgr.activate.assert_called_once()

    def test_auto_detect_skips_when_device_set(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Should NOT call find_android_mic() when audio_device is explicitly set."""
        config = MoonDictConfig(audio_device=0)

        with (
            patch("moondict.audio.capture.sd") as mock_sd,
            patch("moondict.audio.capture.find_android_mic") as mock_find,
            patch("moondict.audio.capture.AndroidMicManager") as mock_mgr_cls,
        ):
            mock_stream = MagicMock()
            mock_sd.InputStream.return_value = mock_stream
            mock_sd.query_devices.return_value = [
                {"name": "Default Mic", "max_input_channels": 1}
            ]

            capture = AudioCapture(config, auto_detect_android=True)
            capture.start()

            mock_find.assert_not_called()
            mock_mgr_cls.assert_not_called()

    def test_auto_detect_false_does_not_autodetect(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Should NOT call find_android_mic() when auto_detect_android is False."""
        config = MoonDictConfig(audio_device=None)

        with (
            patch("moondict.audio.capture.sd") as mock_sd,
            patch("moondict.audio.capture.find_android_mic") as mock_find,
            patch("moondict.audio.capture.AndroidMicManager") as mock_mgr_cls,
        ):
            mock_stream = MagicMock()
            mock_sd.InputStream.return_value = mock_stream

            capture = AudioCapture(config, auto_detect_android=False)
            capture.start()

            mock_find.assert_not_called()
            mock_mgr_cls.assert_not_called()

    def test_auto_detect_restores_on_stop(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Should restore original default source when stopping."""
        config = MoonDictConfig(audio_device=None)

        with (
            patch("moondict.audio.capture.sd") as mock_sd,
            patch("moondict.audio.capture.find_android_mic") as mock_find,
            patch("moondict.audio.capture.AndroidMicManager") as mock_mgr_cls,
        ):
            mock_stream = MagicMock()
            mock_sd.InputStream.return_value = mock_stream
            mock_find.return_value = "android-c8ab597"
            mock_mgr = MagicMock()
            mock_mgr_cls.return_value = mock_mgr

            capture = AudioCapture(config, auto_detect_android=True)
            capture.start()
            capture.stop()

            mock_mgr.restore.assert_called_once()

    def test_auto_detect_restores_on_stream_error(
        self,
        sample_config: MoonDictConfig,
    ) -> None:
        """Should restore original default source when stream fails to open."""
        config = MoonDictConfig(audio_device=None)

        with (
            patch("moondict.audio.capture.sd") as mock_sd,
            patch("moondict.audio.capture.find_android_mic") as mock_find,
            patch("moondict.audio.capture.AndroidMicManager") as mock_mgr_cls,
        ):
            mock_sd.InputStream.side_effect = PortAudioError("Permission denied")
            mock_find.return_value = "android-c8ab597"
            mock_mgr = MagicMock()
            mock_mgr_cls.return_value = mock_mgr

            capture = AudioCapture(config, auto_detect_android=True)

            with pytest.raises(StreamOpenError):
                capture.start()

            mock_mgr.restore.assert_called_once()
