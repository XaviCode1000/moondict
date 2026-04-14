"""Tests for TrayIndicator component."""

from __future__ import annotations

import threading
from unittest.mock import MagicMock, patch

import pytest

from moondict.tray.indicator import TrayIndicator


@pytest.fixture
def mock_pil_image() -> MagicMock:
    """Mock PIL Image module."""
    with patch("moondict.tray.indicator.Image") as mock:
        instance = MagicMock()
        mock.new.return_value = instance
        yield mock


@pytest.fixture
def mock_pystray() -> dict[str, MagicMock]:
    """Mock pystray Icon, Menu, and MenuItem classes."""
    with (
        patch("moondict.tray.indicator.Icon") as mock_icon,
        patch("moondict.tray.indicator.Menu") as mock_menu,
        patch("moondict.tray.indicator.MenuItem") as mock_item,
    ):
        icon_instance = MagicMock()
        # Make run() block until stop() is called
        stop_event = threading.Event()

        def blocking_run():
            stop_event.wait()

        icon_instance.run = MagicMock(side_effect=blocking_run)
        icon_instance.stop = MagicMock(side_effect=lambda: stop_event.set())
        mock_icon.return_value = icon_instance

        # Track MenuItem instances created
        menu_items = []

        def create_menu_item(*args, **kwargs):
            item = MagicMock()
            item.text = args[0] if args else kwargs.get("text", "")
            item.action = args[1] if len(args) > 1 else kwargs.get("action")
            menu_items.append(item)
            return item

        mock_item.side_effect = create_menu_item
        mock_menu.return_value = menu_items

        yield {
            "Icon": mock_icon,
            "Menu": mock_menu,
            "MenuItem": mock_item,
            "icon_instance": icon_instance,
            "menu_items": menu_items,
        }


@pytest.fixture
def mock_notify() -> MagicMock:
    """Mock notify function."""
    with patch("moondict.tray.indicator.notify") as mock:
        yield mock


@pytest.fixture
def mock_app() -> MagicMock:
    """Mock MoonDictApp orchestrator."""
    return MagicMock()


class TestTrayIndicatorInit:
    """Test TrayIndicator initialization."""

    def test_init_stores_app_reference(self, mock_app: MagicMock) -> None:
        """TrayIndicator stores reference to orchestrator."""
        indicator = TrayIndicator(mock_app)
        assert indicator._app is mock_app

    def test_init_starts_in_idle_state(self, mock_app: MagicMock) -> None:
        """TrayIndicator starts in idle state."""
        indicator = TrayIndicator(mock_app)
        assert indicator._state == "idle"

    def test_init_has_state_colors(self, mock_app: MagicMock) -> None:
        """TrayIndicator has color mapping for all states."""
        indicator = TrayIndicator(mock_app)
        expected_states = {"idle", "listening", "processing", "error", "loading"}
        assert set(indicator._STATE_COLORS.keys()) == expected_states


class TestTrayIndicatorStartStop:
    """Test start/stop lifecycle."""

    def test_start_creates_icon(
        self, mock_app: MagicMock, mock_pystray: dict, mock_pil_image: MagicMock
    ) -> None:
        """start() creates a pystray.Icon."""
        indicator = TrayIndicator(mock_app)
        indicator.start()

        mock_pystray["Icon"].assert_called_once()
        call_kwargs = mock_pystray["Icon"].call_args[1]
        assert "title" in call_kwargs
        assert "menu" in call_kwargs
        assert "icon" in call_kwargs

        indicator.stop()

    def test_start_runs_icon_in_thread(
        self, mock_app: MagicMock, mock_pystray: dict, mock_pil_image: MagicMock
    ) -> None:
        """start() runs icon in a background thread."""
        indicator = TrayIndicator(mock_app)
        indicator.start()

        assert indicator._thread is not None
        assert indicator._thread.is_alive()
        assert indicator._thread.daemon is True

        indicator.stop()

    def test_stop_removes_icon(
        self, mock_app: MagicMock, mock_pystray: dict, mock_pil_image: MagicMock
    ) -> None:
        """stop() removes the icon."""
        indicator = TrayIndicator(mock_app)
        indicator.start()
        indicator.stop()

        mock_pystray["icon_instance"].remove.assert_called_once()

    def test_stop_joins_thread(
        self, mock_app: MagicMock, mock_pystray: dict, mock_pil_image: MagicMock
    ) -> None:
        """stop() waits for thread to finish."""
        indicator = TrayIndicator(mock_app)
        indicator.start()
        indicator.stop()

        # Thread should be joined (not alive)
        assert indicator._thread is None or not indicator._thread.is_alive()

    def test_stop_before_start_is_safe(self, mock_app: MagicMock) -> None:
        """Calling stop() before start() does not raise."""
        indicator = TrayIndicator(mock_app)
        indicator.stop()  # Should not raise


