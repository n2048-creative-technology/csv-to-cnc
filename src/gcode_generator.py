from __future__ import annotations

from typing import List, Tuple, Dict

from .config import MachineConfig


def clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def map_height_to_hole_y(height: float, cfg: MachineConfig) -> float:
    hmin, hmax = cfg.height_y_min_in, cfg.height_y_max_in
    ymin, ymax = cfg.hole_y_min_out, cfg.hole_y_max_out
    if hmax == hmin:
        t = 0.0
    else:
        t = (height - hmin) / (hmax - hmin)
    t = clamp01(t)
    return ymin + t * (ymax - ymin)


# Simple stick font for digits 0-9 in unit box [0,1]x[0,1] as strokes ((x1,y1),(x2,y2))
_DIGIT_STROKES_MONO: Dict[str, List[Tuple[Tuple[float, float], Tuple[float, float]]]] = {
    "0": [((0.1, 0.1), (0.9, 0.1)), ((0.9, 0.1), (0.9, 0.9)), ((0.9, 0.9), (0.1, 0.9)), ((0.1, 0.9), (0.1, 0.1))],
    "1": [((0.5, 0.1), (0.5, 0.9))],
    "2": [((0.1, 0.9), (0.9, 0.9)), ((0.9, 0.9), (0.9, 0.5)), ((0.9, 0.5), (0.1, 0.1)), ((0.1, 0.1), (0.9, 0.1))],
    "3": [((0.1, 0.9), (0.9, 0.9)), ((0.9, 0.9), (0.5, 0.5)), ((0.5, 0.5), (0.9, 0.1)), ((0.9, 0.1), (0.1, 0.1))],
    "4": [((0.1, 0.9), (0.1, 0.5)), ((0.1, 0.5), (0.9, 0.5)), ((0.9, 0.9), (0.9, 0.1))],
    "5": [((0.9, 0.9), (0.1, 0.9)), ((0.1, 0.9), (0.1, 0.5)), ((0.1, 0.5), (0.9, 0.5)), ((0.9, 0.5), (0.9, 0.1)), ((0.9, 0.1), (0.1, 0.1))],
    "6": [((0.9, 0.9), (0.1, 0.9)), ((0.1, 0.9), (0.1, 0.1)), ((0.1, 0.5), (0.9, 0.5)), ((0.9, 0.5), (0.9, 0.1)), ((0.9, 0.1), (0.1, 0.1))],
    "7": [((0.1, 0.9), (0.9, 0.9)), ((0.9, 0.9), (0.5, 0.1))],
    "8": [((0.1, 0.1), (0.9, 0.1)), ((0.9, 0.1), (0.9, 0.9)), ((0.9, 0.9), (0.1, 0.9)), ((0.1, 0.9), (0.1, 0.1)), ((0.1, 0.5), (0.9, 0.5))],
    "9": [((0.1, 0.1), (0.9, 0.1)), ((0.9, 0.1), (0.9, 0.9)), ((0.9, 0.9), (0.1, 0.9)), ((0.1, 0.9), (0.1, 0.5)), ((0.1, 0.5), (0.9, 0.5))],
}

# A simple seven-segment style font for variety
_DIGIT_STROKES_7SEG: Dict[str, List[Tuple[Tuple[float, float], Tuple[float, float]]]] = {
    # segments: a,b,c,d,e,f,g; normalized lines
    "0": [((0.1,0.9),(0.9,0.9)), ((0.9,0.9),(0.9,0.5)), ((0.9,0.5),(0.9,0.1)), ((0.1,0.1),(0.9,0.1)), ((0.1,0.5),(0.1,0.9)), ((0.1,0.5),(0.1,0.1))],
    "1": [((0.5,0.1),(0.5,0.9))],
    "2": [((0.1,0.9),(0.9,0.9)), ((0.9,0.9),(0.9,0.5)), ((0.1,0.5),(0.9,0.5)), ((0.1,0.1),(0.9,0.1)), ((0.1,0.5),(0.1,0.1))],
    "3": [((0.1,0.9),(0.9,0.9)), ((0.5,0.5),(0.9,0.5)), ((0.9,0.9),(0.9,0.1)), ((0.1,0.1),(0.9,0.1))],
    "4": [((0.1,0.9),(0.1,0.5)), ((0.1,0.5),(0.9,0.5)), ((0.9,0.9),(0.9,0.1))],
    "5": [((0.9,0.9),(0.1,0.9)), ((0.1,0.9),(0.1,0.5)), ((0.1,0.5),(0.9,0.5)), ((0.9,0.5),(0.9,0.1)), ((0.1,0.1),(0.9,0.1))],
    "6": [((0.9,0.9),(0.1,0.9)), ((0.1,0.9),(0.1,0.1)), ((0.1,0.5),(0.9,0.5)), ((0.9,0.5),(0.9,0.1)), ((0.1,0.1),(0.9,0.1))],
    "7": [((0.1,0.9),(0.9,0.9)), ((0.9,0.9),(0.5,0.1))],
    "8": [((0.1,0.9),(0.9,0.9)), ((0.9,0.9),(0.9,0.1)), ((0.1,0.1),(0.9,0.1)), ((0.1,0.9),(0.1,0.1)), ((0.1,0.5),(0.9,0.5))],
    "9": [((0.1,0.9),(0.9,0.9)), ((0.9,0.9),(0.9,0.1)), ((0.1,0.1),(0.9,0.1)), ((0.1,0.5),(0.9,0.5)), ((0.1,0.9),(0.1,0.5))],
}

