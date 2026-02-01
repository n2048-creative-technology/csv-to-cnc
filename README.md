CSV-Driven CNC Carving App

Overview
- Desktop app to process a CSV of workpieces and drive a CNC to engrave an ID and drill a positioning hole.
- Supports real GRBL serial and a full-featured simulation mode.
- Safe, testable, and deterministic G-code generation.

Setup
- Python 3.9+
- Install dependencies: `pip install -r requirements.txt`

Run
- Start the GUI: `python -m src.app`

Generate Sample CSV
- Regenerate a sample CSV with 7-digit IDs and heights 0–5 cm:
  - Evenly spaced: `python scripts/gen_sample_csv.py --out sample_data/jobs_20.csv --rows 20`
  - Random heights: `python scripts/gen_sample_csv.py --out sample_data/jobs_20.csv --rows 20 --random`

Virtualenv + Executable
- Create venv and install deps (Linux/macOS):
  - `bash scripts/setup_venv.sh`
- Create venv and install deps (Windows):
  - `scripts\setup_venv.bat`
- Build self-contained executable (Linux/macOS):
  - `bash scripts/build_exe.sh`
  - Output: `dist/cnc-carver`
- Build self-contained executable (Windows):
  - `scripts\build_exe.bat`
  - Output: `dist\cnc-carver.exe`

CSV Format
- CSV must include headers: `ID number,height,status`
- Optional header: `error_msg` (created automatically if missing)
- Example:
  ID number,height,status
  12345,17.2,not carved
  67890,15.1,carved

Default Preset
- The app starts with a basic preset from `src/config_presets.py`:
  - Units: mm (G21)
  - Safe Z: 5.0
  - Engrave Z: -0.25
  - Drill Z: -3.0 (peck 1.0)
  - Feeds: XY 600, Z 120
  - Spindle: 9000 RPM
  - Font: monospace (built-in stroke font); height 8.0 mm, spacing 6.5 mm, stroke width 0.8 mm
  - ID position: X 10.0, Y 10.0
  - Hole position: X 5.0, Y mapped from height
  - Height mapping: CSV height in centimeters (0–5 cm) mapped to Y 20–120 mm

Simulation Mode
- Toggle "Simulation (no CNC connected)" in the UI.
- Uses the same streaming pipeline without opening serial.
- Emits `ok` per line and periodic status lines. Adjustable parameters:
  - Per-line delay (ms)
  - Random extra delay (ms) range
  - Inject error after N lines (0 disables)

Output G-code Naming
- Default output directory: `./gcode_out`
- Files are named `{ID}_carve.nc` where the ID is sanitized for filesystem safety (non-digits replaced with `_`).

Safety Notes
- Always test jobs in air first.
- Confirm the serial port, GRBL is configured, and the machine origin and Z zero are correct for your stock and fixturing.
- Verify generated G-code in the preview before streaming.

Workflow
1) Load a CSV.
2) Optionally choose simulation mode.
3) Click "Process next" to pick the first row with status `not carved`.
4) App sets status to `carving` and saves the CSV, generates and saves G-code, then streams it.
5) On success, the app waits for the controller to report Idle and marks the row `carved`.
6) Errors mark the row `error` and record a message in `error_msg`.

Dry Run
- Toggle "Dry run" to generate and save G-code without streaming.
- Status remains `not carved`; logs indicate that nothing was executed.

Switching Between Modes
- Simulation mode: no serial connection needed; Connect/Disconnect are disabled.
- Real mode: provide serial port and baud, then Connect. The app streams line by line and waits for controller Idle at completion.

Tests
- Run tests: `python -m pytest -q`
- Includes basic tests for filename sanitization, height mapping, CSV updates, and G-code generation.
Other UI Features
- Preview panel (read-only) displays generated or loaded G-code.
- Copy G-code: use the “Copy G-code to clipboard” button to copy the preview content.
- CSV Rows are highlighted by status:
  - not carved: white
  - carving: light yellow
  - carved: light green
  - error: light red
Fonts
- Built-in vector stroke fonts, no external font files needed.
- Default: `monospace`. Other options include aliases and styles:
  - Stick: `monospace`, `simplex`, `duplex`, `triplex`
  - Serif-like: `times`, `times_new_roman` (adds small terminal ticks)
  - Segment/Angular: `sevenseg`, `lcd`, `digital`, `gothic`
  - Slanted script: `cursive` (applies italic shear to strokes)
- Only digits 0–9 are engraved for the ID; non-digits are ignored in engraving and replaced in filenames.
# csv-to-cnc
