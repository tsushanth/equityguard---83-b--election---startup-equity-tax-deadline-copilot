"""Renders the 83(b) election letter and IRS cover sheet from templates."""

import os
from datetime import datetime

from equityguard.deadline import compute_deadline
from equityguard.models import Grant

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


def _load_template(filename: str) -> str:
    with open(os.path.join(TEMPLATES_DIR, filename), "r") as f:
        return f.read()


def render_election_letter(grant: Grant) -> str:
    deadline_result = compute_deadline(grant.grant_date)
    template = _load_template("election_letter.txt")
    return template.format(
        name=grant.name,
        company=grant.company,
        taxable_year=grant.grant_date.year,
        shares=grant.shares,
        grant_date=grant.grant_date.isoformat(),
        fmv_per_share=f"{grant.fmv:.4f}",
        total_fmv=f"{grant.total_fmv:.2f}",
        price_paid_per_share=f"{grant.price_paid:.4f}",
        total_price_paid=f"{grant.total_price_paid:.2f}",
        taxable_income=f"{grant.taxable_income:.2f}",
        deadline=deadline_result.deadline.isoformat(),
    )


def render_cover_sheet(grant: Grant, generated_at: str = None) -> str:
    deadline_result = compute_deadline(grant.grant_date)
    template = _load_template("cover_sheet.txt")
    return template.format(
        name=grant.name,
        company=grant.company,
        shares=grant.shares,
        grant_date=grant.grant_date.isoformat(),
        deadline=deadline_result.deadline.isoformat(),
        generated_at=generated_at or datetime.now().isoformat(timespec="seconds"),
    )
