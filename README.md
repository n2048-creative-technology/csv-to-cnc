CSV-Driven CNC Carving App

Overview
- Desktop app that reads a CSV and drives a CNC to engrave a numeric ID and cut a positioning circle on wooden boards.
- Supports real GRBL serial and a full-featured simulation mode with realistic responses and delays.
- Uses installed system fonts to outline digits so carved text matches the chosen font.

Key Geometry (defaults)
- Coordinate system: origin at top-left (0,0); bottom-right is (30 mm, 90 mm).
- Workpiece size: 30 x 90 mm (3 x 9 cm) aligned along Y.
- ID text: vertical top-to-bottom, horizontally centered, top margin 20 mm, total length ~50 mm, depth 5 mm.
- Positioning circle: depth 10 mm, horizontally centered. Y offset from the top equals `top_margin + height_cm * 10 mm`.

Requirements
- Python 3.9+
- Install dependencies: `pip install -r requirements.txt`

Run
- Start the GUI: `python -m src.app`

Virtualenv and Executable
- Create venv and install deps (Linux/macOS): `bash scripts/setup_venv.sh`
- Create venv and install deps (Windows): `scripts\setup_venv.bat`
- Build self-contained executable (Linux/macOS): `bash scripts/build_exe.sh` (output `dist/cnc-carver`)
- Build self-contained executable (Windows): `scripts\build_exe.bat` (output `dist\cnc-carver.exe`)

CSV Format
- Required headers: `ID number,height,status`
- Optional header: `error_msg` (created if missing)
- Example:
  ID number,height,status
  1000001,2.50,not carved
  1000002,1.75,carved

Using the App
- CSV: click “CSV path” and pick your file (for example `sample_data/jobs_20.csv`). The table shows all rows with statuses and error messages.
- Simulation: enable “Simulation (no CNC connected)” to test without hardware.
- Serial (real mode): enter Port and Baud, click Connect. Use Process next to stream.
- Output dir: keep `./gcode_out` or choose a directory.
- Font: pick an installed system font from the dropdown or click “List fonts…” to browse and filter. The ID engraving uses that font’s outline.

Main Actions
- Process next: marks the first `not carved` row as `carving`, saves the CSV, generates and saves G-code, streams it, waits for Idle, then marks `carved`.
- Generate only: generates and saves G-code for the next `not carved` row without streaming. Status remains `not carved`.
- Stream loaded/previewed G-code: streams whatever is currently in the preview.
- Load G-code for selected row: loads `{ID}_carve.nc` for the selected row into the preview.
- Save last G-code: save-as for the current preview content.
- Copy G-code to clipboard: copies the previewed lines to the clipboard.

Manual and Recovery Controls
- Re-run selected error row: regenerates and streams the selected row if its status is `error`.
- Set status for selected row: manually change status to `not carved`, `carving`, `carved`, or `error` and optionally set an error message. Changes save atomically to CSV.

Simulation Mode
- Uses the same pipeline as real mode without opening serial.
- Emits `ok` per line and periodic `<Run|...>` and a final `<Idle|...>`.
- Adjustable parameters:
  - Per-line delay (ms)
  - Random extra delay (ms)
  - Inject error after N lines

Output G-code Naming
- Default output directory: `./gcode_out`
- File name: `{ID}_carve.nc`. Non-digits in ID are replaced with `_` for filesystem safety.

Generate Sample CSV
- Evenly spaced heights: `python scripts/gen_sample_csv.py --out sample_data/jobs_20.csv --rows 20`
- Random heights: `python scripts/gen_sample_csv.py --out sample_data/jobs_20.csv --rows 20 --random`

Safety Notes
- Always run a dry test in air first and confirm spindle, feeds, and Z zero.
- Verify the correct serial port and GRBL settings before streaming.
- Check previewed G-code and geometry placement before running.

Tests
- Run: `python -m pytest -q`
- Includes basic tests for filename sanitization, height mapping, CSV updates, and G-code generation.
