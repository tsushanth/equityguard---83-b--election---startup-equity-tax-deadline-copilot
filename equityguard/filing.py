"""Mock certified-mail submission of the 83(b) filing.

This stubs out what a real certified-mail API (e.g. Lob) would do: take a
rendered document, "mail" it via certified mail with return receipt, and
return a tracking ID plus proof-of-filing metadata. No network call is
made and no API key is required. A real integration could later implement
this same `submit_filing` signature against a live Lob client without
touching any other module.
"""

import hashlib
from datetime import datetime

from equityguard.deadline import compute_deadline
from equityguard.models import FilingRecord, Grant

MOCK_METHOD = "certified_mail_mock"


def _fake_tracking_id(grant: Grant, submitted_at: str) -> str:
    digest = hashlib.sha256(f"{grant.id}:{grant.name}:{submitted_at}".encode()).hexdigest()
    return f"MOCK-USPS-{digest[:16].upper()}"


def submit_filing(
    grant: Grant, letter_path: str, cover_sheet_path: str, now: datetime = None
) -> FilingRecord:
    """Simulate a certified-mail submission and return a proof-of-filing record."""
    submitted_at = (now or datetime.now()).isoformat(timespec="seconds")
    tracking_id = _fake_tracking_id(grant, submitted_at)
    deadline_result = compute_deadline(grant.grant_date)

    print(f"[mock certified mail] Submitting 83(b) election for {grant.name}...")
    print(f"[mock certified mail] Documents: {letter_path}, {cover_sheet_path}")
    print(f"[mock certified mail] Tracking ID: {tracking_id}")
    print("[mock certified mail] Status: submitted (no network call made)")

    return FilingRecord(
        grant_id=grant.id,
        tracking_id=tracking_id,
        method=MOCK_METHOD,
        status="submitted",
        submitted_at=submitted_at,
        postmark_deadline=deadline_result.deadline.isoformat(),
        letter_path=letter_path,
        cover_sheet_path=cover_sheet_path,
    )
