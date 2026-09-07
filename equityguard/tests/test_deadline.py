from datetime import date

from equityguard.deadline import compute_deadline


def test_basic_30_day_deadline():
    result = compute_deadline(date(2026, 8, 20))
    assert result.deadline == date(2026, 9, 19)


def test_leap_year_february_grant():
    # 2028 is a leap year; grant on Feb 1 -> deadline crosses Feb 29.
    result = compute_deadline(date(2028, 2, 1))
    assert result.deadline == date(2028, 3, 2)


def test_deadline_on_weekend_is_flagged_not_shifted():
    # 2026-09-05 is a Saturday; grant date 30 days earlier lands the
    # deadline squarely on that weekend day.
    grant_date = date(2026, 8, 6)
    result = compute_deadline(grant_date)
    assert result.deadline == date(2026, 9, 5)
    assert result.deadline.weekday() == 5  # Saturday
    assert result.is_weekend is True
    assert result.flagged is True
    assert "does not assume" in result.note


def test_deadline_on_holiday_is_flagged_not_shifted():
    # Grant date such that +30 days lands on Thanksgiving 2026 (Nov 26,
    # a Thursday -- a holiday but not a weekend, to isolate the check).
    grant_date = date(2026, 10, 27)
    result = compute_deadline(grant_date)
    assert result.deadline == date(2026, 11, 26)
    assert result.is_weekend is False
    assert result.is_holiday is True
    assert result.flagged is True


def test_non_flagged_weekday_deadline_has_no_note():
    # 2026-07-01 + 30 days = 2026-07-31, a Friday with no federal holiday.
    result = compute_deadline(date(2026, 7, 1))
    assert result.deadline == date(2026, 7, 31)
    assert result.flagged is False
    assert result.note == ""


def test_days_remaining():
    result = compute_deadline(date(2026, 7, 1))
    assert result.days_remaining(date(2026, 7, 1)) == 30
    assert result.days_remaining(date(2026, 7, 31)) == 0
    assert result.days_remaining(date(2026, 8, 1)) == -1
