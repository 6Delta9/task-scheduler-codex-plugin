#!/usr/bin/env python3
"""MCP server for the Task Scheduler plugin."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from task_scheduler_core import (
    build_schedule_options,
    parse_tasks_json,
    plan_schedule,
    render_markdown,
    schedule_summary,
)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - runtime dependency check
    raise SystemExit(
        "Missing dependency 'mcp'. Install it with "
        "`python -m pip install -r ./scripts/requirements-mcp.txt`."
    ) from exc


PLUGIN_ROOT = Path(__file__).resolve().parent.parent
README_PATH = PLUGIN_ROOT / "README.md"
SAMPLE_INPUT_PATH = PLUGIN_ROOT / "scripts" / "example_tasks.json"
mcp = FastMCP("task-scheduler")


def _plan_from_json(
    tasks_json: str,
    *,
    start_date: str | None = None,
    days: int | None = None,
    hours_per_day: float | None = None,
) -> tuple[str, dict[str, Any]]:
    tasks, metadata = parse_tasks_json(tasks_json)
    options = build_schedule_options(
        metadata,
        start_date=start_date,
        days=days,
        hours_per_day=hours_per_day,
    )
    slots, overflow = plan_schedule(tasks, options)
    notes = str(metadata.get("notes", "")).strip()
    markdown = render_markdown(slots, overflow, options, notes=notes)
    return markdown, schedule_summary(slots, overflow)


@mcp.tool()
def build_task_schedule(
    tasks_json: str,
    start_date: str | None = None,
    days: int | None = None,
    hours_per_day: float | None = None,
) -> str:
    """Build a markdown task schedule from JSON task data."""
    markdown, _summary = _plan_from_json(
        tasks_json,
        start_date=start_date,
        days=days,
        hours_per_day=hours_per_day,
    )
    return markdown


@mcp.tool()
def analyze_schedule_capacity(
    tasks_json: str,
    start_date: str | None = None,
    days: int | None = None,
    hours_per_day: float | None = None,
) -> dict[str, Any]:
    """Return capacity and overflow metrics for JSON task data."""
    _markdown, summary = _plan_from_json(
        tasks_json,
        start_date=start_date,
        days=days,
        hours_per_day=hours_per_day,
    )
    return summary


@mcp.tool()
def build_task_schedule_from_file(
    input_path: str,
    start_date: str | None = None,
    days: int | None = None,
    hours_per_day: float | None = None,
) -> str:
    """Build a markdown task schedule from a local JSON file path."""
    payload = Path(input_path).expanduser().read_text(encoding="utf-8")
    markdown, _summary = _plan_from_json(
        payload,
        start_date=start_date,
        days=days,
        hours_per_day=hours_per_day,
    )
    return markdown


@mcp.resource("task-scheduler://sample-input")
def sample_input() -> str:
    """Sample planning payload for the task scheduler."""
    return SAMPLE_INPUT_PATH.read_text(encoding="utf-8")


@mcp.resource("task-scheduler://readme")
def plugin_readme() -> str:
    """Plugin README with setup notes."""
    return README_PATH.read_text(encoding="utf-8")


@mcp.prompt()
def schedule_prompt(tasks_json: str) -> str:
    """Suggested prompt for asking an agent to use the scheduler."""
    return (
        "Use the task scheduler MCP tools to turn this task JSON into a realistic plan, "
        "then call out overflow, risks, and follow-ups:\n\n"
        f"{tasks_json}"
    )


if __name__ == "__main__":
    mcp.run()
