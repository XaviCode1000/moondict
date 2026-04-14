"""Tests for xdotool text injection with clipboard fallback."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from moondict.injection.xdotool import copy_to_clipboard, inject_text


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for all injection tests."""
    with patch("moondict.injection.xdotool.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        yield mock_run


@pytest.fixture
def mock_subprocess_run_with_clipboard():
    """Mock subprocess.run that tracks clipboard and xdotool calls."""
    with patch("moondict.injection.xdotool.subprocess.run") as mock_run:
        yield mock_run


class TestInjectText:
    """Tests for inject_text function."""

    def test_inject_text_calls_xdotool_type(self, mock_subprocess_run):
        """inject_text should call xdotool type with the given text."""
        result = inject_text("hello world")

        assert result is True
        mock_subprocess_run.assert_called_once_with(
            ["xdotool", "type", "--", "hello world"],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_inject_text_unicode_falls_back_to_clipboard(
        self, mock_subprocess_run_with_clipboard
    ):
        """If xdotool type fails (e.g., Unicode), fallback to clipboard + Ctrl+V."""
        mock_run = mock_subprocess_run_with_clipboard

        mock_run.side_effect = [
            subprocess.CalledProcessError(
                1, ["xdotool", "type"], output="", stderr="error"
            ),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
        ]

        result = inject_text("hola ñoño")

        assert result is True
        assert mock_run.call_count == 3

        assert mock_run.call_args_list[0].args[0] == [
            "xdotool",
            "type",
            "--",
            "hola ñoño",
        ]
        assert mock_run.call_args_list[1].args[0][0] == "xclip"
        assert mock_run.call_args_list[2].args[0] == ["xdotool", "key", "ctrl+v"]

    def test_inject_text_xdotool_not_installed(self, mock_subprocess_run):
        """If xdotool is not installed, return False."""
        mock_run = mock_subprocess_run
        mock_run.side_effect = FileNotFoundError("xdotool not found")

        result = inject_text("hello")

        assert result is False

    def test_inject_text_empty_string(self, mock_subprocess_run):
        """Empty string should still attempt injection."""
        result = inject_text("")

        assert result is True
        mock_subprocess_run.assert_called_once_with(
            ["xdotool", "type", "--", ""],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_inject_text_special_characters(self, mock_subprocess_run):
        """Text with special characters should be passed correctly."""
        result = inject_text("hello <world> & 'quotes'")

        assert result is True
        call_args = mock_subprocess_run.call_args.args[0]
        assert call_args == ["xdotool", "type", "--", "hello <world> & 'quotes'"]


class TestCopyToClipboard:
    """Tests for copy_to_clipboard function."""

    def test_copy_to_clipboard_calls_xclip(self, mock_subprocess_run):
        """copy_to_clipboard should call xclip with the text."""
        copy_to_clipboard("test text")

        mock_subprocess_run.assert_called_once()
        call_args = mock_subprocess_run.call_args
        assert call_args.args[0][0] == "xclip"
        assert call_args.args[0] == ["xclip", "-selection", "clipboard"]
        assert call_args.kwargs["input"] == "test text"

    def test_copy_to_clipboard_xclip_not_installed(self, mock_subprocess_run):
        """If xclip is not installed, raise appropriate error."""
        mock_run = mock_subprocess_run
        mock_run.side_effect = FileNotFoundError("xclip not found")

        with pytest.raises(FileNotFoundError, match="xclip"):
            copy_to_clipboard("test")

    def test_copy_to_clipboard_unicode_text(self, mock_subprocess_run):
        """Unicode text should be passed correctly to xclip."""
        copy_to_clipboard("hola ñoño 🎉")

        call_args = mock_subprocess_run.call_args
        assert call_args.kwargs["input"] == "hola ñoño 🎉"
        assert (
            call_args.kwargs.get("text") is True
            or call_args.kwargs.get("encoding") == "utf-8"
        )


class TestInjectTextEdgeCases:
    """Edge case tests for injection."""

    def test_inject_text_both_fail_returns_false(self, mock_subprocess_run):
        """If both xdotool type and clipboard fallback fail, return False."""
        mock_run = mock_subprocess_run
        mock_run.side_effect = [
            subprocess.CalledProcessError(1, ["xdotool", "type"]),
            FileNotFoundError("xclip not found"),
        ]

        result = inject_text("hello")

        assert result is False

    def test_inject_text_paste_fails_returns_false(self, mock_subprocess_run):
        """If clipboard succeeds but xdotool paste fails, return False."""
        mock_run = mock_subprocess_run
        mock_run.side_effect = [
            subprocess.CalledProcessError(1, ["xdotool", "type"]),
            MagicMock(returncode=0),
            subprocess.CalledProcessError(1, ["xdotool", "key"]),
        ]

        result = inject_text("hello")

        assert result is False
