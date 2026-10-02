#!/usr/bin/env python3
"""Obsidian Project Planner -- Core Manager

Full CLI for managing projects, tasks, buckets, and views. All operations
are deterministic -- the LLM calls this script rather than generating files
directly.

Usage:
    uv run python scripts/pp_manager.py --vault <path> <command> [options]

Commands:
    status              Show project overview
    create-project      Create a new project
    delete-project      Delete a project
    list-projects       List all projects
    add-bucket          Add a bucket to a project
    add-task            Add a task to a project
    update-task         Update an existing task
    delete-task         Delete a task
    list                List and filter tasks
    board               Board view of a project
    query               Query tasks (raw output)
    install             Install skill into a vault
    ensure-sync         Check markdown sync status
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

# Ensure the scripts directory is on the path for sibling imports
sys.path.insert(0, str(Path(__file__).parent))

from common import (
    create_project_data,
    find_bucket,
    find_task_by_title,
    is_sync_enabled,
    load_data,
    new_uuid,
    register_tags,
    resolve_project,
    sanitize_filename,
    save_data,
    today_str,
    date_in_days,
    write_task_file,
)


def _output(data_obj: dict | list, human_fn, *, output_json: bool = False):
    """If --json, print JSON; otherwise call human_fn to print human-readable output."""
    if output_json:
        print(json.dumps(data_obj, indent=2, ensure_ascii=False))
    else:
        human_fn()


# ---------------------------------------------------------------------------
# Project Operations
# ---------------------------------------------------------------------------


def cmd_status(vault_path: str, output_json: bool = False) -> dict:
    """Show overview of all projects and task counts."""
    data = load_data(vault_path)
    projects = data.get("projects", [])
    tasks_by_project = data.get("tasksByProject", {})
    today = today_str()

    result = {"projects": [], "total_tasks": 0, "total_completed": 0, "total_overdue": 0}

    for proj in projects:
        pid = proj["id"]
        tasks = tasks_by_project.get(pid, [])
        n_tasks = len(tasks)
        n_completed = sum(1 for t in tasks if t.get("completed", False))
        n_overdue = sum(
            1 for t in tasks
            if not t.get("completed", False)
            and t.get("dueDate")
            and t["dueDate"] < today
        )
        pct = round(n_completed / n_tasks * 100) if n_tasks > 0 else 0
        buckets = [b["name"] for b in proj.get("buckets", [])]

        result["projects"].append({
            "name": proj["name"],
            "id": pid,
            "tasks": n_tasks,
            "completed": n_completed,
            "overdue": n_overdue,
            "percent_complete": pct,
            "buckets": buckets,
        })
        result["total_tasks"] += n_tasks
        result["total_completed"] += n_completed
        result["total_overdue"] += n_overdue

    def _print():
        if not result["projects"]:
            print('No projects found. Create one with: /pp create-project "Name"')
            return
        print("--=={ Project Planner }==--\n")
        print("  Projects")
        print("  ========")
        for i, p in enumerate(result["projects"], 1):
            overdue_str = f", {p['overdue']} overdue" if p["overdue"] > 0 else ""
            print(f"  {i}. {p['name']} ({p['tasks']} tasks -- {p['percent_complete']}% complete{overdue_str})")
            if p["buckets"]:
                print(f"     Buckets: {' | '.join(p['buckets'])}")
        print(f"\n  Summary: {result['total_tasks']} total tasks, "
              f"{result['total_completed']} completed, {result['total_overdue']} overdue")

    _output(result, _print, output_json=output_json)
    return result


def cmd_create_project(
    vault_path: str,
    name: str,
    start_date: str | None = None,
    due_date: str | None = None,
    bucket_names: list[str] | None = None,
    output_json: bool = False,
) -> dict:
    """Create a new project in data.json and create the folder structure."""
    data = load_data(vault_path)
    data, project = create_project_data(data, name, bucket_names, start_date, due_date)
    save_data(vault_path, data)

    # Create folder structure
    tasks_dir = Path(vault_path) / name / "Tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    bnames = [b["name"] for b in project["buckets"]]

    def _print():
        print(f'Created project "{name}"')
        print(f"  ID: {project['id']}")
        print(f"  Buckets: {' | '.join(bnames)}")
        print(f"  Folder: {name}/Tasks/")

    _output(project, _print, output_json=output_json)
    return project


def cmd_list_projects(vault_path: str, output_json: bool = False) -> list:
    """List all projects."""
    data = load_data(vault_path)
    projects = data.get("projects", [])
    result = []
    for proj in projects:
        task_count = len(data.get("tasksByProject", {}).get(proj["id"], []))
        result.append({"name": proj["name"], "id": proj["id"], "task_count": task_count})

    def _print():
        if not result:
            print("No projects found.")
            return
        for p in result:
            print(f"  {p['name']} ({p['task_count']} tasks) -- ID: {p['id']}")

    _output(result, _print, output_json=output_json)
    return result


def cmd_delete_project(vault_path: str, name: str, output_json: bool = False) -> dict:
    """Delete a project from data.json."""
    data = load_data(vault_path)
    projects = data.get("projects", [])
    match = [p for p in projects if p["name"].lower() == name.lower()]
    if not match:
        print(f"Error: Project '{name}' not found.", file=sys.stderr)
        sys.exit(1)

    proj = match[0]
    pid = proj["id"]
    task_count = len(data.get("tasksByProject", {}).get(pid, []))

    data["projects"] = [p for p in projects if p["id"] != pid]
    data["tasksByProject"].pop(pid, None)
    save_data(vault_path, data)

    result = {"deleted": proj["name"], "id": pid, "tasks_removed": task_count}

    def _print():
        print(f'Deleted project "{proj["name"]}" ({task_count} tasks)')
        print("Note: markdown task files were NOT deleted -- remove the folder manually if desired.")

    _output(result, _print, output_json=output_json)
    return result


# ---------------------------------------------------------------------------
# Bucket Operations
# ---------------------------------------------------------------------------


def cmd_add_bucket(
    vault_path: str, project_name: str, bucket_name: str, output_json: bool = False
) -> dict:
    """Add a bucket to a project."""
    data = load_data(vault_path)
    proj = resolve_project(data, project_name)

    existing = [b for b in proj.get("buckets", []) if b["name"].lower() == bucket_name.lower()]
    if existing:
        result = {"exists": True, "bucket": existing[0]}

        def _print():
            print(f"Bucket '{bucket_name}' already exists in project '{proj['name']}'.")

        _output(result, _print, output_json=output_json)
        return result

    bucket = {"id": new_uuid(), "name": bucket_name}
    proj.setdefault("buckets", []).append(bucket)
    save_data(vault_path, data)

    result = {"created": True, "bucket": bucket, "project": proj["name"]}

    def _print():
        print(f'Added bucket "{bucket_name}" to project "{proj["name"]}"')
        print(f"  Bucket ID: {bucket['id']}")

    _output(result, _print, output_json=output_json)
    return result


# ---------------------------------------------------------------------------
# Task Operations
# ---------------------------------------------------------------------------


def cmd_add_task(
    vault_path: str,
    title: str,
    project_name: str | None = None,
    status: str = "Not Started",
    priority: str | None = None,
    bucket_name: str | None = None,
    start_date: str | None = None,
    due_date: str | None = None,
    tags: list[str] | None = None,
    parent_title: str | None = None,
    depends_on_title: str | None = None,
    description: str | None = None,
    effort_remaining: float | None = None,
    output_json: bool = False,
) -> dict:
    """Add a new task to a project."""
    data = load_data(vault_path)
    proj = resolve_project(data, project_name)
    pid = proj["id"]
    tasks = data.get("tasksByProject", {}).get(pid, [])

    task = {
        "id": new_uuid(),
        "title": title,
        "status": status,
        "completed": status.lower() in ("completed", "done", "closed"),
    }

    if priority:
        task["priority"] = priority
    if start_date:
        task["startDate"] = start_date
    if due_date:
        task["dueDate"] = due_date
    if description:
        task["description"] = description
    if effort_remaining is not None:
        task["effortRemaining"] = effort_remaining
    if tags:
        task["tags"] = tags

    # Resolve bucket
    if bucket_name:
        bucket = find_bucket(proj, bucket_name)
        if bucket:
            task["bucketId"] = bucket["id"]
        else:
            available = ", ".join(b["name"] for b in proj.get("buckets", []))
            print(f"Warning: Bucket '{bucket_name}' not found. Available: {available}", file=sys.stderr)

    # Resolve parent
    if parent_title:
        matches = find_task_by_title(tasks, parent_title)
        if len(matches) == 1:
            task["parentId"] = matches[0]["id"]
        elif len(matches) > 1:
            print(f"Error: Multiple tasks match parent '{parent_title}':", file=sys.stderr)
            for m in matches:
                print(f"  - {m['title']} (ID: {m['id']})", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"Warning: Parent task '{parent_title}' not found.", file=sys.stderr)

    # Resolve dependencies
    if depends_on_title:
        dep_refs = [d.strip() for d in depends_on_title.split(",") if d.strip()]
        deps = []
        for ref in dep_refs:
            matches = find_task_by_title(tasks, ref)
            if len(matches) == 1:
                deps.append({"taskId": matches[0]["id"], "type": "blockedBy"})
            elif len(matches) > 1:
                print(f"Warning: Multiple tasks match dependency '{ref}', skipping.", file=sys.stderr)
            else:
                print(f"Warning: Dependency task '{ref}' not found.", file=sys.stderr)
        if deps:
            task["dependencies"] = deps

    # Always write to data.json for immediate queryability
    data["tasksByProject"].setdefault(pid, []).append(task)

    # Also write markdown file when sync is enabled
    sync = is_sync_enabled(data)
    filepath = None
    if sync:
        filepath = write_task_file(vault_path, proj["name"], task)

    # Register tags
    if tags:
        register_tags(data, tags)

    save_data(vault_path, data)

    result = {
        "task": task,
        "project": proj["name"],
        "method": "markdown" if sync else "data.json",
    }
    if filepath:
        result["file"] = str(filepath)

    def _print():
        print(f'Added task "{title}" to project "{proj["name"]}"')
        print(f"  ID: {task['id']}")
        if filepath:
            print(f"  File: {filepath}")
        else:
            print("  Written to: data.json")
        if task.get("bucketId"):
            print(f"  Bucket: {bucket_name}")
        if task.get("parentId"):
            print(f"  Parent: {parent_title}")
        if task.get("dependencies"):
            print(f"  Dependencies: {len(task['dependencies'])}")

    _output(result, _print, output_json=output_json)
    return result


def cmd_update_task(
    vault_path: str,
    title: str,
    project_name: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    bucket_name: str | None = None,
    start_date: str | None = None,
    due_date: str | None = None,
    tags: list[str] | None = None,
    description: str | None = None,
    effort_remaining: float | None = None,
    complete: bool = False,
    rename: str | None = None,
    output_json: bool = False,
) -> dict:
    """Update an existing task's fields."""
    data = load_data(vault_path)
    proj = resolve_project(data, project_name)
    pid = proj["id"]
    tasks = data.get("tasksByProject", {}).get(pid, [])

    matches = find_task_by_title(tasks, title)
    if not matches:
        print(f"Error: Task '{title}' not found in project '{proj['name']}'.", file=sys.stderr)
        sys.exit(1)
    if len(matches) > 1:
        print(f"Error: Multiple tasks match '{title}':", file=sys.stderr)
        for m in matches:
            print(f"  - {m['title']} ({m.get('status', '?')})", file=sys.stderr)
        print("Please be more specific.", file=sys.stderr)
        sys.exit(1)

    task = matches[0]
    changes = {}

    if complete:
        changes["status"] = "Completed"
        changes["completed"] = True
    if status:
        changes["status"] = status
        changes["completed"] = status.lower() in ("completed", "done", "closed")
    if priority is not None:
        changes["priority"] = priority
    if start_date:
        changes["startDate"] = start_date
    if due_date:
        changes["dueDate"] = due_date
    if description is not None:
        changes["description"] = description
    if effort_remaining is not None:
        changes["effortRemaining"] = effort_remaining
    if tags is not None:
        changes["tags"] = tags

    # Resolve bucket
    if bucket_name:
        bucket = find_bucket(proj, bucket_name)
        if bucket:
            changes["bucketId"] = bucket["id"]
        else:
            print(f"Warning: Bucket '{bucket_name}' not found.", file=sys.stderr)

    if rename:
        changes["title"] = rename

    # Apply changes to the task object in memory
    task.update(changes)

    sync = is_sync_enabled(data)
    old_filepath = None
    new_filepath = None

    if sync:
        tasks_dir = Path(vault_path) / proj["name"] / "Tasks"

        if rename:
            # Write new file first, then delete old
            old_filepath = tasks_dir / f"{sanitize_filename(title)}.md"
            new_filepath = write_task_file(vault_path, proj["name"], task)
            if old_filepath.exists() and old_filepath != new_filepath:
                old_filepath.unlink()
        else:
            new_filepath = write_task_file(vault_path, proj["name"], task)

    # Register any new tags
    if tags:
        register_tags(data, tags)

    save_data(vault_path, data)

    result = {
        "task": task,
        "project": proj["name"],
        "changes": changes,
        "method": "markdown" if sync else "data.json",
    }
    if new_filepath:
        result["file"] = str(new_filepath)

    def _print():
        print(f'Updated task "{task["title"]}" in project "{proj["name"]}"')
        for k, v in changes.items():
            print(f"  {k}: {v}")
        if new_filepath:
            print(f"  File: {new_filepath}")

    _output(result, _print, output_json=output_json)
    return result


