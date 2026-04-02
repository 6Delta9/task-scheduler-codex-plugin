# Architecture

This document explains how Task Scheduler is structured internally.

## High-Level Design

The plugin has four layers:

1. Plugin metadata
2. Scheduling engine
3. Interfaces
4. User-facing assets and docs

## 1. Plugin Metadata

These files describe the plugin to Codex:

- `.codex-plugin/plugin.json`
- `.mcp.json`
- `.app.json`
- `hooks.json`
- `.agents/plugins/marketplace.json` in the workspace root

`plugin.json` is the main manifest and points to skills, hooks, MCP config, and app config.

## 2. Scheduling Engine

Core logic lives in:

```text
scripts/task_scheduler_core.py
```

This module handles:

- parsing JSON input
- validating task and date fields
- resolving planning options
- sorting work by due date and priority
- assigning work across available days
- computing overflow and utilization summaries
- rendering markdown output

### Scheduling rules

The current strategy is intentionally simple and transparent:

- earlier due dates are scheduled first
- higher-priority tasks win ties
- capacity is enforced per day
- blocked dates get zero capacity
- daily capacity overrides replace the default hours for a specific date
- remaining work becomes overflow when it cannot fit before its due date

This design favors explainability over optimization complexity.

## 3. Interfaces

### CLI

The CLI wrapper lives in:

```text
scripts/build_schedule.py
```

It loads a JSON file, resolves overrides from command-line flags, and prints markdown output.

### MCP

The MCP interface lives in:

```text
scripts/mcp_server.py
```

It exposes the scheduler as tools, resources, and a prompt so other agents can interact with the planner programmatically.

### Skill

The Codex skill lives in:

```text
skills/task-planner/SKILL.md
```

It guides the agent toward collecting the right planning inputs and presenting results in a useful structure.

## 4. Assets and Documentation

User-facing presentation lives in:

- `assets/`
- `README.md`
- `docs/`

These files make the plugin understandable and discoverable in both Codex UI and GitHub.

## Extension Points

Good future extension points include:

- recurring task support
- task dependencies
- smarter rescheduling strategies
- exports to task systems or calendars
- additional MCP tools for optimization and explanation

## Why The Core Is Shared

The CLI and MCP server both call the same scheduling engine. That reduces drift and keeps output behavior consistent across direct shell usage and agent-driven usage.
