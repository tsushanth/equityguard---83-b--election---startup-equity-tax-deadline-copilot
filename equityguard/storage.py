"""Local JSON flat-file storage for grants and filing records."""

import json
import os
from typing import List, Optional

from equityguard.models import FilingRecord, Grant

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
GRANTS_FILE = os.path.join(DATA_DIR, "grants.json")
FILINGS_DIR = os.path.join(DATA_DIR, "filings")


def _ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def load_grants() -> List[Grant]:
    _ensure_data_dir()
    if not os.path.exists(GRANTS_FILE):
        return []
    with open(GRANTS_FILE, "r") as f:
        raw = json.load(f)
    return [Grant.from_dict(d) for d in raw]


def save_grants(grants: List[Grant]) -> None:
    _ensure_data_dir()
    with open(GRANTS_FILE, "w") as f:
        json.dump([g.to_dict() for g in grants], f, indent=2)


def next_grant_id(grants: List[Grant]) -> int:
    return max((g.id for g in grants), default=0) + 1


def add_grant(grant: Grant) -> Grant:
    grants = load_grants()
    grants.append(grant)
    save_grants(grants)
    return grant


def get_grant(grant_id: int) -> Optional[Grant]:
    for g in load_grants():
        if g.id == grant_id:
            return g
    return None


def grant_filing_dir(grant_id: int) -> str:
    path = os.path.join(FILINGS_DIR, str(grant_id))
    os.makedirs(path, exist_ok=True)
    return path


def save_filing_record(record: FilingRecord) -> str:
    path = os.path.join(grant_filing_dir(record.grant_id), "proof_of_filing.json")
    with open(path, "w") as f:
        json.dump(record.to_dict(), f, indent=2)
    return path


def load_filing_record(grant_id: int) -> Optional[FilingRecord]:
    path = os.path.join(grant_filing_dir(grant_id), "proof_of_filing.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return FilingRecord.from_dict(json.load(f))
