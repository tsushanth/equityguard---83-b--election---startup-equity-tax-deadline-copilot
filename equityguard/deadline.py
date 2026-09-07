"""30-calendar-day 83(b) election deadline math.

The IRS requires an 83(b) election to be filed (i.e. postmarked, per the
IRC section 7502 mailbox rule) within 30 days after the date restricted
property is transferred. This module computes that raw calendar-day
deadline and flags -- but does not silently shift -- cases where the
deadline lands on a weekend or federal holiday, since IRC section 7503
extends the deadline to the next business day in that case and a founder
should be told explicitly rather than have the tool guess.
"""

from dataclasses import dataclass
from datetime import date, timedelta

ELECTION_WINDOW_DAYS = 30


def _nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    """weekday: Monday=0 ... Sunday=6. n is 1-indexed occurrence."""
    d = date(year, month, 1)
    offset = (weekday - d.weekday()) % 7
    d += timedelta(days=offset + 7 * (n - 1))
    return d


def _last_weekday_of_month(year: int, month: int, weekday: int) -> date:
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    d = next_month - timedelta(days=1)
    offset = (d.weekday() - weekday) % 7
    return d - timedelta(days=offset)


def _observed(d: date) -> date:
    """Federal holidays falling on Sat/Sun are observed the nearest weekday."""
    if d.weekday() == 5:  # Saturday -> observed Friday
        return d - timedelta(days=1)
    if d.weekday() == 6:  # Sunday -> observed Monday
        return d + timedelta(days=1)
    return d


def us_federal_holidays(year: int) -> set:
    """Fixed-date and floating US federal holidays, with weekend observance."""
    fixed = [
        date(year, 1, 1),   # New Year's Day
        date(year, 6, 19),  # Juneteenth
        date(year, 7, 4),   # Independence Day
        date(year, 11, 11), # Veterans Day
        date(year, 12, 25), # Christmas Day
    ]
    holidays = {_observed(d) for d in fixed}
    holidays.add(_nth_weekday_of_month(year, 1, 0, 3))   # MLK Day: 3rd Mon Jan
    holidays.add(_nth_weekday_of_month(year, 2, 0, 3))   # Presidents Day: 3rd Mon Feb
    holidays.add(_last_weekday_of_month(year, 5, 0))     # Memorial Day: last Mon May
    holidays.add(_nth_weekday_of_month(year, 9, 0, 1))   # Labor Day: 1st Mon Sep
    holidays.add(_nth_weekday_of_month(year, 10, 0, 2))  # Columbus Day: 2nd Mon Oct
    holidays.add(_nth_weekday_of_month(year, 11, 3, 4))  # Thanksgiving: 4th Thu Nov
    return holidays


@dataclass
class DeadlineResult:
    grant_date: date
    deadline: date
    is_weekend: bool
    is_holiday: bool

    @property
    def flagged(self) -> bool:
        return self.is_weekend or self.is_holiday

    @property
    def note(self) -> str:
        if not self.flagged:
            return ""
        reason = "a weekend" if self.is_weekend else "a federal holiday"
        return (
            f"Note: the 30-day deadline of {self.deadline.isoformat()} falls on "
            f"{reason}. Under IRC section 7503, a mailing postmarked on the next "
            "business day may still be timely, but this tool does not assume "
            "that extension for you -- confirm with a tax professional and, "
            "when in doubt, mail earlier."
        )

    def days_remaining(self, as_of: date) -> int:
        return (self.deadline - as_of).days


def compute_deadline(grant_date: date) -> DeadlineResult:
    deadline = grant_date + timedelta(days=ELECTION_WINDOW_DAYS)
    is_weekend = deadline.weekday() >= 5
    is_holiday = deadline in us_federal_holidays(deadline.year)
    return DeadlineResult(
        grant_date=grant_date,
        deadline=deadline,
        is_weekend=is_weekend,
        is_holiday=is_holiday,
    )
