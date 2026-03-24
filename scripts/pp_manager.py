#!/usr/bin/env python3
"""Obsidian Project Planner — Core Manager

Handles project-level operations that require direct data.json manipulation:
- Create/list/delete projects
- Manage buckets
- Query tasks across projects
- Install/update skill into vaults

Usage:
    uv run python scripts/pp_manager.py <command> [options]

Commands:
    status              Show project overview
    create-project      Create a new project
    delete-project      Delete a project
    list-projects       List all projects
    add-bucket          Add a bucket to a project
    query               Query tasks with filters
    install             Install skill into a vault
    ensure-sync         Check and optionally enable markdown sync
"""

import argparse
import json
import os
import shutil
import sys
import uuid
from datetime import datetime
from pathlib import Path


def load_data(vault_path: str) -> dict:
    """Load data.json from the plugin directory."""
    data_path = Path(vault_path) / ".obsidian" / "plugins" / "obsidian-project-planner" / "data.json"
    if not data_path.exists():
        print(f"Error: Plugin data not found at {data_path}", file=sys.stderr)
        print("Is obsidian-project-planner installed in this vault?", file=sys.stderr)
        sys.exit(1)
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(vault_path: str, data: dict) -> None:
    """Write data.json back to the plugin directory."""
    data_path = Path(vault_path) / ".obsidian" / "plugins" / "obsidian-project-planner" / "data.json"
    # Create backup before writing
    if data_path.exists():
        backup_path = data_path.with_suffix(".json.bak")
        shutil.copy2(data_path, backup_path)
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def new_uuid() -> str:
    """Generate a new UUID v4."""
    return str(uuid.uuid4())


# --- Project Operations ---


def cmd_status(vault_path: str) -> None:
    """Show overview of all projects and task counts."""
    data = load_data(vault_path)
    projects = data.get("projects", [])
    tasks_by_project = data.get("tasksByProject", {})
    today = datetime.now().strftime("%Y-%m-%d")

    if not projects:
        print("No projects found. Create one with: /pp create-project \"Name\"")
        return

    print("--=={ Project Planner }==--\n")
    print("  Projects")
    print("  ========")

    total_tasks = 0
    total_completed = 0
    total_overdue = 0

    for i, proj in enumerate(projects, 1):
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
        buckets = " | ".join(b["name"] for b in proj.get("buckets", []))

        overdue_str = f", {n_overdue} overdue" if n_overdue > 0 else ""
        print(f"  {i}. {proj['name']} ({n_tasks} tasks — {pct}% complete{overdue_str})")
        if buckets:
            print(f"     Buckets: {buckets}")

        total_tasks += n_tasks
        total_completed += n_completed
        total_overdue += n_overdue

    print(f"\n  Summary: {total_tasks} total tasks, {total_completed} completed, {total_overdue} overdue")


def cmd_create_project(
    vault_path: str,
    name: str,
    start_date: str | None = None,
    due_date: str | None = None,
    bucket_names: list[str] | None = None,
) -> dict:
    """Create a new project in data.json and create the folder structure."""
    data = load_data(vault_path)

    # Check for duplicate name
    existing = [p for p in data.get("projects", []) if p["name"].lower() == name.lower()]
    if existing:
        print(f"Error: Project '{name}' already exists (ID: {existing[0]['id']})", file=sys.stderr)
        sys.exit(1)

    if bucket_names is None:
        bucket_names = ["To Do", "In Progress", "Done"]

    project = {
        "id": new_uuid(),
        "name": name,
        "buckets": [{"id": new_uuid(), "name": bn} for bn in bucket_names],
    }
    if start_date:
        project["startDate"] = start_date
    if due_date:
        project["dueDate"] = due_date

    if "projects" not in data:
        data["projects"] = []
    if "tasksByProject" not in data:
        data["tasksByProject"] = {}

    data["projects"].append(project)
    data["tasksByProject"][project["id"]] = []

    save_data(vault_path, data)

    # Create folder structure
    tasks_dir = Path(vault_path) / name / "Tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    buckets_str = " | ".join(bucket_names)
    print(f"Created project \"{name}\"")
    print(f"  ID: {project['id']}")
    print(f"  Buckets: {buckets_str}")
    print(f"  Folder: {name}/Tasks/")

    return project


def cmd_list_projects(vault_path: str) -> None:
    """List all projects."""
    data = load_data(vault_path)
    projects = data.get("projects", [])
    if not projects:
        print("No projects found.")
        return
    for proj in projects:
        task_count = len(data.get("tasksByProject", {}).get(proj["id"], []))
        print(f"  {proj['name']} ({task_count} tasks) — ID: {proj['id']}")


def cmd_delete_project(vault_path: str, name: str) -> None:
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

    print(f"Deleting project \"{proj['name']}\" ({task_count} tasks)")
    data["projects"] = [p for p in projects if p["id"] != pid]
    data["tasksByProject"].pop(pid, None)
    save_data(vault_path, data)
    print("Done. Note: markdown task files were NOT deleted — remove the folder manually if desired.")


# --- Bucket Operations ---


def cmd_add_bucket(vault_path: str, project_name: str, bucket_name: str) -> None:
    """Add a bucket to a project."""
    data = load_data(vault_path)
    proj = find_project(data, project_name)
    if not proj:
        print(f"Error: Project '{project_name}' not found.", file=sys.stderr)
        sys.exit(1)

    # Check for duplicate
    existing = [b for b in proj.get("buckets", []) if b["name"].lower() == bucket_name.lower()]
    if existing:
        print(f"Bucket '{bucket_name}' already exists in project '{proj['name']}'.")
        return

    bucket = {"id": new_uuid(), "name": bucket_name}
    proj.setdefault("buckets", []).append(bucket)
    save_data(vault_path, data)
    print(f"Added bucket \"{bucket_name}\" to project \"{proj['name']}\"")
    print(f"  Bucket ID: {bucket['id']}")


