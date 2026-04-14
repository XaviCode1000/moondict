"""Entry point for MoonDict CLI application."""

from __future__ import annotations

import argparse
import signal
import sys
from typing import TYPE_CHECKING

from loguru import logger

from moondict.config import MoonDictConfig
from moondict.main import MoonDictApp

if TYPE_CHECKING:
    from collections.abc import Callable


def _create_signal_handler(app: MoonDictApp) -> Callable[[int, object | None], None]:
    """Create a signal handler that stops the app gracefully.

    Args:
        app: The MoonDictApp instance to stop.

    Returns:
        A callable suitable for signal.signal().
    """

    def handler(sig: int, frame: object | None) -> None:
        logger.info("Received signal {}, shutting down...", sig)
        app.stop()
        sys.exit(0)

    return handler


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        prog="moondict",
        description="Voice dictation for Linux powered by Moonshine AI",
    )

    parser.add_argument(
        "--push-to-talk",
        action="store_true",
        default=False,
        help="Use push-to-talk mode (hold key to record)",
    )
    parser.add_argument(
        "--toggle",
        action="store_true",
        default=False,
        help="Use toggle mode (double-tap to start/stop)",
    )
    parser.add_argument(
        "--device",
        type=int,
        default=None,
        help="Audio input device index",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="ASR model name",
    )
    parser.add_argument(
        "--no-tray",
        action="store_true",
        default=False,
        help="Disable system tray indicator",
    )
    parser.add_argument(
        "--android-mic",
        action="store_true",
        default=False,
        help="Auto-detect Android microphone via PipeWire (audiosource)",
    )

    return parser.parse_args()


def main() -> None:
    """Entry point for the MoonDict CLI.

    Parses arguments, loads configuration, creates the application,
    registers signal handlers, and starts the dictation loop.
    """
    args = _parse_args()

    # Load configuration (from env vars, config file, and CLI overrides)
    config = MoonDictConfig()

    # Apply CLI overrides
    if args.push_to_talk:
        object.__setattr__(config, "shortcut_mode", "push_to_talk")
    elif args.toggle:
        object.__setattr__(config, "shortcut_mode", "toggle")

    if args.device is not None:
        object.__setattr__(config, "audio_device", args.device)

    if args.model is not None:
        object.__setattr__(config, "model", args.model)

    if args.android_mic:
        object.__setattr__(config, "android_mic", True)

    use_tray = not args.no_tray

    # Create and start application
    app = MoonDictApp(config, use_tray=use_tray)

    # Register signal handlers for graceful shutdown
    handler = _create_signal_handler(app)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    try:
        app.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        app.stop()


if __name__ == "__main__":
    main()
