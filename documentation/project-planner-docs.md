# Project Planner for Obsidian — Complete Documentation

> **Source:** [https://projectplanner.md/docs/](https://projectplanner.md/docs/)
> **Harvested:** 2026-03-24
> **Plugin Version:** 0.8.1 (latest as of harvest date)

---

# Table of Contents

- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [First Steps](#first-steps)
  - [FAQ](#frequently-asked-questions)
- [Views](#views)
  - [Dashboard View](#dashboard-view)
  - [Grid View](#grid-view)
  - [Board View](#board-view-kanban)
  - [Timeline View](#timeline-view-gantt-chart)
  - [Dependency Graph View](#dependency-graph-view)
  - [Task Details View](#task-details-panel)
- [Features](#features)
  - [Data Structure](#data-structure-reference)
  - [Markdown Sync](#bidirectional-markdown-sync)
  - [Task Tagging](#daily-note-task-tagging)
  - [URI Linking](#uri-linking-feature)
- [Community](#community)
  - [Contributing](#contributing)
  - [Share Your Ideas](#sharing-ideas-for-new-features)
  - [Security Policy](#security-policy)
- [Changelog](#changelog)
- [Roadmap](#roadmap)

---

# Getting Started

## Installation

Project Planner is available for **Obsidian Desktop**. There are two ways to install the plugin: manual installation from GitHub, or automatic installation via BRAT.

### Method 1: Manual Installation

1. Download `main.js`, `manifest.json`, and `styles.css` from the [GitHub Releases page](https://github.com/ArctykDev/obsidian-project-planner/releases).
2. Open your vault's root folder and navigate to `.obsidian/plugins/`.
3. Create a new folder called `obsidian-project-planner`.
4. Copy the three downloaded files (`main.js`, `manifest.json`, `styles.css`) into the `obsidian-project-planner` folder.
5. Restart Obsidian.
6. Go to **Settings → Community plugins** and enable **Project Planner**.

**Note:** If you don't see the `.obsidian` folder, make sure hidden files are visible in your file explorer. On macOS press `Cmd+Shift+.`, on Windows enable "Show hidden files" in File Explorer options.

### Method 2: Using BRAT

[BRAT](https://github.com/TfTHacker/obsidian42-brat) (Beta Reviewers Auto-update Tester) is a community plugin that makes it easy to install and automatically update beta plugins.

1. Install the **BRAT** plugin from Obsidian's built-in Community Plugins browser (**Settings → Community plugins → Browse**).
2. Enable BRAT, then open **BRAT Settings**.
3. Click **Add Beta plugin** and enter the repository URL:
   ```
   ArctykDev/obsidian-project-planner
   ```
4. BRAT will automatically download and install the latest release.
5. Go to **Settings → Community plugins** and enable **Project Planner**.

**Tip:** BRAT automatically checks for updates and keeps the plugin current. You don't need to re-download files when a new version is released.

---

## First Steps

### Opening Project Planner

There are three ways to open Project Planner:

- **Ribbon Icon** — Click the Project Planner icon in the left-hand ribbon bar.
- **Command Palette** — Press `Ctrl/Cmd+P`, then type `Project Planner` and select the command.
- **View Menu** — Use the Obsidian **View** menu to open a new Project Planner pane.

**Tip:** You can customize the ribbon by right-clicking on it and hiding icons you don't use. Drag and drop to reorder.

### Understanding the Interface

Project Planner provides six views, each designed for a different aspect of project management:

- **[Dashboard](#dashboard-view)** — A high-level overview of all your projects with completion stats, upcoming deadlines, and quick-access cards.
- **[Grid](#grid-view)** — A spreadsheet-like table where you can view, sort, filter, and bulk-edit tasks.
- **[Board](#board-view-kanban)** — A Kanban-style board that lets you organise and drag tasks between configurable columns.
- **[Timeline](#timeline-view-gantt-chart)** — A Gantt-chart view showing task durations, milestones, and scheduling across a calendar.
- **[Dependency Graph](#dependency-graph-view)** — A visual node graph that maps out how tasks depend on one another.
- **[Task Details](#task-details-panel)** — A focused single-task view for editing every field, managing dependencies, and viewing activity.

### Creating Your First Project

1. Open Project Planner using any of the methods described above.
2. Navigate to the **Dashboard** view.
3. Click the **+ New Project** button.
4. Enter a name for your project and, optionally, a description.
5. Click **Create**. Your new project will appear on the Dashboard and a corresponding folder is created inside your vault.

**Note:** Every project and task is stored as a plain Markdown file inside your vault. This means your data is always portable, version-controllable, and fully yours.

### Adding Your First Tasks

1. Open your project and switch to the **Grid** or **Board** view.
2. Click **+ Add Task** (or press `Ctrl/Cmd+Enter` as a shortcut).
3. Type a title for the task.
4. Optionally fill in additional details:
   - **Due Date** — When the task should be completed.
   - **Priority** — Low, Medium, High, or Critical.
   - **Status** — To Do, In Progress, Done, or a custom status.
   - **Tags** — Labels for filtering and grouping.
5. Press **Enter** or click **Save** to create the task.

**Tip:** Use `Ctrl/Cmd+Enter` from anywhere inside a project to instantly create a new task without reaching for the button.

### Basic Task Management

#### Updating Status

- **Grid View** — Click the status cell for a task and select the new status from the dropdown.
- **Board View** — Drag a task card from one column to another.
- **Task Details** — Open the task and choose a status from the dropdown.

#### Setting Due Dates

- Click the date field to open a **date picker**.
- Or type a **natural-language date** such as `next Friday` or `in 3 days`, and Project Planner will resolve it automatically.

#### Adding Dependencies

1. Open the task in **Task Details**.
2. Click **Add Dependency**.
3. Search for and select the task you want to depend on.
4. Choose the dependency type (Finish-to-Start, Start-to-Start, Finish-to-Finish, or Start-to-Finish).

### Working with Markdown Sync

Project Planner keeps your task data in **bidirectional sync** with your vault's Markdown files. When you edit a task inside the plugin, the corresponding `.md` file is updated instantly. Likewise, if you edit the Markdown file directly, Project Planner picks up the changes the next time it reads the file.

Each task file uses **YAML frontmatter** to store structured fields. Here is an example:

```yaml
---
title: Design landing page
status: In Progress
priority: High
due: 2026-03-15
tags:
  - design
  - sprint-4
dependencies:
  - task: Gather requirements
    type: FS
---

Additional notes and context for the task can go in the body of the file.
```

**Important:** Avoid renaming or moving task files outside of Obsidian while Project Planner is running. Use the plugin or Obsidian's file explorer to ensure links and references stay intact.

---

## Frequently Asked Questions

### Data Structure

**Where are tasks stored?**
Every task is a plain Markdown file stored inside your Obsidian vault. Project Planner creates a folder for each project and saves one `.md` file per task, with structured data kept in YAML frontmatter. Your data never leaves your device.

### Markdown Sync

**What is Markdown Sync?**
Markdown Sync is the bidirectional synchronisation engine that keeps your task files and the plugin's internal state in lockstep. Edits made in the plugin are written to disk immediately, and changes you make to the Markdown files are picked up automatically.

**What settings control Markdown Sync?**
In **Settings → Project Planner → Sync** you can configure the sync interval, choose whether to sync on file open, and toggle auto-sync on or off. Disabling auto-sync lets you trigger syncs manually via the Command Palette.

**Can I manually create tasks by writing Markdown files?**
Yes. Create a `.md` file inside a project folder and add valid YAML frontmatter with at least a `title` field. Project Planner will detect the file and import it as a task on the next sync cycle.

**What fields can I use in task frontmatter?**
The supported fields are: `title`, `status`, `priority`, `due`, `tags`, `dependencies`, `created`, `completed`, and `bucket`. Any additional fields you add are preserved but not displayed in the plugin UI.

### Dashboard View

**How do I create a new project?**
Open the Dashboard and click the **+ New Project** button. Enter a name and optional description, then click **Create**. The project folder and an index file are generated automatically.

**How is completion rate calculated?**
Completion rate is the number of tasks with a *Done* status divided by the total number of tasks in the project, expressed as a percentage. Tasks in any other status — including custom statuses — count as incomplete.

### Grid View

**Can I reorder columns?**
Yes. In the Grid View, drag a column header to a new position. Your custom column order is saved per-project and persists between sessions.

**How do I export grid data?**
Right-click the grid header row and select **Export to CSV**. The exported file respects any active filters and sorting, so you get exactly the data you see on screen.

### Board View

**What are buckets and how are they different from status?**
Buckets are custom grouping columns on the Board that you define yourself. Status is a built-in field (To Do, In Progress, Done). By default the Board groups by status, but you can switch to bucket-based grouping for a more flexible layout.

**Can I customise buckets?**
Yes. Open Board settings and click **Manage Buckets**. You can add, rename, reorder, and delete buckets. Tasks assigned to a deleted bucket are moved to the default bucket automatically.

### Dependency Graph

**What's the difference between FS, SS, FF, and SF?**
These are the four standard dependency types:

- **FS (Finish-to-Start)** — Task B cannot start until Task A finishes.
- **SS (Start-to-Start)** — Task B cannot start until Task A starts.
- **FF (Finish-to-Finish)** — Task B cannot finish until Task A finishes.
- **SF (Start-to-Finish)** — Task B cannot finish until Task A starts.

**What happens with circular dependencies?**
Project Planner detects circular dependencies in real time and highlights the offending tasks with a warning badge. You won't be able to save a dependency that would create a cycle. Resolve the conflict by removing or changing one of the links in the chain.

### Timeline View

**How do I change dates on the timeline?**
In the Timeline View, drag the left or right edge of a task bar to adjust its start or due date. You can also drag the entire bar to shift both dates while keeping the duration the same.

**What are the zoom levels?**
The Timeline supports four zoom levels: **Day**, **Week**, **Month**, and **Quarter**. Switch between them using the zoom controls in the toolbar, or scroll while holding `Ctrl/Cmd` to zoom in and out smoothly.

---

# Views

## Dashboard View

The Dashboard View provides a high-level overview of all your projects and tasks. At a glance you can monitor key performance indicators, track progress across multiple projects, and jump straight into the work that matters most.

### Overview

- **Project Cards** — visual summaries of every project in your workspace.
- **KPI Metrics** — real-time counters for total tasks, completed tasks, overdue items, and overall progress.
- **Show All Projects** — a single toggle to surface tasks from every project at once.
- **Real-Time Updates** — the dashboard refreshes automatically whenever task data changes.

### Project Cards

Each project in your workspace is represented by a visual card. Cards display the project's **status**, **priority**, and **due-date** metrics so you can assess health without opening individual projects.

#### Card Anatomy

- **Title & Icon** — the project name and its assigned icon.
- **Status Badge** — indicates whether the project is active, on hold, or completed.
- **Priority Indicator** — shows the highest-priority incomplete task.
- **Due-Date Summary** — displays the nearest upcoming due date and any overdue count.
- **Progress Bar** — a visual meter of completed vs. total tasks.

**Tip:** Click any project card to jump directly to its task list in the Grid View.

### KPI Metrics

The top of the dashboard displays key performance indicators that aggregate data across the currently visible projects:

- **Total Tasks** — the combined count of all tasks.
- **Completed** — how many tasks have been marked done.
- **Overdue** — tasks whose due date has passed without completion.
- **Completion Rate** — the percentage of tasks finished.

**Note:** KPI values update in real time. If you complete a task in any view, the dashboard reflects the change instantly.

### View Multiple Projects

By default the dashboard scopes metrics to the currently selected project. To see tasks from *every* project at once, enable the **"Show All Tasks"** checkbox in the dashboard header bar.

1. Open the Dashboard View.
2. Locate the **"Show All Tasks"** checkbox in the header.
3. Check the box — the KPI metrics and project cards will now reflect all projects.
4. Uncheck to return to single-project view.

**Tip:** "Show All Tasks" is especially useful during stand-ups or weekly reviews when you need a cross-project summary.

### Real-Time Updates

The Dashboard View listens for changes to the underlying Markdown files. Whenever a task is created, edited, completed, or deleted in any view, the dashboard automatically recalculates every metric and re-renders affected project cards — no manual refresh required.

---

## Grid View

The Grid View is a powerful, spreadsheet-like interface for managing tasks. It supports hierarchical organization, inline editing, multi-column layouts, filtering, sorting, and drag-and-drop — giving you full control over your project data without ever leaving the table.

### Overview

- **Hierarchical Organization** — tasks and subtasks displayed in a collapsible tree structure.
- **Multiple Columns** — status, priority, due date, tags, bucket, and more.
- **Inline Editing** — click any cell to edit its value directly in the grid.
- **Filtering & Sorting** — narrow down tasks by any column or keyword.
- **Drag-and-Drop** — reorder tasks or nest them as subtasks by dragging rows.

### Navigation

#### Header Bar

The header bar sits at the top of the Grid View and provides quick access to common actions:

- **Project Selector** — switch between projects via the dropdown.
- **View Buttons** — toggle between Grid, Board, Timeline, and other views.
- **+ Add Task** — create a new top-level task at the bottom of the list.
- **Filters** — open the filter bar to narrow tasks by status, priority, tag, or keyword.

#### Column Customization

Every column in the grid can be tailored to your workflow:

- **Sort** — click a column header to sort ascending/descending.
- **Resize** — drag the right edge of a column header to adjust width.
- **Reorder** — drag a column header to a new position.
- **Show / Hide** — click the **"Columns"** button in the header to toggle column visibility.

**Tip:** Hide columns you rarely use to keep the grid compact on smaller screens.

#### Task Rows

Each row represents a single task. Rows support the following interactions:

- **Expand / Collapse** — click the arrow icon on parent tasks to show or hide subtasks.
- **Checkbox** — mark a task complete directly from the grid.
- **Editable Cells** — click any cell (title, status, priority, dates, etc.) to modify its value inline.
- **Action Buttons** — hover over a row to reveal quick-action icons (delete, open details, etc.).

### Creating Tasks

#### Top-Level Tasks

1. Click the **"+ Add Task"** button in the header bar, *or*
2. Right-click any row and choose **"Add new task above"** from the context menu.
3. Type a title and press Enter to confirm.

#### Subtasks

1. Click the **"…"** menu on the target task and select **"Make subtask"**, *or*
2. Drag a task row and drop it onto another task to nest it as a child.

**Note:** Subtasks inherit the parent's project but maintain their own status, priority, and due-date fields.

### Editing Tasks

#### Inline Editing

Click any editable cell to activate it. Change the value, then press Enter or click outside the cell to save. Changes are written back to the Markdown file immediately.

#### Task Details Panel

For a more comprehensive editor, right-click a row and select **"Open details"** to open the Task Details Panel. The panel provides access to every field including description, dependencies, links, and checklists.

### Data Storage

All task data is stored as structured Markdown and synced in real time. For a detailed breakdown of how tasks are represented on disk, see the [Data Structure](#data-structure-reference) reference.

**Important:** Edits made in the Grid View are reflected instantly in the Markdown source. Avoid editing the same file manually while the grid is open to prevent conflicts.

---

## Board View (Kanban)

The Board View offers a Microsoft Planner-style kanban interface. Tasks are displayed as cards organized into custom buckets, and you can move them with simple drag-and-drop interactions.

### Overview

- **Drag-and-Drop Interface** — move task cards between buckets effortlessly.
- **Custom Buckets** — create, rename, reorder, and delete columns per project.
- **Rich Task Cards** — see priority, tags, status, dates, and progress at a glance.
- **Active & Completed Sections** — completed tasks are separated automatically.

### Buckets

Buckets are the vertical columns on the board. Each project has its own set of buckets, so you can tailor the board layout to every workflow.

#### Key Behaviors

- **Per-Project Configuration** — each project maintains its own bucket list.
- **Drag to Reorder** — grab a bucket header to move it left or right.
- **Add / Rename / Delete** — use the bucket header menu (**"…"**) for all management actions.
- **Default Buckets** — new projects start with sensible defaults (e.g., "To Do", "In Progress", "Done").
- **"Unassigned" Bucket** — tasks that haven't been assigned to a bucket appear here.
- **Active & Completed Sections** — within each bucket, completed tasks collapse into a separate section at the bottom.

**Important — Bucket vs. Status:** A bucket is a *visual grouping* on the board, while status (e.g., "Not Started", "In Progress", "Completed") is a *task property*. Moving a card between buckets changes its bucket assignment, **not** its status. Update status independently via the card's context menu or the Task Details Panel.

### Task Cards

Each card on the board surfaces the most important task information:

- **Title** — the task name, clickable to open details.
- **Priority Badge** — color-coded indicator (Critical, High, Medium, Low, None).
- **Tags** — small labels for categorization.
- **Status** — current workflow state.
- **Due Date** — with overdue highlighting when applicable.
- **Subtask Progress** — a mini progress bar showing completed vs. total subtasks.
- **Dependencies** — an icon indicates when dependencies exist.
- **Attachments** — paperclip icon if links or attachments are present.
- **Checkbox** — quickly mark the task complete.
- **Context Menu** — right-click for actions like edit, move, delete.

### Managing Tasks

- **Create** — Click **"+ Add Task"** in the board header or **"+ Add"** at the bottom of a specific bucket.
- **Move** — Drag a card from one bucket and drop it into another.
- **Complete** — Click the checkbox on any card to toggle its completed status.
- **Edit** — Click the task title to open the Task Details Panel.
- **Delete** — Right-click the card and select **"Delete task"**.

### Managing Buckets

1. **Add a Bucket** — click **"+ Add Bucket"** at the far right of the board.
2. **Rename** — click the **"…"** menu on the bucket header and select **"Rename"**.
3. **Reorder** — drag the bucket header left or right.
4. **Delete** — click **"…"** → **"Delete bucket"**. Tasks in the bucket are moved to "Unassigned".

**Warning:** Deleting a bucket does *not* delete its tasks. They are automatically reassigned to the "Unassigned" bucket.

### Tips & Best Practices

1. Limit the number of buckets to 5–7 to keep the board scannable.
2. Use WIP (work-in-progress) limits mentally — avoid piling too many cards in one bucket.
3. Review the board daily; drag cards to reflect the latest status.
4. Archive or delete completed tasks periodically to keep the board clean.
5. Combine the Board View with the Timeline View for both visual and temporal perspectives.

---

## Timeline View (Gantt Chart)

The Timeline View renders your tasks as horizontal bars on a time axis, giving you a visual Gantt-chart perspective of your project schedule. Drag, resize, and rearrange tasks to plan dates interactively.

### Overview

- **Hierarchical Display** — parent tasks and subtasks are shown in a collapsible tree.
- **Horizontal Bars** — each task spans from its start date to its due date on the timeline.
- **Resizable Split-Pane** — a draggable divider separates the task list from the timeline canvas.
- **Collapsible Parents** — expand or collapse parent tasks to focus on specific areas.
- **Today Indicator** — a vertical line marks the current date on the timeline.

### Zoom Levels

- **Day** — each column represents a single day. Best for short sprints.
- **Week** — each column represents a week. Good for iteration planning.
- **Month** — each column represents a month. Ideal for roadmap overviews.

**Tip:** Use the zoom buttons in the toolbar or scroll while holding Ctrl/Cmd to zoom in and out.

### Interactive Bars

Task bars on the timeline support three interaction modes:

- **Move** — drag the body of a bar to shift both the start and due dates.
- **Resize Left** — drag the left handle to change the start date.
- **Resize Right** — drag the right handle to change the due date.
- **Click** — single-click a bar to open the Task Details Panel.

### Task List Panel

The left side of the split-pane contains the task list. It mirrors the hierarchical structure of the Grid View with additional features: drag handle for resizing, collapse/expand for subtask visibility, inline title editing, context menu for actions, and color coding reflecting priority or status.

### Smart Filtering

- **Status Filter** — show only active, completed, or specific statuses.
- **Priority Filter** — focus on critical and high-priority items.
- **Search** — type keywords to filter tasks by title.

### Task Display Rules

#### Date Handling

- Tasks with both a start date and a due date render as a bar spanning the range.
- Tasks with only a due date display as a single-day marker on that date.
- Tasks with no dates do not appear on the timeline canvas (they are still listed in the task list).

#### Bar Colors

- **Default** — uses the project's accent colour.
- **Overdue** — bar turns red when the due date has passed.
- **Completed** — bar is dimmed with a strikethrough label.

### Timeline vs. Grid vs. Board

| Feature | Timeline | Grid | Board |
| --- | --- | --- | --- |
| Date visualization | Horizontal bars | Date columns | Due-date label |
| Drag to reschedule | Yes | No | No |
| Hierarchy | Collapsible tree | Collapsible tree | Flat cards |
| Best for | Scheduling & deadlines | Detailed data entry | Workflow & status tracking |

### Troubleshooting

**Tasks not showing on the timeline** — Ensure the task has at least a **due date** set. Tasks without any dates are listed in the task list panel but do not render a bar on the canvas.

**Bar positions look incorrect after editing Markdown manually** — Verify that the date format follows `YYYY-MM-DD`. Reopen the project to trigger a refresh.

**Drag-and-drop not working** — Check that you are dragging from the *body* of the bar (not the handles). Also ensure the file is not read-only.

---

## Dependency Graph View

The Dependency Graph View visualizes your tasks as an interactive network of nodes and edges. It helps you understand how tasks relate to one another, identify bottlenecks, and plan work in the correct order.

### Overview

- **Node-Based Layout** — every task is a draggable node on the canvas.
- **Dependency Links** — edges connect tasks that depend on one another.
- **Dependency Types** — supports Finish-to-Start (FS), Start-to-Start (SS), Finish-to-Finish (FF), and Start-to-Finish (SF).
- **Interactive Canvas** — zoom, pan, and rearrange nodes freely.
- **Real-Time Sync** — changes to dependencies in any view update the graph instantly.

### Opening the Dependency Graph

1. Click the **Dependency Graph** icon in the view ribbon.
2. Or open the **Command Palette** and run **"Project Planner: Open Dependency Graph"**.
3. Or right-click a task in any other view and select **"Show in Dependency Graph"**.

### Graph Visualization

#### Task Nodes

- **Appearance** — rounded rectangles with the task title. Border colour reflects priority.
- **States** — normal, selected (highlighted border), hovered (tooltip), completed (dimmed).
- **Indicators** — small icons for overdue, has-subtasks, has-attachments, and blocked status.

#### Dependency Edges

- **Styles** — solid lines for active dependencies; dashed lines for completed predecessors.
- **Types** — FS, SS, FF, SF — indicated by a small label on the edge midpoint.

#### Layout Algorithms

- **Hierarchical (default)** — arranges nodes in layers from left to right based on dependency depth.
- **Force-Directed** — a physics-based simulation that clusters related nodes together.
- **Manual** — drag nodes to any position; the graph remembers your layout.

**Tip:** Use the hierarchical layout first to get an overview, then switch to manual mode for fine-tuning.

### Task Relationships

#### Dependency Types

| Type | Abbreviation | Description | Example |
| --- | --- | --- | --- |
| Finish-to-Start | FS | Task B cannot start until Task A finishes. | "Design" must finish before "Development" starts. |
| Start-to-Start | SS | Task B cannot start until Task A starts. | "QA Setup" starts when "Development" starts. |
| Finish-to-Finish | FF | Task B cannot finish until Task A finishes. | "Documentation" finishes when "Development" finishes. |
| Start-to-Finish | SF | Task B cannot finish until Task A starts. | Rare — used for just-in-time scheduling. |

#### Managing Dependencies

- **Add** — drag from one node's output handle to another node's input handle, or use the Task Details Panel.
- **Remove** — right-click an edge and select **"Remove dependency"**.
- **Edit Type** — right-click an edge and choose a different dependency type from the submenu.

**Warning:** Creating a circular dependency (A → B → A) is not allowed. The graph will reject the connection and display an error message.

### Path Tracing

Select a node and press T (or click **"Trace Path"** in the toolbar) to highlight every predecessor and successor in the dependency chain. This is invaluable for understanding the critical path of your project.

### Best Practices

**Do:**
- Keep dependency chains as short as possible.
- Use Finish-to-Start (FS) as the default type — it's the most intuitive.
- Review the graph regularly to catch outdated dependencies.
- Use path tracing to identify the critical path before major milestones.

**Don't:**
- Don't create dependencies between unrelated tasks just to force ordering — use task priority instead.
- Don't leave completed tasks with active outgoing dependencies — clean them up.
- Don't rely solely on the graph for scheduling — pair it with the Timeline View for date-based planning.

---

## Task Details Panel

The Task Details Panel is a dedicated sidebar for viewing and editing every property of an individual task. It opens alongside any view and keeps your context intact while you make changes.

### Overview

The panel provides a single place to manage all task metadata — title, status, priority, tags, bucket assignment, dates, Markdown description, dependencies, links, attachments, and checklists. Changes are saved instantly and synced to every other view in real time.

### Features

#### Comprehensive Editor

- **Title** — editable text field at the top of the panel.
- **Description** — a rich Markdown editor with an edit/preview toggle.
- **Status** — dropdown with project-defined statuses (e.g., Not Started, In Progress, Completed).
- **Priority** — dropdown selector (Critical, High, Medium, Low, None).
- **Tags** — add, remove, and create new tags with an auto-complete input.
- **Checklist** — a sortable list of subtask items with drag-to-reorder.
- **Bucket** — assign the task to a bucket (reflects on the Board View).
- **Start Date & Due Date** — date pickers with optional time selection.
- **Effort** — assign time to tasks, track completed hours.
- **Cost** — choose between fixed and hourly, add estimated and actual cost.
- **Dependencies** — manage predecessor and successor relationships (FS, SS, FF, SF).
- **Links & Attachments** — add Obsidian-style internal links or external URLs.

#### Quick Actions

- **Complete Task** — toggle the task's completed state with one click.
- **Copy Task Link** — copy a direct URI to the task for sharing or cross-referencing.
- **Close Panel** — dismiss the panel and return focus to the main view.

#### Markdown Description

The description field supports full Markdown syntax. Toggle between **Edit** and **Preview** modes using the button in the field header. In edit mode you write raw Markdown; in preview mode it is rendered as formatted HTML.

**Tip:** Use Markdown checklists (`- [ ] item`) inside the description for quick inline to-do lists that are separate from the main checklist feature.

#### Task Effort Tracking

With task effort tracking, you can assign **Completed Hours**, **Remaining Hours**, and **Total Hours** for tasks.

- **Effort Completed** — Hours of work done on a task.
- **Effort Remaining** — Hours left of work (auto-adjusts when completed hours are updated).
- **Effort Total** — Read-only sum of Completed + Remaining hours.
- **Duration** — Auto-calculated days between Start Date and Due Date.
- **% Complete** — Auto-derived from effort values using `round(completed / total × 100)`

#### Cost Tracking

Choose between **Fixed** and **Hourly** cost types.

- **Fixed** — Enter estimated and actual cost directly.
- **Hourly** — Cost is auto-calculated from effort hours × hourly rate (read-only).

#### Dependency Manager

The Dependencies section lists all predecessors and successors. Each dependency shows the related task name, the dependency type, and a remove button.

- **Finish-to-Start (FS)** — the default type.
- **Start-to-Start (SS)**
- **Finish-to-Finish (FF)**
- **Start-to-Finish (SF)**

#### Links & Attachments

- **Obsidian Links** — internal `[[wiki-link]]` style references to other notes.
- **External Links** — standard URLs (https://…) to external resources.

#### Checklist

Add checklist items to break the task into smaller, trackable steps. Each item has a checkbox and supports drag-and-drop reordering.

### Opening the Panel

1. **Click a task** in any view — the panel slides open on the right.
2. Or open the **Command Palette** and run **"Project Planner: Open Task Details"**, then search for the task.
3. Or follow a **URI protocol link** (`projectplanner://task/{id}`) to open the panel directly.

### Copying a Task Link

Click the **"Copy Link"** button to copy the task's unique URI to your clipboard. The format is:

```
projectplanner://task/{task-id}
```

Paste this link anywhere — in another note, a chat message, or a browser — to open the task directly.

### Troubleshooting

**Panel doesn't open when clicking a task** — Ensure the Task Details Panel is not disabled in your settings. Go to **Settings → Views → Task Details** and verify it is enabled.

**Changes are not saving** — Check that the underlying Markdown file is not read-only or locked by another process.

**Tags or buckets are missing from dropdowns** — Tags and buckets are project-scoped. Make sure you are viewing the correct project.

**Dependency search returns no results** — The search only includes tasks in the *same project*. Cross-project dependencies are not currently supported.

---

# Features

## Data Structure Reference

A comprehensive reference for how Project Planner stores, organizes, and manages your project data.

### Storage Locations

Project Planner stores data across three distinct locations depending on the type of information.

#### Primary Data File

All project, task, and settings data lives in a single JSON file inside your vault:

```
.obsidian/plugins/obsidian-project-planner/data.json
```

This file contains four top-level keys:

- **projects** — array of project objects
- **tasksByProject** — object mapping project IDs to arrays of tasks
- **tags** — array of tag objects
- **settings** — plugin configuration values

#### Markdown Task Files

When Bidirectional Markdown Sync is enabled, each task is also stored as an individual Markdown file:

```
{ProjectName}/Tasks/{TaskTitle}.md
```

These files mirror the data in `data.json` and are kept in sync automatically.

#### View Preferences

Per-view display settings (column widths, sort order, collapsed groups, etc.) are stored in the browser's `localStorage`. These preferences are local to the device and are not synced between machines.

### Data Schema

#### Project Object

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

- **id** *(required)* — UUID v4 unique identifier
- **name** *(required)* — display name of the project
- **buckets** *(required)* — array of bucket objects used in Board view; each has an `id` and `name`
- **startDate** *(optional)* — project start date in `YYYY-MM-DD` format
- **dueDate** *(optional)* — project due date in `YYYY-MM-DD` format
- **lastSyncTimestamp** *(optional)* — Unix timestamp (ms) of the last Markdown sync

#### Task Object

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
  ]
}
```

**Required Fields:** `id`, `title`, `status`, `completed`

**Optional Fields:** `priority` (`"high"`, `"medium"`, `"low"`, or `null`), `parentId`, `bucketId`, `startDate` / `dueDate` (YYYY-MM-DD), `tags`, `description`, `subtasks`, `links`, `dependencies`

#### Tag Object

```json
{
  "id": "tag-uuid-1",
  "name": "design",
  "color": "#4a90d9"
}
```

### Hierarchical Relationships

Parent-child task relationships are established through the `parentId` field. A task with `parentId: null` is a root-level task; otherwise it is nested under the referenced parent.

### Markdown File Format

When Markdown Sync is enabled, each task is written as a `.md` file with YAML frontmatter followed by body content:

```yaml
---
id: f8e7d6c5-b4a3-2190-fedc-ba0987654321
title: Design landing page
status: In Progress
completed: false
priority: high
bucketId: bucket-uuid-2
startDate: 2025-02-01
dueDate: 2025-02-14
tags:
  - design
  - frontend
dependencies:
  - blockedBy:other-task-uuid
---

Create the initial wireframes and high-fidelity mockups.

## Subtasks
- [x] Wireframe
- [ ] Hi-fi mockup

## Links
- [Figma file](https://figma.com/...)
```

### Date Format

- **Current format:** `YYYY-MM-DD` (e.g., `2025-02-14`)
- **Legacy format:** Full ISO 8601 strings (e.g., `2025-02-14T00:00:00.000Z`)

Project Planner is backward-compatible and accepts both formats when reading data. New dates are always written in the short `YYYY-MM-DD` format.

### Settings Schema

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

### Performance Considerations

Because all data is stored in a single JSON file, performance can degrade with very large datasets.

**Recommended Limits:**
- **Tasks per project:** ≤ 500
- **Total tasks:** ≤ 2,000
- **Subtasks per task:** ≤ 50
- **Nesting depth:** ≤ 5 levels

### Data Backup Best Practices

1. **Version control:** Keep your vault in a Git repository.
2. **Regular copies:** Periodically copy `data.json` to a separate backup location.
3. **Before upgrades:** Always back up `data.json` before updating the plugin.
4. **Enable Markdown Sync:** With sync enabled, your tasks also exist as individual Markdown files—a built-in secondary copy.
5. **Cloud storage:** Store your vault on a cloud-synced folder for automatic off-site backup.

### Data Migration

When a new plugin version changes the data schema, Project Planner automatically migrates `data.json` on first load. A backup of the pre-migration file is saved as `data.json.bak` in the same directory.

### Technical Notes

- **UUID Generation:** All IDs are RFC 4122 v4 UUIDs generated client-side using `crypto.randomUUID()`.
- **Sync Conflict Resolution:** When Markdown Sync detects a conflict, the **last write wins**. A `syncInProgress` guard prevents recursive writes.
- **Data Integrity:** Plugin validates required fields on every save. Orphaned child tasks are promoted to root level automatically. Duplicate IDs are detected and regenerated on load.

---

## Bidirectional Markdown Sync

Bidirectional Markdown Sync keeps your JSON data and individual Markdown task files in lockstep. Every change you make in the plugin UI is written to a `.md` file, and every edit you make to a `.md` file is picked up by the plugin automatically.

### How It Works

#### Automatic JSON → Markdown Sync

Whenever you add, update, or delete a task through the plugin UI, the corresponding Markdown file is created, updated, or removed automatically. Files are stored at:

```
{ProjectName}/Tasks/{TaskTitle}.md
```

If a task is renamed, the old file is deleted and a new one is created with the updated title.

#### Automatic Markdown → JSON Sync

When you modify, create, or delete a Markdown task file directly, the plugin detects the change via Obsidian's metadata cache and updates `data.json` to match.

#### Initial Sync

On plugin startup (when *Sync on Startup* is enabled), a full reconciliation runs: existing Markdown files are compared against the JSON data and any discrepancies are resolved.

**Warning:** If you use **Obsidian Sync** across multiple devices, enable *Sync on Startup* with caution. Simultaneous edits on different devices can cause last-write-wins conflicts. Consider disabling *Sync on Startup* and using the manual **Sync All Tasks Now** button after confirming your vault is fully synced.

### Task Markdown Format

Each synced task file follows this structure:

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

### YAML Frontmatter Fields

**Required Fields:** `id`, `title`, `status`, `completed`

**Optional Fields:** `parentId`, `priority`, `bucketId`, `startDate` / `dueDate` (YYYY-MM-DD), `tags`, `collapsed`, `dependencies` (format: `TYPE:TASK_ID`)

### Settings

1. **Enable Markdown Sync** — Toggle on *Settings → Markdown Sync → Enable Markdown Sync*.
2. **Auto-Create Task Notes** — When enabled, a Markdown file is automatically created for every new task.
3. **Sync on Startup** — Runs a full reconciliation when the plugin loads.
4. **Sync All Tasks Now** — A manual button that triggers an immediate full sync.

### Creating Tasks from Markdown

You can create a new task entirely from a Markdown file:

1. Create a new `.md` file inside the `{ProjectName}/Tasks/` folder.
2. Add valid YAML frontmatter with at least the required fields.
3. Save the file. The plugin will detect it and add the task to `data.json`.

#### Minimal Example

```yaml
---
id: 550e8400-e29b-41d4-a716-446655440000
title: Review pull request
status: To Do
completed: false
---

Check the latest PR for the auth module.
```

**Tip:** Generate a valid UUID quickly by running `crypto.randomUUID()` in the Obsidian developer console (`Ctrl+Shift+I` → Console).

### Conflict Resolution

To prevent recursive write loops, Project Planner uses a `syncInProgress` guard set. When a sync operation starts, the affected task ID is added to the set. A 200 ms timeout clears each entry.

If both sources are modified simultaneously, the **last write wins**.

### Limitations

- **Last save wins:** There is no merge strategy.
- **Subtask and link IDs are regenerated:** When syncing from Markdown to JSON, subtask and link IDs are regenerated because Markdown does not store them.
- **New file detection delay:** Newly created Markdown files may take up to 1 second to be detected.
- **Board view leaf-only:** In Board view, only leaf-level tasks (tasks without children) are displayed.

---

## Daily Note Task Tagging

Automatically import tasks from your daily notes into Project Planner by tagging them with a simple hashtag pattern.

### Quick Start

1. **Enable Daily Note Sync** — Go to *Settings → Daily Notes → Enable Daily Note Sync* and toggle it on.
2. **Set a Default Project** — Choose the project that will receive tasks.
3. **Tag Your Tasks** — In any daily note, write a checklist item with the `#planner` tag:
   ```
   - [ ] Finish quarterly report #planner
   ```
4. **Watch Them Appear** — Project Planner detects the tag and imports the task automatically.

### Basic Usage

#### Simple Import

```
## Today's Tasks
- [ ] Reply to client email #planner
- [ ] Update project timeline #planner
- [ ] Review design mockups #planner
```

#### Project-Specific Import

```
- [ ] Deploy staging environment #planner/Work
- [ ] Book dentist appointment #planner/Personal
- [ ] Write blog post outline #planner/Side Project
```

**Note:** Project names with spaces or hyphens are matched case-insensitively.

### Advanced Features

#### Priority Indicators

```
- [ ] Critical bug fix !!! #planner        → High priority
- [ ] Update dependencies !! #planner       → Medium priority
- [ ] Refactor CSS ! #planner               → Low priority
- [ ] Fix auth flow (high) #planner         → High priority
```

#### Due Dates

```
- [ ] Submit report 📅 2025-03-15 #planner
- [ ] Submit report due:2025-03-15 #planner
- [ ] Submit report @2025-03-15 #planner
```

#### Additional Tags

Any other hashtags in the line (besides the planner tag) are imported as task tags:

```
- [ ] Fix login bug #planner #urgent #backend
```

### Configuration

- **Enable Daily Note Sync** — Master toggle.
- **Tag Pattern** — The hashtag prefix (default: `#planner`).
- **Scan Folders** — Comma-separated list of vault-relative folder paths to watch.
- **Default Project** *(required)* — The project that receives tasks tagged without a project suffix.

### Limitations

- **One-way sync:** Tasks are imported from daily notes into Project Planner, but changes made in the plugin are *not* written back to the daily note.
- **No deletion sync:** Removing a tagged line does not delete the imported task.
- **No subtask support:** Only top-level checklist items are imported.
- **No dependency support:** Dependency relationships cannot be expressed in daily note syntax.

---

## URI Linking Feature

Create deep links that open a specific task directly in Project Planner from anywhere in your Obsidian vault.

### URI Format

```
obsidian://open-planner-task?id=TASK_ID&project=PROJECT_ID
```

- **id** — the UUID of the target task
- **project** — the UUID of the project containing the task

### Copy Link from Task Details

1. Open the task in the Task Details panel.
2. Click the **⋮** (more options) menu in the top-right corner.
3. Select **Copy Link**.
4. Paste the link anywhere in your vault.

### Example Usage

```markdown
## Sprint Planning — 2025-02-13

### Action Items
- Assign [Design landing page](obsidian://open-planner-task?id=f8e7d6c5-...&project=a1b2c3d4-...) to Sarah
- Review dependencies for [API integration](obsidian://open-planner-task?id=11223344-...&project=a1b2c3d4-...)
```

### Commands

- **Create/Update Project Hub** — Generates a hub note with clickable links to every task in the project, grouped by bucket/status.
- **Create Notes for All Tasks** — Creates individual Markdown files for every task and appends an "Open in Project Planner" URI link to each file.
- **Copy Link** — Copies the URI link for the currently open task to your clipboard.

### Cross-Vault Links

```
obsidian://open-planner-task?vault=MyOtherVault&id=TASK_ID&project=PROJECT_ID
```

**Important:** If a task has been deleted, clicking its URI link will show a "Task not found" notice.

---

# Community

## Contributing

Project Planner is an actively maintained plugin built for the Obsidian community. Contributions of all kinds are welcome — reporting bugs, suggesting features, improving documentation, or participating in discussions.

**You don't need to write code to contribute.** Opening issues, joining discussions, and sharing feedback are all valuable.

### How to Contribute

- **Discussion** — Join on [GitHub Discussions](https://github.com/arctykdev/projectplannermd/discussions).
- **Report a Vulnerability** — See the [Security Policy](#security-policy).
- **Report a Bug** — Create an issue on [GitHub Issues](https://github.com/arctykdev/projectplannermd/issues).
- **Share an Idea** — Submit through the [Ideas category](https://github.com/arctykdev/projectplannermd/discussions/categories/ideas).

### Donations

Project Planner is free and open source. Donations help support infrastructure costs. Support on [Buy Me A Coffee](https://www.buymeacoffee.com/arctykdev).

---

## Sharing Ideas for New Features

[GitHub Discussions](https://github.com/arctykdev/projectplannermd/discussions/categories/ideas) is the best place to submit feature requests.

### What Makes a Good Feature Request

- **Clear Description** — State exactly what the feature should do.
- **Use Case** — Explain the problem you're trying to solve.
- **Context and Examples** — Include mockups, screenshots, or references.
- **Consider the Philosophy** — Local-first, plain text, flexibility, Markdown compatibility.

### What Happens Next

1. **Community discussion** — Others comment, refine, and upvote.
2. **Developer review** — Evaluated for alignment, benefit, feasibility, and impact.
3. **Status updates** — Discussion updated with decisions.
4. **Implementation** — Accepted features added to the roadmap.

---

## Security Policy

### Supported Versions

| Version | Supported |
| --- | --- |
| Latest | ✅ Yes |
| 0.6.x | ✅ Yes |
| < 0.6 | ❌ No |

### Reporting a Vulnerability

**Do NOT open a public issue** for security vulnerabilities.

Report via:
- **Email** — [support@projectplanner.md](mailto:support@projectplanner.md)
- **GitHub** — [Private vulnerability reporting](https://github.com/arctykdev/projectplannermd/security/advisories/new)

**What to Expect:**
1. Initial response within 48–72 hours.
2. Updates within 7 days.
3. Fix within 30 days.
4. Credit in release notes (with permission).

### Security Best Practices

- Always run the latest version.
- Only install from the official Obsidian Community Plugins directory or GitHub releases.
- Project Planner operates entirely on your local device. Your data is never sent to external servers.

---

# Changelog

All notable changes to Obsidian Project Planner. Format based on [Keep a Changelog](https://keepachangelog.com/).

## [0.8.1] - 2026-03-15

### Fixed

#### Obsidian Community Plugin Guidelines
- `.gitignore` updated: Removed `main.js` and `main.js.map` from ignore list
- `isDesktopOnly` set to `true`: Plugin uses Node `crypto` and desktop-only APIs
- Cross-platform clean script: Replaced PowerShell-only `Remove-Item` with portable `rm -rf`

#### Event Listener & Resource Cleanup
- DependencyGraphView listener leaks: Replaced manual listeners with Obsidian's `registerDomEvent()`
- Unsafe TaskDetailView cast: Replaced `as TaskDetailView` cast with duck-type check

#### Data Integrity
- Hash collision in daily note task IDs: Replaced 32-bit hash with `crypto.randomUUID()`
- Invalid date handling: Added `isValidDateStr()` validation
- `createFolder` crash: Wrapped with try-catch for existing folders

#### Performance
- O(1) task lookups: Added `taskIndex` Map to TaskStore
- `taskIndex` not updated in `addTaskToProject`: Fixed regression
- Incremental grid rendering: Renders rows in batches of 100

### Changed
- View activation deduplicated: Six methods consolidated into `openViewByType()`
- Dead code removed: Deleted unused `uuid.ts`

## [0.8.0] - 2026-03-08

### Added

#### My Tasks View (Today)
- New "My Tasks" view with cross-project task aggregation for today
- Summary bar with task count and progress indicator
- Filters: Priority dropdown, text search, "Show completed" toggle

#### My Tasks View (Week)
- Outlook-style weekly layout with 7 day columns
- Today/Week segmented toggle
- Week navigation with previous/next buttons

#### Cost Tracking System
- Per-task cost fields: `costEstimate`, `costActual`, `costType`, `hourlyRate`
- Fixed and Hourly cost modes
- Parent task cost roll-up
- Project-level budget settings
- Dashboard Budget & Cost card
- Cost Report modal with tabbed breakdown

### Fixed
- Settings save race condition
- Task note creation path now respects `projectsBasePath`
- TaskSync delete handler rebuilt with pre-computed map
- 23 additional bug fixes (see full changelog)

## [0.7.1] - 2026-02-28

### Fixed
- Board View stale settings cache causing lost buckets between sessions

## [0.7.0] - 2026-02-22

### Added

#### Task Effort Tracking
- Microsoft Planner-style effort system: Completed, Remaining, Total hours
- Smart effort auto-sync with status
- Effort columns in Grid View, effort section in Task Detail View
- Markdown sync for effort fields

#### Dependency-Driven Auto-Scheduling
- Automatic date cascading through dependency chains (FS, SS, FF, SF)
- Duration preservation, forward-only scheduling, recursive cascade
- Circular dependency guard

#### Timeline/Gantt Dependency Arrows
- SVG overlay draws right-angle connector arrows between linked task bars
- Smart routing with L-shaped orthogonal paths

#### Parent Task Roll-Up
- Automatic parent field calculation from subtasks (dates, effort, % complete, status)
- Read-only parent fields in Grid and Task Detail views

### Fixed
- Grid View column drag-and-drop sync
- Grid View cell rendering architecture refactored
- Scroll position preservation across all views

## [0.6.13] - 2026-02-10
- Grid View drag-and-drop column reordering
- Header view switcher icons
- DailyNoteTaskScanner deduplication system overhaul

## [0.6.12] - 2026-02-04
- 313 automated tests (98.4% passing)
- DailyNoteTaskScanner project name parsing fix

## [0.6.11] - 2026-02-02
- Board View card reordering with drag-and-drop
- Task Details panel layout reorganization

## [0.6.10] - 2026-02-01
- Fixed date display timezone issues
- Grid View inline edit polish (optimistic updates, smooth animations)

## [0.6.9] - 2026-01-31
- Grid View scroll preservation
- Markdown sync improvements (rename handling, bidirectional title sync)

## [0.6.7] - 2026-01-28
- Board View bucket menu and inline editing
- Cut/Copy/Paste, Copy Link, Open Markdown Note in context menus
- Ribbon icon customization
- Memory leak fixes, synchronized timeline scrolling

## [0.6.6] - 2026-01-25
- Projects base path setting
- Dashboard completed task filtering fix
- Markdown sync auto-create and folder creation fixes

## [0.6.5] - 2026-01-22
- Task timestamps (created/modified dates)
- Simplified date storage (YYYY-MM-DD)
- Obsidian Sync duplicate prevention

## [0.6.4] - 2026-01-20
- Card preview options (checklist or description on board cards)
- Board View UI enhancements (Microsoft Planner style)

## [0.6.3] - 2026-01-14
- Daily Note Task Tagging feature
- Smart task parsing (priority, due dates, tags, completion status)

## [0.6.2] - 2026-01-13
- Bidirectional Markdown Sync
- Project metadata tracking
- TaskSync utility class

## [0.6.1] - 2026-01-07
- View tab opening behavior setting
- Bucket selection in Task Details and Grid View

## [0.6.0] - 2026-01-07
- Dashboard View, Dependency Graph View, Header Component
- Project Hub Manager
- GitHub Actions release workflow

## [0.5.0] — Previous Release
See the [GitHub repository](https://github.com/ArctykDev/obsidian-project-planner) for previous entries.

---

# Roadmap

### Version 0.8.2 — Completed
- My Tasks view header matching other views
- Board view context menu consistency
- Grid & Timeline "Add task below" option

### Version 0.8.3 — Planned
- My Tasks — Add a new task to Today and Weekly views

### Version 0.9.0 — Planned
- Move tasks between projects
- Per-project customization for statuses, priorities and tags
- Dashboard customization — re-arrange and show/hide project cards
- Copy/duplicate projects / Save project as template

### Version 1.0.0 — Planned
- Apply to become an official Obsidian plugin
- Full calendar view — monthly view
- Project Goals linked to tasks
- Improved Markdown notes integration
- Project Planner for Teams — multi-user support

### Future Plans
- Full mobile support — custom mobile app for iOS and Android
- Custom API — API support for integration with other apps
- Obsidian Bases support
