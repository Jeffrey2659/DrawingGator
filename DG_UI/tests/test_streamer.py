# tests/test_streamer.py
"""Tests for GCodeStreamer (gcode_streamer.py).

Requires: pip install pytest-qt
These tests use a mock serial service to avoid needing hardware.
"""
import pytest
from PyQt6.QtCore import QObject, pyqtSignal

from gcode_streamer import GCodeStreamer


class MockSerialService(QObject):
    """Minimal mock that mimics SerialService's interface for the streamer."""
    dataReceived = pyqtSignal(bytes)

    def __init__(self):
        super().__init__()
        self._open = True
        self.written: list[bytes] = []

    def is_open(self) -> bool:
        return self._open

    def write(self, data: bytes) -> int:
        self.written.append(data)
        return len(data)

    def send_ok(self):
        """Simulate the device responding with 'ok'."""
        self.dataReceived.emit(b"ok\r\n")

    def send_response(self, text: str):
        """Simulate an arbitrary device response."""
        self.dataReceived.emit((text + "\r\n").encode("ascii"))


@pytest.fixture
def mock_serial():
    return MockSerialService()


@pytest.fixture
def streamer(mock_serial):
    return GCodeStreamer(mock_serial)


def _lines(*texts: str) -> list[bytes]:
    return [(t + "\r\n").encode("ascii") for t in texts]


class TestStartConditions:
    def test_empty_list_finishes_immediately(self, streamer, qtbot):
        with qtbot.waitSignal(streamer.finished, timeout=1000):
            streamer.start([])

    def test_serial_not_open_finishes_immediately(self, mock_serial, qtbot):
        mock_serial._open = False
        s = GCodeStreamer(mock_serial)
        with qtbot.waitSignal(s.finished, timeout=1000):
            s.start(_lines("G0 X0 Y0"))

    def test_none_input_finishes_immediately(self, streamer, qtbot):
        with qtbot.waitSignal(streamer.finished, timeout=1000):
            streamer.start(None)


class TestNormalFlow:
    def test_sends_first_line_on_start(self, streamer, mock_serial):
        lines = _lines("G0 X0 Y0", "G1 X5 Y5")
        streamer.start(lines)
        assert len(mock_serial.written) == 1
        assert b"G0 X0 Y0" in mock_serial.written[0]

    def test_sends_next_line_after_ok(self, streamer, mock_serial):
        lines = _lines("G0 X0 Y0", "G1 X5 Y5", "G1 X10 Y10")
        streamer.start(lines)
        assert len(mock_serial.written) == 1

        mock_serial.send_ok()
        assert len(mock_serial.written) == 2
        assert b"G1 X5 Y5" in mock_serial.written[1]

    def test_complete_stream(self, streamer, mock_serial, qtbot):
        lines = _lines("G0 X0 Y0", "G1 X5 Y5", "G1 X10 Y10")
        streamer.start(lines)

        # Send ok for each line, last ok triggers finished
        mock_serial.send_ok()  # advances to line 2
        mock_serial.send_ok()  # advances to line 3

        with qtbot.waitSignal(streamer.finished, timeout=1000):
            mock_serial.send_ok()  # line 3 done -> finished

        assert len(mock_serial.written) == 3

    def test_progress_signals(self, streamer, mock_serial, qtbot):
        lines = _lines("G0 X0 Y0", "G1 X5 Y5")
        progress_values = []
        streamer.progress.connect(lambda sent, total: progress_values.append((sent, total)))

        streamer.start(lines)
        # First line sent on start -> progress(1, 2)
        assert progress_values == [(1, 2)]

        mock_serial.send_ok()
        # Second line sent -> progress(2, 2)
        assert progress_values == [(1, 2), (2, 2)]


class TestFlowControl:
    def test_no_double_send_while_awaiting_ok(self, streamer, mock_serial):
        lines = _lines("G0 X0 Y0", "G1 X5 Y5")
        streamer.start(lines)
        assert len(mock_serial.written) == 1

        # Manually call _try_send_next (simulates timer firing)
        streamer._try_send_next()
        streamer._try_send_next()
        streamer._try_send_next()
        # Should still only have 1 line sent (awaiting_ok blocks it)
        assert len(mock_serial.written) == 1

    def test_error_response_advances(self, streamer, mock_serial):
        lines = _lines("G0 X0 Y0", "G1 X5 Y5")
        streamer.start(lines)
        assert len(mock_serial.written) == 1

        mock_serial.send_response("error:20")
        # error: is a terminal token, should advance to next line
        assert len(mock_serial.written) == 2

    def test_alarm_response_advances(self, streamer, mock_serial):
        lines = _lines("G0 X0 Y0", "G1 X5 Y5")
        streamer.start(lines)

        mock_serial.send_response("alarm:1")
        assert len(mock_serial.written) == 2

    def test_start_token_advances(self, streamer, mock_serial):
        lines = _lines("G0 X0 Y0", "G1 X5 Y5")
        streamer.start(lines)

        mock_serial.send_response("start")
        assert len(mock_serial.written) == 2


