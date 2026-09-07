from datetime import date

from equityguard.vesting import add_months, compute_vesting_reminders


def test_add_months_basic():
    assert add_months(date(2026, 8, 20), 12) == date(2027, 8, 20)
    assert add_months(date(2026, 8, 20), 24) == date(2028, 8, 20)


def test_add_months_clamps_day_for_shorter_month():
    # Jan 31 + 1 month -> Feb has no 31st day, clamp to Feb 28/29.
    assert add_months(date(2026, 1, 31), 1) == date(2026, 2, 28)
    assert add_months(date(2028, 1, 31), 1) == date(2028, 2, 29)  # leap year


def test_four_year_one_year_cliff_schedule():
    grant_date = date(2026, 8, 20)
    reminders = compute_vesting_reminders(grant_date, [12, 24, 36, 48])

    assert [r.months_from_grant for r in reminders] == [12, 24, 36, 48]
    assert reminders[0].vest_date == date(2027, 8, 20)
    assert reminders[1].vest_date == date(2028, 8, 20)
    assert reminders[2].vest_date == date(2029, 8, 20)
    assert reminders[3].vest_date == date(2030, 8, 20)

    # Reminder fires 14 days before each vesting event.
    for r in reminders:
        assert (r.vest_date - r.reminder_date).days == 14


def test_default_vesting_months_used_when_not_specified():
    reminders = compute_vesting_reminders(date(2026, 8, 20))
    assert [r.months_from_grant for r in reminders] == [12, 24, 36, 48]
