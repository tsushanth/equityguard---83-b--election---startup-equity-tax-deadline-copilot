"""Upcoming vesting-event tax-reminder date computation."""

import calendar
from datetime import date, timedelta
from typing import List

from equityguard.models import VestingReminder

REMINDER_LEAD_DAYS = 14
DEFAULT_VESTING_MONTHS = [12, 24, 36, 48]


def add_months(d: date, months: int) -> date:
    total_month_index = d.month - 1 + months
    year = d.year + total_month_index // 12
    month = total_month_index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def compute_vesting_reminders(
    grant_date: date, vesting_months: List[int] = None
) -> List[VestingReminder]:
    """Reminders fire REMINDER_LEAD_DAYS before each vesting-event date."""
    months = vesting_months or DEFAULT_VESTING_MONTHS
    reminders = []
    for m in months:
        vest_date = add_months(grant_date, m)
        reminder_date = vest_date - timedelta(days=REMINDER_LEAD_DAYS)
        reminders.append(
            VestingReminder(
                months_from_grant=m, vest_date=vest_date, reminder_date=reminder_date
            )
        )
    return reminders
