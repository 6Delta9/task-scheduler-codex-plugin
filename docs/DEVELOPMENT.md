# Development Guide

This guide covers day-to-day development for Task Scheduler.

## Local Workflow

### Install dependencies

```powershell
python -m pip install -r .\scripts\requirements-mcp.txt
```

### Run compile checks

```powershell
python -m py_compile `
  .\scripts\task_scheduler_core.py `
  .\scripts\build_schedule.py `
  .\scripts\mcp_server.py
```

### Run the sample schedule

```powershell
python .\scripts\build_schedule.py `
  --input .\scripts\example_tasks.json
```

### Start the MCP server

```powershell
python .\scripts\mcp_server.py
```

## File Responsibilities

- `scripts/task_scheduler_core.py`: scheduling model, parsing, summaries, rendering
- `scripts/build_schedule.py`: CLI entrypoint
- `scripts/mcp_server.py`: MCP entrypoint
- `scripts/example_tasks.json`: sample input and test fixture
- `skills/task-planner/SKILL.md`: Codex skill behavior
- `.codex-plugin/plugin.json`: plugin manifest and UI metadata
- `.mcp.json`: MCP server registration

## When Adding Features

If you add a feature, try to answer these questions:

- Does it belong in the shared core or only in one interface?
- Does it change the JSON input shape?
- Does it change tool signatures in the MCP server?
- Does it require README or docs updates?
- Does it need new sample data?

## Suggested Testing Strategy

- use `py_compile` for quick syntax validation
- run the CLI with the example JSON
- test at least one overflow scenario
- test at least one blocked-date scenario
- test one per-day capacity override
- if MCP is installed, start the server and exercise the tools

## Backward Compatibility

When possible:

- keep existing input keys stable
- keep MCP tool names stable
- add new optional fields rather than breaking existing shapes

This makes the plugin easier to adopt and safer to evolve.
