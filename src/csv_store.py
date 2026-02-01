from __future__ import annotations

import csv
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Tuple


REQUIRED_FIELDS = ["ID number", "height", "status"]
ERROR_FIELD = "error_msg"


@dataclass
class CsvRow:
    id_number: str
    height: float
    status: str
    error_msg: str = ""
    extra: Dict[str, str] = None

    def to_dict(self, field_order: List[str]) -> Dict[str, str]:
        base = {"ID number": self.id_number, "height": str(self.height), "status": self.status}
        if ERROR_FIELD in field_order:
            base[ERROR_FIELD] = self.error_msg
        if self.extra:
            for k, v in self.extra.items():
                if k not in base:
                    base[k] = v
        return base


def _ensure_headers(fieldnames: List[str]) -> List[str]:
    names = list(fieldnames)
    for f in REQUIRED_FIELDS:
        if f not in names:
            names.append(f)
    if ERROR_FIELD not in names:
        names.append(ERROR_FIELD)
    return names


def load_csv(path: str) -> Tuple[List[Dict[str, str]], List[str]]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    with p.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = _ensure_headers(reader.fieldnames or [])
        rows: List[Dict[str, str]] = []
        for r in reader:
            # normalize required fields
            out = {k: r.get(k, "") for k in fieldnames}
            rows.append(out)
    return rows, fieldnames


def save_csv_atomic(path: str, rows: List[Dict[str, str]], fieldnames: Optional[List[str]] = None) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        # union of keys in rows
        keys = set()
        for r in rows:
            keys.update(r.keys())
        fieldnames = _ensure_headers(sorted(keys))
    else:
        fieldnames = _ensure_headers(fieldnames)

    fd, tmp_path = tempfile.mkstemp(prefix=p.name, dir=str(p.parent))
    os.close(fd)
    try:
        with open(tmp_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in rows:
                row = {k: r.get(k, "") for k in fieldnames}
                writer.writerow(row)
        os.replace(tmp_path, p)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def find_first_not_carved(rows: List[Dict[str, str]]) -> Optional[int]:
    for i, r in enumerate(rows):
        if (r.get("status", "").strip().lower() == "not carved"):
            return i
    return None


def set_row_status(rows: List[Dict[str, str]], index: int, status: str, error_msg: str = "") -> None:
    r = rows[index]
    r["status"] = status
    if error_msg:
        r[ERROR_FIELD] = error_msg
    elif ERROR_FIELD not in r:
        r[ERROR_FIELD] = ""


def get_row_id_and_height(r: Dict[str, str]) -> Tuple[str, float]:
    id_num = str(r.get("ID number", "")).strip()
    try:
        height = float(r.get("height", 0) or 0)
    except ValueError:
        height = 0.0
    return id_num, height