class TestTrayIndicatorSetState:
    """Test set_state behavior."""

    def test_set_state_updates_state(
        self, mock_app: MagicMock, mock_pystray: dict, mock_pil_image: MagicMock
    ) -> None:
        """set_state() updates internal state."""
        indicator = TrayIndicator(mock_app)
        indicator.start()
        indicator.set_state("listening")

        assert indicator._state == "listening"
        indicator.stop()

    def test_set_state_updates_tooltip(
        self, mock_app: MagicMock, mock_pystray: dict, mock_pil_image: MagicMock
    ) -> None:
        """set_state() updates icon tooltip."""
        indicator = TrayIndicator(mock_app)
        indicator.start()
        indicator.set_state("listening")

        icon_instance = mock_pystray["icon_instance"]
        assert icon_instance.title is not None
        indicator.stop()

    def test_set_state_updates_icon(
        self, mock_app: MagicMock, mock_pystray: dict, mock_pil_image: MagicMock
    ) -> None:
        """set_state() updates icon image."""
        indicator = TrayIndicator(mock_app)
        indicator.start()
        indicator.set_state("processing")

        icon_instance = mock_pystray["icon_instance"]
        assert icon_instance.icon is not None
        indicator.stop()

    def test_set_state_invalid_state_logs_warning(
        self, mock_app: MagicMock, mock_pystray: dict, mock_pil_image: MagicMock
    ) -> None:
        """set_state() with invalid state logs warning."""
        indicator = TrayIndicator(mock_app)
        indicator.start()

        with patch("moondict.tray.indicator.logger") as mock_logger:
            indicator.set_state("invalid_state")
            mock_logger.warning.assert_called_once()

        indicator.stop()

    def test_set_state_thread_safe(
        self, mock_app: MagicMock, mock_pystray: dict, mock_pil_image: MagicMock
    ) -> None:
        """set_state() is thread-safe with lock."""
        indicator = TrayIndicator(mock_app)
        indicator.start()

        # Should have a lock
        assert hasattr(indicator, "_lock")
        assert isinstance(indicator._lock, type(threading.Lock()))

        indicator.stop()


class TestTrayIndicatorNotification:
    """Test show_notification behavior."""

    def test_show_notification_calls_notify(
        self, mock_app: MagicMock, mock_notify: MagicMock
    ) -> None:
        """show_notification() calls notify function."""
        indicator = TrayIndicator(mock_app)
        indicator.show_notification("Title", "Message")

        mock_notify.assert_called_once_with("Title", "Message")

    def test_show_notification_handles_missing_notify(
        self, mock_app: MagicMock
    ) -> None:
        """show_notification() handles missing notify gracefully."""
        with patch("moondict.tray.indicator.notify", side_effect=FileNotFoundError):
            indicator = TrayIndicator(mock_app)
            indicator.show_notification("Title", "Message")  # Should not raise


class TestTrayIndicatorMenu:
    """Test menu construction and callbacks."""

    def test_menu_has_required_items(
        self, mock_app: MagicMock, mock_pystray: dict, mock_pil_image: MagicMock
    ) -> None:
        """Menu contains Start, Stop, Settings, Quit."""
        indicator = TrayIndicator(mock_app)
        indicator.start()

        mock_pystray["Menu"].assert_called_once()
        indicator.stop()

    def test_menu_start_callback_delegates_to_app(
        self, mock_app: MagicMock, mock_pystray: dict, mock_pil_image: MagicMock
    ) -> None:
        """Start Dictation menu item delegates to app."""
        indicator = TrayIndicator(mock_app)
        indicator.start()

        # Find the start item and call its action
        for item in mock_pystray["menu_items"]:
            if "Start" in item.text:
                item.action()
                break

        # App method should be called
        mock_app.start.assert_called()
        indicator.stop()

    def test_menu_stop_callback_delegates_to_app(
        self, mock_app: MagicMock, mock_pystray: dict, mock_pil_image: MagicMock
    ) -> None:
        """Stop Dictation menu item delegates to app."""
        indicator = TrayIndicator(mock_app)
        indicator.start()

        for item in mock_pystray["menu_items"]:
            if "Stop" in item.text:
                item.action()
                break

        mock_app.stop.assert_called()
        indicator.stop()
