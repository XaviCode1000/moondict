"""Tests for dictation state machine."""

from __future__ import annotations

import threading
import time

from moondict.state import DictationState, StateMachine


class TestDictationState:
    """Tests for DictationState enum."""

    def test_enum_values(self):
        """DictationState should have IDLE, LISTENING, PROCESSING, ERROR."""
        assert DictationState.IDLE.value == "idle"
        assert DictationState.LISTENING.value == "listening"
        assert DictationState.PROCESSING.value == "processing"
        assert DictationState.ERROR.value == "error"


class TestStateMachine:
    """Tests for thread-safe state machine."""

    def test_initial_state_is_idle(self):
        """StateMachine should start in IDLE state."""
        sm = StateMachine()
        assert sm.current_state == DictationState.IDLE

    def test_idle_to_listening(self):
        """Valid transition: IDLE → LISTENING."""
        sm = StateMachine()
        assert sm.transition_to(DictationState.LISTENING)
        assert sm.current_state == DictationState.LISTENING

    def test_listening_to_processing(self):
        """Valid transition: LISTENING → PROCESSING."""
        sm = StateMachine()
        sm.transition_to(DictationState.LISTENING)
        assert sm.transition_to(DictationState.PROCESSING)
        assert sm.current_state == DictationState.PROCESSING

    def test_processing_to_idle(self):
        """Valid transition: PROCESSING → IDLE."""
        sm = StateMachine()
        sm.transition_to(DictationState.LISTENING)
        sm.transition_to(DictationState.PROCESSING)
        assert sm.transition_to(DictationState.IDLE)
        assert sm.current_state == DictationState.IDLE

    def test_error_to_idle(self):
        """Valid transition: ERROR → IDLE (recovery)."""
        sm = StateMachine()
        sm.transition_to(DictationState.ERROR)
        assert sm.transition_to(DictationState.IDLE)
        assert sm.current_state == DictationState.IDLE

    def test_invalid_transition_idle_to_processing(self):
        """Invalid transition: IDLE → PROCESSING should fail."""
        sm = StateMachine()
        assert not sm.transition_to(DictationState.PROCESSING)
        assert sm.current_state == DictationState.IDLE

    def test_invalid_transition_processing_to_listening(self):
        """Invalid transition: PROCESSING → LISTENING should fail."""
        sm = StateMachine()
        sm.transition_to(DictationState.LISTENING)
        sm.transition_to(DictationState.PROCESSING)
        assert not sm.transition_to(DictationState.LISTENING)
        assert sm.current_state == DictationState.PROCESSING

    def test_is_state(self):
        """is_state() should return True for matching state."""
        sm = StateMachine()
        assert sm.is_state(DictationState.IDLE)
        sm.transition_to(DictationState.LISTENING)
        assert sm.is_state(DictationState.LISTENING)
        assert not sm.is_state(DictationState.IDLE)

    def test_thread_safety(self):
        """Concurrent transitions should not corrupt state."""
        sm = StateMachine()
        errors: list[Exception] = []

        def transition_loop():
            try:
                for _ in range(100):
                    sm.transition_to(DictationState.LISTENING)
                    sm.transition_to(DictationState.PROCESSING)
                    sm.transition_to(DictationState.IDLE)
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=transition_loop) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert sm.current_state in (
            DictationState.IDLE,
            DictationState.LISTENING,
            DictationState.PROCESSING,
        )

    def test_wait_for_state(self):
        """wait_for_state() should block until state changes."""
        sm = StateMachine()
        result: list[bool] = []

        def wait_and_check():
            result.append(sm.wait_for_state(DictationState.LISTENING, timeout=2.0))

        thread = threading.Thread(target=wait_and_check)
        thread.start()

        time.sleep(0.1)
        sm.transition_to(DictationState.LISTENING)

        thread.join(timeout=3.0)
        assert result == [True]

    def test_wait_for_state_timeout(self):
        """wait_for_state() should return False on timeout."""
        sm = StateMachine()
        result = sm.wait_for_state(DictationState.LISTENING, timeout=0.1)
        assert result is False

    def test_transition_to_same_state_is_noop(self):
        """Transitioning to the current state should succeed (no-op)."""
        sm = StateMachine()
        assert sm.transition_to(DictationState.IDLE)
        assert sm.current_state == DictationState.IDLE