def cmd_delete_task(
    vault_path: str,
    title: str,
    project_name: str | None = None,
    force: bool = False,
    output_json: bool = False,
) -> dict:
    """Delete a task from a project."""
    data = load_data(vault_path)
    proj = resolve_project(data, project_name)
    pid = proj["id"]
    tasks = data.get("tasksByProject", {}).get(pid, [])

    matches = find_task_by_title(tasks, title)
    if not matches:
        print(f"Error: Task '{title}' not found in project '{proj['name']}'.", file=sys.stderr)
        sys.exit(1)
    if len(matches) > 1:
        print(f"Error: Multiple tasks match '{title}':", file=sys.stderr)
        for m in matches:
            print(f"  - {m['title']} ({m.get('status', '?')})", file=sys.stderr)
        sys.exit(1)

    task = matches[0]
    tid = task["id"]

    # Find dependents and children
    children = [t for t in tasks if t.get("parentId") == tid]
    dependents = [t for t in tasks if any(d.get("taskId") == tid for d in t.get("dependencies", []))]

    if not force:
        info = [f'Task: "{task["title"]}" ({task.get("status", "?")})']
        if children:
            info.append(f"  Children: {', '.join(c['title'] for c in children)}")
        if dependents:
            info.append(f"  Dependents: {', '.join(d['title'] for d in dependents)}")
        info.append("Pass --force to confirm deletion.")
        print("\n".join(info), file=sys.stderr)
        sys.exit(1)

    # Remove the task
    data["tasksByProject"][pid] = [t for t in tasks if t["id"] != tid]

    # Promote children to root level
    for child in children:
        child["parentId"] = None

    # Remove dependency references from other tasks
    for t in data["tasksByProject"][pid]:
        if t.get("dependencies"):
            t["dependencies"] = [d for d in t["dependencies"] if d.get("taskId") != tid]

    save_data(vault_path, data)

    # Delete markdown file if it exists
    md_path = Path(vault_path) / proj["name"] / "Tasks" / f"{sanitize_filename(task['title'])}.md"
    file_deleted = False
    if md_path.exists():
        md_path.unlink()
        file_deleted = True

    result = {
        "deleted": task["title"],
        "id": tid,
        "project": proj["name"],
        "children_promoted": len(children),
        "dependency_refs_removed": len(dependents),
        "file_deleted": file_deleted,
    }

    def _print():
        print(f'Deleted task "{task["title"]}" from project "{proj["name"]}"')
        if children:
            print(f"  Promoted {len(children)} child task(s) to root level")
        if dependents:
            print(f"  Removed {len(dependents)} dependency reference(s)")
        if file_deleted:
            print(f"  Deleted file: {md_path}")

    _output(result, _print, output_json=output_json)
    return result


