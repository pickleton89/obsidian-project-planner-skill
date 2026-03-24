# Obsidian Project Planner — Data Schema Reference

> Quick reference for the JSON data structures in `data.json` and how they map to markdown task files.

## Storage Locations

| Data | Location | Notes |
|------|----------|-------|
| All project/task/settings data | `.obsidian/plugins/obsidian-project-planner/data.json` | Single JSON file, always present |
| Individual task files | `{ProjectName}/Tasks/{TaskTitle}.md` | Only when Markdown Sync is enabled |
| View preferences | Browser localStorage | Per-device, not synced |

## data.json Top-Level Structure

```json
{
  "projects": [ /* array of Project objects */ ],
  "tasksByProject": { /* projectId → Task[] mapping */ },
  "tags": [ /* array of Tag objects */ ],
  "settings": { /* plugin configuration */ }
}
```

## Project Object

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "My Project",
  "buckets": [
    { "id": "bucket-uuid-1", "name": "To Do" },
    { "id": "bucket-uuid-2", "name": "In Progress" },
    { "id": "bucket-uuid-3", "name": "Done" }
  ],
  "startDate": "2025-01-15",
  "dueDate": "2025-06-30",
  "lastSyncTimestamp": 1700000000000
}
```

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `id` | yes | UUID v4 | `crypto.randomUUID()` format |
| `name` | yes | string | Display name |
| `buckets` | yes | array | Each has `id` (UUID) and `name` |
| `startDate` | no | `YYYY-MM-DD` | Project start |
| `dueDate` | no | `YYYY-MM-DD` | Project deadline |
| `lastSyncTimestamp` | no | Unix ms | Last markdown sync time |

## Task Object

```json
{
  "id": "f8e7d6c5-b4a3-2190-fedc-ba0987654321",
  "title": "Design landing page",
  "status": "In Progress",
  "completed": false,
  "priority": "high",
  "parentId": null,
  "bucketId": "bucket-uuid-2",
  "startDate": "2025-02-01",
  "dueDate": "2025-02-14",
  "tags": ["design", "frontend"],
  "description": "Create the initial wireframes and high-fidelity mockups.",
  "subtasks": [
    { "id": "sub-uuid-1", "title": "Wireframe", "completed": true },
    { "id": "sub-uuid-2", "title": "Hi-fi mockup", "completed": false }
  ],
  "links": [
    { "id": "link-uuid-1", "label": "Figma file", "url": "https://figma.com/..." }
  ],
  "dependencies": [
    { "taskId": "other-task-uuid", "type": "blockedBy" }
  ],
  "effortCompleted": 0,
  "effortRemaining": 0,
  "costEstimate": 0,
  "costActual": 0,
  "costType": "fixed",
  "hourlyRate": null
}
```

### Required Fields

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID v4 | Unique identifier |
| `title` | string | Task name |
| `status` | string | `"Not Started"`, `"In Progress"`, `"Completed"`, or custom |
| `completed` | boolean | `true` when status is done |

### Optional Fields

| Field | Type | Notes |
|-------|------|-------|
| `priority` | string/null | `"high"`, `"medium"`, `"low"`, or `null` |
| `parentId` | UUID/null | Parent task ID for subtask hierarchy |
| `bucketId` | UUID/null | Board view bucket assignment |
| `startDate` | `YYYY-MM-DD` | Task start date |
| `dueDate` | `YYYY-MM-DD` | Task due date |
| `tags` | string[] | Task labels |
| `description` | string | Markdown body content |
| `subtasks` | array | Checklist items: `{id, title, completed}` |
| `links` | array | `{id, label, url}` |
| `dependencies` | array | `{taskId, type}` — type is `"blockedBy"` |
| `effortCompleted` | number | Hours of work done |
| `effortRemaining` | number | Hours left |
| `costEstimate` | number | Estimated cost |
| `costActual` | number | Actual cost |
| `costType` | string | `"fixed"` or `"hourly"` |
| `hourlyRate` | number/null | Rate when costType is hourly |

## Tag Object

```json
{
  "id": "tag-uuid-1",
  "name": "design",
  "color": "#4a90d9"
}
```

## Settings Schema

```json
{
  "settings": {
    "enableMarkdownSync": false,
    "autoCreateTaskNotes": false,
    "syncOnStartup": false,
    "enableDailyNoteSync": false,
    "dailyNoteTagPattern": "#planner",
    "dailyNoteScanFolders": "",
    "dailyNoteDefaultProject": "",
    "defaultView": "list",
    "showCompletedTasks": true,
    "confirmBeforeDelete": true,
    "theme": "system"
  }
}
```

## Dependency Types

| Type | Abbreviation | Meaning |
|------|-------------|---------|
| Finish-to-Start | FS | B cannot start until A finishes |
| Start-to-Start | SS | B cannot start until A starts |
| Finish-to-Finish | FF | B cannot finish until A finishes |
| Start-to-Finish | SF | B cannot finish until A starts |

In `data.json`, dependencies use `"type": "blockedBy"` with the predecessor's task ID.
In markdown frontmatter, dependencies use the format `TYPE:TASK_ID` (e.g., `blockedBy:other-task-uuid`).

## Hierarchical Relationships

- `parentId: null` → root-level task
- `parentId: "some-uuid"` → nested under that parent
- Parent tasks auto-roll-up: dates, effort, % complete, cost from children
- Max recommended nesting: 5 levels

## Performance Limits

| Metric | Recommended Max |
|--------|----------------|
| Tasks per project | 500 |
| Total tasks | 2,000 |
| Subtasks per task | 50 |
| Nesting depth | 5 levels |

## UUID Generation

All IDs are RFC 4122 v4 UUIDs. Generate with:
- Python: `import uuid; str(uuid.uuid4())`
- JavaScript: `crypto.randomUUID()`
- CLI: `uuidgen` (macOS)