# --- Query Operations ---


def cmd_query(
    vault_path: str,
    project_name: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    tag: str | None = None,
    overdue: bool = False,
) -> list[dict]:
    """Query tasks with filters. Returns matching tasks."""
    data = load_data(vault_path)
    today = datetime.now().strftime("%Y-%m-%d")
    results = []

    projects_to_search = data.get("projects", [])
    if project_name:
        proj = find_project(data, project_name)
        if not proj:
            print(f"Error: Project '{project_name}' not found.", file=sys.stderr)
            sys.exit(1)
        projects_to_search = [proj]

    for proj in projects_to_search:
        pid = proj["id"]
        tasks = data.get("tasksByProject", {}).get(pid, [])
        for task in tasks:
            if status and task.get("status", "").lower() != status.lower():
                continue
            if priority and (task.get("priority") or "").lower() != priority.lower():
                continue
            if tag and tag.lower() not in [t.lower() for t in task.get("tags", [])]:
                continue
            if overdue:
                if task.get("completed", False):
                    continue
                if not task.get("dueDate") or task["dueDate"] >= today:
                    continue
            results.append({"project": proj["name"], **task})

    return results


# --- Install Operations ---


def cmd_install(source_dir: str, vault_path: str) -> None:
    """Install or update the skill into a vault."""
    source = Path(source_dir)
    target = Path(vault_path) / ".claude" / "skills" / "obsidian-project-planner"

    if not source.exists():
        print(f"Error: Source directory not found: {source}", file=sys.stderr)
        sys.exit(1)

    if not Path(vault_path).exists():
        print(f"Error: Vault path not found: {vault_path}", file=sys.stderr)
        sys.exit(1)

    # Determine what to copy (exclude documentation/, evals/, .git, etc.)
    include = ["SKILL.md", "scripts", "references"]
    updating = target.exists()

    target.mkdir(parents=True, exist_ok=True)

    for item_name in include:
        src = source / item_name
        dst = target / item_name
        if not src.exists():
            continue
        if src.is_file():
            shutil.copy2(src, dst)
        elif src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

    action = "Updated" if updating else "Installed"
    print(f"{action} obsidian-project-planner skill")
    print(f"  Source: {source}")
    print(f"  Target: {target}")
    for item_name in include:
        if (source / item_name).exists():
            print(f"  ✓ {item_name}")


# --- Sync Check ---


def cmd_ensure_sync(vault_path: str) -> None:
    """Check markdown sync status and report."""
    data = load_data(vault_path)
    settings = data.get("settings", {})
    sync_enabled = settings.get("enableMarkdownSync", False)
    auto_create = settings.get("autoCreateTaskNotes", False)
    sync_on_startup = settings.get("syncOnStartup", False)

    print("Markdown Sync Status:")
    print(f"  Enable Markdown Sync: {'ON' if sync_enabled else 'OFF'}")
    print(f"  Auto-Create Task Notes: {'ON' if auto_create else 'OFF'}")
    print(f"  Sync on Startup: {'ON' if sync_on_startup else 'OFF'}")

    if not sync_enabled:
        print("\n  ⚠ Markdown Sync is disabled.")
        print("  Task files created by this skill won't be picked up by the plugin.")
        print("  Enable it in Obsidian: Settings → Project Planner → Markdown Sync")


# --- Helpers ---


def find_project(data: dict, name: str) -> dict | None:
    """Find a project by name (case-insensitive)."""
    for proj in data.get("projects", []):
        if proj["name"].lower() == name.lower():
            return proj
    return None


def find_bucket(project: dict, name: str) -> dict | None:
    """Find a bucket by name within a project (case-insensitive)."""
    for bucket in project.get("buckets", []):
        if bucket["name"].lower() == name.lower():
            return bucket
    return None


def find_task_by_title(tasks: list[dict], title: str) -> list[dict]:
    """Find tasks by title. Returns exact matches first, then substring matches."""
    title_lower = title.lower()
    exact = [t for t in tasks if t.get("title", "").lower() == title_lower]
    if exact:
        return exact
    partial = [t for t in tasks if title_lower in t.get("title", "").lower()]
    return partial


# --- CLI ---


def main():
    parser = argparse.ArgumentParser(description="Obsidian Project Planner Manager")
    parser.add_argument("--vault", required=True, help="Path to Obsidian vault")
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

    # query
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

    if args.command == "status":
        cmd_status(args.vault)
    elif args.command == "create-project":
        bucket_names = args.buckets.split(",") if args.buckets else None
        cmd_create_project(args.vault, args.name, args.start, args.due, bucket_names)
    elif args.command == "delete-project":
        cmd_delete_project(args.vault, args.name)
    elif args.command == "list-projects":
        cmd_list_projects(args.vault)
    elif args.command == "add-bucket":
        cmd_add_bucket(args.vault, args.project, args.name)
    elif args.command == "query":
        results = cmd_query(args.vault, args.project, args.status, args.priority, args.tag, args.overdue)
        if not results:
            print("No tasks match the filters.")
        else:
            for t in results:
                proj_name = t.get("project", "")
                status = t.get("status", "")
                priority = t.get("priority", "")
                due = t.get("dueDate", "")
                print(f"  [{proj_name}] {t['title']} — {status} | {priority} | due: {due}")
    elif args.command == "install":
        cmd_install(args.source, args.vault)
    elif args.command == "ensure-sync":
        cmd_ensure_sync(args.vault)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