# ---------------------------------------------------------------------------
# Display Operations
# ---------------------------------------------------------------------------


def cmd_list_tasks(
    vault_path: str,
    project_name: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    bucket_name: str | None = None,
    tag: str | None = None,
    overdue: bool = False,
    due_this_week: bool = False,
    fmt: str = "table",
    output_json: bool = False,
) -> list:
    """List and filter tasks."""
    data = load_data(vault_path)
    today = today_str()
    week_end = date_in_days(7)
    results = []

    projects_to_search = data.get("projects", [])
    if project_name:
        proj = resolve_project(data, project_name)
        projects_to_search = [proj]

    for proj in projects_to_search:
        pid = proj["id"]
        tasks = data.get("tasksByProject", {}).get(pid, [])

        # Build bucket ID lookup for filtering
        bucket_id = None
        if bucket_name:
            b = find_bucket(proj, bucket_name)
            if b:
                bucket_id = b["id"]

        for task in tasks:
            if status and task.get("status", "").lower() != status.lower():
                continue
            if priority and (task.get("priority") or "").lower() != priority.lower():
                continue
            if bucket_id and task.get("bucketId") != bucket_id:
                continue
            if tag and tag.lower() not in [t.lower() for t in task.get("tags", [])]:
                continue
            if overdue:
                if task.get("completed", False):
                    continue
                if not task.get("dueDate") or task["dueDate"] >= today:
                    continue
            if due_this_week:
                if not task.get("dueDate"):
                    continue
                if task["dueDate"] < today or task["dueDate"] > week_end:
                    continue
            results.append({"project": proj["name"], **task})

    def _print():
        if not results:
            print("No tasks match the filters.")
            return

        if fmt == "compact":
            for t in results:
                pri_str = f" [{t.get('priority', '')}]" if t.get("priority") else ""
                due_str = f" due:{t.get('dueDate', '')}" if t.get("dueDate") else ""
                print(f"  [{t['project']}] {t['title']} -- {t.get('status', '?')}{pri_str}{due_str}")
            return

        if fmt == "detailed":
            for t in results:
                print(f"\n  {t['title']}")
                print(f"  {'=' * len(t['title'])}")
                print(f"  Project:  {t['project']}")
                print(f"  Status:   {t.get('status', '?')}")
                print(f"  Priority: {t.get('priority', '-')}")
                if t.get("startDate"):
                    print(f"  Start:    {t['startDate']}")
                if t.get("dueDate"):
                    print(f"  Due:      {t['dueDate']}")
                if t.get("tags"):
                    print(f"  Tags:     {', '.join(t['tags'])}")
                if t.get("description"):
                    print(f"  Notes:    {t['description'][:80]}")
            return

        # Default: table format
        # Group by project
        by_project: dict[str, list] = {}
        for t in results:
            by_project.setdefault(t["project"], []).append(t)

        for proj_name, proj_tasks in by_project.items():
            total = len(data.get("tasksByProject", {}).get(
                next((p["id"] for p in data.get("projects", []) if p["name"] == proj_name), ""), []
            ))
            print(f"\n  {proj_name} -- {total} tasks (filtered: {len(proj_tasks)})")

            # Column widths
            max_title = min(max((len(t["title"]) for t in proj_tasks), default=5), 30)
            max_status = max((len(t.get("status", "")) for t in proj_tasks), default=6)

            hdr = (f"  {'#':>3}  {'Title':<{max_title}}  {'Status':<{max_status}}  "
                   f"{'Priority':<8}  {'Due':<10}")
            sep = "  " + "-" * (len(hdr) - 2)

            print(hdr)
            print(sep)
            for i, t in enumerate(proj_tasks, 1):
                t_title = t["title"][:max_title]
                print(
                    f"  {i:>3}  {t_title:<{max_title}}  "
                    f"{t.get('status', ''):<{max_status}}  "
                    f"{t.get('priority', '-'):<8}  "
                    f"{t.get('dueDate', ''):<10}"
                )

    _output(results, _print, output_json=output_json)
    return results


