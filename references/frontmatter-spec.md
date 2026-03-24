# Task Markdown File — Frontmatter Specification

> Reference for the YAML frontmatter format used by Obsidian Project Planner's bidirectional markdown sync.

## File Location

```
{VaultRoot}/{ProjectName}/Tasks/{TaskTitle}.md
```

The project folder name must match the project's `name` field in `data.json`. The `Tasks/` subfolder is created automatically when sync is enabled.

## Full Template

```yaml
---
id: f8e7d6c5-b4a3-2190-fedc-ba0987654321
title: Design landing page
status: In Progress
completed: false
priority: high
parentId: null
bucketId: bucket-uuid-2
startDate: 2025-02-01
dueDate: 2025-02-14
tags:
  - design
  - frontend
collapsed: false
effortCompleted: 4
effortRemaining: 6
costEstimate: 500
costActual: 200
costType: fixed
hourlyRate: null
dependencies:
  - blockedBy:other-task-uuid
---

Create the initial wireframes and high-fidelity mockups.

## Subtasks
- [x] Wireframe
- [ ] Hi-fi mockup

## Dependencies
- Blocked by: [[other-task-title]]

## Links
- [Figma file](https://figma.com/...)

---
*Managed by Project Planner — do not remove the frontmatter.*
```

## Minimal Template (New Task)

Only four frontmatter fields are required. The plugin fills in defaults for everything else.

```yaml
---
id: 550e8400-e29b-41d4-a716-446655440000
title: Review pull request
status: Not Started
completed: false
---

Check the latest PR for the auth module.
```

## Field Reference

### Required Fields

| Field | Type | Values | Notes |
|-------|------|--------|-------|
| `id` | UUID v4 | — | Must be unique across the project |
| `title` | string | — | Task display name |
| `status` | string | `Not Started`, `In Progress`, `Completed` | Or any custom status defined in the project |
| `completed` | boolean | `true` / `false` | Must agree with status (completed = true when status is terminal) |

### Optional Fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `priority` | string | `null` | `high`, `medium`, `low`, or omit |
| `parentId` | UUID | `null` | Set to parent task's ID for subtask hierarchy |
| `bucketId` | UUID | `null` | Must match a bucket ID from the project's bucket list |
| `startDate` | date | — | Format: `YYYY-MM-DD` |
| `dueDate` | date | — | Format: `YYYY-MM-DD` |
| `tags` | list | `[]` | YAML list of strings |
| `collapsed` | boolean | `false` | Whether subtasks are collapsed in UI |
| `effortCompleted` | number | `0` | Hours of work done |
| `effortRemaining` | number | `0` | Hours of work remaining |
| `costEstimate` | number | `0` | Estimated cost |
| `costActual` | number | `0` | Actual cost incurred |
| `costType` | string | `fixed` | `fixed` or `hourly` |
| `hourlyRate` | number | `null` | Rate per hour (when costType is hourly) |
| `dependencies` | list | `[]` | Format: `TYPE:TASK_ID` per item |

### Dependency Format in Frontmatter

Each dependency is a string in the format `TYPE:TASK_ID`:

```yaml
dependencies:
  - blockedBy:a1b2c3d4-e5f6-7890-abcd-ef1234567890
  - blockedBy:11223344-5566-7788-9900-aabbccddeeff
```

The dependency types map to standard project management relationships:
- `blockedBy` → Finish-to-Start (FS) — most common
- Other types (SS, FF, SF) use the same format with the type prefix

## Body Content Sections

The markdown body (below the frontmatter) is free-form but the plugin recognizes these sections:

### Subtasks Section
```markdown
## Subtasks
- [x] Completed subtask
- [ ] Pending subtask
```
Rendered as the task's checklist in the UI. Subtask IDs are regenerated on sync from markdown → JSON.

### Dependencies Section
```markdown
## Dependencies
- Blocked by: [[other-task-title]]
```
Human-readable dependency references using wiki links. The actual dependency data comes from the frontmatter `dependencies` field.

### Links Section
```markdown
## Links
- [Label](https://url.com)
- [[Internal Note]]
```
Both external URLs and Obsidian internal links are supported.

## Date Formats

| Format | Example | Status |
|--------|---------|--------|
| `YYYY-MM-DD` | `2025-02-14` | Current (always use this) |
| ISO 8601 | `2025-02-14T00:00:00.000Z` | Legacy (read-only compat) |

## Creating Tasks via Markdown

1. Ensure the project exists in `data.json` (projects cannot be created via markdown)
2. Ensure Markdown Sync is enabled in plugin settings
3. Create a `.md` file in `{ProjectName}/Tasks/`
4. Add valid YAML frontmatter with at least the four required fields
5. Generate a fresh UUID v4 for the `id` field
6. Save the file — the plugin detects it within ~1 second and imports to `data.json`

## Important Caveats

- **Project must exist first** — the plugin only watches folders for known projects
- **Markdown Sync must be enabled** — without it, markdown files are ignored
- **Last write wins** — no merge strategy for simultaneous edits
- **Subtask/link IDs regenerated** — markdown → JSON sync regenerates these IDs
- **File rename = task rename** — renaming the .md file updates the task title
- **Don't edit while plugin writes** — avoid editing the same file the plugin is writing to
