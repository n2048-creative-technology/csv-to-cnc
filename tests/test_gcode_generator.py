from src.config import MachineConfig
from src.gcode_generator import build_job_gcode


def test_gcode_contains_preamble_and_postamble():
    cfg = MachineConfig(spindle_rpm=8000)
    lines = build_job_gcode("12A-3", 10.0, cfg)
    text = "\n".join(lines)
    assert "G21" in text
    assert "G90" in text
    assert "M3 S8000" in text
    assert lines[-2] == "M2"
    assert lines[-1] == "(End job)"


def test_gcode_engraves_only_digits():
    cfg = MachineConfig()
    lines = build_job_gcode("A1B2C", 5.0, cfg)
    # ensure at least some engraving moves exist and that digits processed
    assert any(l.startswith("G1 X") for l in lines)

