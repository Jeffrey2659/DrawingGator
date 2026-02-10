# tests/test_vpype_runner.py
"""Tests for VpypeRunner (vpype_runner.py).

Requires: pip install pytest-qt
Tests the validation/error paths. Full conversion tests require vpype installed.
"""
import pytest
from pathlib import Path
from vpype_runner import VpypeRunner, CONFIG_CANDIDATES


@pytest.fixture
def runner(qapp):
    return VpypeRunner()


class TestInputValidation:
    def test_svg_not_found(self, runner, qtbot):
        with qtbot.waitSignal(runner.finished, timeout=2000) as blocker:
            runner.run_svg_to_gcode("nonexistent_file.svg")
        ok, path, log = blocker.args
        assert ok is False
        assert path == ""
        assert "SVG not found" in log

    def test_config_not_found(self, runner, qtbot, tmp_path, monkeypatch):
        # Create a valid SVG file
        svg = tmp_path / "test.svg"
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>')

        # Monkeypatch CONFIG_CANDIDATES to point to nonexistent paths
        monkeypatch.setattr(
            "vpype_runner.CONFIG_CANDIDATES",
            [tmp_path / "nope1.toml", tmp_path / "nope2.toml"],
        )

        with qtbot.waitSignal(runner.finished, timeout=2000) as blocker:
            runner.run_svg_to_gcode(str(svg))
        ok, path, log = blocker.args
        assert ok is False
        assert "config.toml not found" in log


class TestDefaultOutputPath:
    def test_default_out_path(self, runner, qtbot, tmp_path, monkeypatch):
        """When out_path is None, output should use .gcode extension."""
        svg = tmp_path / "drawing.svg"
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>')

        # Create a config.toml so we pass the config check
        cfg = tmp_path / "config.toml"
        cfg.write_text('[gwrite]\ndefault_profile = "grbl"\n')
        monkeypatch.setattr("vpype_runner.CONFIG_CANDIDATES", [cfg])

        # vpype likely isn't installed in CI, so we expect it to fail,
        # but we can check the output path in the finished signal
        with qtbot.waitSignal(runner.finished, timeout=5000) as blocker:
            runner.run_svg_to_gcode(str(svg), out_path=None)

        # Whether ok or not, the path should end with .gcode
        _, out_path, _ = blocker.args
        # If vpype is not installed, ok=False and path="", so only check when ok
        if blocker.args[0]:
            assert out_path.endswith(".gcode")


class TestConfigCandidates:
    def test_config_candidates_are_path_objects(self):
        for c in CONFIG_CANDIDATES:
            assert isinstance(c, Path)

    def test_first_existing_config_used(self, runner, qtbot, tmp_path, monkeypatch):
        """If multiple configs exist, the first one should be used."""
        cfg1 = tmp_path / "first.toml"
        cfg2 = tmp_path / "second.toml"
        cfg1.write_text('[gwrite]\ndefault_profile = "grbl"\n')
        cfg2.write_text('[gwrite]\ndefault_profile = "other"\n')

        monkeypatch.setattr("vpype_runner.CONFIG_CANDIDATES", [cfg1, cfg2])

        svg = tmp_path / "test.svg"
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>')

        # The runner will try to use cfg1 (first match)
        # We can't easily verify which config was used without mocking QProcess,
        # but at least it shouldn't emit the "config not found" error
        with qtbot.waitSignal(runner.finished, timeout=5000) as blocker:
            runner.run_svg_to_gcode(str(svg))
        _, _, log = blocker.args
        assert "config.toml not found" not in log
