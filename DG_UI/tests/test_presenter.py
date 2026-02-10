# tests/test_presenter.py
"""Tests for Presenter logic (presenter.py).

Requires: pip install pytest-qt
Uses mock View and SerialService to isolate Presenter behavior.
"""
import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QObject, pyqtSignal

from model import GCodeModel
from serial_service import SerialService
from presenter import Presenter


class MockView:
    """Stub view that records all calls made by the Presenter."""

    def __init__(self):
        self.logs: list[str] = []
        self.warnings: list[str] = []
        self.ports_set: list[list[str]] = []
        self.connected_calls: list[tuple[bool, str]] = []
        self.progress_calls: list[tuple[int, int]] = []
        self.mpl_widget = MagicMock()

        # Callbacks the Presenter will overwrite
        self.on_refresh_clicked = None
        self.on_connect_clicked = None
        self.on_upload_clicked = None
        self.on_send_clicked = None
        self.on_upload_svg = None
        self.on_manual_send = None
        self.on_pause_clicked = None
        self.on_resume_clicked = None

    def set_ports(self, ports):
        self.ports_set.append(ports)

    def set_connected(self, ok, desc):
        self.connected_calls.append((ok, desc))

    def set_progress(self, sent, total):
        self.progress_calls.append((sent, total))

    def log(self, msg):
        self.logs.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def ask_open_file(self):
        return None

    def current_port(self):
        return "COM3  (USB Serial)"

    def current_baud(self):
        return 9600


@pytest.fixture
def mock_view():
    return MockView()


@pytest.fixture
def model():
    return GCodeModel()


@pytest.fixture
def serial_service(qapp):
    """Real SerialService but we won't open any ports."""
    return SerialService()


@pytest.fixture
def presenter(mock_view, serial_service, model):
    """Create a Presenter wired to mock view."""
    # Patch the svg_algorithm import since it may not be on path
    with patch("presenter.conversion_svg", return_value=([], 100, 100, 6, 8, 15, 20, "out.svg")), \
         patch("presenter.extract_coordinates", return_value=([], 0)):
        p = Presenter(mock_view, serial_service, model)
    return p


class TestCallbackWiring:
    def test_callbacks_assigned(self, presenter, mock_view):
        assert mock_view.on_refresh_clicked is not None
        assert mock_view.on_connect_clicked is not None
        assert mock_view.on_upload_clicked is not None
        assert mock_view.on_send_clicked is not None
        assert mock_view.on_manual_send is not None


class TestHandleRefresh:
    def test_refresh_sets_ports(self, presenter, mock_view, serial_service):
        presenter.handle_refresh()
        assert len(mock_view.ports_set) >= 1
        # The last call to set_ports should be a list (could be empty)
        assert isinstance(mock_view.ports_set[-1], list)

    def test_refresh_no_ports_logs_message(self, presenter, mock_view, serial_service):
        # On a machine with no serial ports, should log a helpful message
        presenter.handle_refresh()
        if not mock_view.ports_set[-1]:
            assert any("No serial ports" in msg for msg in mock_view.logs)


class TestHandleConnectToggle:
    def test_connect_empty_port_warns(self, presenter, mock_view):
        mock_view.current_port = lambda: "   "
        presenter.handle_connect_toggle()
        assert any("Select a port" in w for w in mock_view.warnings)

    def test_connect_baud_typo_corrected(self, presenter, mock_view, serial_service):
        mock_view.current_baud = lambda: 1115200
        # open() will fail since COM3 likely doesn't exist,
        # but we verify the baud was corrected internally
        with patch.object(serial_service, "open", return_value=False) as mock_open:
            presenter.handle_connect_toggle()
            mock_open.assert_called_once_with("COM3", 115200)

    def test_disconnect_when_open(self, presenter, serial_service):
        with patch.object(serial_service, "is_open", return_value=True), \
             patch.object(serial_service, "close") as mock_close:
            presenter.handle_connect_toggle()
            mock_close.assert_called_once()


class TestHandleSend:
    def test_send_not_connected_warns(self, presenter, mock_view, serial_service):
        # serial is not open
        presenter.handle_send()
        assert any("Not connected" in w for w in mock_view.warnings)

    def test_send_no_gcode_warns(self, presenter, mock_view, serial_service):
        with patch.object(serial_service, "is_open", return_value=True):
            presenter.handle_send()
        assert any("No G-code" in w for w in mock_view.warnings)

    def test_send_with_gcode_starts_stream(self, presenter, mock_view, model, serial_service, tmp_path):
        # Load some gcode
        f = tmp_path / "test.gcode"
        f.write_text("G0 X0 Y0\nG1 X5 Y5\n")
        model.load_from_file(str(f))

        with patch.object(serial_service, "is_open", return_value=True), \
             patch.object(presenter.streamer, "start") as mock_start:
            presenter.handle_send()
            mock_start.assert_called_once_with(model.lines)


