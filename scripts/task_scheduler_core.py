#!/usr/bin/env python3
"""Shared scheduling logic for the Task Scheduler plugin."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


DATE_FORMAT = "%Y-%m-%d"


@dataclass
class Task:
    title: str
    due: date
    estimated_hours: float
    priority: int
    notes: str
    tags: list[str]


@dataclass
class ScheduleOptions:
    start_date: date
    days: int
    hours_per_day: float
    blocked_dates: set[date]
    daily_capacity_overrides: dict[date, float]


def parse_iso_date(value: str, field_name: str) -> date:
    try:
        return datetime.strptime(value, DATE_FORMAT).date()
    except ValueError as exc:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format.") from exc


def load_input_file(path: Path) -> tuple[list[Task], dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return parse_input_payload(payload)


def parse_tasks_json(tasks_json: str) -> tuple[list[Task], dict[str, Any]]:
    payload = json.loads(tasks_json)
    return parse_input_payload(payload)


def parse_input_payload(payload: Any) -> tuple[list[Task], dict[str, Any]]:
    if isinstance(payload, list):
        return parse_tasks(payload), {}

    if not isinstance(payload, dict):
        raise ValueError("Task input must be a JSON array or an object with a tasks array.")

    raw_tasks = payload.get("tasks")
    if not isinstance(raw_tasks, list):
        raise ValueError("Object-style task input must include a 'tasks' array.")

    metadata: dict[str, Any] = {}
    for key in (
        "start_date",
        "days",
        "hours_per_day",
        "blocked_dates",
        "daily_capacity_overrides",
        "notes",
    ):
        if key in payload:
            metadata[key] = payload[key]

    return parse_tasks(raw_tasks), metadata


def parse_tasks(raw_tasks: list[Any]) -> list[Task]:
    tasks: list[Task] = []
    for index, item in enumerate(raw_tasks, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Task {index} must be an object.")

        title = str(item.get("title", "")).strip()
        if not title:
            raise ValueError(f"Task {index} is missing a title.")

        due_raw = str(item.get("due", "")).strip()
        if not due_raw:
            raise ValueError(f"Task {index} is missing a due date.")

        notes = str(item.get("notes", "")).strip()
        raw_tags = item.get("tags", [])
        tags = []
        if isinstance(raw_tags, list):
            tags = [str(tag).strip() for tag in raw_tags if str(tag).strip()]

        tasks.append(
            Task(
                title=title,
                due=parse_iso_date(due_raw, f"Task {index} due"),
                estimated_hours=max(0.5, float(item.get("estimated_hours", 1))),
                priority=max(1, min(int(item.get("priority", 3)), 5)),
                notes=notes,
                tags=tags,
            )
        )

    return tasks


def build_schedule_options(
    metadata: dict[str, Any],
    *,
    start_date: str | None = None,
    days: int | None = None,
    hours_per_day: float | None = None,
) -> ScheduleOptions:
    resolved_start = start_date or metadata.get("start_date") or date.today().isoformat()
    resolved_days = days if days is not None else int(metadata.get("days", 5))
    resolved_hours = (
        hours_per_day if hours_per_day is not None else float(metadata.get("hours_per_day", 6.0))
    )

    raw_blocked = metadata.get("blocked_dates", [])
    blocked_dates = set()
    if isinstance(raw_blocked, list):
        blocked_dates = {
            parse_iso_date(str(day), "blocked_dates entry")
            for day in raw_blocked
            if str(day).strip()
        }

    raw_overrides = metadata.get("daily_capacity_overrides", {})
    overrides: dict[date, float] = {}
    if isinstance(raw_overrides, dict):
        for raw_day, raw_hours in raw_overrides.items():
            overrides[parse_iso_date(str(raw_day), "daily_capacity_overrides key")] = max(
                0.0, float(raw_hours)
            )

    return ScheduleOptions(
        start_date=parse_iso_date(str(resolved_start), "start_date"),
        days=max(1, int(resolved_days)),
        hours_per_day=max(0.5, float(resolved_hours)),
        blocked_dates=blocked_dates,
        daily_capacity_overrides=overrides,
    )


def sort_tasks(tasks: list[Task]) -> list[Task]:
    return sorted(
        tasks,
        key=lambda task: (
            task.due,
            -task.priority,
            task.estimated_hours,
            task.title.lower(),
        ),
    )


def plan_schedule(
    tasks: list[Task], options: ScheduleOptions
) -> tuple[list[dict[str, Any]], list[Task]]:
    slots: list[dict[str, Any]] = []
    for offset in range(options.days):
        slot_date = options.start_date + timedelta(days=offset)
        capacity = options.daily_capacity_overrides.get(slot_date, options.hours_per_day)
        if slot_date in options.blocked_dates:
            capacity = 0.0

        slots.append(
            {
                "date": slot_date,
                "capacity": capacity,
                "remaining": capacity,
                "blocked": slot_date in options.blocked_dates,
                "tasks": [],
            }
        )

    overflow: list[Task] = []
    for task in sort_tasks(tasks):
        remaining = task.estimated_hours
        eligible_slots = [slot for slot in slots if slot["date"] <= task.due]
        if not eligible_slots:
            overflow.append(task)
            continue

        for slot in eligible_slots:
            if remaining <= 0:
                break
            if slot["remaining"] <= 0:
                continue

            assigned = min(float(slot["remaining"]), remaining)
            slot["tasks"].append(
                {
                    "title": task.title,
                    "hours": assigned,
                    "due": task.due.isoformat(),
                    "priority": task.priority,
                    "notes": task.notes,
                    "tags": task.tags,
                }
            )
            slot["remaining"] -= assigned
            remaining -= assigned

        if remaining > 0:
            overflow.append(
                Task(
                    title=task.title,
                    due=task.due,
                    estimated_hours=remaining,
                    priority=task.priority,
                    notes=task.notes,
                    tags=task.tags,
                )
            )

    return slots, overflow


def schedule_summary(
    slots: list[dict[str, Any]], overflow: list[Task]
) -> dict[str, Any]:
    total_capacity = sum(float(slot["capacity"]) for slot in slots)
    total_scheduled = sum(
        float(item["hours"]) for slot in slots for item in cast_task_entries(slot["tasks"])
    )
    blocked_days = [slot["date"].isoformat() for slot in slots if slot["blocked"]]
    return {
        "window_start": slots[0]["date"].isoformat(),
        "window_end": slots[-1]["date"].isoformat(),
        "scheduled_days": len(slots),
        "blocked_days": blocked_days,
        "total_capacity_hours": round(total_capacity, 2),
        "scheduled_hours": round(total_scheduled, 2),
        "overflow_hours": round(sum(task.estimated_hours for task in overflow), 2),
        "overflow_count": len(overflow),
        "utilization_percent": round((total_scheduled / total_capacity) * 100, 1)
        if total_capacity
        else 0.0,
    }


def cast_task_entries(entries: Any) -> list[dict[str, Any]]:
    return entries if isinstance(entries, list) else []


def render_markdown(
    slots: list[dict[str, Any]],
    overflow: list[Task],
    options: ScheduleOptions,
    notes: str = "",
) -> str:
    summary = schedule_summary(slots, overflow)
    lines = [
        "# Task Schedule",
        "",
        "## Summary",
        (
            f"- Planning window: {summary['window_start']} to {summary['window_end']} "
            f"({summary['scheduled_days']} days)"
        ),
        f"- Daily capacity target: {options.hours_per_day:g} hours",
        f"- Total scheduled: {summary['scheduled_hours']:g}/{summary['total_capacity_hours']:g} hours",
        f"- Overflow: {summary['overflow_count']} task(s), {summary['overflow_hours']:g} hours",
    ]
    if summary["blocked_days"]:
        lines.append(f"- Blocked dates: {', '.join(summary['blocked_days'])}")
    if notes:
        lines.append(f"- Planning notes: {notes}")

    lines.extend(["", "## Schedule", ""])

    for slot in slots:
        used_hours = float(slot["capacity"]) - float(slot["remaining"])
        heading = (
            f"### {slot['date'].isoformat()} "
            f"({used_hours:g}/{float(slot['capacity']):g} hours)"
        )
        if slot["blocked"]:
            heading += " [blocked]"
        lines.append(heading)

        if slot["blocked"]:
            lines.append("- Reserved day with no scheduling capacity.")
            lines.append("")
            continue

        if not slot["tasks"]:
            lines.append("- Buffer or admin time")
            lines.append("")
            continue

        for item in cast_task_entries(slot["tasks"]):
            reason = f"due {item['due']}, priority {item['priority']}"
            detail = f"- {item['title']} ({item['hours']:g}h, {reason})"
            if item["tags"]:
                detail += f" [{', '.join(item['tags'])}]"
            if item["notes"]:
                detail += f" - {item['notes']}"
            lines.append(detail)
        lines.append("")

    lines.append("## Follow-Ups")
    if overflow:
        for task in overflow:
            line = (
                f"- {task.title} ({task.estimated_hours:g}h unscheduled, "
                f"due {task.due.isoformat()}, priority {task.priority})"
            )
            if task.tags:
                line += f" [{', '.join(task.tags)}]"
            if task.notes:
                line += f" - {task.notes}"
            lines.append(line)
    else:
        lines.append("- No overflow tasks.")

    lines.extend(["", "## Risks"])
    tight_days = [slot for slot in slots if not slot["blocked"] and float(slot["remaining"]) <= 0.25]
    if tight_days:
        for slot in tight_days:
            lines.append(
                f"- {slot['date'].isoformat()} is effectively full. Consider adding buffer."
            )
    else:
        lines.append("- The schedule keeps some breathing room across the planning window.")

    return "\n".join(lines) + "\n"
