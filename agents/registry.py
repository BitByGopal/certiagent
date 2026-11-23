"""Registry agent: compare extracted fields with the institution database (data/registry.csv)."""
import difflib
from pathlib import Path
import pandas as pd

REGISTRY_PATH = Path(__file__).resolve().parent.parent / "data" / "registry.csv"
_db = None


def db() -> pd.DataFrame:
    global _db
    if _db is None:
        _db = pd.read_csv(REGISTRY_PATH, dtype=str)
    return _db


def _sim(a, b) -> float:
    return difflib.SequenceMatcher(None, str(a or "").lower(), str(b or "").lower()).ratio()


def lookup(cert_id=None, roll=None):
    """Tool: find a record by certificate ID, falling back to roll number."""
    d = db()
    if cert_id:
        hit = d[d.cert_id == cert_id]
        if len(hit): return hit.iloc[0].to_dict()
    if roll:
        hit = d[d.roll == roll]
        if len(hit): return hit.iloc[0].to_dict()
    return None


def run(fields: dict) -> dict:
    rec = lookup(fields.get("cert_id"), fields.get("roll"))
    if rec is None:
        return {"registry": {"status": "NOT_FOUND", "mismatches": [], "record": None}}
    mismatches = []
    for k in ["name", "roll", "year", "cgpa"]:
        need = 0.85 if k == "name" else 1.0
        if _sim(fields.get(k), rec[k]) < need:
            mismatches.append({"field": k, "certificate": fields.get(k), "registry": rec[k]})
    status = "MATCH" if not mismatches else "MISMATCH"
    return {"registry": {"status": status, "mismatches": mismatches, "record": rec}}
