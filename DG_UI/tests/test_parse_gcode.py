# tests/test_parse_gcode.py
"""Tests for parse_gcode_to_strokes() in presenter.py."""
import pytest
from presenter import parse_gcode_to_strokes


def _lines(*texts: str) -> list[bytes]:
    """Helper: convert string G-code lines to bytes (as model produces them)."""
    return [(t + "\r\n").encode("ascii") for t in texts]


class TestBasicStrokes:
    def test_single_stroke(self):
        data = _lines(
            "M3 S70",       # pen up
            "G00 X1 Y1",   # travel
            "M3 S250",     # pen down
            "G01 X2 Y2",   # draw
            "G01 X3 Y3",   # draw
            "M3 S70",      # pen up
        )
        strokes = parse_gcode_to_strokes(data)
        assert len(strokes) == 1
        # Stroke starts at (1,1) where pen went down, then moves to (2,2) and (3,3)
        assert strokes[0][0] == (1.0, 1.0)
        assert strokes[0][1] == (2.0, 2.0)
        assert strokes[0][2] == (3.0, 3.0)

    def test_two_strokes(self):
        data = _lines(
            "M3 S250",     # pen down at origin
            "G01 X1 Y1",
            "G01 X2 Y2",
            "M3 S70",      # pen up
            "G00 X5 Y5",   # travel
            "M3 S250",     # pen down
            "G01 X6 Y6",
            "G01 X7 Y7",
            "M3 S70",      # pen up
        )
        strokes = parse_gcode_to_strokes(data)
        assert len(strokes) == 2

    def test_empty_input(self):
        strokes = parse_gcode_to_strokes([])
        assert strokes == []

    def test_no_drawing_commands(self):
        data = _lines("G20", "G90", "G92 X0 Y0")
        strokes = parse_gcode_to_strokes(data)
        assert strokes == []


class TestPenUpDown:
    def test_s70_is_pen_up(self):
        data = _lines(
            "M3 S250",     # pen down
            "G01 X1 Y1",
            "M3 S70",      # pen up
            "G00 X5 Y5",   # travel (pen is up)
        )
        strokes = parse_gcode_to_strokes(data)
        # Only one stroke: (0,0)->(1,1)
        assert len(strokes) == 1

    def test_s100_is_pen_up(self):
        """S <= 100 should be treated as pen up."""
        data = _lines(
            "M3 S100",     # pen up (boundary: <= 100)
            "G01 X1 Y1",
        )
        strokes = parse_gcode_to_strokes(data)
        assert strokes == []  # pen never went down

    def test_s101_is_pen_down(self):
        """S > 100 should be treated as pen down."""
        data = _lines(
            "M3 S101",     # pen down (boundary: > 100)
            "G01 X1 Y1",
            "G01 X2 Y2",
            "M3 S70",
        )
        strokes = parse_gcode_to_strokes(data)
        assert len(strokes) == 1

    def test_pen_down_without_moves(self):
        """Pen down then immediately up — current code appends single-point strokes.

        BUG: The pen-up handler (line 58-60 in presenter.py) appends
        current_stroke without checking len > 1, unlike the end-of-function
        guard. This means single-point strokes leak through. Uncomment the
        stricter assertion once the bug is fixed.
        """
        data = _lines(
            "M3 S250",     # pen down
            "M3 S70",      # pen up immediately
        )
        strokes = parse_gcode_to_strokes(data)
        # Current behavior: single-point stroke [(0,0)] IS appended
        assert len(strokes) == 1
        assert len(strokes[0]) == 1
        # After fix, this should be: assert strokes == []


class TestCoordinateParsing:
    def test_negative_coordinates(self):
        data = _lines(
            "M3 S250",
            "G01 X-5 Y-10",
            "G01 X-3.5 Y-7.25",
            "M3 S70",
        )
        strokes = parse_gcode_to_strokes(data)
        assert len(strokes) == 1
        assert strokes[0][1] == (-5.0, -10.0)
        assert strokes[0][2] == (-3.5, -7.25)

    def test_decimal_coordinates(self):
        data = _lines(
            "M3 S250",
            "G01 X1.2345 Y6.7890",
            "G01 X0.0001 Y99.9999",
            "M3 S70",
        )
        strokes = parse_gcode_to_strokes(data)
        assert len(strokes) == 1
        assert strokes[0][1] == pytest.approx((1.2345, 6.7890))
        assert strokes[0][2] == pytest.approx((0.0001, 99.9999))

    def test_partial_coordinates(self):
        """Only X provided — Y should keep its previous value."""
        data = _lines(
            "M3 S250",
            "G01 X5 Y10",
            "G01 X8",       # Y stays at 10
            "M3 S70",
        )
        strokes = parse_gcode_to_strokes(data)
        assert strokes[0][2] == (8.0, 10.0)

    def test_g0_with_coordinates(self):
        """G0 travel updates internal position."""
        data = _lines(
            "G00 X5 Y5",   # travel to (5,5)
            "M3 S250",     # pen down at (5,5)
            "G01 X6 Y6",
            "M3 S70",
        )
        strokes = parse_gcode_to_strokes(data)
        assert len(strokes) == 1
        assert strokes[0][0] == (5.0, 5.0)  # pen down records current pos


