#!/usr/bin/env python3
"""Obsidian Project Planner -- Shared Utilities

Common functions used by pp_manager.py and csv_import.py:
- Data I/O (load/save data.json with backup and validation)
- Entity lookup (projects, buckets, tasks)
- UUID generation
- Markdown task file generation
- Vault auto-discovery
"""

import json
import re
import shutil
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

PLUGIN_DIR = ".obsidian/plugins/obsidian-project-planner"
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.I)


# ---------------------------------------------------------------------------
# Data I/O
# ---------------------------------------------------------------------------

def data_path(vault_path: str) -> Path:
    """Return the path to data.json for a vault."""
    return Path(vault_path) / PLUGIN_DIR / "data.json"


def load_data(vault_path: str) -> dict:
    """Load data.json from the plugin directory."""
    dp = data_path(vault_path)
    if not dp.exists():
        print(f"Error: Plugin data not found at {dp}", file=sys.stderr)
        print("Is obsidian-project-planner installed in this vault?", file=sys.stderr)
        sys.exit(1)
    with open(dp, "r", encoding="utf-8") as f:
        data = json.load(f)
    settings = data.get("settings", {})
    if "projects" in settings:
        if "projects" in data and data["projects"] != settings["projects"]:
            raise ValueError("Conflicting Planner project layouts; refusing to guess")
        data["projects"] = settings["projects"]
        data["tags"] = settings.get("availableTags", [])
    if not isinstance(data.get("projects"), list):
        raise ValueError("Unsupported Planner project layout")
    if "tasksByProject" not in data:
        # Newer plugin storage is per-project. A missing file is not an empty board.
        tasks = {}
        vault = Path(vault_path).resolve()
        for project in data["projects"]:
            key = project.get("storageKey")
            if not key:
                raise ValueError("Unsupported Planner task layout: missing storageKey")
            path = (vault / settings.get("projectsBasePath", "Project Planner") / key / ".planner-tasks.json").resolve()
            if not path.is_relative_to(vault):
                raise ValueError("Planner storage path escapes the vault")
            record = json.loads(path.read_text())
            if record.get("version") != 1 or record.get("projectId") != project["id"] or not isinstance(record.get("tasks"), list):
                raise ValueError("Unsupported or mismatched Planner task file")
            tasks[project["id"]] = record["tasks"]
        data["tasksByProject"] = tasks
    if not isinstance(data["tasksByProject"], dict):
        raise ValueError("Invalid Planner tasksByProject")
    return data


def mutation_unavailable() -> None:
    raise SystemExit(
        "Planner writes are disabled: this legacy writer cannot safely preserve "
        "the installed plugin schema, note bodies and synchronized files. "
        "Use the Project Planner plugin to make changes; read-only queries remain available."
    )


def save_data(vault_path: str, data: dict) -> None:
    """Fail before disk I/O until a compatible transactional writer is implemented."""
    mutation_unavailable()


# ---------------------------------------------------------------------------
# UUID
# ---------------------------------------------------------------------------

def new_uuid() -> str:
    """Generate a new RFC 4122 v4 UUID."""
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Entity Lookup
# ---------------------------------------------------------------------------

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
    """Return exact case-insensitive matches; never silently use substrings."""
    return [t for t in tasks if t.get("title", "").casefold() == title.casefold()]


