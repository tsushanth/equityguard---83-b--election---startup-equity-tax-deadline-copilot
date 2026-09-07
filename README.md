# EquityGuard

A local CLI proving the core value of an 83(b) election / startup-equity
tax-deadline copilot: given a restricted-stock grant, it

1. computes the hard 30-calendar-day IRS 83(b) filing deadline (and flags,
   without silently shifting, cases where that deadline lands on a weekend
   or federal holiday),
2. generates a correctly-filled 83(b) election letter and IRS transmittal
   cover sheet as real text files,
3. simulates the certified-mail submission step and writes a
   proof-of-filing record, and
4. computes upcoming vesting-event tax-reminder dates.

This is a local MVP scaffold, not the product: no web UI, no accounts, no
payments, and no real certified-mail API calls. See `plan.md` for the full
scope and what's intentionally left out.

## Requirements

Python 3.9+, stdlib only. `pytest` is only needed to run the test suite.

```
pip install -r requirements-dev.txt
```

## Usage

Run everything as a module from the repository root.

```bash
# 1. Record a new restricted stock grant.
python -m equityguard new-grant --name "Jane Doe" --company "Acme Inc" \
    --grant-date 2026-08-20 --shares 10000 --fmv 0.01 --price-paid 0.0001

# 2. Check the 83(b) deadline and days remaining.
python -m equityguard status --grant-id 1

# 3. Generate the election letter + cover sheet, and simulate certified-mail
#    filing (writes a proof-of-filing record with a fake tracking ID).
python -m equityguard file --grant-id 1

# 4. Compute upcoming vesting-event tax-reminder dates.
python -m equityguard remind --grant-id 1 --vesting-months 12,24,36,48
```

All data is stored locally as flat JSON/text files under `equityguard/data/`
(created on first run, gitignored):

```
equityguard/data/
  grants.json                       # all grants entered so far
  filings/<grant-id>/
    election_letter.txt             # generated 83(b) election letter
    cover_sheet.txt                 # generated IRS submission cover sheet
    proof_of_filing.json            # mock certified-mail tracking record
    vesting_reminders.json          # computed vesting reminder dates
```

No network calls are made anywhere in this flow. The mock certified-mail
step in `equityguard/filing.py` is written behind a `submit_filing(...)`
function boundary so a real API (e.g. Lob) could later be swapped in
without touching any other module.

## Tests

```bash
python -m pytest equityguard/tests -q
```

Covers deadline math (including a leap-year grant and weekend/holiday
deadlines), the generated letter's figures and required IRS statement
language, the mock filing's proof-of-filing record, and vesting-reminder
date computation for a 4-year/1-year-cliff schedule.

## Project layout

```
equityguard/
  __main__.py     # `python -m equityguard` entry point
  cli.py          # argparse subcommands: new-grant, status, file, remind
  models.py       # Grant, FilingRecord, VestingReminder dataclasses
  deadline.py     # 30-day deadline math + weekend/holiday flagging
  document.py     # renders election letter + cover sheet from templates
  filing.py       # mock certified-mail submission (no network calls)
  vesting.py      # vesting-event tax-reminder date computation
  storage.py      # local JSON flat-file read/write
  templates/      # election_letter.txt, cover_sheet.txt
  tests/          # pytest suite
```
