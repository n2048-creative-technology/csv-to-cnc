import re
from pathlib import Path


def sanitize_id_to_filename(id_value: str) -> str:
    # Keep digits; replace others with underscore
    safe = re.sub(r"[^0-9]", "_", str(id_value))
    safe = re.sub(r"_+", "_", safe).strip("_")
    if not safe:
        safe = "id"
    return f"{safe}_carve.nc"


def ensure_out_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

