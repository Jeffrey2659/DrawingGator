# vpype_runner.py
from PyQt6.QtCore import QObject, pyqtSignal, QProcess, QIODevice
from pathlib import Path
import shlex
import sys
import os
import tempfile

# _CONFIG_TOML = r"""
# [gwrite]
# default_default = "marlin"

# [gwrite.profiles.marlin]
# unit = "mm"
# absolute_coordinates = true
# pen_up_command   = "G0 Z5"
# pen_down_command = "G1 Z0"
# travel_speed = 6000
# draw_speed   = 2000
# header = ["G21","G90","M107","G0 Z5"]
# footer = ["G0 Z5","M84"]

# [gwrite.profiles.grbl]
# unit = "mm"
# absolute_coordinates = true
# pen_up_command   = "M3 S0"
# pen_down_command = "M3 S90"
# travel_speed = 3000
# draw_speed   = 1200
# header = ["G21","G90","G92 X0 Y0","M3 S0"]
# footer = ["M3 S0","M5","M2"]
# """

CONFIG_CANDIDATES = [
    Path(__file__).with_name("config.toml"),
    Path.home() / "OneDrive" / "Desktop" / "DrawingGator" / "DG_UI" /"config.toml",
]


class VpypeRunner(QObject):
    finished = pyqtSignal(bool, str, str)   # (ok, gcode_path, log_text)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._proc = None
        self._log = []
        
    
   

    def run_svg_to_gcode(self, svg_path: str, out_path: str | None = None):
        svg = Path(svg_path)
        if not svg.exists():
            self.finished.emit(False, "", f"SVG not found: {svg_path}")
            return

        if out_path is None:
            out_path = str(Path(svg_path).with_suffix(".gcode"))

        cfg_path = None
        print(f"Config candidates: {CONFIG_CANDIDATES}")
        for c in CONFIG_CANDIDATES:
            if c.exists():
                cfg_path = c
                break
        if not cfg_path:
            self.finished.emit(False, "", "config.toml not found (looked in standard locations).")
            return
        if cfg_path:
            print(f"Using config: {cfg_path}")
            print(f"Config contents:\n{cfg_path.read_text()}") 
        program = "vpype"
        args = [
            "--config", cfg_path.as_posix(),         # <-- ensure string
            "read", svg.as_posix(),
            "linemerge", "reloop", "linesort",
            "gwrite",                                 # <-- no -p; uses [gwrite].default_profile
            Path(out_path).as_posix(),
        ]

        self._log = []
        self._proc = QProcess(self)
        self._proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._proc.readyReadStandardOutput.connect(self._on_read)
        self._proc.finished.connect(lambda code, status: self._on_finished(code, status, out_path))
        self._proc.start(program, args)

    def _on_read(self):
       if not self._proc:
            return
       data = bytes(self._proc.readAllStandardOutput()).decode("utf-8", "replace")
       if data:
            self._log.append(data)
    def _on_finished(self, code, status, out_path: str):
        ok = (code == 0)
        self.finished.emit(ok, out_path if ok else "", "".join(self._log))
        self._proc = None