def resolve_project(data: dict, project_name: str | None) -> dict:
    """Resolve a project by name, or auto-select if only one exists.

    Exits with an error message if resolution fails.
    """
    projects = data.get("projects", [])
    if project_name:
        proj = find_project(data, project_name)
        if not proj:
            print(f"Error: Project '{project_name}' not found.", file=sys.stderr)
            available = ", ".join(p["name"] for p in projects) or "(none)"
            print(f"Available projects: {available}", file=sys.stderr)
            sys.exit(1)
        return proj
    if len(projects) == 1:
        return projects[0]
    if not projects:
        print("Error: No projects exist. Create one first.", file=sys.stderr)
        sys.exit(1)
    names = ", ".join(p["name"] for p in projects)
    print(f"Error: Multiple projects exist. Specify --project: {names}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Project Creation (pure data, no I/O)
# ---------------------------------------------------------------------------

def create_project_data(
    data: dict,
    name: str,
    bucket_names: list[str] | None = None,
    start_date: str | None = None,
    due_date: str | None = None,
) -> tuple[dict, dict]:
    """Create a project object and insert it into data. Returns (data, project).

    Does NOT perform file I/O -- caller is responsible for save_data().
    """
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

    data.setdefault("projects", []).append(project)
    data.setdefault("tasksByProject", {})[project["id"]] = []
    return data, project


# ---------------------------------------------------------------------------
# Markdown Generation
# ---------------------------------------------------------------------------

def task_to_markdown(task: dict) -> str:
    """Convert a task dict to a markdown string with YAML frontmatter.

    Produces the canonical format expected by the Project Planner plugin's
    bidirectional markdown sync.
    """
    lines = ["---"]

    # Required fields
    lines.append(f"id: {task['id']}")
    lines.append(f"title: {task['title']}")
    lines.append(f"status: {task.get('status', 'Not Started')}")
    lines.append(f"completed: {'true' if task.get('completed') else 'false'}")

    # Optional scalar fields
    for field in ["priority", "parentId", "bucketId", "startDate", "dueDate"]:
        if task.get(field) is not None:
            lines.append(f"{field}: {task[field]}")

    # Collapsed
    if task.get("collapsed"):
        lines.append("collapsed: true")

    # Effort fields
    for field in ["effortCompleted", "effortRemaining"]:
        if task.get(field) is not None:
            lines.append(f"{field}: {task[field]}")

    # Cost fields
    for field in ["costEstimate", "costActual", "costType", "hourlyRate"]:
        if task.get(field) is not None:
            lines.append(f"{field}: {task[field]}")

    # Tags
    if task.get("tags"):
        lines.append("tags:")
        for tag in task["tags"]:
            lines.append(f"  - {tag}")

    # Dependencies
    if task.get("dependencies"):
        lines.append("dependencies:")
        for dep in task["dependencies"]:
            lines.append(f"  - {dep['type']}:{dep['taskId']}")

    lines.append("---")
    lines.append("")

    # Body
    if task.get("description"):
        lines.append(task["description"])
        lines.append("")

    # Subtasks
    if task.get("subtasks"):
        lines.append("## Subtasks")
        for st in task["subtasks"]:
            check = "x" if st.get("completed") else " "
            lines.append(f"- [{check}] {st['title']}")
        lines.append("")

    lines.append("---")
    lines.append("*Managed by Project Planner -- do not remove the frontmatter.*")

    return "\n".join(lines) + "\n"


def sanitize_filename(title: str) -> str:
    """Remove characters that are invalid in file paths."""
    return "".join(c for c in title if c not in r'\/:*?"<>|').strip()


def write_task_file(vault_path: str, project_name: str, task: dict) -> Path:
    """Disabled alongside JSON writes: never replace a task note from stale data."""
    mutation_unavailable()


def read_task_frontmatter(filepath: Path) -> dict:
    """Read YAML frontmatter from a task markdown file.

    Returns a dict of frontmatter fields. Uses simple line-based parsing
    to avoid requiring PyYAML as a dependency.
    """
    text = filepath.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}

    end = text.find("\n---", 3)
    if end == -1:
        return {}

    fm_text = text[4:end]  # skip opening "---\n"
    result: dict = {}
    current_list_key: str | None = None

    for line in fm_text.split("\n"):
        # List item
        if line.startswith("  - "):
            if current_list_key:
                result.setdefault(current_list_key, []).append(line[4:].strip())
            continue

        current_list_key = None

        if ":" not in line:
            continue

        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()

        # Detect list-type fields
        if val == "":
            current_list_key = key
            continue

        # Type coercion
        if val == "null":
            result[key] = None
        elif val == "true":
            result[key] = True
        elif val == "false":
            result[key] = False
        elif re.match(r"^-?\d+$", val):
            result[key] = int(val)
        elif re.match(r"^-?\d+\.\d+$", val):
            result[key] = float(val)
        else:
            result[key] = val

    return result


def read_task_body(filepath: Path) -> str:
    """Read the body content (below frontmatter) from a task markdown file."""
    text = filepath.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return text

    end = text.find("\n---", 3)
    if end == -1:
        return ""

    body = text[end + 4:].strip()
    # Strip the footer line
    footer = "\n---\n*Managed by Project Planner"
    idx = body.find(footer)
    if idx != -1:
        body = body[:idx].strip()
    return body


# ---------------------------------------------------------------------------
# Sync Helpers
# ---------------------------------------------------------------------------

