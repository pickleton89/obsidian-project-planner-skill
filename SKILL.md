---
name: obsidian-project-planner
description: >-
  Inspect explicitly requested Obsidian Project Planner projects, tasks, boards,
  and Gantt-related data. Use for /pp or a named Project Planner request.
  Generic Obsidian task requests use obsidian-tasknotes. This helper is read-only.
version: "2.1.0"
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash
argument-hint: "[status|list-projects|list|board|query|ensure-sync]"
---

# Project Planner

Read the selected vault's Project Planner data using `scripts/pp_manager.py`
relative to this skill source. Use `uv run --no-project --no-config --offline python`
and supply an explicit `--vault` path. Read `--help` for command-specific options.
Use JSON output for analysis, and preserve project/task IDs in reports.

The reader supports the installed `settings.projects` plus `tasksByProject` layout.
A version 1 per-project `.planner-tasks.json` reader is fixture-tested, including
project identity and path containment. It has not been tested with a live newer plugin.
Missing or unrecognized storage must be reported, never described as an empty board.

## Write boundary

The old JSON/Markdown writer is disabled. It can lose note content, ignore the
configured project path, and conflict with plugin synchronization. Creation, updates,
deletes and CSV execution therefore stop before file mutation. This is a containment
repair, not a replacement writer. Make such changes through the Project Planner UI;
do not bypass the guard by editing `.obsidian` data or generating task files manually.
CSV dry-run can preview the parser but is not evidence of successful import support.

## Host behavior

Use the tools actually available in the current host. No model, fork, or sub-agent
is required. Claude invocation metadata does not define Codex permissions.
`install` remains a maintenance operation backed by the shared source installer;
it is not part of ordinary project inspection. Reference documents describing old
write workflows are historical and do not override this boundary.
