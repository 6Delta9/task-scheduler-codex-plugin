# Publishing Guide

This guide helps you prepare Task Scheduler for a public GitHub release.

## Before Publishing

Replace the current placeholders in:

```text
.codex-plugin/plugin.json
```

Recommended updates:

- `interface.websiteURL`
- `interface.privacyPolicyURL`
- `interface.termsOfServiceURL`

## GitHub Repository Checklist

- add a repository-level `LICENSE`
- add a repository-level `.gitignore`
- add a repository-level `SECURITY.md`
- add a repository-level `.codexignore`
- include this plugin `README.md` at the repo root or link to it clearly
- confirm all screenshots and icons are final
- remove generated cache files before publishing
- ensure example data is safe to share publicly
- enable the Codex plugin scanner workflow in `.github/workflows/`

## Codex Plugin Checklist

- confirm `.codex-plugin/plugin.json` is accurate
- confirm `.mcp.json` starts the intended local server
- confirm marketplace entry points to `./plugins/task-scheduler`
- confirm the skill path is correct
- confirm MCP dependency installation instructions are accurate

## Recommended Validation Before Release

```powershell
python -m py_compile `
  .\scripts\task_scheduler_core.py `
  .\scripts\build_schedule.py `
  .\scripts\mcp_server.py

python .\scripts\build_schedule.py `
  --input .\scripts\example_tasks.json
```

If dependencies are installed:

```powershell
python .\scripts\mcp_server.py
```

## Suggested Release Notes Structure

- what the plugin does
- who it is for
- how to install it
- what MCP tools it exposes
- what is still a placeholder or starter implementation

## Public Positioning

When you publish, describe it honestly:

- it is a functional local Codex plugin
- it includes a working MCP server
- it is a strong starter for scheduling and planning workflows
- it is also a reference implementation for authors building their own Codex plugins
