from __future__ import annotations

import os
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import List, Optional

try:
    from .config import AppConfig, MachineConfig, SimulationConfig  # type: ignore
    from .config_presets import basic_default  # type: ignore
    from .csv_store import (
        load_csv,
        save_csv_atomic,
        find_first_not_carved,
        set_row_status,
        get_row_id_and_height,
    )  # type: ignore
    from .gcode_generator import build_job_gcode, map_height_to_hole_y  # type: ignore
    from .sender.base import Sender  # type: ignore
    from .sender.grbl_serial import GrblSerialSender  # type: ignore
    from .sender.simulator import SimulatorSender  # type: ignore
    from .util.filenames import sanitize_id_to_filename, ensure_out_dir  # type: ignore
    from .util.logging import LogEmitter  # type: ignore
    from .util.threading import UIEventQueue, run_in_thread  # type: ignore
except Exception:  # pragma: no cover - supports running as a script
    from config import AppConfig, MachineConfig, SimulationConfig
    from config_presets import basic_default
    from csv_store import (
        load_csv,
        save_csv_atomic,
        find_first_not_carved,
        set_row_status,
        get_row_id_and_height,
    )
    from gcode_generator import build_job_gcode, map_height_to_hole_y
    from sender.base import Sender
    from sender.grbl_serial import GrblSerialSender
    from sender.simulator import SimulatorSender
    from util.filenames import sanitize_id_to_filename, ensure_out_dir
    from util.logging import LogEmitter
    from util.threading import UIEventQueue, run_in_thread


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("CSV-driven CNC Carving")
        # Initialize with the basic default preset
        self.cfg = basic_default()
        self.machine = self.cfg.machine
        self.simcfg = self.cfg.simulation

        self.uiq = UIEventQueue(root)
        self.uiq.start_auto_pump(50)

        self.sender: Optional[Sender] = None
        self.connected = False

        self.current_lines: List[str] = []
        self.total_lines = 0
        self.sent_lines = 0
        self.job_status = tk.StringVar(value="Idle")
        self.current_id_var = tk.StringVar(value="-")

        self._build_ui()

    def _build_ui(self) -> None:
        pad = 6
        frm = ttk.Frame(self.root)
        frm.pack(fill=tk.BOTH, expand=True)

        # Row 0: CSV path
        row = 0
        ttk.Label(frm, text="CSV path:").grid(row=row, column=0, sticky="w", padx=pad, pady=pad)
        self.csv_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.csv_var, width=50).grid(row=row, column=1, sticky="we", padx=pad, pady=pad)
        ttk.Button(frm, text="Browse…", command=self._choose_csv).grid(row=row, column=2, padx=pad, pady=pad)
        frm.grid_columnconfigure(1, weight=1)

        # Row 1: Serial settings
        row += 1
        self.sim_var = tk.BooleanVar(value=True)
        sim_chk = ttk.Checkbutton(frm, text="Simulation (no CNC connected)", variable=self.sim_var, command=self._on_sim_toggle)
        sim_chk.grid(row=row, column=0, sticky="w", padx=pad, pady=pad)

        ttk.Label(frm, text="Port:").grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        self.port_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.port_var, width=15).grid(row=row, column=1, sticky="e", padx=(50, pad), pady=pad)
        ttk.Label(frm, text="Baud:").grid(row=row, column=2, sticky="w", padx=pad, pady=pad)
        self.baud_var = tk.StringVar(value=str(self.cfg.serial_baud))
        ttk.Entry(frm, textvariable=self.baud_var, width=8).grid(row=row, column=2, sticky="e", padx=(50, pad), pady=pad)

        row += 1
        self.btn_connect = ttk.Button(frm, text="Connect", command=self._connect)
        self.btn_disconnect = ttk.Button(frm, text="Disconnect", command=self._disconnect)
        self.btn_connect.grid(row=row, column=0, sticky="w", padx=pad, pady=pad)
        self.btn_disconnect.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)

        # Simulation params
        row += 1
        ttk.Label(frm, text="Sim per-line delay (ms):").grid(row=row, column=0, sticky="w", padx=pad, pady=pad)
        self.sim_delay_var = tk.StringVar(value=str(self.simcfg.per_line_delay_ms))
        ttk.Entry(frm, textvariable=self.sim_delay_var, width=8).grid(row=row, column=0, sticky="e", padx=(250, pad), pady=pad)
        ttk.Label(frm, text="Random extra (ms):").grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        self.sim_rand_var = tk.StringVar(value=str(self.simcfg.random_extra_delay_ms))
        ttk.Entry(frm, textvariable=self.sim_rand_var, width=8).grid(row=row, column=1, sticky="e", padx=(150, pad), pady=pad)
        ttk.Label(frm, text="Inject error after N:").grid(row=row, column=2, sticky="w", padx=pad, pady=pad)
        self.sim_err_var = tk.StringVar(value=str(self.simcfg.error_after_n_lines))
        ttk.Entry(frm, textvariable=self.sim_err_var, width=8).grid(row=row, column=2, sticky="e", padx=(150, pad), pady=pad)

        # Row: Options
        row += 1
        self.dry_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Dry run", variable=self.dry_var).grid(row=row, column=0, sticky="w", padx=pad, pady=pad)
        ttk.Label(frm, text="G-code out dir:").grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        self.outdir_var = tk.StringVar(value=self.cfg.gcode_out_dir)
        ttk.Entry(frm, textvariable=self.outdir_var, width=40).grid(row=row, column=1, sticky="e", padx=(120, pad), pady=pad)
        ttk.Button(frm, text="Choose…", command=self._choose_outdir).grid(row=row, column=2, padx=pad, pady=pad)

        # Font selection
        row += 1
        ttk.Label(frm, text="Font:").grid(row=row, column=0, sticky="w", padx=pad, pady=pad)
        fonts = self._available_fonts()
        default_font = self._pick_default_font(fonts)
        # Use saved font if available; otherwise pick default
        initial_font = self.machine.font_name if self.machine.font_name in fonts else default_font
        self.font_var = tk.StringVar(value=initial_font)
        self.machine.font_name = initial_font
        self.font_combo = ttk.Combobox(frm, textvariable=self.font_var, values=fonts, width=28, state="readonly")
        self.font_combo.grid(row=row, column=0, sticky="e", padx=(60, pad), pady=pad)
        self.font_combo.bind("<<ComboboxSelected>>", lambda e: self._on_font_change())
        ttk.Button(frm, text="List fonts…", command=self._show_fonts_dialog).grid(row=row, column=1, sticky="w", padx=pad, pady=pad)

        # Buttons
        row += 1
        btns = ttk.Frame(frm)
        btns.grid(row=row, column=0, columnspan=3, sticky="w", padx=pad, pady=pad)
        ttk.Button(btns, text="Process next", command=self._process_next).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btns, text="Generate only", command=self._generate_only).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btns, text="Stream loaded/previewed G-code", command=self._stream_preview).pack(side=tk.LEFT, padx=(0, 5))

        # Load/Save G-code
        row += 1
        idfrm = ttk.Frame(frm)
        idfrm.grid(row=row, column=0, columnspan=3, sticky="we", padx=pad, pady=pad)
        ttk.Button(idfrm, text="Re-run selected error row", command=self._rerun_selected_row).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(idfrm, text="Load G-code for selected row…", command=self._load_gcode_for_id).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(idfrm, text="Save last G-code…", command=self._save_last_gcode).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(idfrm, text="Copy G-code to clipboard", command=self._copy_gcode_to_clipboard).pack(side=tk.LEFT)

        # Manual status update controls
        row += 1
        statedit = ttk.Frame(frm)
        statedit.grid(row=row, column=0, columnspan=3, sticky="we", padx=pad, pady=(0, pad))
        ttk.Label(statedit, text="Set status for selected row:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="not carved")
        self.status_combo = ttk.Combobox(
            statedit,
            textvariable=self.status_var,
            width=12,
            state="readonly",
            values=["not carved", "carving", "carved", "error"],
        )
        self.status_combo.pack(side=tk.LEFT, padx=(6, 6))
        self.status_combo.bind("<<ComboboxSelected>>", lambda e: self._on_status_choice())
        ttk.Label(statedit, text="Error msg:").pack(side=tk.LEFT, padx=(10, 4))
        self.error_msg_var = tk.StringVar()
        self.error_msg_entry = ttk.Entry(statedit, textvariable=self.error_msg_var, width=40)
        self.error_msg_entry.pack(side=tk.LEFT, padx=(0, 6))
        self.error_msg_entry.configure(state=tk.DISABLED)
        ttk.Button(statedit, text="Update status", command=self._update_selected_status).pack(side=tk.LEFT)

        # Job status and progress
        row += 1
        statfrm = ttk.Frame(frm)
        statfrm.grid(row=row, column=0, columnspan=3, sticky="we", padx=pad, pady=pad)
        ttk.Label(statfrm, textvariable=self.job_status).pack(side=tk.LEFT)
        self.progress = ttk.Progressbar(statfrm, length=300)
        self.progress.pack(side=tk.LEFT, padx=(10, 5))
        self.line_counter_var = tk.StringVar(value="0/0 (0%)")
        ttk.Label(statfrm, textvariable=self.line_counter_var).pack(side=tk.LEFT)
        ttk.Label(statfrm, text="   Current ID:").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Label(statfrm, textvariable=self.current_id_var).pack(side=tk.LEFT)

        # Text areas
        row += 1
        paned = ttk.Panedwindow(frm, orient=tk.HORIZONTAL)
        paned.grid(row=row, column=0, columnspan=3, sticky="nsew", padx=pad, pady=pad)
        frm.grid_rowconfigure(row, weight=1)
        frm.grid_columnconfigure(1, weight=1)

        # Log panel
        log_frame = ttk.Labelframe(paned, text="Log")
        self.log_text = tk.Text(log_frame, height=20, wrap=tk.NONE)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        paned.add(log_frame, weight=1)

        # Preview panel
        prev_frame = ttk.Labelframe(paned, text="G-code Preview")
        self.preview_text = tk.Text(prev_frame, height=20, wrap=tk.NONE)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        paned.add(prev_frame, weight=1)

        # CSV rows status panel
        rows_frame = ttk.Labelframe(paned, text="CSV Rows")
        rows_container = ttk.Frame(rows_frame)
        rows_container.pack(fill=tk.BOTH, expand=True)
        columns = ("id", "height", "status", "error")
        self.rows_tree = ttk.Treeview(rows_container, columns=columns, show="headings", height=10)
        self.rows_tree.heading("id", text="ID number")
        self.rows_tree.heading("height", text="height")
        self.rows_tree.heading("status", text="status")
        self.rows_tree.heading("error", text="error_msg")
        self.rows_tree.column("id", width=120, anchor=tk.W)
        self.rows_tree.column("height", width=80, anchor=tk.E)
        self.rows_tree.column("status", width=100, anchor=tk.W)
        self.rows_tree.column("error", width=200, anchor=tk.W)
        yscroll = ttk.Scrollbar(rows_container, orient=tk.VERTICAL, command=self.rows_tree.yview)
        self.rows_tree.configure(yscrollcommand=yscroll.set)
        self.rows_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        # Status color tags
        try:
            self.rows_tree.tag_configure("not_carved", background="#ffffff")
            self.rows_tree.tag_configure("carving", background="#fff3cd")
            self.rows_tree.tag_configure("carved", background="#d4edda")
            self.rows_tree.tag_configure("error", background="#f8d7da")
            self.rows_tree.tag_configure("other", background="#e2e3e5")
        except Exception:
            pass
        paned.add(rows_frame, weight=1)

        # Logging helpers
        self.logger = LogEmitter(self._append_log)
        self._on_sim_toggle()

    # UI helpers
    def _append_log(self, s: str) -> None:
        self.log_text.insert(tk.END, s)
        self.log_text.see(tk.END)

    def _set_preview(self, lines: List[str]) -> None:
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, "\n".join(lines) + ("\n" if lines else ""))

    def _choose_csv(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("All", "*.*")])
        if path:
            self.csv_var.set(path)
            self._refresh_rows_table()

    def _choose_outdir(self) -> None:
        d = filedialog.askdirectory()
        if d:
            self.outdir_var.set(d)

    def _on_sim_toggle(self) -> None:
        sim = self.sim_var.get()
        state = tk.DISABLED if sim else tk.NORMAL
        self.btn_connect.config(state=state)
        self.btn_disconnect.config(state=state)
        if sim and self.connected:
            self._disconnect()

    def _on_font_change(self) -> None:
        chosen = self.font_var.get().strip()
        if not chosen:
            return
        # Ensure only available fonts are used
        if chosen not in self._available_fonts():
            messagebox.showwarning("Font", f"Selected font '{chosen}' is not available.")
            return
        self.machine.font_name = chosen

    def _sync_font_from_ui(self) -> None:
        try:
            chosen = self.font_var.get().strip()
        except Exception:
            chosen = ""
        if chosen and chosen in self._available_fonts():
            self.machine.font_name = chosen

    def _on_status_choice(self) -> None:
        st = (self.status_var.get() or "").strip().lower()
        # Enable error message entry only when status is error
        try:
            self.error_msg_entry.configure(state=(tk.NORMAL if st == "error" else tk.DISABLED))
        except Exception:
            pass

    def _update_selected_status(self) -> None:
        path = self.csv_var.get().strip()
        if not path:
            messagebox.showwarning("CSV", "Please choose a CSV file")
            return
        selection = self.rows_tree.selection() if hasattr(self, "rows_tree") else []
        if not selection:
            messagebox.showwarning("Update status", "Please select a row in the CSV Rows list.")
            return
        try:
            idx = int(selection[0])
        except Exception:
            messagebox.showwarning("Update status", "Invalid selection.")
            return
        try:
            rows, fields = load_csv(path)
        except Exception as e:
            messagebox.showerror("CSV", f"Failed to load CSV: {e}")
            return
        if idx < 0 or idx >= len(rows):
            messagebox.showwarning("Update status", "Selection out of range.")
            return
        new_status = (self.status_var.get() or "").strip()
        msg = self.error_msg_var.get().strip() if new_status.lower() == "error" else ""
        set_row_status(rows, idx, new_status, error_msg=msg)
        try:
            save_csv_atomic(path, rows, fields)
        except Exception as e:
            messagebox.showerror("CSV", f"Failed to save CSV: {e}")
            return
        id_num, _ = get_row_id_and_height(rows[idx])
        self.logger.info(f"CSV updated: set ID {id_num} to {new_status}\n")
        self._refresh_rows_table()

    def _available_fonts(self) -> list[str]:
        try:
            from matplotlib.font_manager import fontManager
        except Exception:
            return ["DejaVu Sans Mono"]
        fams = sorted({f.name for f in getattr(fontManager, "ttflist", [])})
        return fams or ["DejaVu Sans Mono"]

    def _pick_default_font(self, fonts: list[str]) -> str:
        # Prefer a monospace if available
        prefs = [
            "DejaVu Sans Mono",
            "Liberation Mono",
            "Courier New",
            "Monospace",
        ]
        for p in prefs:
            if p in fonts:
                return p
        return fonts[0] if fonts else "DejaVu Sans Mono"

    def _show_fonts_dialog(self) -> None:
        top = tk.Toplevel(self.root)
        top.title("Available Fonts")
        top.geometry("400x500")
        search_var = tk.StringVar()
        ttk.Label(top, text="Filter:").pack(anchor="w", padx=6, pady=(6, 0))
        ent = ttk.Entry(top, textvariable=search_var)
        ent.pack(fill=tk.X, padx=6)
        lst = tk.Listbox(top)
        lst.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        fonts = self._available_fonts()
        for f in fonts:
            lst.insert(tk.END, f)

        def on_filter(*_):
            q = search_var.get().strip().lower()
            lst.delete(0, tk.END)
            for f in fonts:
                if q in f.lower():
                    lst.insert(tk.END, f)

        def on_pick(evt=None):
            sel = lst.curselection()
            if not sel:
                return
            f = lst.get(sel[0])
            self.font_var.set(f)
            self._on_font_change()
            top.destroy()

        search_var.trace_add("write", on_filter)
        lst.bind("<Double-1>", on_pick)
        ttk.Button(top, text="Use selected", command=on_pick).pack(pady=6)

    

    def _refresh_rows_table(self) -> None:
        path = self.csv_var.get().strip()
        for item in getattr(self, "rows_tree", ()).get_children() if hasattr(self, "rows_tree") else []:
            self.rows_tree.delete(item)
        if not path or not hasattr(self, "rows_tree"):
            return
        try:
            rows, _ = load_csv(path)
        except Exception as e:
            self.logger.info(f"Failed to load CSV rows: {e}\n")
            return
        for i, r in enumerate(rows):
            status = (r.get("status", "") or "").strip().lower()
            tag = status.replace(" ", "_") if status in {"not carved", "carving", "carved", "error"} else "other"
            self.rows_tree.insert("", tk.END, iid=str(i), values=(
                r.get("ID number", ""),
                r.get("height", ""),
                r.get("status", ""),
                r.get("error_msg", ""),
            ), tags=(tag,))
        # resize columns to content bounds (basic)
        try:
            df = tkfont.nametofont("TkDefaultFont")
            for col in ("id", "height", "status", "error"):
                self.rows_tree.column(col, width=df.measure(col) + 30)
        except Exception:
            pass

    # Sender handling
    def _make_sender(self) -> Sender:
        if self.sim_var.get():
            # simulator
            try:
                per = int(self.sim_delay_var.get() or "0")
                rnd = int(self.sim_rand_var.get() or "0")
                err = int(self.sim_err_var.get() or "0")
            except ValueError:
                per, rnd, err = 20, 0, 0
            return SimulatorSender(self.logger.out, self.logger.inc, self.logger.info, per, rnd, err)
        # real
        port = self.port_var.get().strip()
        try:
            baud = int(self.baud_var.get() or "115200")
        except ValueError:
            baud = 115200
        return GrblSerialSender(self.logger.out, self.logger.inc, self.logger.info, port, baud)

    def _connect(self) -> None:
        if self.sim_var.get():
            messagebox.showinfo("Simulation", "Simulation mode enabled; no serial connection.")
            return
        if self.connected:
            return
        self.sender = self._make_sender()
        try:
            self.sender.connect()
            self.connected = True
            self.job_status.set("Connected")
        except Exception as e:
            messagebox.showerror("Connect failed", str(e))
            self.sender = None

    def _disconnect(self) -> None:
        if self.sender:
            try:
                self.sender.disconnect()
            except Exception:
                pass
        self.sender = None
        self.connected = False
        self.job_status.set("Disconnected")

    # Actions
    def _generate_job_for_row(self, row: dict) -> List[str]:
        id_num, height = get_row_id_and_height(row)
        # Ensure current font choice is synced to config
        self._sync_font_from_ui()
        self.current_id_var.set(id_num or "-")
        lines = build_job_gcode(id_num, height, self.machine)
        out_dir = ensure_out_dir(self.outdir_var.get() or self.cfg.gcode_out_dir)
        fname = sanitize_id_to_filename(id_num)
        out_path = out_dir / fname
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        self.logger.info(f"Saved G-code: {out_path}\n")
        self.current_lines = lines
        self._set_preview(lines)
        return lines

    def _process_next(self) -> None:
        path = self.csv_var.get().strip()
        if not path:
            messagebox.showwarning("CSV", "Please choose a CSV file")
            return
        try:
            rows, fields = load_csv(path)
        except Exception as e:
            messagebox.showerror("CSV", f"Failed to load CSV: {e}")
            return
        idx = find_first_not_carved(rows)
        if idx is None:
            self.logger.info("No rows with status not carved\n")
            return
        row = rows[idx]
        id_num, _ = get_row_id_and_height(row)
        if self.dry_var.get():
            self.logger.info("Dry run: generating only, no streaming\n")
            self._generate_job_for_row(row)
            return

        # Set status to carving and save
        set_row_status(rows, idx, "carving")
        save_csv_atomic(path, rows, fields)
        self.logger.info(f"CSV updated: set ID {id_num} to carving\n")
        self._refresh_rows_table()
        lines = self._generate_job_for_row(row)
        self._start_stream(lines, csv_update=(path, rows, fields, idx, id_num))

    def _generate_only(self) -> None:
        path = self.csv_var.get().strip()
        if not path:
            messagebox.showwarning("CSV", "Please choose a CSV file")
            return
        try:
            rows, _ = load_csv(path)
        except Exception as e:
            messagebox.showerror("CSV", f"Failed to load CSV: {e}")
            return
        idx = find_first_not_carved(rows)
        if idx is None:
            self.logger.info("No rows with status not carved\n")
            return
        row = rows[idx]
        self._generate_job_for_row(row)
        self.logger.info("Generated only; status remains not carved\n")
        self._refresh_rows_table()

    def _stream_preview(self) -> None:
        if not self.current_lines:
            messagebox.showinfo("Stream", "No G-code loaded to stream.")
            return
        self._start_stream(self.current_lines, csv_update=None)

    def _load_gcode_for_id(self) -> None:
        selection = self.rows_tree.selection()
        if not selection:
            messagebox.showwarning("Load G-code", "Please select a row in the CSV Rows list.")
            return
        values = self.rows_tree.item(selection[0], "values")
        idv = str(values[0]) if values else ""
        fname = sanitize_id_to_filename(idv)
        out_dir = Path(self.outdir_var.get() or self.cfg.gcode_out_dir)
        p = out_dir / fname
        if not p.exists():
            messagebox.showwarning("Load G-code", f"File not found: {p}")
            return
        with open(p, "r", encoding="utf-8") as f:
            content = f.read().splitlines()
        self.current_lines = content
        self._set_preview(content)
        self.logger.info(f"Loaded G-code: {p}\n")
        # set current ID from selection
        self.current_id_var.set(idv or "-")

    def _rerun_selected_row(self) -> None:
        path = self.csv_var.get().strip()
        if not path:
            messagebox.showwarning("CSV", "Please choose a CSV file")
            return
        selection = self.rows_tree.selection() if hasattr(self, "rows_tree") else []
        if not selection:
            messagebox.showwarning("Re-run", "Please select a row with status error.")
            return
        try:
            idx = int(selection[0])
        except Exception:
            messagebox.showwarning("Re-run", "Invalid selection.")
            return
        try:
            rows, fields = load_csv(path)
        except Exception as e:
            messagebox.showerror("CSV", f"Failed to load CSV: {e}")
            return
        if idx < 0 or idx >= len(rows):
            messagebox.showwarning("Re-run", "Selection out of range.")
            return
        row = rows[idx]
        status = (row.get("status", "") or "").strip().lower()
        if status != "error":
            messagebox.showwarning("Re-run", "Selected row is not in error status.")
            return
        if self.dry_var.get():
            self.logger.info("Dry run: re-run generate only, no streaming\n")
            self._generate_job_for_row(row)
            self._refresh_rows_table()
            return
        # Set status to carving and save, clear prior error
        set_row_status(rows, idx, "carving")
        save_csv_atomic(path, rows, fields)
        id_num, _ = get_row_id_and_height(row)
        self.logger.info(f"CSV updated: set ID {id_num} to carving (re-run)\n")
        lines = self._generate_job_for_row(row)
        self._refresh_rows_table()
        self._start_stream(lines, csv_update=(path, rows, fields, idx, id_num))

    def _save_last_gcode(self) -> None:
        if not self.current_lines:
            messagebox.showinfo("Save G-code", "No G-code to save.")
            return
        p = filedialog.asksaveasfilename(defaultextension=".nc", filetypes=[("G-code", "*.nc"), ("All", "*.*")])
        if not p:
            return
        with open(p, "w", encoding="utf-8") as f:
            f.write("\n".join(self.current_lines) + "\n")
        self.logger.info(f"Saved G-code: {p}\n")

    def _copy_gcode_to_clipboard(self) -> None:
        if not self.current_lines:
            messagebox.showinfo("Copy", "No G-code to copy.")
            return
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append("\n".join(self.current_lines) + "\n")
            self.logger.info("Copied G-code to clipboard\n")
        except Exception as e:
            messagebox.showerror("Copy", f"Failed to copy: {e}")

    # Streaming
    def _start_stream(self, lines: List[str], csv_update: Optional[tuple]) -> None:
        # Create sender on demand
        self.sender = self._make_sender()
        self.sent_lines = 0
        self.total_lines = len(lines)
        self.progress.config(maximum=max(1, self.total_lines), value=0)
        self.line_counter_var.set(f"0/{self.total_lines} (0%)")
        self.job_status.set("Streaming")

        def on_progress(sent: int, total: int) -> None:
            self.uiq.post(self._update_progress, sent, total)

        def worker():
            try:
                self.sender.connect()
                self.sender.stream(lines, on_progress)
                self.sender.wait_for_idle(timeout_s=5.0)
            except Exception as e:
                self.uiq.post(self._stream_failed, csv_update, str(e))
                return
            self.uiq.post(self._stream_finished, csv_update)
        run_in_thread(worker)

    def _update_progress(self, sent: int, total: int) -> None:
        self.sent_lines = sent
        self.total_lines = total
        self.progress.config(value=sent, maximum=max(1, total))
        pct = int(round(100.0 * sent / total)) if total else 0
        self.line_counter_var.set(f"{sent}/{total} ({pct}%)")

    def _stream_finished(self, csv_update: Optional[tuple]) -> None:
        self.job_status.set("Completed")
        if csv_update is not None:
            path, rows, fields, idx, id_num = csv_update
            set_row_status(rows, idx, "carved")
            save_csv_atomic(path, rows, fields)
            self.logger.info(f"CSV updated: set ID {id_num} to carved\n")
            self._refresh_rows_table()

    def _stream_failed(self, csv_update: Optional[tuple], msg: str) -> None:
        self.job_status.set("Error")
        self.logger.info(f"Streaming error: {msg}\n")
        if csv_update is not None:
            path, rows, fields, idx, id_num = csv_update
            set_row_status(rows, idx, "error", error_msg=msg)
            save_csv_atomic(path, rows, fields)
            self.logger.info(f"CSV updated: set ID {id_num} to error\n")
            self._refresh_rows_table()


def main() -> None:
    try:
        root = tk.Tk()
    except tk.TclError as e:
        import sys
        print(f"GUI cannot start: {e}. Run on a desktop or use pytest for tests.")
        sys.exit(1)
    app = App(root)
    root.geometry("1000x700")
    root.mainloop()


if __name__ == "__main__":
    main()
