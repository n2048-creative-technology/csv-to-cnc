"""
Default configuration presets for the CNC app.

Includes a basic preset with reasonable machine values and font properties
for engraving 7-digit IDs. Heights in the CSV are expected in centimeters
for this preset (0–5 cm), mapped to a Y position range in mm.
"""

from .config import AppConfig, MachineConfig, SimulationConfig


def basic_default() -> AppConfig:
    machine = MachineConfig(
        safe_z=5.0,
        engrave_z=-5.0,
        hole_z=-10.0,
        feed_xy=600.0,
        feed_z=120.0,
        peck_depth=1.0,
        spindle_rpm=9000,
        origin_x=0.0,
        origin_y=0.0,
        # Font properties
        char_height=8.0,        # legacy; auto-scaled by width below
        char_spacing=6.5,
        char_stroke_width=0.8,
        font_name="monospace",
        # Workpiece and layout
        board_width_mm=900.0,
        board_height_mm=30.0,
        text_left_margin_mm=20.0,
        text_total_width_mm=50.0,
        text_gap_mm=1.0,
        # Hole parameters
        hole_radius_mm=2.0,
        hole_depth_mm=10.0,
        hole_offset_per_cm_mm=10.0,
    )

    sim = SimulationConfig(
        enabled=True,
        per_line_delay_ms=20,
        random_extra_delay_ms=0,
        error_after_n_lines=0,
    )

    return AppConfig(
        csv_path="",
        gcode_out_dir="./gcode_out",
        serial_port="",
        serial_baud=115200,
        dry_run=False,
        simulation=sim,
        machine=machine,
    )
