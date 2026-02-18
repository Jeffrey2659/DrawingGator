# tests/test_model.py
"""Tests for GCodeModel (model.py)."""
import pytest
from model import GCodeModel


class TestLoadFromFile:
    def test_loads_correct_line_count(self, tmp_gcode):
        m = GCodeModel()
        count = m.load_from_file(str(tmp_gcode))
        # 7 non-comment, non-blank lines: G20, G90, G92, M3 S70, G00, M3 S250, G01 x2, G01 x3, M3 S70, G00
        # Let's count: G20, G90, G92 X0 Y0, M3 S70, G00 X1 Y1, M3 S250, G01 X2 Y2, G01 X3 Y3, M3 S70, G00 X0 Y0
        assert count == 10
        assert m.total == 10

    def test_lines_are_bytes(self, tmp_gcode):
        m = GCodeModel()
        m.load_from_file(str(tmp_gcode))
        for line in m.lines:
            assert isinstance(line, bytes)

    def test_lines_end_with_crlf(self, tmp_gcode):
        m = GCodeModel()
        m.load_from_file(str(tmp_gcode))
        for line in m.lines:
            assert line.endswith(b"\r\n")

    def test_comments_stripped(self, tmp_gcode):
        m = GCodeModel()
        m.load_from_file(str(tmp_gcode))
        for line in m.lines:
            text = line.decode("ascii").strip()
            assert not text.startswith(";")

    def test_inline_comments_stripped(self, tmp_gcode_comments):
        m = GCodeModel()
        m.load_from_file(str(tmp_gcode_comments))
        for line in m.lines:
            text = line.decode("ascii").strip()
            assert ";" not in text

    def test_inline_comment_preserves_command(self, tmp_gcode_comments):
        m = GCodeModel()
        m.load_from_file(str(tmp_gcode_comments))
        # "G0 X5 Y5 ; inline comment" should become "G0 X5 Y5"
        texts = [l.decode("ascii").strip() for l in m.lines]
        assert "G0 X5 Y5" in texts

    def test_blank_lines_skipped(self, tmp_gcode_comments):
        m = GCodeModel()
        m.load_from_file(str(tmp_gcode_comments))
        for line in m.lines:
            text = line.decode("ascii").strip()
            assert len(text) > 0

    def test_empty_file_returns_zero(self, tmp_gcode_empty):
        m = GCodeModel()
        count = m.load_from_file(str(tmp_gcode_empty))
        assert count == 0
        assert m.total == 0
        assert m.lines == []

    def test_nonexistent_file_raises(self, tmp_path):
        m = GCodeModel()
        with pytest.raises(FileNotFoundError):
            m.load_from_file(str(tmp_path / "does_not_exist.gcode"))

    def test_loaded_name(self, tmp_gcode):
        m = GCodeModel()
        m.load_from_file(str(tmp_gcode))
        assert m.loaded_name == "test.gcode"

    def test_reloading_resets_state(self, tmp_gcode, tmp_gcode_comments):
        m = GCodeModel()
        m.load_from_file(str(tmp_gcode))
        m.sent = 5
        m.paused = True
        m.load_from_file(str(tmp_gcode_comments))
        assert m.sent == 0
        assert m.paused is False
        # Line count should reflect the second file
        assert m.loaded_name == "comments.gcode"


class TestResetJobCounters:
    def test_resets_sent_and_paused(self, tmp_gcode):
        m = GCodeModel()
        m.load_from_file(str(tmp_gcode))
        m.sent = 7
        m.paused = True
        m.reset_job_counters()
        assert m.sent == 0
        assert m.paused is False

    def test_lines_preserved_after_reset(self, tmp_gcode):
        m = GCodeModel()
        m.load_from_file(str(tmp_gcode))
        original_lines = list(m.lines)
        m.sent = 5
        m.reset_job_counters()
        assert m.lines == original_lines
        assert m.total == len(original_lines)
