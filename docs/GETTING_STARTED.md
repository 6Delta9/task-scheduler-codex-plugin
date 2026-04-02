# Getting Started

This guide walks through local setup for the Task Scheduler Codex plugin.

## Prerequisites

- Python 3.11 or later
- a Codex workspace with plugin support
- PowerShell or another shell that can run Python commands

## 1. Place the plugin in your plugin directory

Repo-local layout:

```text
<repo-root>/plugins/task-scheduler
```

## 2. Install Python dependencies

```powershell
python -m pip install -r .\scripts\requirements-mcp.txt
```

## 3. Review the plugin manifest

Open:

```text
.codex-plugin/plugin.json
```

Confirm the manifest points to:

- `./skills/`
- `./hooks.json`
- `./.mcp.json`
- `./.app.json`

## 4. Review the MCP config

Open:

```text
.mcp.json
```

This plugin uses a local stdio MCP server launched with Python.

## 5. Run the CLI once

```powershell
python .\scripts\build_schedule.py `
  --input .\scripts\example_tasks.json
```

## 6. Start the MCP server once

```powershell
python .\scripts\mcp_server.py
```

If the `mcp` package is not installed yet, install it first with the command above.

## 7. Register the plugin in marketplace.json if desired

Marketplace file:

```text
<workspace-root>/.agents/plugins/marketplace.json
```

The plugin entry should point to:

```json
{
  "name": "task-scheduler",
  "source": {
    "source": "local",
    "path": "./plugins/task-scheduler"
  }
}
```

## First Things To Customize

Before publishing publicly, replace:

- author contact information
- screenshots and branding assets if you want production polish
- `.app.json` and `hooks.json` if you add real integrations
