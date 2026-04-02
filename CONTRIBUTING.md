# Contributing

Thanks for contributing to Task Scheduler.

This plugin is intended to be a practical reference for OpenAI Codex plugin authors, so changes should keep the codebase understandable, local-first, and easy to extend.

## Principles

- Keep the plugin simple to run locally.
- Prefer readable scheduling logic over clever heuristics.
- Keep MCP and CLI behavior aligned by sharing core logic.
- Document user-visible changes alongside code changes.
- Avoid breaking the plugin manifest, skill layout, or MCP config paths without updating the docs.

## Development Setup

1. Use Python 3.11+.
2. Install MCP dependencies:

```powershell
python -m pip install -r .\scripts\requirements-mcp.txt
```

3. Run the CLI against the sample input:

```powershell
python .\scripts\build_schedule.py `
  --input .\scripts\example_tasks.json
```

## What To Update When You Change Things

- If you change tool names or MCP resources, update `docs/MCP_REFERENCE.md`.
- If you change scheduling behavior, update `docs/ARCHITECTURE.md` and example output where needed.
- If you add new setup steps, update `README.md` and `docs/GETTING_STARTED.md`.
- If you change public plugin metadata, update `.codex-plugin/plugin.json`.

## Validation Checklist

Before opening a pull request:

1. Run Python compile checks:

```powershell
python -m py_compile `
  .\scripts\task_scheduler_core.py `
  .\scripts\build_schedule.py `
  .\scripts\mcp_server.py
```

2. Run the CLI:

```powershell
python .\scripts\build_schedule.py `
  --input .\scripts\example_tasks.json
```

3. If MCP dependencies are installed, start the MCP server and confirm it boots cleanly:

```powershell
python .\scripts\mcp_server.py
```

## Pull Request Guidance

- Keep PRs focused.
- Explain behavior changes, not just file changes.
- Include example input or example output when scheduling behavior changes.
- Call out any new placeholders, assumptions, or follow-up work explicitly.