class TestPauseResume:
    def test_pause_stops_sending(self, streamer, mock_serial, qtbot):
        lines = _lines("G0 X0 Y0", "G1 X5 Y5", "G1 X10 Y10")
        streamer.start(lines)
        assert len(mock_serial.written) == 1

        streamer.pause()
        assert streamer.is_paused()

        # Send ok while paused -- should NOT advance
        mock_serial.send_ok()
        # awaiting_ok is cleared, but _try_send_next returns early due to pause
        # The ok processing clears awaiting_ok and calls _try_send_next,
        # but _try_send_next checks paused first
        assert len(mock_serial.written) == 1

    def test_resume_continues(self, streamer, mock_serial):
        lines = _lines("G0 X0 Y0", "G1 X5 Y5", "G1 X10 Y10")
        streamer.start(lines)

        mock_serial.send_ok()  # line 1 done, line 2 sent
        assert len(mock_serial.written) == 2

        streamer.pause()
        mock_serial.send_ok()  # ok while paused, clears awaiting_ok but no send

        streamer.resume()
        # resume calls _try_send_next, which should now send line 3
        assert len(mock_serial.written) == 3
        assert not streamer.is_paused()

    def test_resume_when_not_paused_is_noop(self, streamer, mock_serial):
        lines = _lines("G0 X0 Y0")
        streamer.start(lines)
        count_before = len(mock_serial.written)
        streamer.resume()  # not paused, should be a no-op
        assert len(mock_serial.written) == count_before

    def test_pause_emits_signal(self, streamer, mock_serial, qtbot):
        lines = _lines("G0 X0 Y0")
        streamer.start(lines)

        with qtbot.waitSignal(streamer.pausedChanged, timeout=1000) as blocker:
            streamer.pause()
        assert blocker.args == [True]

        with qtbot.waitSignal(streamer.pausedChanged, timeout=1000) as blocker:
            streamer.resume()
        assert blocker.args == [False]


class TestRxBuffering:
    def test_fragmented_ok(self, streamer, mock_serial):
        """'ok' split across two data chunks."""
        lines = _lines("G0 X0 Y0", "G1 X5 Y5")
        streamer.start(lines)
        assert len(mock_serial.written) == 1

        # Send 'ok' in two fragments
        mock_serial.dataReceived.emit(b"o")
        assert len(mock_serial.written) == 1  # not yet
        mock_serial.dataReceived.emit(b"k\r\n")
        assert len(mock_serial.written) == 2  # now advanced

    def test_two_oks_in_one_chunk(self, streamer, mock_serial):
        """Two 'ok' responses arrive in a single data chunk."""
        lines = _lines("G0 X0 Y0", "G1 X5 Y5", "G1 X10 Y10")
        streamer.start(lines)
        assert len(mock_serial.written) == 1

        # Two oks at once
        mock_serial.dataReceived.emit(b"ok\r\nok\r\n")
        # Should advance twice: line 2 sent after first ok, line 3 sent after second ok
        assert len(mock_serial.written) == 3

    def test_blank_lines_in_rx_ignored(self, streamer, mock_serial):
        """Empty lines in device response should not count as ok."""
        lines = _lines("G0 X0 Y0", "G1 X5 Y5")
        streamer.start(lines)

        mock_serial.dataReceived.emit(b"\r\n\r\n")
        # No ok token, should not advance
        assert len(mock_serial.written) == 1


class TestStop:
    def test_stop_resets_state(self, streamer, mock_serial):
        lines = _lines("G0 X0 Y0", "G1 X5 Y5", "G1 X10 Y10")
        streamer.start(lines)
        mock_serial.send_ok()
        assert len(mock_serial.written) == 2

        streamer.stop()
        assert streamer.idx == 0
        assert streamer.lines == []
        assert not streamer.awaiting_ok
        assert not streamer.is_paused()

    def test_stop_does_not_reset_total(self, streamer, mock_serial):
        """BUG: stop() clears lines and idx but not total.

        This means a late 'ok' after stop() causes an IndexError in
        _try_send_next() because idx(0) < total(old value) but lines is [].
        Fix: add `self.total = 0` to stop().
        """
        lines = _lines("G0 X0 Y0", "G1 X5 Y5")
        streamer.start(lines)
        streamer.stop()
        # total is NOT reset — this documents the bug
        assert streamer.total == 2  # should be 0 after fix

    @pytest.mark.xfail(
        reason="BUG: stop() doesn't reset self.total, causing IndexError on late ok",
        strict=True,
    )
    def test_stop_then_late_ok_causes_index_error(self, streamer, mock_serial, qtbot):
        """Demonstrates the stop() bug: late ok after stop triggers IndexError.

        The IndexError occurs inside Qt's event loop (in _on_data -> _try_send_next),
        so pytest.raises can't catch it directly. pytest-qt captures it and fails
        the test at teardown, which is expected. Marked xfail until the bug is fixed.
        Fix: add `self.total = 0` to GCodeStreamer.stop().
        """
        lines = _lines("G0 X0 Y0", "G1 X5 Y5")
        streamer.start(lines)
        streamer.stop()

        # A late "ok" arrives — triggers IndexError in the Qt event loop
        mock_serial.send_ok()