def cmd_board(
    vault_path: str,
    project_name: str | None = None,
    output_json: bool = False,
) -> dict:
    """Show a text-based board view of a project."""
    data = load_data(vault_path)
    proj = resolve_project(data, project_name)
    pid = proj["id"]
    tasks = data.get("tasksByProject", {}).get(pid, [])
    buckets = proj.get("buckets", [])

    # Group tasks by bucket
    bucket_map: dict[str, list] = {b["id"]: [] for b in buckets}
    no_bucket: list = []

    for task in tasks:
        bid = task.get("bucketId")
        if bid and bid in bucket_map:
            bucket_map[bid].append(task)
        else:
            no_bucket.append(task)

    result = {
        "project": proj["name"],
        "columns": [],
    }
    for b in buckets:
        col_tasks = bucket_map.get(b["id"], [])
        result["columns"].append({
            "bucket": b["name"],
            "count": len(col_tasks),
            "tasks": col_tasks,
        })
    if no_bucket:
        result["columns"].append({
            "bucket": "(No Bucket)",
            "count": len(no_bucket),
            "tasks": no_bucket,
        })

    def _print():
        COL_W = 22
        MAX_DISPLAY = 6

        print(f"\n  {proj['name']} -- Board View")
        print("  " + "=" * (COL_W * len(result["columns"]) + len(result["columns"]) - 1))
        print()

        # Column headers
        headers = []
        for col in result["columns"]:
            h = f"{col['bucket']} ({col['count']})"
            headers.append(f"{h:<{COL_W}}")
        print("  " + "|".join(headers))
        print("  " + "|".join("-" * COL_W for _ in result["columns"]))

        # Rows
        max_rows = max((min(col["count"], MAX_DISPLAY) for col in result["columns"]), default=0)
        for row in range(max_rows):
            cells = []
            for col in result["columns"]:
                if row < len(col["tasks"]) and row < MAX_DISPLAY:
                    t = col["tasks"][row]
                    s = t.get("status", "")
                    icon = "x" if t.get("completed") else ("~" if "progress" in s.lower() else " ")
                    name = t["title"][:COL_W - 5]
                    cells.append(f"  [{icon}] {name:<{COL_W - 5}}")
                elif row == MAX_DISPLAY - 1 and len(col["tasks"]) > MAX_DISPLAY:
                    extra = len(col["tasks"]) - MAX_DISPLAY + 1
                    cells.append(f"  ...+{extra} more{' ' * (COL_W - 13)}")
                else:
                    cells.append(" " * COL_W)
            print("  " + "|".join(cells))

            # Second line: priority + due
            detail_cells = []
            for col in result["columns"]:
                if row < len(col["tasks"]) and row < MAX_DISPLAY:
                    t = col["tasks"][row]
                    pri = t.get("priority", "")
                    due = t.get("dueDate", "")
                    detail = f"    {pri}"
                    if due:
                        detail += f" | {due}"
                    detail_cells.append(f"{detail:<{COL_W}}")
                else:
                    detail_cells.append(" " * COL_W)
            print("  " + "|".join(detail_cells))

    _output(result, _print, output_json=output_json)
    return result


