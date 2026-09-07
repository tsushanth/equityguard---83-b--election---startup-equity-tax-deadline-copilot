"""Data models for grants, filings, and vesting events."""

from dataclasses import dataclass, asdict
from datetime import date, datetime
from typing import Optional


@dataclass
class Grant:
    id: int
    name: str
    company: str
    grant_date: date
    shares: int
    fmv: float
    price_paid: float
    created_at: str

    def to_dict(self) -> dict:
        d = asdict(self)
        d["grant_date"] = self.grant_date.isoformat()
        return d

    @staticmethod
    def from_dict(d: dict) -> "Grant":
        d = dict(d)
        d["grant_date"] = date.fromisoformat(d["grant_date"])
        return Grant(**d)

    @property
    def total_fmv(self) -> float:
        return round(self.shares * self.fmv, 2)

    @property
    def total_price_paid(self) -> float:
        return round(self.shares * self.price_paid, 2)

    @property
    def taxable_income(self) -> float:
        return round(self.total_fmv - self.total_price_paid, 2)


@dataclass
class FilingRecord:
    grant_id: int
    tracking_id: str
    method: str
    status: str
    submitted_at: str
    postmark_deadline: str
    letter_path: str
    cover_sheet_path: str

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "FilingRecord":
        return FilingRecord(**d)


@dataclass
class VestingReminder:
    months_from_grant: int
    vest_date: date
    reminder_date: date

    def to_dict(self) -> dict:
        return {
            "months_from_grant": self.months_from_grant,
            "vest_date": self.vest_date.isoformat(),
            "reminder_date": self.reminder_date.isoformat(),
        }
