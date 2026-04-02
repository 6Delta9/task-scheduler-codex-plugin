# MCP Reference

Task Scheduler exposes a local stdio MCP server from:

```text
scripts/mcp_server.py
```

The server is registered in:

```text
.mcp.json
```

## Server Purpose

The MCP server gives agents a structured way to request schedule generation and capacity analysis without calling the CLI directly.

## Tools

### `build_task_schedule`

Builds a markdown task schedule from a JSON string.

Parameters:

- `tasks_json`: string containing either a task array or an object with `tasks`
- `start_date`: optional override in `YYYY-MM-DD`
- `days`: optional planning window override
- `hours_per_day`: optional daily capacity override

Returns:

- markdown schedule with `Summary`, `Schedule`, `Follow-Ups`, and `Risks`

### `analyze_schedule_capacity`

Computes high-level capacity information from the same JSON input.

Parameters:

- `tasks_json`
- `start_date`
- `days`
- `hours_per_day`

Returns a JSON object containing:

- `window_start`
- `window_end`
- `scheduled_days`
- `blocked_days`
- `total_capacity_hours`
- `scheduled_hours`
- `overflow_hours`
- `overflow_count`
- `utilization_percent`

### `build_task_schedule_from_file`

Builds a markdown schedule from a local JSON file path.

Parameters:

- `input_path`
- `start_date`
- `days`
- `hours_per_day`

Returns:

- markdown schedule

## Resources

### `task-scheduler://sample-input`

Returns the contents of the sample task input file.

### `task-scheduler://readme`

Returns the plugin README.

## Prompt

### `schedule_prompt`

Accepts a JSON string and returns a ready-to-use planning prompt that tells an agent to use the task scheduler MCP tools.

## Local Configuration

Current `.mcp.json` shape:

```json
{
  "mcpServers": {
    "taskScheduler": {
      "command": "python",
      "args": ["./scripts/mcp_server.py"],
      "cwd": ".",
      "env": {
        "PYTHONUTF8": "1"
      },
      "startup_timeout_sec": 20,
      "tool_timeout_sec": 60
    }
  }
}
```

## Notes

- The server depends on the Python `mcp` package.
- The scheduling logic is shared with the CLI through `task_scheduler_core.py`.
- If you add or rename tools, update this document and the public README.
