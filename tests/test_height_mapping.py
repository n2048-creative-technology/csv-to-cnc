from src.config import MachineConfig
from src.gcode_generator import map_height_to_hole_y


def test_height_mapping_clamp_low():
    cfg = MachineConfig(height_y_min_in=10, height_y_max_in=20, hole_y_min_out=100, hole_y_max_out=200)
    assert map_height_to_hole_y(0, cfg) == 100


def test_height_mapping_clamp_high():
    cfg = MachineConfig(height_y_min_in=10, height_y_max_in=20, hole_y_min_out=100, hole_y_max_out=200)
    assert map_height_to_hole_y(1000, cfg) == 200


def test_height_mapping_mid():
    cfg = MachineConfig(height_y_min_in=0, height_y_max_in=100, hole_y_min_out=0, hole_y_max_out=50)
    assert map_height_to_hole_y(50, cfg) == 25

