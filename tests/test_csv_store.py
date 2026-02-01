import os
from tempfile import TemporaryDirectory

from src.csv_store import load_csv, save_csv_atomic, find_first_not_carved, set_row_status


CSV_CONTENT = """ID number,height,status
123,10.5,not carved
456,11.0,carved
"""


def test_load_and_update_and_atomic_write():
    with TemporaryDirectory() as td:
        p = os.path.join(td, "jobs.csv")
        with open(p, "w", encoding="utf-8") as f:
            f.write(CSV_CONTENT)

        rows, fields = load_csv(p)
        assert find_first_not_carved(rows) == 0
        set_row_status(rows, 0, "carving")
        save_csv_atomic(p, rows, fields)

        rows2, _ = load_csv(p)
        assert rows2[0]["status"] == "carving"