def is_sync_enabled(data: dict) -> bool:
    """Check if markdown sync is enabled in plugin settings."""
    return data.get("settings", {}).get("enableMarkdownSync", False)


def register_tags(data: dict, tags: list[str]) -> None:
    """Register new tags in data.json if they don't already exist."""
    existing = {t["name"].lower() for t in data.get("tags", [])}
    for tag in tags:
        if tag.lower() not in existing:
            data.setdefault("tags", []).append({
                "id": new_uuid(),
                "name": tag,
                "color": "#808080",
            })
            existing.add(tag.lower())


# ---------------------------------------------------------------------------
# Vault Discovery
# ---------------------------------------------------------------------------

def discover_vault(hint: str | None = None) -> Path | None:
    """Try to locate an Obsidian vault.

    Search order:
    1. Explicit hint (if provided and contains .obsidian/)
    2. Current working directory (if contains .obsidian/)
    3. Common locations: ~/Documents, ~/Obsidian, ~/

    Returns None if no single vault is found (caller should ask the user).
    """
    if hint:
        p = Path(hint).expanduser().resolve()
        if (p / ".obsidian").is_dir():
            return p
        return None

    # Check cwd
    cwd = Path.cwd()
    if (cwd / ".obsidian").is_dir():
        return cwd

    # Scan common parent directories for vaults
    candidates: list[Path] = []
    search_roots = [
        Path.home() / "Documents",
        Path.home() / "Obsidian",
        Path.home(),
    ]
    for root in search_roots:
        if not root.is_dir():
            continue
        for child in root.iterdir():
            if child.is_dir() and (child / ".obsidian").is_dir():
                candidates.append(child)

    if len(candidates) == 1:
        return candidates[0]
    return None


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_data(data: dict) -> list[str]:
    """Validate data.json structure. Returns a list of error messages (empty = valid)."""
    errors: list[str] = []

    if not isinstance(data.get("projects"), list):
        errors.append("Missing or invalid 'projects' array")
        return errors  # Can't validate further

    if not isinstance(data.get("tasksByProject"), dict):
        errors.append("Missing or invalid 'tasksByProject' dict")

    # Collect all valid IDs
    project_ids = set()
    bucket_ids = set()
    all_task_ids = set()

    for proj in data.get("projects", []):
        pid = proj.get("id", "")
        if not pid:
            errors.append(f"Project '{proj.get('name', '?')}' has no id")
            continue
        if not UUID_RE.match(pid):
            errors.append(f"Project '{proj.get('name', '?')}' has invalid UUID: {pid}")
        project_ids.add(pid)
        if not proj.get("name"):
            errors.append(f"Project {pid} has no name")
        for b in proj.get("buckets", []):
            bid = b.get("id", "")
            if bid:
                bucket_ids.add(bid)

    tasks_by_project = data.get("tasksByProject", {})

    for pid, tasks in tasks_by_project.items():
        if pid not in project_ids:
            errors.append(f"tasksByProject has orphan project ID: {pid}")
        if not isinstance(tasks, list):
            errors.append(f"tasksByProject[{pid}] is not a list")
            continue
        for task in tasks:
            tid = task.get("id", "")
            if tid:
                all_task_ids.add(tid)
            for field in ("id", "title", "status"):
                if not task.get(field):
                    errors.append(f"Task '{task.get('title', '?')}' missing required field: {field}")
            if "completed" not in task:
                errors.append(f"Task '{task.get('title', '?')}' missing 'completed' field")

    # Reference checks
    for _pid, tasks in tasks_by_project.items():
        if not isinstance(tasks, list):
            continue
        for task in tasks:
            bid = task.get("bucketId")
            if bid and bid not in bucket_ids:
                errors.append(f"Task '{task.get('title', '?')}' references unknown bucket: {bid}")
            par = task.get("parentId")
            if par and par not in all_task_ids:
                errors.append(f"Task '{task.get('title', '?')}' references unknown parent: {par}")
            for dep in task.get("dependencies", []):
                dep_id = dep.get("taskId", "")
                if dep_id and dep_id not in all_task_ids:
                    errors.append(f"Task '{task.get('title', '?')}' references unknown dependency: {dep_id}")

    return errors


# ---------------------------------------------------------------------------
# Date Helpers
# ---------------------------------------------------------------------------

def today_str() -> str:
    """Return today's date as YYYY-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")


def date_in_days(days: int) -> str:
    """Return a date N days from today as YYYY-MM-DD."""
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