# ---------------------------------------------------------------------------
# Query (kept for backward compat, list is preferred)
# ---------------------------------------------------------------------------


def cmd_query(
    vault_path: str,
    project_name: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    tag: str | None = None,
    overdue: bool = False,
    output_json: bool = False,
) -> list:
    """Query tasks with filters. Returns matching tasks."""
    return cmd_list_tasks(
        vault_path,
        project_name=project_name,
        status=status,
        priority=priority,
        tag=tag,
        overdue=overdue,
        fmt="compact",
        output_json=output_json,
    )


# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------


def cmd_install(source_dir: str, vault_path: str, output_json: bool = False) -> dict:
    """Link runtime members to the maintained source; never overwrite copies."""
    import os
    import runpy
    helper = Path(os.environ.get("OBSIDIAN_VAULT_TOOLS_PATH", str(Path(__file__).resolve().parents[2] / "obsidian-vault-tools"))) / "scripts/skill_install.py"
    if not helper.is_file():
        raise RuntimeError("Missing obsidian-vault-tools source; install it beside this repository or set OBSIDIAN_VAULT_TOOLS_PATH")
    install = runpy.run_path(str(helper))["install"]
    result = install(source_dir, vault_path, "obsidian-project-planner")
    _output(result, lambda: print(f"{result['action']}: {result['target']} -> {result['source']}"), output_json=output_json)
    return result


