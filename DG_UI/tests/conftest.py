# tests/conftest.py
"""Shared fixtures for DG_UI tests."""
import sys
from pathlib import Path

# Add DG_UI to sys.path so we can import model, presenter, etc.
_dg_ui = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_dg_ui))
# Add the DrawingGator root so "Interface.svg_algorithm" imports work
sys.path.insert(0, str(_dg_ui.parent))

import pytest


@pytest.fixture
def tmp_gcode(tmp_path):
    """Create a small .gcode file and return its path."""
    f = tmp_path / "test.gcode"
    f.write_text(
        "G20\n"
        "G90\n"
        "; this is a comment\n"
        "G92 X0 Y0\n"
        "M3 S70\n"
        "G00 X1 Y1\n"
        "M3 S250\n"
        "G01 X2 Y2\n"
        "G01 X3 Y3\n"
        "M3 S70\n"
        "G00 X0 Y0\n",
        encoding="utf-8",
    )
    return f


@pytest.fixture
def tmp_gcode_comments(tmp_path):
    """G-code file with inline comments and blank lines."""
    f = tmp_path / "comments.gcode"
    f.write_text(
        "; full line comment\n"
        "\n"
        "G0 X5 Y5 ; inline comment\n"
        "  ; indented comment\n"
        "G1 X10 Y10\n",
        encoding="utf-8",
    )
    return f


@pytest.fixture
def tmp_gcode_empty(tmp_path):
    """G-code file with only comments and blanks."""
    f = tmp_path / "empty.gcode"
    f.write_text(
        "; comment 1\n"
        "; comment 2\n"
        "\n"
        "\n",
        encoding="utf-8",
    )
    return f
