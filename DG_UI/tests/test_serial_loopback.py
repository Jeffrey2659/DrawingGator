# tests/test_serial_loopback.py
"""Tests for SerialService using pyserial's loop:// virtual port.

Requires: pip install pytest-qt
No hardware needed -- uses pyserial's built-in loopback.

NOTE: The loop:// port may fail to open depending on platform/pyserial version.
Tests that need a loopback connection are skipped if open() fails.
"""
import pytest
import serial
from serial_service import SerialService


def _loopback_available() -> bool:
    """Check if pyserial's loop:// virtual port can be opened."""
    try:
        s = serial.Serial("loop://", 9600, timeout=0.1)
        s.close()
        return True
    except Exception:
        return False


loopback = pytest.mark.skipif(
    not _loopback_available(),
    reason="pyserial loop:// port not available on this platform",
)


@pytest.fixture
def svc(qapp):
    s = SerialService()
    yield s
    s.close()


class TestAvailablePorts:
    def test_returns_list(self, svc):
        ports = svc.available_ports()
        assert isinstance(ports, list)
        # Each entry is (label, device_path)
        for label, path in ports:
            assert isinstance(label, str)
            assert isinstance(path, str)


class TestOpenClose:
    @loopback
    def test_open_loopback(self, svc, qtbot):
        with qtbot.waitSignal(svc.connectionChanged, timeout=2000) as blocker:
            result = svc.open("loop://", 9600)
        assert result is True
        assert svc.is_open()
        assert blocker.args[0] is True  # connected=True

    @loopback
    def test_close_emits_signal(self, svc, qtbot):
        svc.open("loop://", 9600)
        with qtbot.waitSignal(svc.connectionChanged, timeout=2000) as blocker:
            svc.close()
        assert not svc.is_open()
        assert blocker.args[0] is False  # connected=False

    @loopback
    def test_double_close_no_crash(self, svc):
        svc.open("loop://", 9600)
        svc.close()
        svc.close()  # should not raise
        assert not svc.is_open()

    def test_open_invalid_port(self, svc, qtbot):
        with qtbot.waitSignal(svc.errorText, timeout=2000):
            result = svc.open("NONEXISTENT_PORT_XYZ", 9600)
        assert result is False
        assert not svc.is_open()

    @loopback
    def test_reopen_cleans_previous(self, svc, qtbot):
        svc.open("loop://", 9600)
        assert svc.is_open()
        # Open again -- should close the first one cleanly
        svc.open("loop://", 9600)
        assert svc.is_open()
        svc.close()
        assert not svc.is_open()


class TestWriteWhenClosed:
    def test_write_not_open_returns_zero(self, svc, qtbot):
        with qtbot.waitSignal(svc.errorText, timeout=2000):
            n = svc.write(b"hello")
        assert n == 0


class TestLoopbackEcho:
    @loopback
    def test_echo(self, svc, qtbot):
        """Write data to loopback port, expect the same bytes back."""
        svc.open("loop://", 9600)

        with qtbot.waitSignal(svc.dataReceived, timeout=3000) as blocker:
            svc.write(b"G0 X0 Y0\r\n")

        # loopback echoes what we write
        assert b"G0 X0 Y0" in blocker.args[0]

    @loopback
    def test_multiple_writes(self, svc, qtbot):
        """Multiple writes should all be echoed back."""
        svc.open("loop://", 9600)
        received = bytearray()

        def on_rx(data):
            received.extend(data)

        svc.dataReceived.connect(on_rx)
        svc.write(b"line1\r\n")
        svc.write(b"line2\r\n")

        # Wait for data to arrive (polling interval is 20ms)
        qtbot.waitUntil(
            lambda: b"line1" in received and b"line2" in received,
            timeout=3000,
        )
        assert b"line1" in received
        assert b"line2" in received