class TestComments:
    def test_full_line_semicolon_comment(self):
        data = _lines(
            "; this is a comment",
            "M3 S250",
            "G01 X1 Y1",
            "G01 X2 Y2",
            "M3 S70",
        )
        strokes = parse_gcode_to_strokes(data)
        assert len(strokes) == 1

    def test_inline_semicolon_comment(self):
        data = _lines(
            "M3 S250",
            "G01 X5 Y5 ; move to 5,5",
            "G01 X10 Y10",
            "M3 S70",
        )
        strokes = parse_gcode_to_strokes(data)
        assert strokes[0][1] == (5.0, 5.0)

    def test_parenthetical_comment(self):
        data = _lines(
            "M3 S250",
            "G01 X5 (test) Y10",
            "G01 X15 Y20",
            "M3 S70",
        )
        strokes = parse_gcode_to_strokes(data)
        assert strokes[0][1] == (5.0, 10.0)

    def test_full_line_paren_comment(self):
        data = _lines(
            "(this is a comment)",
            "M3 S250",
            "G01 X1 Y1",
            "G01 X2 Y2",
            "M3 S70",
        )
        strokes = parse_gcode_to_strokes(data)
        assert len(strokes) == 1


class TestEdgeCases:
    def test_g0_while_pen_is_down(self):
        """G0 during pen down should still add the point to the stroke."""
        data = _lines(
            "M3 S250",     # pen down
            "G01 X1 Y1",
            "G00 X5 Y5",  # rapid move while pen is down
            "G01 X6 Y6",
            "M3 S70",
        )
        strokes = parse_gcode_to_strokes(data)
        assert len(strokes) == 1
        points = strokes[0]
        # (5,5) should be in the stroke since pen was down during G0
        assert (5.0, 5.0) in points

    def test_last_stroke_captured_without_pen_up(self):
        """If file ends without a final pen-up, last stroke should still be captured."""
        data = _lines(
            "M3 S250",
            "G01 X1 Y1",
            "G01 X2 Y2",
            # no pen-up at end
        )
        strokes = parse_gcode_to_strokes(data)
        assert len(strokes) == 1
        assert len(strokes[0]) == 3  # origin + 2 points

    def test_non_ascii_bytes_handled(self):
        """Non-ASCII bytes should not crash the parser."""
        data = [b"\xff\xfe\r\n", b"M3 S250\r\n", b"G01 X1 Y1\r\n", b"G01 X2 Y2\r\n", b"M3 S70\r\n"]
        strokes = parse_gcode_to_strokes(data)
        assert len(strokes) == 1

    def test_mixed_case_gcode(self):
        """Parser uppercases input, so lowercase should work."""
        data = _lines(
            "m3 s250",
            "g01 x1 y1",
            "g01 x2 y2",
            "m3 s70",
        )
        strokes = parse_gcode_to_strokes(data)
        assert len(strokes) == 1

    def test_g1_without_pen_down(self):
        """G1 moves without pen down should not create strokes."""
        data = _lines(
            "G01 X5 Y5",
            "G01 X10 Y10",
        )
        strokes = parse_gcode_to_strokes(data)
        assert strokes == []

    def test_many_strokes(self):
        """Test with multiple pen up/down cycles."""
        cmds = []
        for i in range(10):
            cmds.append(f"M3 S70")
            cmds.append(f"G00 X{i*10} Y0")
            cmds.append(f"M3 S250")
            cmds.append(f"G01 X{i*10+5} Y5")
            cmds.append(f"G01 X{i*10+10} Y0")
        cmds.append("M3 S70")
        data = _lines(*cmds)
        strokes = parse_gcode_to_strokes(data)
        assert len(strokes) == 10