# ---------------------------------------------------------------------------
# Sync Check
# ---------------------------------------------------------------------------


def cmd_ensure_sync(vault_path: str, output_json: bool = False) -> dict:
    """Check markdown sync status and report."""
    data = load_data(vault_path)
    settings = data.get("settings", {})
    result = {
        "enableMarkdownSync": settings.get("enableMarkdownSync", False),
        "autoCreateTaskNotes": settings.get("autoCreateTaskNotes", False),
        "syncOnStartup": settings.get("syncOnStartup", False),
    }

    def _print():
        print("Markdown Sync Status:")
        for key, val in result.items():
            label = "ON" if val else "OFF"
            print(f"  {key}: {label}")
        if not result["enableMarkdownSync"]:
            print("\n  Warning: Markdown Sync is disabled.")
            print("  Task files created by this skill won't be picked up by the plugin.")
            print("  Enable it in Obsidian: Settings > Project Planner > Markdown Sync")

    _output(result, _print, output_json=output_json)
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Obsidian Project Planner Manager")
    parser.add_argument("--vault", required=True, help="Path to Obsidian vault")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output as JSON")
    sub = parser.add_subparsers(dest="command")

    # status
    sub.add_parser("status", help="Show project overview")

    # create-project
    cp = sub.add_parser("create-project", help="Create a new project")
    cp.add_argument("name", help="Project name")
    cp.add_argument("--start", help="Start date (YYYY-MM-DD)")
    cp.add_argument("--due", help="Due date (YYYY-MM-DD)")
    cp.add_argument("--buckets", help="Comma-separated bucket names")

    # delete-project
    dp = sub.add_parser("delete-project", help="Delete a project")
    dp.add_argument("name", help="Project name")

    # list-projects
    sub.add_parser("list-projects", help="List all projects")

    # add-bucket
    ab = sub.add_parser("add-bucket", help="Add a bucket to a project")
    ab.add_argument("--project", required=True, help="Project name")
    ab.add_argument("name", help="Bucket name")

    # add-task
    at = sub.add_parser("add-task", help="Add a task to a project")
    at.add_argument("title", help="Task title")
    at.add_argument("--project", help="Project name")
    at.add_argument("--status", default="Not Started", help="Task status")
    at.add_argument("--priority", choices=["high", "medium", "low"], help="Priority level")
    at.add_argument("--bucket", help="Bucket name")
    at.add_argument("--start", help="Start date (YYYY-MM-DD)")
    at.add_argument("--due", help="Due date (YYYY-MM-DD)")
    at.add_argument("--tags", help="Comma-separated tags")
    at.add_argument("--parent", help="Parent task title")
    at.add_argument("--depends-on", help="Dependency task title(s), comma-separated")
    at.add_argument("--description", help="Task description")
    at.add_argument("--effort-remaining", type=float, help="Estimated hours remaining")

    # update-task
    ut = sub.add_parser("update-task", help="Update an existing task")
    ut.add_argument("title", help="Task title to find")
    ut.add_argument("--project", help="Project name")
    ut.add_argument("--status", help="New status")
    ut.add_argument("--priority", choices=["high", "medium", "low"], help="New priority")
    ut.add_argument("--bucket", help="New bucket name")
    ut.add_argument("--start", help="New start date (YYYY-MM-DD)")
    ut.add_argument("--due", help="New due date (YYYY-MM-DD)")
    ut.add_argument("--tags", help="New tags (comma-separated, replaces existing)")
    ut.add_argument("--description", help="New description")
    ut.add_argument("--effort-remaining", type=float, help="Estimated hours remaining")
    ut.add_argument("--complete", action="store_true", help="Mark as completed")
    ut.add_argument("--rename", help="Rename the task")

    # delete-task
    dt = sub.add_parser("delete-task", help="Delete a task")
    dt.add_argument("title", help="Task title to find")
    dt.add_argument("--project", help="Project name")
    dt.add_argument("--force", action="store_true", help="Skip confirmation")

    # list (display)
    ls = sub.add_parser("list", help="List and filter tasks")
    ls.add_argument("--project", help="Filter by project name")
    ls.add_argument("--status", help="Filter by status")
    ls.add_argument("--priority", help="Filter by priority")
    ls.add_argument("--bucket", help="Filter by bucket name")
    ls.add_argument("--tag", help="Filter by tag")
    ls.add_argument("--overdue", action="store_true", help="Show only overdue tasks")
    ls.add_argument("--due-this-week", action="store_true", help="Tasks due within 7 days")
    ls.add_argument("--format", choices=["table", "compact", "detailed"], default="table",
                    help="Output format (default: table)")

    # board
    bd = sub.add_parser("board", help="Board view of a project")
    bd.add_argument("--project", help="Project name")

    # query (backward compat)
    q = sub.add_parser("query", help="Query tasks with filters")
    q.add_argument("--project", help="Project name")
    q.add_argument("--status", help="Filter by status")
    q.add_argument("--priority", help="Filter by priority")
    q.add_argument("--tag", help="Filter by tag")
    q.add_argument("--overdue", action="store_true", help="Show only overdue tasks")

    # install
    inst = sub.add_parser("install", help="Install skill into a vault")
    inst.add_argument("--source", required=True, help="Path to skill repo")

    # ensure-sync
    sub.add_parser("ensure-sync", help="Check markdown sync status")

    args = parser.parse_args()
    oj = args.output_json

    if args.command == "status":
        cmd_status(args.vault, output_json=oj)
    elif args.command == "create-project":
        bucket_names = [b.strip() for b in args.buckets.split(",")] if args.buckets else None
        cmd_create_project(args.vault, args.name, args.start, args.due, bucket_names, output_json=oj)
    elif args.command == "delete-project":
        cmd_delete_project(args.vault, args.name, output_json=oj)
    elif args.command == "list-projects":
        cmd_list_projects(args.vault, output_json=oj)
    elif args.command == "add-bucket":
        cmd_add_bucket(args.vault, args.project, args.name, output_json=oj)
    elif args.command == "add-task":
        tag_list = [t.strip() for t in args.tags.split(",")] if args.tags else None
        cmd_add_task(
            args.vault, args.title, project_name=args.project,
            status=args.status, priority=args.priority, bucket_name=args.bucket,
            start_date=args.start, due_date=args.due, tags=tag_list,
            parent_title=args.parent, depends_on_title=args.depends_on,
            description=args.description, effort_remaining=args.effort_remaining,
            output_json=oj,
        )
    elif args.command == "update-task":
        tag_list = [t.strip() for t in args.tags.split(",")] if args.tags else None
        cmd_update_task(
            args.vault, args.title, project_name=args.project,
            status=args.status, priority=args.priority, bucket_name=args.bucket,
            start_date=args.start, due_date=args.due, tags=tag_list,
            description=args.description, effort_remaining=args.effort_remaining,
            complete=args.complete, rename=args.rename, output_json=oj,
        )
    elif args.command == "delete-task":
        cmd_delete_task(args.vault, args.title, project_name=args.project,
                        force=args.force, output_json=oj)
    elif args.command == "list":
        cmd_list_tasks(
            args.vault, project_name=args.project, status=args.status,
            priority=args.priority, bucket_name=args.bucket, tag=args.tag,
            overdue=args.overdue, due_this_week=args.due_this_week,
            fmt=args.format, output_json=oj,
        )
    elif args.command == "board":
        cmd_board(args.vault, project_name=args.project, output_json=oj)
    elif args.command == "query":
        cmd_query(args.vault, args.project, args.status, args.priority,
                  args.tag, args.overdue, output_json=oj)
    elif args.command == "install":
        cmd_install(args.source, args.vault, output_json=oj)
    elif args.command == "ensure-sync":
        cmd_ensure_sync(args.vault, output_json=oj)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
