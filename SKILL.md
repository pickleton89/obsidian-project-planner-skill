---
name: obsidian-project-planner
description: >
  Create, manage, and query projects and tasks for the Obsidian Project Planner plugin.
  Handles full CRUD on projects, tasks, buckets, dependencies, effort tracking, and cost tracking
  by writing markdown task files and managing the plugin's data.json. Includes CSV/TSV import
  for migrating from other project management tools. Use this skill whenever the user mentions
  project planner, project planning in Obsidian, task management with planner, Gantt charts
  in Obsidian, kanban boards in their vault, importing project data, or wants to create/update/query
  tasks and projects in their Obsidian vault using the Project Planner plugin. Also triggers on
  "/pp" slash commands.
version: "1.0.0"
user-invocable: true
context: fork
model: sonnet
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Agent
argument-hint: "[status|create-project|add-task|update-task|list|board|import-csv|install|help] — manage Obsidian Project Planner"
---

# Obsidian Project Planner Skill

Manage projects and tasks for the [Obsidian Project Planner](https://projectplanner.md/) plugin
directly from Claude Code. This skill reads and writes the plugin's data through markdown task
files (bidirectional sync) and `data.json` (for project-level operations).

**Plugin docs:** https://projectplanner.md/docs/
**GitHub:** https://github.com/ArctykDev/obsidian-project-planner

## Runtime Configuration (Step 0)

Before any operation, resolve the vault path and plugin data:

1. **Vault path** — Check `$ARGUMENTS` for an explicit `--vault PATH`. If absent, look for
   the environment or default to the user's known vault. Confirm the vault exists.

2. **Plugin data** — Read `{vault}/.obsidian/plugins/obsidian-project-planner/data.json`.
   If it doesn't exist, the plugin isn't installed — inform the user and offer `/pp install`
   guidance (see Installation section).

3. **Sync status** — Check `settings.enableMarkdownSync` in data.json. If sync is disabled,
   warn the user that markdown task file operations won't be picked up by the plugin until
   sync is enabled. Recommend enabling it.

4. **Load references as needed:**
   - For task operations → read `references/frontmatter-spec.md` (YAML field reference)
   - For project/JSON operations → read `references/data-schema.md` (JSON schema reference)

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

**START NOW.** Execute the requested operation.

---

## Data Strategy

**Markdown-first, JSON-when-needed.**

- **Tasks** — Create and update by writing `.md` files with YAML frontmatter into
  `{ProjectName}/Tasks/{TaskTitle}.md`. The plugin's bidirectional sync picks these up
  and writes them into `data.json` automatically. This is the Obsidian-native approach.

- **Projects, buckets, settings** — These can only be managed by editing `data.json` directly.
  There is no markdown representation for projects.

- **Reading/querying** — Always read from `data.json` for the complete picture. Markdown files
  may lag behind if the plugin hasn't synced yet.

### UUID Generation

All IDs must be RFC 4122 v4 UUIDs. Generate with:
```bash
python3 -c "import uuid; print(uuid.uuid4())"
```
Or use the `pp_manager.py` script which handles this automatically.

---

## Commands

### /pp status

Show an overview of all projects, task counts, and completion rates.

**Steps:**
1. Read `data.json`
2. For each project, count tasks by status (Not Started, In Progress, Completed)
3. Calculate completion percentage
4. Show overdue tasks (dueDate < today and not completed)

**Output format:**
```
--=={ Project Planner }==--

  Projects
  ========
  1. Project Alpha (12 tasks — 58% complete, 2 overdue)
     Buckets: To Do | In Progress | Review | Done
  2. Project Beta (5 tasks — 20% complete)
     Buckets: Backlog | Active | Done

  Summary: 17 total tasks, 8 completed, 2 overdue
```

### /pp create-project "Name"

Create a new project with default buckets.

**Options:**
- `--start YYYY-MM-DD` — project start date
- `--due YYYY-MM-DD` — project due date
- `--buckets "Bucket1,Bucket2,Bucket3"` — custom bucket names (default: To Do, In Progress, Done)

**Steps:**
1. Read `data.json`
2. Check that no project with the same name exists
3. Generate a UUID for the project and each bucket
4. Create the project object and append to `projects` array
5. Add an empty task array in `tasksByProject` for the new project ID
6. Write updated `data.json`
7. Create the project folder: `{vault}/{ProjectName}/Tasks/`
8. Report success

**Example:**
```
Created project "Sprint 4"
  ID: a1b2c3d4-...
  Buckets: To Do | In Progress | Done
  Folder: Sprint 4/Tasks/
```

### /pp add-task "Title"

Add a new task to a project.

**Options:**
- `--project "Name"` — target project (required if multiple projects exist; if only one, it's implied)
- `--status "Not Started"` — task status (default: Not Started)
- `--priority high|medium|low` — priority level
- `--bucket "Bucket Name"` — board bucket assignment
- `--start YYYY-MM-DD` — start date
- `--due YYYY-MM-DD` — due date
- `--tags "tag1,tag2"` — comma-separated tags
- `--parent "Parent Task Title"` — make this a subtask of another task
- `--depends-on "Task Title"` — add a dependency (Finish-to-Start)
- `--description "text"` — task description body
- `--effort-remaining N` — estimated hours of work

**Steps:**
1. Read `data.json` to resolve project ID, bucket ID, parent task ID, dependency task IDs
2. Generate a UUID for the new task
3. If markdown sync is enabled:
   a. Write a `.md` file to `{ProjectName}/Tasks/{Title}.md` with full YAML frontmatter
   b. The plugin will detect it and add to `data.json` automatically
4. If markdown sync is NOT enabled:
   a. Build the task JSON object
   b. Append to `tasksByProject[projectId]`
   c. Write updated `data.json`
5. Register any new tags that don't already exist in the tags array
6. Report success with task ID and file path

**Markdown file template** (see `references/frontmatter-spec.md` for full field reference):
```yaml
---
id: {generated-uuid}
title: {Title}
status: {status}
completed: false
priority: {priority}
parentId: {parentId or null}
bucketId: {bucketId or null}
startDate: {startDate}
dueDate: {dueDate}
tags:
  - {tag1}
  - {tag2}
dependencies:
  - blockedBy:{dependencyTaskId}
---

{description}

## Subtasks

## Links
```

### /pp update-task "Title"

Update an existing task's fields.

**Options:** Same as `add-task` plus:
- `--complete` — mark as completed (sets `status: Completed`, `completed: true`)
- `--rename "New Title"` — rename the task

**Steps:**
1. Read `data.json`, find the task by title (case-insensitive fuzzy match within the project)
2. If multiple matches, list them and ask the user to be more specific
3. If markdown sync is enabled:
   a. Read the existing `.md` file
   b. Update the YAML frontmatter fields that changed
   c. Update body content if description changed
   d. If renaming, delete old file and create new one
4. If markdown sync is NOT enabled:
   a. Update the task object in `data.json`
   b. Write updated `data.json`
5. Report what changed

### /pp delete-task "Title"

Delete a task.

**Options:**
- `--project "Name"` — target project

**Steps:**
1. Find the task (same matching as update-task)
2. Confirm with the user before deleting (show task title, status, any dependents)
3. Remove from `data.json` tasksByProject array
4. Delete the markdown file if it exists
5. Remove any dependencies pointing to this task from other tasks
6. If this was a parent task, decide: promote children to root level or delete them too (ask user)
7. Write updated `data.json`

### /pp list

List and filter tasks.

**Options:**
- `--project "Name"` — filter by project (default: all projects)
- `--status "In Progress"` — filter by status
- `--priority high` — filter by priority
- `--bucket "Bucket Name"` — filter by bucket
- `--tag "tagname"` — filter by tag
- `--overdue` — show only overdue tasks
- `--due-this-week` — tasks due within 7 days
- `--format table|compact|detailed` — output format (default: table)

**Output (table format):**
```
  Project Alpha — 12 tasks (filtered: 5)
  ┌────┬──────────────────────┬─────────────┬──────────┬────────────┐
  │ #  │ Title                │ Status      │ Priority │ Due        │
  ├────┼──────────────────────┼─────────────┼──────────┼────────────┤
  │ 1  │ Design landing page  │ In Progress │ High     │ 2026-03-28 │
  │ 2  │ API integration      │ Not Started │ Medium   │ 2026-04-01 │
  └────┴──────────────────────┴─────────────┴──────────┴────────────┘
```

### /pp board

Show a text-based board view of a project.

**Options:**
- `--project "Name"` — target project

**Output:**
```
  Project Alpha — Board View
  ══════════════════════════════════════════════════════════

  To Do (3)          │ In Progress (2)     │ Done (7)
  ───────────────────┼─────────────────────┼──────────────
  □ Write tests      │ ◐ Design landing    │ ✓ Setup repo
    med · Apr 01     │   high · Mar 28     │ ✓ Create DB
  □ Update docs      │ ◐ API integration   │ ✓ Auth flow
    low              │   med · Apr 01      │   ...+4 more
  □ Fix CSS bug      │                     │
    high · Mar 26    │                     │
```

### /pp import-csv

Import tasks from a CSV or TSV file exported from other project management tools.

**Options:**
- `<file>` — path to CSV/TSV file (required)
- `--project "Name"` — target project (creates if doesn't exist)
- `--mapping "column=field,..."` — custom column-to-field mapping
- `--dry-run` — preview what would be imported without writing anything
- `--delimiter ","` — field delimiter (auto-detected from extension by default)

**Steps:**
1. Read and parse the CSV/TSV file
2. Auto-detect column mapping by matching headers to known field names:
   - `title`, `name`, `task`, `task name`, `summary` → `title`
   - `status`, `state` → `status`
   - `priority`, `importance` → `priority`
   - `due`, `due date`, `deadline`, `end date` → `dueDate`
   - `start`, `start date`, `begin date` → `startDate`
   - `tags`, `labels`, `categories` → `tags`
   - `parent`, `parent task`, `wbs parent` → parent relationship
   - `depends on`, `predecessors`, `blocked by` → dependencies
   - `bucket`, `column`, `swimlane` → `bucketId`
   - `description`, `notes`, `details` → `description`
   - `effort`, `estimated hours`, `work` → `effortRemaining`
   - `actual hours`, `hours spent` → `effortCompleted`
   - `cost`, `estimated cost` → `costEstimate`
   - `actual cost` → `costActual`
3. If `--mapping` is provided, use it to override auto-detection
4. If `--dry-run`, show the parsed tasks and mapping without writing
5. Resolve parent-child relationships by matching parent references (by title or row number)
6. Resolve dependency references between tasks
7. Create the project if needed (via data.json)
8. Generate UUIDs for all tasks
9. Write markdown task files (or data.json entries if sync is disabled)
10. Report: tasks imported, relationships created, any warnings

The `scripts/csv_import.py` script handles the heavy lifting. Run it with:
```bash
uv run python scripts/csv_import.py <file> --vault <vault-path> --project "Name" [--dry-run]
```

**Supported source formats:**
- Microsoft Project exports (CSV)
- Jira exports (CSV)
- Asana exports (CSV)
- Monday.com exports (CSV)
- Generic CSV/TSV with headers

### /pp install

Install or update this skill into an Obsidian vault.

**Usage:**
```
/pp install [vault-path]
```

If no vault path is given, prompt the user for it.

**Steps:**
1. Resolve the skill source directory (where this SKILL.md lives)
2. Resolve the target: `{vault-path}/.claude/skills/obsidian-project-planner/`
3. If the target already exists, compare versions and show what changed
4. Copy all skill files (SKILL.md, scripts/, references/) to the target
5. Do NOT copy documentation/ (too large for installed skill, and not needed at runtime)
6. Report success

```bash
uv run python scripts/pp_manager.py install --source <skill-repo> --vault <vault-path>
```

### /pp help

Show available commands and brief descriptions.

```
Obsidian Project Planner — Commands
════════════════════════════════════
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

Docs: https://projectplanner.md/
```

---

## Working with the Obsidian CLI

When Obsidian is running, the skill can use the Obsidian CLI for certain operations:

```bash
# Search for tasks across the vault
obsidian search query="project planner" path="ProjectName/Tasks"

# Read a specific task file
obsidian read file="TaskTitle"

# Set a property on a task file
obsidian property:set name="status" value="Completed" path="ProjectName/Tasks/TaskTitle.md"

# Append to a task's description
obsidian append path="ProjectName/Tasks/TaskTitle.md" content="Updated notes..."
```

The CLI queries Obsidian's metadata cache which is faster than file scanning. However, for
bulk operations (creating many tasks, CSV import), direct file writes are more efficient.

**When to use CLI vs direct file ops:**
- CLI: quick single-task reads/updates, searching, property changes
- Direct file ops: bulk creation, CSV import, project-level data.json changes

---

## Task Matching

When the user references a task by title (in update, delete, etc.), use fuzzy matching:

1. Exact case-insensitive match → use it
2. Substring match → use if unique, otherwise list matches
3. No match → report "Task not found" with suggestions from similar titles

Always scope the search to the specified project. If no project is specified and multiple
projects exist, search all projects but prefix results with the project name.

---

## Error Handling

| Situation | Response |
|-----------|----------|
| Plugin not installed | Guide user to install the plugin first, or offer `/pp install` for the skill itself |
| Markdown sync disabled | Warn and fall back to data.json writes. Suggest enabling sync. |
| Project doesn't exist | Offer to create it |
| Duplicate task title in project | Warn and ask for confirmation |
| Circular dependency | Reject and explain the cycle |
| data.json is malformed | Report the issue, suggest restoring from .bak |
| Task file write conflict | Warn about potential sync issues if plugin is actively running |

---

## Integration Notes

- This skill is independent of the vault's task stack system (ac-tasks, ops/tasks.md). They
  serve different purposes and should not cross-reference each other.
- The skill uses the obsidian-cli skill for CLI operations when beneficial, but does not depend
  on it — all operations can fall back to direct file reads/writes.
- Tags created by this skill are Project Planner tags (stored in data.json), NOT the vault's
  V4 namespaced tag system. Do not mix them.

---

## Installation & Updates

This skill is developed at its own repo and installed by copying into vaults.

**Install into a vault:**
```bash
uv run python scripts/pp_manager.py install --source /path/to/skill-repo --vault /path/to/vault
```

**Update an existing installation:**
Same command — it overwrites the installed files with the latest from the repo.

**What gets installed:**
- `SKILL.md` — this file
- `scripts/` — Python utilities
- `references/` — data schema and frontmatter docs

**What stays in the repo only:**
- `documentation/` — full plugin docs (too large for runtime)
- `evals/` — test cases
- `changelog.md` — development history
