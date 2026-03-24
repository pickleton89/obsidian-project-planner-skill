---
name: obsidian-project-planner
description: >
  Manage projects and tasks for the Obsidian Project Planner plugin via markdown files
  and data.json. Supports full CRUD, CSV import, board/list views, and batch operations.
  Triggers on "/pp" commands or mentions of project planner, task management, kanban, or Gantt in Obsidian.
version: "2.0.0"
user-invocable: true
context: fork
model: sonnet
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Agent
argument-hint: "[status|create-project|add-task|update-task|list|board|import-csv|install|help] -- manage Obsidian Project Planner"
---

# Obsidian Project Planner Skill

Manage projects and tasks for the [Obsidian Project Planner](https://projectplanner.md/) plugin
directly from Claude Code. All operations are handled by deterministic Python scripts that read
and write the plugin's data through markdown task files (bidirectional sync) and `data.json`.

**Plugin docs:** https://projectplanner.md/docs/
**GitHub:** https://github.com/ArctykDev/obsidian-project-planner

## Runtime Configuration (Step 0)

Before any operation, resolve the vault path and plugin data:

1. **Vault path** -- Check `$ARGUMENTS` for an explicit `--vault PATH`. If absent, try
   auto-discovery by running:
   ```bash
   python3 -c "import sys; sys.path.insert(0,'scripts'); from common import discover_vault; v=discover_vault(); print(v or 'NOT_FOUND')"
   ```
   If not found, ask the user for their vault path.

2. **Plugin data** -- Verify the plugin is installed:
   ```bash
   uv run python scripts/pp_manager.py --vault <vault-path> ensure-sync
   ```
   If data.json doesn't exist, the plugin isn't installed -- inform the user.

3. **Load both reference files** (always, regardless of operation):
   - `references/frontmatter-spec.md` (YAML field reference for task markdown files)
   - `references/data-schema.md` (JSON schema reference for data.json)

---

## EXECUTE NOW

**Target: $ARGUMENTS**

Parse the command:

| Command | Action |
|---------|--------|
| (none) or `status` | Show project/task overview |
| `create-project "Name"` | Create a new project |
| `add-task "Title" [options]` | Add a task to a project |
| `update-task "Title" [options]` | Update an existing task |
| `delete-task "Title" [options]` | Delete a task |
| `list [options]` | List/filter tasks |
| `board [project]` | Show board view summary |
| `import-csv <file> [options]` | Import tasks from CSV/TSV |
| `install [vault-path]` | Install/update skill into a vault |
| `help` | Show available commands |

**START NOW.** Execute the requested operation using the scripts below.

---

## Data Strategy

**Markdown-first, JSON-when-needed.** The scripts detect sync mode automatically and route
writes to the appropriate target. You do not need to branch between markdown and JSON writes --
just call the script.

- **Tasks** -- Created and updated via `pp_manager.py add-task` / `update-task`. When markdown
  sync is enabled, the script writes `.md` files to `{ProjectName}/Tasks/{TaskTitle}.md` with
  YAML frontmatter. When sync is disabled, it writes directly to `data.json`.

- **Projects, buckets, settings** -- Managed via `pp_manager.py create-project` / `add-bucket`.
  There is no markdown representation for projects.

- **Reading/querying** -- Use `pp_manager.py status`, `list`, or `board`. These always read
  from `data.json` for the complete picture.

All IDs are RFC 4122 v4 UUIDs, generated automatically by the scripts.

---

## Commands

### /pp status

Show an overview of all projects, task counts, and completion rates.

```bash
uv run python scripts/pp_manager.py --vault <vault-path> status
```

Add `--json` for machine-readable output.

### /pp create-project "Name"

Create a new project with default buckets.

**Options:**
- `--start YYYY-MM-DD` -- project start date
- `--due YYYY-MM-DD` -- project due date
- `--buckets "Bucket1,Bucket2,Bucket3"` -- custom bucket names (default: To Do, In Progress, Done)

```bash
uv run python scripts/pp_manager.py --vault <vault-path> create-project "Sprint 4" \
  --start 2026-04-01 --due 2026-04-30 --buckets "To Do,In Progress,Review,Done"
```

### /pp add-task "Title"

Add a new task to a project. The script handles UUID generation, bucket/parent/dependency
resolution, markdown file creation (or data.json writes), and tag registration.

**Options:**
- `--project "Name"` -- target project (required if multiple projects exist)
- `--status "Not Started"` -- task status (default: Not Started)
- `--priority high|medium|low` -- priority level
- `--bucket "Bucket Name"` -- board bucket assignment
- `--start YYYY-MM-DD` -- start date
- `--due YYYY-MM-DD` -- due date
- `--tags "tag1,tag2"` -- comma-separated tags
- `--parent "Parent Task Title"` -- make this a subtask of another task
- `--depends-on "Task Title"` -- add a dependency (comma-separated for multiple)
- `--description "text"` -- task description body
- `--effort-remaining N` -- estimated hours of work

```bash
uv run python scripts/pp_manager.py --vault <vault-path> add-task "Design landing page" \
  --project "Sprint 4" --priority high --due 2026-04-15 --bucket "To Do" --tags "design,frontend"
```

### /pp update-task "Title"

Update an existing task's fields. Uses 2-tier matching (exact then substring) to find the task.

**Options:** Same as `add-task` plus:
- `--complete` -- mark as completed (sets `status: Completed`, `completed: true`)
- `--rename "New Title"` -- rename the task (handles file rename for markdown sync)

```bash
uv run python scripts/pp_manager.py --vault <vault-path> update-task "Design landing" \
  --project "Sprint 4" --status "In Progress" --priority high
```

If multiple tasks match the title, the script lists them and exits -- be more specific.

### /pp delete-task "Title"

Delete a task. Requires `--force` to confirm.

**Options:**
- `--project "Name"` -- target project
- `--force` -- confirm deletion

The script automatically:
- Removes the task from `data.json`
- Deletes the markdown file if it exists
- Removes dependency references from other tasks
- Promotes child tasks to root level

```bash
uv run python scripts/pp_manager.py --vault <vault-path> delete-task "Old task" \
  --project "Sprint 4" --force
```

### /pp list

List and filter tasks.

**Options:**
- `--project "Name"` -- filter by project (default: all projects)
- `--status "In Progress"` -- filter by status
- `--priority high` -- filter by priority
- `--bucket "Bucket Name"` -- filter by bucket
- `--tag "tagname"` -- filter by tag
- `--overdue` -- show only overdue tasks
- `--due-this-week` -- tasks due within 7 days
- `--format table|compact|detailed` -- output format (default: table)

```bash
uv run python scripts/pp_manager.py --vault <vault-path> list \
  --project "Sprint 4" --overdue --format table
```

### /pp board

Show a text-based board view of a project's tasks organized by bucket.

```bash
uv run python scripts/pp_manager.py --vault <vault-path> board --project "Sprint 4"
```

### /pp import-csv

Import tasks from a CSV or TSV file exported from other project management tools.

**Options:**
- `<file>` -- path to CSV/TSV file (required)
- `--project "Name"` -- target project (creates if doesn't exist)
- `--mapping "column=field,..."` -- custom column-to-field mapping
- `--dry-run` -- preview what would be imported without writing anything
- `--delimiter ","` -- field delimiter (auto-detected from extension by default)
- `--status-map "source=target"` -- map source status values (repeatable)
- `--priority-map "source=target"` -- map source priority values (repeatable)

```bash
# Preview first
uv run python scripts/csv_import.py tasks.csv --vault <vault-path> --project "Migration" --dry-run

# Then import
uv run python scripts/csv_import.py tasks.csv --vault <vault-path> --project "Migration"
```

**Supported source formats:** Microsoft Project, Jira, Asana, Monday.com, generic CSV/TSV.

Column auto-detection handles common header names (see `COLUMN_ALIASES` in `scripts/csv_import.py`).

### /pp install

Install or update this skill into an Obsidian vault.

```bash
uv run python scripts/pp_manager.py --vault <vault-path> install \
  --source /path/to/skill-repo
```

### /pp help

Show available commands and brief descriptions.

```
Obsidian Project Planner -- Commands
====================================
  /pp                          Overview of projects and tasks
  /pp create-project "Name"    Create a new project
  /pp add-task "Title" [opts]  Add a task to a project
  /pp update-task "Title"      Update a task's fields
  /pp delete-task "Title"      Delete a task
  /pp list [filters]           List and filter tasks
  /pp board [project]          Board view summary
  /pp import-csv <file>        Import from CSV/TSV
  /pp install [vault]          Install/update skill into vault
  /pp help                     This help message

Options apply across commands:
  --project "Name"    Target project
  --priority high     Priority: high, medium, low
  --status "Status"   Task status
  --due YYYY-MM-DD    Due date
  --start YYYY-MM-DD  Start date
  --tags "a,b"        Comma-separated tags
  --dry-run           Preview without writing
  --json              Machine-readable JSON output

Docs: https://projectplanner.md/
```

---

## Working with the Obsidian CLI

> **Note:** The Obsidian CLI (`obsidian` command) is only available when the obsidian-cli
> skill is installed and Obsidian is running. These commands are optional optimizations --
> all operations fall back to direct file reads/writes via the Python scripts.

When Obsidian is running, the CLI can be used for quick single-task operations:

```bash
# Search for tasks across the vault
obsidian search query="project planner" path="ProjectName/Tasks"

# Set a property on a task file
obsidian property:set name="status" value="Completed" path="ProjectName/Tasks/TaskTitle.md"
```

**When to use CLI vs scripts:**
- CLI: quick single-task reads/updates, property changes, searching
- Scripts: bulk creation, CSV import, project-level data.json changes, any operation requiring consistency

---

## Task Matching

When the user references a task by title (in update, delete, etc.), the scripts use
2-tier matching (implemented in `common.find_task_by_title`):

1. **Exact** case-insensitive match -- use it directly
2. **Substring** case-insensitive match -- use if unique, otherwise list all matches and ask user to clarify
3. No match -- report "Task not found"

Always scoped to the specified project. If no project is specified and only one exists,
it's auto-selected. If multiple exist, the user must specify `--project`.

---

## Error Handling

| Situation | Response |
|-----------|----------|
| Plugin not installed | Guide user to install the plugin first, or offer `/pp install` for the skill itself |
| Markdown sync disabled | Scripts fall back to data.json writes automatically. Suggest enabling sync. |
| Project doesn't exist | Offer to create it |
| Duplicate task title in project | Warn and ask for confirmation |
| Circular dependency | Reject and explain the cycle |
| data.json is malformed | Post-write validation reports warnings. Suggest restoring from .bak |
| Multiple task title matches | Script lists matches and exits -- user must be more specific |

---

## Integration Notes

- This skill is independent of the vault's task stack system (ac-tasks, ops/tasks.md). They
  serve different purposes and should not cross-reference each other.
- The skill uses the obsidian-cli skill for CLI operations when beneficial, but does not depend
  on it -- all operations can fall back to direct file reads/writes.
- Tags created by this skill are Project Planner tags (stored in data.json), NOT the vault's
  V4 namespaced tag system. Do not mix them.

---

## Installation & Updates

This skill is developed at its own repo and installed by copying into vaults.

**Install into a vault:**
```bash
uv run python scripts/pp_manager.py --vault /path/to/vault install --source /path/to/skill-repo
```

**What gets installed:**
- `SKILL.md` -- this file
- `scripts/` -- Python utilities (common.py, pp_manager.py, csv_import.py)
- `references/` -- data schema and frontmatter docs

**What stays in the repo only:**
- `documentation/` -- full plugin docs (too large for runtime)
- `evals/` -- test cases
- `changelog.md` -- development history