class TestHandleUpload:
    def test_upload_cancelled(self, presenter, mock_view):
        mock_view.ask_open_file = lambda: None
        presenter.handle_upload()
        # No warnings, no errors -- just a no-op
        assert not mock_view.warnings

    def test_upload_loads_model(self, presenter, mock_view, model, tmp_path):
        f = tmp_path / "test.gcode"
        f.write_text("G0 X0 Y0\nG1 X5 Y5\n")
        mock_view.ask_open_file = lambda: str(f)
        presenter.handle_upload()
        assert model.total == 2
        assert any("Loaded 2 lines" in msg for msg in mock_view.logs)

    def test_upload_updates_progress(self, presenter, mock_view, tmp_path):
        f = tmp_path / "test.gcode"
        f.write_text("G0 X0 Y0\nG1 X5 Y5\nG1 X10 Y10\n")
        mock_view.ask_open_file = lambda: str(f)
        presenter.handle_upload()
        # set_progress(0, total) should have been called
        assert (0, 3) in mock_view.progress_calls

    def test_upload_updates_preview(self, presenter, mock_view, tmp_path):
        f = tmp_path / "drawing.gcode"
        f.write_text(
            "M3 S70\nG00 X1 Y1\nM3 S250\nG01 X2 Y2\nG01 X3 Y3\nM3 S70\n"
        )
        mock_view.ask_open_file = lambda: str(f)
        presenter.handle_upload()
        # mpl_widget.plot_svg should have been called
        mock_view.mpl_widget.plot_svg.assert_called()


class TestHandleManualSend:
    def test_manual_send_not_connected(self, presenter, mock_view, serial_service):
        presenter.handle_manual_send("G0 X0 Y0")
        assert any("Not connected" in w for w in mock_view.warnings)

    def test_manual_send_empty_string(self, presenter, mock_view, serial_service):
        with patch.object(serial_service, "is_open", return_value=True):
            presenter.handle_manual_send("   ")
        # Empty after strip, should not call write
        # No warnings or errors expected
        assert not mock_view.warnings

    def test_manual_send_appends_crlf(self, presenter, mock_view, serial_service):
        with patch.object(serial_service, "is_open", return_value=True), \
             patch.object(serial_service, "write", return_value=10) as mock_write:
            presenter.handle_manual_send("G0 X0 Y0")
            mock_write.assert_called_once()
            data = mock_write.call_args[0][0]
            assert data.endswith(b"\r\n")

    def test_manual_send_normalizes_lone_lf(self, presenter, mock_view, serial_service):
        with patch.object(serial_service, "is_open", return_value=True), \
             patch.object(serial_service, "write", return_value=10) as mock_write:
            presenter.handle_manual_send("G0 X0 Y0\n")
            data = mock_write.call_args[0][0]
            assert data.endswith(b"\r\n")
            assert not data.endswith(b"\n\r\n")


class TestRxHandling:
    def test_handle_rx_line_normal(self, presenter, mock_view):
        presenter._handle_rx_line("ok")
        assert "<< ok" in mock_view.logs

    def test_handle_rx_line_state_block(self, presenter, mock_view):
        presenter._handle_rx_line("Printing State:")
        presenter._handle_rx_line("X: 0.00")
        presenter._handle_rx_line("Y: 0.00")
        presenter._handle_rx_line("End of States")
        # All lines should be in one block
        block_log = [msg for msg in mock_view.logs if "Printing State" in msg]
        assert len(block_log) == 1
        assert "X: 0.00" in block_log[0]
        assert "End of States" in block_log[0]

    def test_fragmented_rx_buffering(self, presenter, mock_view):
        """Data arriving in fragments should be buffered until newline."""
        presenter._on_device_data(b"o")
        presenter._on_device_data(b"k")
        # No complete line yet
        assert "<< ok" not in mock_view.logs

        presenter._on_device_data(b"\r\n")
        assert "<< ok" in mock_view.logs

    def test_multiple_lines_in_one_chunk(self, presenter, mock_view):
        presenter._on_device_data(b"ok\r\nerror:20\r\n")
        assert "<< ok" in mock_view.logs
        assert "<< error:20" in mock_view.logs

    def test_empty_lines_filtered(self, presenter, mock_view):
        presenter._on_device_data(b"\r\n\r\n")
        # Blank lines should not produce log entries
        assert not any(msg.startswith("<< ") for msg in mock_view.logs)


class TestOnProgress:
    def test_progress_updates_model_and_view(self, presenter, mock_view, model, tmp_path):
        f = tmp_path / "test.gcode"
        f.write_text("G0 X0 Y0\nG1 X5 Y5\n")
        model.load_from_file(str(f))

        presenter._on_progress(1, 2)
        assert model.sent == 1
        assert (1, 2) in mock_view.progress_calls

    def test_finished_sets_full_progress(self, presenter, mock_view, model, tmp_path):
        f = tmp_path / "test.gcode"
        f.write_text("G0 X0 Y0\nG1 X5 Y5\n")
        model.load_from_file(str(f))

        presenter._on_finished()
        assert (model.total, max(1, model.total)) in mock_view.progress_calls
        assert any("Stream complete" in msg for msg in mock_view.logs)


class TestVpypeFinished:
    def test_vpype_success_loads_model(self, presenter, mock_view, model, tmp_path):
        gcode_file = tmp_path / "output.gcode"
        gcode_file.write_text("G0 X0 Y0\nG1 X5 Y5\n")

        presenter._on_vpype_finished(True, str(gcode_file), "vpype log output")
        assert model.total == 2
        assert any("Loaded 2 lines" in msg for msg in mock_view.logs)

    def test_vpype_failure_warns(self, presenter, mock_view):
        presenter._on_vpype_finished(False, "", "some error")
        assert any("vpype conversion failed" in w for w in mock_view.warnings)

    def test_vpype_log_displayed(self, presenter, mock_view, tmp_path):
        gcode_file = tmp_path / "output.gcode"
        gcode_file.write_text("G0 X0 Y0\n")
        presenter._on_vpype_finished(True, str(gcode_file), "Processing complete")
        assert any("Processing complete" in msg for msg in mock_view.logs)
