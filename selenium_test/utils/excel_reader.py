"""Đọc dữ liệu test từ CSV hoặc Excel thành list[dict]."""
import csv
from pathlib import Path

try:
    import openpyxl
except ImportError:
    openpyxl = None

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_csv(filename: str) -> list[dict]:
    path = DATA_DIR / filename if not Path(filename).is_absolute() else Path(filename)
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def load_excel(filename: str, sheet: str | None = None) -> list[dict]:
    if openpyxl is None:
        raise RuntimeError("openpyxl chưa được cài: pip install openpyxl")
    path = DATA_DIR / filename if not Path(filename).is_absolute() else Path(filename)
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[sheet] if sheet else wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    headers = [str(h) if h is not None else "" for h in rows[0]]
    out = []
    for r in rows[1:]:
        if all(c is None for c in r):
            continue
        out.append({h: ("" if v is None else v) for h, v in zip(headers, r)})
    return out


def to_bool(v) -> bool:
    return str(v).strip().lower() in ("1", "true", "yes", "y", "có", "co", "tick")
