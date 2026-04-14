"""Thread-safe state machine for MoonDict dictation lifecycle."""

from __future__ import annotations

import threading
from enum import StrEnum

from loguru import logger


class DictationState(StrEnum):
    """States of the dictation lifecycle.

    Valid transitions:
    - IDLE → LISTENING (user triggers dictation)
    - LISTENING → PROCESSING (audio captured, transcribing)
    - PROCESSING → IDLE (transcription complete)
    - Any → ERROR (exception occurred)
    - ERROR → IDLE (recovery)
    """

    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    ERROR = "error"


# Valid transitions map: state → set of allowed next states
_VALID_TRANSITIONS: dict[DictationState, set[DictationState]] = {
    DictationState.IDLE: {DictationState.LISTENING, DictationState.ERROR},
    DictationState.LISTENING: {DictationState.PROCESSING, DictationState.ERROR},
    DictationState.PROCESSING: {DictationState.IDLE, DictationState.ERROR},
    DictationState.ERROR: {DictationState.IDLE},
}


class StateMachine:
    """Thread-safe finite state machine for dictation control.

    Uses a threading.Lock to protect state transitions and a
    threading.Event to allow waiting for specific states.
    """

    def __init__(self) -> None:
        """Initialize state machine in IDLE state."""
        self._state = DictationState.IDLE
        self._lock = threading.Lock()
        self._event = threading.Event()

    @property
    def current_state(self) -> DictationState:
        """The current dictation state."""
        with self._lock:
            return self._state

    def is_state(self, state: DictationState) -> bool:
        """Check if the current state matches the given state.

        Args:
            state: The state to check against.

        Returns:
            True if the current state matches.
        """
        with self._lock:
            return self._state == state

    def transition_to(self, new_state: DictationState) -> bool:
        """Attempt to transition to a new state.

        Args:
            new_state: The target state.

        Returns:
            True if the transition was valid and executed, False otherwise.
        """
        with self._lock:
            allowed = _VALID_TRANSITIONS.get(self._state, set())
            if new_state not in allowed and new_state != self._state:
                logger.warning(
                    "Invalid state transition: {} → {}", self._state, new_state
                )
                return False

            old_state = self._state
            self._state = new_state
            self._event.set()  # Wake up any waiters
            logger.debug("State transition: {} → {}", old_state, new_state)
            return True

    def wait_for_state(self, state: DictationState, timeout: float = 5.0) -> bool:
        """Block until the state machine reaches the given state.

        Args:
            state: The state to wait for.
            timeout: Maximum seconds to wait.

        Returns:
            True if the state was reached, False on timeout.
        """
        # Check current state first (optimization)
        with self._lock:
            if self._state == state:
                return True
            self._event.clear()

        # Wait for the event (set by any transition)
        if self._event.wait(timeout=timeout):
            with self._lock:
                return self._state == state
        return False
