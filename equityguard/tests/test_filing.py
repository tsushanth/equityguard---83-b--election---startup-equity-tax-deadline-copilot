from datetime import date, datetime
from unittest import mock

from equityguard.filing import submit_filing
from equityguard.models import Grant


def make_grant() -> Grant:
    return Grant(
        id=1,
        name="Jane Doe",
        company="Acme Inc",
        grant_date=date(2026, 8, 20),
        shares=10000,
        fmv=0.01,
        price_paid=0.0001,
        created_at="2026-08-20T00:00:00",
    )


def test_submit_filing_returns_proof_record_with_expected_fields():
    grant = make_grant()
    fixed_now = datetime(2026, 8, 21, 9, 0, 0)

    record = submit_filing(grant, "letter.txt", "cover.txt", now=fixed_now)

    assert record.grant_id == grant.id
    assert record.tracking_id.startswith("MOCK-USPS-")
    assert record.status == "submitted"
    assert record.submitted_at == "2026-08-21T09:00:00"
    assert record.postmark_deadline == "2026-09-19"
    assert record.letter_path == "letter.txt"
    assert record.cover_sheet_path == "cover.txt"


def test_submit_filing_makes_no_network_call():
    grant = make_grant()
    with mock.patch("socket.socket") as mock_socket:
        submit_filing(grant, "letter.txt", "cover.txt", now=datetime(2026, 8, 21))
        mock_socket.assert_not_called()