# A basic serif-like variant with small terminal ticks (Times-style approximation)
_DIGIT_STROKES_SERIF: Dict[str, List[Tuple[Tuple[float, float], Tuple[float, float]]]] = {
    **_DIGIT_STROKES_MONO,
}
# augment with small serifs (ticks) at ends for some digits
_DIGIT_STROKES_SERIF["1"] = [
    ((0.5, 0.1), (0.5, 0.9)),  # main stem
    ((0.3, 0.1), (0.7, 0.1)),  # base serif
    ((0.4, 0.9), (0.6, 0.9)),  # top serif
]
_DIGIT_STROKES_SERIF["7"] = [
    ((0.1, 0.9), (0.9, 0.9)),  # top bar
    ((0.9, 0.9), (0.5, 0.1)),  # diagonal
    ((0.1, 0.9), (0.2, 0.8)),  # left top serif
    ((0.9, 0.9), (0.8, 0.8)),  # right top serif
]
_DIGIT_STROKES_SERIF["0"] = [
    ((0.1, 0.1), (0.9, 0.1)),
    ((0.9, 0.1), (0.9, 0.9)),
    ((0.9, 0.9), (0.1, 0.9)),
    ((0.1, 0.9), (0.1, 0.1)),
    ((0.1, 0.1), (0.2, 0.2)),  # serif ticks
    ((0.9, 0.1), (0.8, 0.2)),
    ((0.1, 0.9), (0.2, 0.8)),
    ((0.9, 0.9), (0.8, 0.8)),
]

_FONTS: Dict[str, Dict[str, List[Tuple[Tuple[float, float], Tuple[float, float]]]]] = {
    # Stick fonts
    "monospace": _DIGIT_STROKES_MONO,
    "simplex": _DIGIT_STROKES_MONO,   # alias to simple stick font
    "duplex": _DIGIT_STROKES_MONO,    # alias for now
    "triplex": _DIGIT_STROKES_MONO,   # alias for now
    # Segment-style fonts
    "sevenseg": _DIGIT_STROKES_7SEG,
    "lcd": _DIGIT_STROKES_7SEG,
    "digital": _DIGIT_STROKES_7SEG,
    # Serif approximation (Times-like)
    "times": _DIGIT_STROKES_SERIF,
    "times_new_roman": _DIGIT_STROKES_SERIF,
    # Gothic as angular/segment style alias
    "gothic": _DIGIT_STROKES_7SEG,
}


def _engrave_digit_gcode_builtin(d: str, x0: float, y0: float, scale: float, cfg: MachineConfig) -> List[str]:
    lines: List[str] = []
    strokes = _FONTS.get(cfg.font_name, _DIGIT_STROKES_MONO).get(d)
    if not strokes:
        return lines
    fxy = cfg.feed_xy
    fz = cfg.feed_z
    for (x1, y1), (x2, y2) in strokes:
        X1 = x0 + x1 * scale
        Y1 = y0 + y1 * scale
        X2 = x0 + x2 * scale
        Y2 = y0 + y2 * scale
        lines.append(f"G0 Z{cfg.safe_z:.3f}")
        lines.append(f"G0 X{X1:.3f} Y{Y1:.3f}")
        lines.append(f"G1 Z{cfg.engrave_z:.3f} F{fz:.1f}")
        lines.append(f"G1 X{X2:.3f} Y{Y2:.3f} F{fxy:.1f}")
    return lines


def _trace_polygons(polys, offset_x: float, offset_y: float, scale: float, cfg: MachineConfig) -> List[str]:
    try:
        import numpy as np
    except Exception:
        return []
    lines: List[str] = []
    fxy = cfg.feed_xy
    fz = cfg.feed_z
    for poly in polys:
        if len(poly) < 2:
            continue
        pts = poly * scale
        X0 = offset_x + float(pts[0, 0])
        Y0 = offset_y + float(pts[0, 1])
        lines.append(f"G0 Z{cfg.safe_z:.3f}")
        lines.append(f"G0 X{X0:.3f} Y{Y0:.3f}")
        lines.append(f"G1 Z{cfg.engrave_z:.3f} F{fz:.1f}")
        for i in range(1, len(pts)):
            xi, yi = float(pts[i, 0]), float(pts[i, 1])
            lines.append(f"G1 X{offset_x + xi:.3f} Y{offset_y + yi:.3f} F{fxy:.1f}")
        lines.append(f"G0 Z{cfg.safe_z:.3f}")
    return lines


