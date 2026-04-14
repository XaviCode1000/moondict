"""Tray indicator for MoonDict — system tray icon with state visualization."""

from __future__ import annotations

import contextlib
import threading
from typing import TYPE_CHECKING

from loguru import logger

try:
    import pystray
    from pystray import Icon, Menu, MenuItem
except ImportError:
    pystray = None

try:
    from PIL import Image as _PILImage
except ImportError:
    _PILImage = None  # type: ignore[assignment]

try:
    from notify2 import Notification as _Notify2Notification

    def notify(title: str, message: str) -> None:
        """Send a system notification using notify2."""
        _Notify2Notification(title, message).show()

except ImportError:
    try:
        from notifypy import Notipy

        _notipy = Notipy()

        def notify(title: str, message: str) -> None:
            """Send a system notification using notifypy."""
            _notipy.notification(title=title, description=message)

    except ImportError:

        def notify(title: str, message: str) -> None:
            """Fallback: no-op when no notification library is available."""
            logger.debug("System notification: {} - {}", title, message)


# Use PIL Image if available
Image = _PILImage

if TYPE_CHECKING:
    from PIL.Image import Image as PILImageType

    from moondict.main import MoonDictApp


# State → RGB color tuple + emoji for tooltip
_STATE_COLORS: dict[str, tuple[tuple[int, int, int], str]] = {
    "idle": ((76, 175, 80), "🟢"),  # Green
    "listening": ((244, 67, 54), "🔴"),  # Red
    "processing": ((255, 193, 7), "🟡"),  # Yellow
    "error": ((158, 158, 158), "⚫"),  # Gray
    "loading": ((33, 150, 243), "🔵"),  # Blue
}

_ICON_SIZE = 32  # pixels


class TrayIndicator:
    """System tray indicator for MoonDict.

    Displays a colored icon representing the current dictation state
    and provides a context menu for controlling the application.

    Thread safety:
    - pystray runs in its own thread.
    - State updates are protected by a threading.Lock.
    - Menu callbacks delegate to MoonDictApp methods.

    States:
    - idle: Green circle — ready for dictation
    - listening: Red circle — recording audio
    - processing: Yellow circle — transcribing
    - error: Gray circle — error occurred
    - loading: Blue circle — loading model/resources
    """

    _STATE_COLORS = _STATE_COLORS

    def __init__(self, app: MoonDictApp) -> None:
        """Initialize the tray indicator.

        Args:
            app: Reference to the MoonDictApp orchestrator for menu callbacks.
        """
        self._app = app
        self._state = "idle"
        self._lock = threading.Lock()
        self._icon: Icon | None = None
        self._thread: threading.Thread | None = None

        logger.debug("TrayIndicator initialized")

    def start(self) -> None:
        """Create and show the system tray icon.

        Runs pystray in a daemon background thread.
        """
        logger.info("Starting tray indicator")

        icon_image = self._create_icon("idle")
        menu = self._build_menu()

        self._icon = Icon(
            name="moondict",
            title="MoonDict - Idle",
            icon=icon_image,
            menu=menu,
        )

        self._thread = threading.Thread(target=self._run_icon, daemon=True)
        self._thread.start()

        logger.info("Tray indicator started")

    def stop(self) -> None:
        """Remove the tray icon and clean up the thread."""
        logger.info("Stopping tray indicator")

        if self._icon is not None:
            self._icon.stop()
            self._icon.remove()
            self._icon = None

        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=2.0)
            self._thread = None

        logger.info("Tray indicator stopped")

    def set_state(self, state: str) -> None:
        """Update the tray icon state (color and tooltip).

        Args:
            state: One of 'idle', 'listening', 'processing', 'error', 'loading'.
        """
        with self._lock:
            if state not in self._STATE_COLORS:
                logger.warning("Invalid tray state: {}", state)
                return

            self._state = state

            if self._icon is not None:
                self._icon.icon = self._create_icon(state)
                self._icon.title = f"MoonDict - {state.capitalize()}"

            logger.debug("Tray state set to: {}", state)

    def show_notification(self, title: str, message: str) -> None:
        """Show a system notification.

        Args:
            title: Notification title.
            message: Notification body text.
        """
        try:
            notify(title, message)
            logger.debug("Notification shown: {}", title)
        except Exception as exc:
            logger.warning("Failed to show notification: {}", exc)

    def _run_icon(self) -> None:
        """Run the pystray icon main loop.

        This method runs in a background thread.
        """
        if self._icon is not None:
            try:
                self._icon.run()
            except Exception as exc:
                logger.error("Tray icon error: {}", exc)

    def _create_icon(self, state: str) -> PILImageType:
        """Create a colored circle icon for the given state.

        Args:
            state: The state to create an icon for.

        Returns:
            A PIL Image suitable for pystray.
        """
        if Image is None:
            # Fallback: create a minimal blank image
            logger.warning("PIL not available, using fallback icon")
            from PIL import Image as PILImage

            return PILImage.new("RGBA", (_ICON_SIZE, _ICON_SIZE), (0, 0, 0, 0))

        color, _ = self._STATE_COLORS.get(state, ((128, 128, 128), "⚫"))

        # Create a solid circle image
        img = Image.new("RGBA", (_ICON_SIZE, _ICON_SIZE), (0, 0, 0, 0))
        from PIL import ImageDraw

        draw = ImageDraw.Draw(img)
        margin = 2
        draw.ellipse(
            [margin, margin, _ICON_SIZE - margin, _ICON_SIZE - margin],
            fill=(*color, 255),
        )

        return img

    def _build_menu(self) -> Menu:
        """Build the tray context menu.

        Returns:
            A pystray Menu with Start, Stop, Settings, and Quit items.
        """
        return Menu(
            MenuItem("Start Dictation", action=self._on_start, default=True),
            MenuItem("Stop Dictation", action=self._on_stop),
            MenuItem("Settings", action=self._on_settings),
            MenuItem("Quit", action=self._on_quit),
        )

    def _on_start(self) -> None:
        """Menu callback: Start dictation."""
        logger.info("Tray menu: Start Dictation")
        try:
            self._app.start()
            self.show_notification("MoonDict", "Dictation started")
        except Exception as exc:
            logger.error("Failed to start dictation from tray: {}", exc)

    def _on_stop(self) -> None:
        """Menu callback: Stop dictation."""
        logger.info("Tray menu: Stop Dictation")
        try:
            self._app.stop()
            self.show_notification("MoonDict", "Dictation stopped")
        except Exception as exc:
            logger.error("Failed to stop dictation from tray: {}", exc)

    def _on_settings(self) -> None:
        """Menu callback: Open settings (placeholder)."""
        logger.info("Tray menu: Settings")
        self.show_notification("MoonDict", "Settings not yet implemented")

    def _on_quit(self) -> None:
        """Menu callback: Quit application."""
        logger.info("Tray menu: Quit")
        with contextlib.suppress(Exception):
            self._app.stop()
        self.stop()
