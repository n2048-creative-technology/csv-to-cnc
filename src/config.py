from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MachineConfig:
    safe_z: float = 5.0
    engrave_z: float = -5.0
    hole_z: float = -10.0  # legacy; not used for circle, see hole_depth_mm
    feed_xy: float = 600.0
    feed_z: float = 120.0
    peck_depth: float = 1.0
    spindle_rpm: Optional[int] = 9000
    origin_x: float = 0.0
    origin_y: float = 0.0
    char_height: float = 10.0  # legacy default height
    char_spacing: float = 8.0  # legacy default spacing
    char_stroke_width: float = 1.0
    font_name: str = "monospace"
    # Workpiece and layout (in mm)
    board_width_mm: float = 900.0
    board_height_mm: float = 30.0
    text_left_margin_mm: float = 20.0
    text_total_width_mm: float = 50.0  # legacy horizontal layout
    # Vertical layout
    text_top_margin_mm: float = 20.0
    text_total_length_mm: float = 50.0
    text_flip_180: bool = False
    text_gap_mm: float = 1.0
    # Hole parameters
    hole_radius_mm: float = 2.0
    hole_depth_mm: float = 10.0
    hole_offset_per_cm_mm: float = 10.0  # distance from left per cm of height
    id_origin_x: float = 10.0
    id_origin_y: float = 10.0
    hole_x: float = 5.0
    height_y_min_in: float = 10.0
    height_y_max_in: float = 100.0
    hole_y_min_out: float = 20.0
    hole_y_max_out: float = 120.0


@dataclass
class SimulationConfig:
    enabled: bool = True
    per_line_delay_ms: int = 20
    random_extra_delay_ms: int = 0
    error_after_n_lines: int = 0


@dataclass
class AppConfig:
    csv_path: str = ""
    gcode_out_dir: str = "./gcode_out"
    serial_port: str = ""
    serial_baud: int = 115200
    dry_run: bool = False
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    machine: MachineConfig = field(default_factory=MachineConfig)