def _resolve_font_family(name: str | None) -> Tuple[str, str]:
    """Return a (family, style) tuple that exists on the system.

    Tries a list of candidates for common aliases like 'monospace', 'times', 'gothic', 'cursive'.
    Falls back to DejaVu Sans Mono.
    """
    try:
        from matplotlib.font_manager import fontManager
    except Exception:
        return (name or "monospace", "normal")
    n = (name or "monospace").strip()
    available = {f.name for f in getattr(fontManager, "ttflist", [])}
    # Exact match first
    if n in available:
        return n, "normal"
    # Case-insensitive contains
    for fam in available:
        if fam.lower() == n.lower():
            return fam, "normal"
    # Simple fallbacks to known common families
    for pref in ("DejaVu Sans Mono", "Liberation Mono", "Courier New", "DejaVu Sans", "DejaVu Serif"):
        if pref in available:
            return pref, "normal"
    # Last resort
    return next(iter(available)) if available else ("DejaVu Sans Mono", "normal")


def build_job_gcode(id_value: str, height: float, cfg: MachineConfig) -> List[str]:
    lines: List[str] = []
    # Preamble
    lines.append("(Begin job)")
    lines.append("G21")  # mm
    lines.append("G17")  # XY plane
    lines.append("G90")  # absolute
    lines.append(f"G0 Z{cfg.safe_z:.3f}")
    if cfg.spindle_rpm:
        lines.append(f"M3 S{cfg.spindle_rpm}")

    # Engrave ID (digits only) scaled to target width and centered vertically
    digits = "".join(ch for ch in str(id_value) if ch.isdigit())
    if digits:
        try:
            from matplotlib.textpath import TextPath
            from matplotlib.font_manager import FontProperties
            import numpy as np
        except Exception:
            # Fallback to builtin strokes roughly scaled by width per digit
            x = cfg.origin_x + cfg.text_left_margin_mm
            y_center = cfg.origin_y + cfg.board_height_mm / 2.0
            y = y_center - cfg.char_height / 2.0
            for ch in digits:
                lines.extend(_engrave_digit_gcode_builtin(ch, x, y, cfg.char_height, cfg))
                x += cfg.char_height + cfg.text_gap_mm
        else:
            fam, style = _resolve_font_family(cfg.font_name)
            tp = TextPath((0, 0), digits, size=100, prop=FontProperties(family=fam, style=style))
            polys = tp.to_polygons()
            if polys:
                all_pts = np.vstack(polys)
                min_x, min_y = float(np.min(all_pts[:, 0])), float(np.min(all_pts[:, 1]))
                max_x, max_y = float(np.max(all_pts[:, 0])), float(np.max(all_pts[:, 1]))
                width = max(1e-6, max_x - min_x)
                height_box = max(1e-6, max_y - min_y)
                scale = cfg.text_total_width_mm / width
                # Offsets to place left at margin and vertically centered
                x0 = cfg.origin_x + cfg.text_left_margin_mm - min_x * scale
                y_center = cfg.origin_y + cfg.board_height_mm / 2.0
                y0 = y_center - 0.5 * (height_box * scale) - min_y * scale
                # Shift polys to baseline 0,0
                shifted = [((poly - (min_x, min_y))) for poly in polys]
                lines.extend(_trace_polygons(shifted, x0, y0, scale, cfg))

    # Positioning hole: circular interpolation at center height, X offset by height value
    hole_center_y = cfg.origin_y + cfg.board_height_mm / 2.0
    hole_center_x = cfg.origin_x + cfg.text_left_margin_mm + (height * cfg.hole_offset_per_cm_mm)
    r = max(0.5, cfg.hole_radius_mm)
    target_z = -abs(cfg.hole_depth_mm)
    z = 0.0
    lines.append(f"G0 Z{cfg.safe_z:.3f}")
    lines.append(f"G0 X{hole_center_x + r:.3f} Y{hole_center_y:.3f}")
    while z > target_z:
        next_z = max(target_z, z - cfg.peck_depth)
        lines.append(f"G1 Z{next_z:.3f} F{cfg.feed_z:.1f}")
        # Two half-circle arcs to make a full circle
        lines.append(f"G2 X{hole_center_x - r:.3f} Y{hole_center_y:.3f} I{-r:.3f} J{0.0:.3f} F{cfg.feed_xy:.1f}")
        lines.append(f"G2 X{hole_center_x + r:.3f} Y{hole_center_y:.3f} I{r:.3f} J{0.0:.3f} F{cfg.feed_xy:.1f}")
        lines.append(f"G0 Z{cfg.safe_z:.3f}")
        lines.append(f"G0 X{hole_center_x + r:.3f} Y{hole_center_y:.3f}")
        z = next_z

    # Postamble
    lines.append(f"G0 Z{cfg.safe_z:.3f}")
    if cfg.spindle_rpm:
        lines.append("M5")
    lines.append("M2")
    lines.append("(End job)")
    return lines
