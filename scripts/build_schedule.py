#!/usr/bin/env python3
"""Build a day-by-day schedule from structured task JSON."""

from __future__ import annotations

import argparse
from pathlib import Path

from task_scheduler_core import (
    build_schedule_options,
    load_input_file,
    plan_schedule,
    render_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a task list into a simple markdown schedule."
    )
    parser.add_argument("--input", required=True, help="Path to a JSON task list.")
    parser.add_argument(
        "--start-date",
        help=(
            "Optional schedule start date in YYYY-MM-DD format. "
            "Overrides any start_date in the input file."
        ),
    )
    parser.add_argument(
        "--days",
        type=int,
        help="Optional number of days to schedule. Overrides any value in the input file.",
    )
    parser.add_argument(
        "--hours-per-day",
        type=float,
        help=(
            "Optional working hours per day. Overrides any hours_per_day value "
            "in the input file."
        ),
    )
    parser.add_argument(
        "--output",
        help="Optional markdown output path. Prints to stdout when omitted.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    tasks, metadata = load_input_file(input_path)
    options = build_schedule_options(
        metadata,
        start_date=args.start_date,
        days=args.days,
        hours_per_day=args.hours_per_day,
    )
    slots, overflow = plan_schedule(tasks, options)
    markdown = render_markdown(slots, overflow, options, notes=str(metadata.get("notes", "")))

    if args.output:
        Path(args.output).write_text(markdown, encoding="utf-8")
    else:
        print(markdown, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
