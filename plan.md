# EquityGuard — Local MVP Scaffold Plan

## Goal

Prove the core value locally: given a restricted-stock grant, (1) compute the
hard 30-day 83(b) filing deadline correctly, (2) generate a correctly-filled
83(b) election letter + IRS cover documents as real files, (3) simulate the
certified-mail submission step and produce a "proof of filing" record, and
(4) compute upcoming vesting-event tax reminder dates. No web app, no
accounts, no payments — just a CLI that produces real, inspectable output
files from real input data.

## 1. Stack

**Python 3 + stdlib only, single CLI entry point.**

- No web framework, no database engine, no external HTTP calls.
- `argparse` for the CLI, `dataclasses` for models, `datetime` for date math,
  `json` for flat-file storage, plain `.format()`/f-strings for document
  templating.
- One dependency exception: `pytest` (dev-only) for tests.

Why this over Node/TS or Go: the core value here is entirely date-math +
text-templating + record-keeping logic — no concurrency, no need for a
compiled binary, no need for npm tooling. Python's stdlib covers all of it
with zero install step beyond the interpreter, which keeps the demo to
`python -m equityguard ...`.

## 2. Explicitly out of scope for this local demo

- **Auth / user accounts** — CLI takes grant data as input args/JSON; no
  login, no multi-tenant concept.
- **Billing / payments** — not needed to demonstrate deadline tracking or
  document generation.
- **Hosting / deployment** — runs locally only.
- **Web UI** — CLI + generated files stand in for the web app's screens.
- **Real Lob (or any) certified-mail API integration** — the "submission"
  step is mocked: it prints what would be sent and writes a fake
  tracking-ID + timestamp to a local JSON "proof of filing" record. The
  module boundary (`filing.py`) is written so a real Lob client could later
  be swapped in behind the same function signature, but no network calls
  are made and no API key is required.
- **Email/SMS delivery of reminders** — vesting reminders are computed and
  printed/written to a file, not actually sent anywhere.
- **Bulk HR/enrollment tooling** — out of scope for this MVP; single-grant
  flow only, since it's the harder and more novel part of the idea to prove
  first.
- **PDF rendering / e-signature** — generated filing documents are plain
  text/Markdown, not styled PDFs.

These are cut because the core value proposition — "never miss the 30-day
83(b) window, and get the correct paperwork automatically" — is fully
demonstrable with local date math, local templating, and a local flat file
standing in for "proof of filing." None of the cut items are load-bearing
for that demonstration.

## 3. File / directory layout

```
equityguard/
  __main__.py          # `python -m equityguard` entry point, wires up argparse subcommands
  cli.py                # argument parsing + subcommand dispatch (new-grant, file, remind, status)
  models.py             # Grant, VestingEvent, FilingRecord dataclasses
  deadline.py           # 30-calendar-day deadline calculation (incl. leap year, IRS mailbox rule)
  document.py           # renders the 83(b) election letter + IRS transmittal cover sheet as text
  filing.py             # mock certified-mail "submission" — stubbed Lob-shaped interface, returns fake tracking ID
  vesting.py            # given a vesting schedule, computes upcoming tax-reminder dates
  storage.py            # read/write local JSON flat files under data/
  templates/
    election_letter.txt # 83(b) election letter template with {placeholders}
    cover_sheet.txt      # IRS submission cover sheet template
  data/                  # created at runtime, gitignored
    grants.json          # local "database" of grants entered so far
    filings/              # one generated letter + proof-of-filing record per grant
  tests/
    test_deadline.py      # deadline math incl. edge cases (leap year, 30-day boundary)
    test_document.py      # generated letter contains correct figures/dates for a sample grant
    test_filing.py         # mock filing produces a proof record with expected fields
    test_vesting.py         # vesting reminder dates computed correctly from a schedule
README.md                # how to run the demo (already covered by section 4 below)
```

## 4. Verification

**Automated:**
- `pytest tests/` covering:
  - `deadline.py`: grant date → correct 30-calendar-day due date, including
    a leap-year Feb grant and a due date landing on a weekend/holiday (IRS
    mailbox rule — postmark by the deadline still counts, so the tool
    should flag but not silently shift the date).
  - `document.py`: rendered letter for a sample grant contains the right
    name, share count, FMV, grant date, and taxpayer statement language
    required by the IRS.
  - `filing.py`: mock submission returns a proof-of-filing record with a
    tracking ID, timestamp, and status, without making any network call.
  - `vesting.py`: a 4-year/1-year-cliff schedule produces the expected list
    of upcoming vesting reminder dates.

**Manual run-through (single command sequence proving the end-to-end flow):**
```
python -m equityguard new-grant --name "Jane Doe" --company "Acme Inc" \
    --grant-date 2026-08-20 --shares 10000 --fmv 0.01 --price-paid 0.0001

python -m equityguard status --grant-id 1
# → shows days remaining until the 30-day 83(b) deadline

python -m equityguard file --grant-id 1
# → writes data/filings/1/election_letter.txt + cover_sheet.txt
# → prints mock certified-mail submission output and writes
#   data/filings/1/proof_of_filing.json with a fake tracking ID

python -m equityguard remind --grant-id 1 --vesting-months 12,24,36,48
# → prints/writes the list of upcoming vesting-event tax-reminder dates
```
Success = each command runs with no network access, the generated letter
file contains correct figures pulled from the input, the deadline shown
matches a hand-calculated 30-calendar-day date, and the proof-of-filing
JSON round-trips through `storage.py`.
