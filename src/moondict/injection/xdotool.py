"""Text injection via xdotool with clipboard fallback for MoonDict."""

from __future__ import annotations

import subprocess

from loguru import logger


def inject_text(text: str) -> bool:
    """Inject text into the focused window via xdotool.

    Strategy:
    1. Try ``xdotool type`` first (fast, direct).
    2. If it fails (e.g., Unicode characters), fall back to
       clipboard + ``xdotool key ctrl+v``.

    Args:
        text: The text to inject.

    Returns:
        True if injection succeeded, False otherwise.
    """
    try:
        _xdotool_type(text)
        logger.debug("Text injected via xdotool type: {!r}", text[:50])
        return True
    except FileNotFoundError:
        logger.error("xdotool is not installed")
        return False
    except subprocess.CalledProcessError as exc:
        logger.warning("xdotool type failed, trying clipboard fallback: {}", exc)
        return _clipboard_fallback(text)


def copy_to_clipboard(text: str) -> None:
    """Copy text to the system clipboard via xclip.

    Args:
        text: The text to copy.

    Raises:
        FileNotFoundError: If xclip is not installed.
        subprocess.CalledProcessError: If xclip exits with an error.
    """
    try:
        subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=text,
            check=True,
            capture_output=True,
            text=True,
        )
        logger.debug("Text copied to clipboard: {!r}", text[:50])
    except FileNotFoundError as exc:
        logger.error("xclip is not installed")
        raise FileNotFoundError("xclip is required for clipboard operations") from exc


def _xdotool_type(text: str) -> None:
    """Type text directly via xdotool.

    Args:
        text: The text to type.

    Raises:
        FileNotFoundError: If xdotool is not installed.
        subprocess.CalledProcessError: If xdotool exits with an error.
    """
    subprocess.run(
        ["xdotool", "type", "--", text],
        check=True,
        capture_output=True,
        text=True,
    )


def _xdotool_paste() -> None:
    """Send Ctrl+V via xdotool to paste from clipboard.

    Raises:
        FileNotFoundError: If xdotool is not installed.
        subprocess.CalledProcessError: If xdotool exits with an error.
    """
    subprocess.run(
        ["xdotool", "key", "ctrl+v"],
        check=True,
        capture_output=True,
        text=True,
    )


def _clipboard_fallback(text: str) -> bool:
    """Fallback strategy: copy to clipboard then paste via xdotool.

    Args:
        text: The text to inject.

    Returns:
        True if both clipboard copy and paste succeeded, False otherwise.
    """
    try:
        copy_to_clipboard(text)
        _xdotool_paste()
        logger.debug("Text injected via clipboard fallback: {!r}", text[:50])
        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        logger.error("Clipboard fallback failed: {}", exc)
        return False
