from datetime import date

from equityguard.document import render_cover_sheet, render_election_letter
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


def test_election_letter_contains_key_figures():
    grant = make_grant()
    letter = render_election_letter(grant)

    assert "Jane Doe" in letter
    assert "10000" in letter
    assert "Acme Inc" in letter
    assert "2026-08-20" in letter
    assert "0.0100" in letter  # fmv per share
    assert "100.00" in letter  # total fmv (10000 * 0.01)
    assert "2026-09-19" in letter  # deadline

    # Required IRS Section 83(b) taxpayer statement language.
    assert "Section 83(b)" in letter
    assert "Internal Revenue Code" in letter
    assert "fair market value" in letter.lower()
    assert "30 days after the date of transfer" in letter


def test_cover_sheet_contains_key_figures():
    grant = make_grant()
    sheet = render_cover_sheet(grant, generated_at="2026-08-21T09:00:00")

    assert "Jane Doe" in sheet
    assert "Acme Inc" in sheet
    assert "10000" in sheet
    assert "2026-08-20" in sheet
    assert "2026-09-19" in sheet
    assert "Section 83(b)" in sheet
