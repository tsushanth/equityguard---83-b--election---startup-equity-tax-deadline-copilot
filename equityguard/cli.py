"""Argument parsing and subcommand dispatch for the EquityGuard CLI."""

import argparse
import os
import sys
from datetime import date, datetime

from equityguard import storage
from equityguard.deadline import compute_deadline
from equityguard.document import render_cover_sheet, render_election_letter
from equityguard.filing import submit_filing
from equityguard.models import Grant
from equityguard.vesting import DEFAULT_VESTING_MONTHS, compute_vesting_reminders


def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def cmd_new_grant(args: argparse.Namespace) -> None:
    grants = storage.load_grants()
    grant = Grant(
        id=storage.next_grant_id(grants),
        name=args.name,
        company=args.company,
        grant_date=_parse_date(args.grant_date),
        shares=args.shares,
        fmv=args.fmv,
        price_paid=args.price_paid,
        created_at=datetime.now().isoformat(timespec="seconds"),
    )
    storage.add_grant(grant)
    deadline_result = compute_deadline(grant.grant_date)
    print(f"Created grant #{grant.id} for {grant.name} at {grant.company}")
    print(f"Grant date: {grant.grant_date.isoformat()}")
    print(f"83(b) filing deadline (30 days): {deadline_result.deadline.isoformat()}")
    if deadline_result.flagged:
        print(deadline_result.note)


def cmd_status(args: argparse.Namespace) -> None:
    grant = storage.get_grant(args.grant_id)
    if grant is None:
        print(f"No grant found with id {args.grant_id}", file=sys.stderr)
        sys.exit(1)
    deadline_result = compute_deadline(grant.grant_date)
    days_remaining = deadline_result.days_remaining(date.today())

    print(f"Grant #{grant.id}: {grant.name} at {grant.company}")
    print(f"  Grant date: {grant.grant_date.isoformat()}")
    print(f"  Shares: {grant.shares}")
    print(f"  83(b) filing deadline: {deadline_result.deadline.isoformat()}")
    if days_remaining >= 0:
        print(f"  Days remaining: {days_remaining}")
    else:
        print(f"  DEADLINE PASSED {-days_remaining} day(s) ago")
    if deadline_result.flagged:
        print(f"  {deadline_result.note}")

    filing_record = storage.load_filing_record(grant.id)
    if filing_record:
        print(f"  Filing status: {filing_record.status} (tracking {filing_record.tracking_id})")
    else:
        print("  Filing status: not yet filed")


def cmd_file(args: argparse.Namespace) -> None:
    grant = storage.get_grant(args.grant_id)
    if grant is None:
        print(f"No grant found with id {args.grant_id}", file=sys.stderr)
        sys.exit(1)

    filing_dir = storage.grant_filing_dir(grant.id)
    letter_path = os.path.join(filing_dir, "election_letter.txt")
    cover_sheet_path = os.path.join(filing_dir, "cover_sheet.txt")

    with open(letter_path, "w") as f:
        f.write(render_election_letter(grant))
    with open(cover_sheet_path, "w") as f:
        f.write(render_cover_sheet(grant))

    print(f"Wrote {letter_path}")
    print(f"Wrote {cover_sheet_path}")

    record = submit_filing(grant, letter_path, cover_sheet_path)
    proof_path = storage.save_filing_record(record)
    print(f"Wrote {proof_path}")


def cmd_remind(args: argparse.Namespace) -> None:
    grant = storage.get_grant(args.grant_id)
    if grant is None:
        print(f"No grant found with id {args.grant_id}", file=sys.stderr)
        sys.exit(1)

    months = DEFAULT_VESTING_MONTHS
    if args.vesting_months:
        months = [int(m) for m in args.vesting_months.split(",")]

    reminders = compute_vesting_reminders(grant.grant_date, months)

    filing_dir = storage.grant_filing_dir(grant.id)
    reminders_path = os.path.join(filing_dir, "vesting_reminders.json")
    import json

    with open(reminders_path, "w") as f:
        json.dump([r.to_dict() for r in reminders], f, indent=2)

    print(f"Vesting-event tax reminders for grant #{grant.id} ({grant.name}):")
    for r in reminders:
        print(
            f"  +{r.months_from_grant} months: vests {r.vest_date.isoformat()}, "
            f"reminder on {r.reminder_date.isoformat()}"
        )
    print(f"Wrote {reminders_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="equityguard",
        description="Track 83(b) election deadlines and generate filing paperwork.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_new = subparsers.add_parser("new-grant", help="Record a new restricted stock grant")
    p_new.add_argument("--name", required=True)
    p_new.add_argument("--company", required=True)
    p_new.add_argument("--grant-date", required=True, help="YYYY-MM-DD")
    p_new.add_argument("--shares", required=True, type=int)
    p_new.add_argument("--fmv", required=True, type=float, help="Fair market value per share")
    p_new.add_argument("--price-paid", required=True, type=float, help="Price paid per share")
    p_new.set_defaults(func=cmd_new_grant)

    p_status = subparsers.add_parser("status", help="Show deadline status for a grant")
    p_status.add_argument("--grant-id", required=True, type=int)
    p_status.set_defaults(func=cmd_status)

    p_file = subparsers.add_parser(
        "file", help="Generate filing documents and simulate certified-mail submission"
    )
    p_file.add_argument("--grant-id", required=True, type=int)
    p_file.set_defaults(func=cmd_file)

    p_remind = subparsers.add_parser("remind", help="Compute upcoming vesting tax-reminder dates")
    p_remind.add_argument("--grant-id", required=True, type=int)
    p_remind.add_argument(
        "--vesting-months",
        required=False,
        help="Comma-separated months from grant date, e.g. 12,24,36,48",
    )
    p_remind.set_defaults(func=cmd_remind)

    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
