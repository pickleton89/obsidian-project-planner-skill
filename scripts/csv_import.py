#!/usr/bin/env python3
"""Obsidian Project Planner — CSV/TSV Import Utility

Parses CSV or TSV exports from project management tools and creates properly
formatted markdown task files (or data.json entries) for the Project Planner plugin.

Supports imports from:
  - Microsoft Project
  - Jira
  - Asana
  - Monday.com
  - Generic CSV/TSV with headers

Usage:
    uv run python scripts/csv_import.py <file> --vault <path> --project "Name" [options]

Options:
    --vault PATH           Path to Obsidian vault (required)
    --project NAME         Target project name (required; created if doesn't exist)
    --mapping COL=FIELD    Custom column mapping (repeatable)
    --delimiter CHAR       Field delimiter (default: auto-detect from extension)
    --dry-run              Preview import without writing files
    --status-map SRC=DST   Map source status values to plugin statuses (repeatable)
    --priority-map SRC=DST Map source priority values (repeatable)
"""

import argparse
import csv
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Known column name → plugin field mappings
COLUMN_ALIASES = {
    # title
    "title": "title",
    "name": "title",
    "task": "title",
    "task name": "title",
    "task_name": "title",
    "summary": "title",
    "issue": "title",
    "subject": "title",
    "item": "title",
    # status
    "status": "status",
    "state": "status",
    "workflow": "status",
    # priority
    "priority": "priority",
    "importance": "priority",
    "urgency": "priority",
    # dates
    "due": "dueDate",
    "due date": "dueDate",
    "due_date": "dueDate",
    "deadline": "dueDate",
    "end date": "dueDate",
    "end_date": "dueDate",
    "finish": "dueDate",
    "start": "startDate",
    "start date": "startDate",
    "start_date": "startDate",
    "begin date": "startDate",
    "begin_date": "startDate",
    # tags
    "tags": "tags",
    "labels": "tags",
    "categories": "tags",
    "label": "tags",
    # parent
    "parent": "parent",
    "parent task": "parent",
    "parent_task": "parent",
    "wbs parent": "parent",
    "wbs_parent": "parent",
    "outline level": "outline_level",
    "outline_level": "outline_level",
    "wbs": "wbs",
    # dependencies
    "depends on": "depends_on",
    "depends_on": "depends_on",
    "predecessors": "depends_on",
    "blocked by": "depends_on",
    "blocked_by": "depends_on",
    "dependencies": "depends_on",
    # bucket
    "bucket": "bucket",
    "column": "bucket",
    "swimlane": "bucket",
    "board column": "bucket",
    # description
    "description": "description",
    "notes": "description",
    "details": "description",
    "body": "description",
    # effort
    "effort": "effortRemaining",
    "estimated hours": "effortRemaining",
    "estimated_hours": "effortRemaining",
    "work": "effortRemaining",
    "estimate": "effortRemaining",
    "actual hours": "effortCompleted",
    "actual_hours": "effortCompleted",
    "hours spent": "effortCompleted",
    "logged hours": "effortCompleted",
    # cost
    "cost": "costEstimate",
    "estimated cost": "costEstimate",
    "estimated_cost": "costEstimate",
    "actual cost": "costActual",
    "actual_cost": "costActual",
    # row ID (for dependency resolution)
    "id": "source_id",
    "task id": "source_id",
    "task_id": "source_id",
    "issue key": "source_id",
    "issue_key": "source_id",
    "row": "source_id",
}

# Default status mapping
DEFAULT_STATUS_MAP = {
    "to do": "Not Started",
    "todo": "Not Started",
    "open": "Not Started",
    "new": "Not Started",
    "backlog": "Not Started",
    "not started": "Not Started",
    "in progress": "In Progress",
    "in-progress": "In Progress",
    "active": "In Progress",
    "doing": "In Progress",
    "working": "In Progress",
    "done": "Completed",
    "completed": "Completed",
    "closed": "Completed",
    "resolved": "Completed",
    "finished": "Completed",
}

# Default priority mapping
DEFAULT_PRIORITY_MAP = {
    "critical": "high",
    "highest": "high",
    "high": "high",
    "p1": "high",
    "urgent": "high",
    "medium": "medium",
    "normal": "medium",
    "p2": "medium",
    "default": "medium",
    "low": "low",
    "lowest": "low",
    "p3": "low",
    "minor": "low",
    "none": None,
    "trivial": "low",
}


def new_uuid() -> str:
    return str(uuid.uuid4())


def detect_delimiter(filepath: str) -> str:
    """Auto-detect CSV vs TSV from extension and content."""
    ext = Path(filepath).suffix.lower()
    if ext in (".tsv", ".tab"):
        return "\t"
    if ext == ".csv":
        return ","
    # Sniff the first line
    with open(filepath, "r", encoding="utf-8") as f:
        first_line = f.readline()
    if "\t" in first_line and "," not in first_line:
        return "\t"
    return ","


def normalize_column(col: str) -> str:
    """Normalize a column header for matching."""
    return col.strip().lower().replace("-", " ").replace("_", " ")


def build_column_map(headers: list[str], custom_mapping: dict[str, str] | None = None) -> dict[int, str]:
    """Map column indices to plugin field names."""
    col_map = {}
    for i, header in enumerate(headers):
        norm = normalize_column(header)
        if custom_mapping and header in custom_mapping:
            col_map[i] = custom_mapping[header]
        elif norm in COLUMN_ALIASES:
            col_map[i] = COLUMN_ALIASES[norm]
    return col_map


def parse_date(value: str) -> str | None:
    """Try to parse a date string into YYYY-MM-DD format."""
    if not value or not value.strip():
        return None
    value = value.strip()
    # Already in correct format
    if len(value) == 10 and value[4] == "-" and value[7] == "-":
        return value
    # Common formats
    for fmt in [
        "%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y", "%d-%m-%Y",
        "%Y/%m/%d", "%B %d, %Y", "%b %d, %Y",
        "%m/%d/%y", "%d/%m/%y",
        "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
    ]:
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def parse_tags(value: str) -> list[str]:
    """Parse a tags field — handles comma-separated, semicolon-separated, or space-separated."""
    if not value or not value.strip():
        return []
    # Try comma first, then semicolon, then space
    for sep in [",", ";", " "]:
        if sep in value:
            return [t.strip().lstrip("#") for t in value.split(sep) if t.strip()]
    return [value.strip().lstrip("#")]


def parse_dependencies(value: str) -> list[str]:
    """Parse dependency references — returns list of source IDs or titles."""
    if not value or not value.strip():
        return []
    # Handle comma-separated list of IDs or titles
    deps = []
    for item in value.split(","):
        item = item.strip()
        if item:
            # Strip common prefixes like "FS:", "SS:", etc.
            for prefix in ["FS:", "SS:", "FF:", "SF:", "fs:", "ss:", "ff:", "sf:"]:
                if item.startswith(prefix):
                    item = item[len(prefix):].strip()
                    break
            deps.append(item)
    return deps


def parse_number(value: str) -> float | None:
    """Parse a numeric value, stripping currency symbols."""
    if not value or not value.strip():
        return None
    value = value.strip().lstrip("$€£¥").replace(",", "")
    try:
        return float(value)
    except ValueError:
        return None


def import_csv(
    filepath: str,
    vault_path: str,
    project_name: str,
    delimiter: str | None = None,
    custom_mapping: dict[str, str] | None = None,
    status_map: dict[str, str] | None = None,
    priority_map: dict[str, str] | None = None,
    dry_run: bool = False,
) -> dict:
    """Import tasks from a CSV/TSV file.

    Returns a summary dict with counts and any warnings.
    """
    if delimiter is None:
        delimiter = detect_delimiter(filepath)

    if status_map is None:
        status_map = DEFAULT_STATUS_MAP
    else:
        merged = dict(DEFAULT_STATUS_MAP)
        merged.update(status_map)
        status_map = merged

    if priority_map is None:
        priority_map = DEFAULT_PRIORITY_MAP
    else:
        merged = dict(DEFAULT_PRIORITY_MAP)
        merged.update(priority_map)
        priority_map = merged

    # Read CSV
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=delimiter)
        headers = next(reader)
        rows = list(reader)

    col_map = build_column_map(headers, custom_mapping)

    if not col_map:
        return {"error": "Could not map any columns. Headers found: " + ", ".join(headers)}

    # Check that we have at least a title column
    title_col = None
    for idx, field in col_map.items():
        if field == "title":
            title_col = idx
            break

    if title_col is None:
        return {"error": "No title column found. Headers: " + ", ".join(headers)}

    # Parse rows into task dicts
    parsed_tasks = []
    warnings = []
    source_id_to_idx = {}  # Map source IDs to parsed_tasks index

    for row_num, row in enumerate(rows, 2):  # 2 because row 1 is headers
        if not row or all(not cell.strip() for cell in row):
            continue  # Skip empty rows

        task = {
            "id": new_uuid(),
            "completed": False,
            "_row": row_num,
            "_source_id": None,
            "_parent_ref": None,
            "_depends_on_refs": [],
        }

        for col_idx, field in col_map.items():
            if col_idx >= len(row):
                continue
            value = row[col_idx].strip()
            if not value:
                continue

            if field == "title":
                task["title"] = value
            elif field == "status":
                mapped = status_map.get(value.lower(), value)
                task["status"] = mapped
                if mapped.lower() in ("completed", "done", "closed"):
                    task["completed"] = True
            elif field == "priority":
                task["priority"] = priority_map.get(value.lower(), value)
            elif field == "startDate":
                parsed = parse_date(value)
                if parsed:
                    task["startDate"] = parsed
                else:
                    warnings.append(f"Row {row_num}: Could not parse start date '{value}'")
            elif field == "dueDate":
                parsed = parse_date(value)
                if parsed:
                    task["dueDate"] = parsed
                else:
                    warnings.append(f"Row {row_num}: Could not parse due date '{value}'")
            elif field == "tags":
                task["tags"] = parse_tags(value)
            elif field == "description":
                task["description"] = value
            elif field == "bucket":
                task["_bucket_name"] = value
            elif field == "parent":
                task["_parent_ref"] = value
            elif field == "depends_on":
                task["_depends_on_refs"] = parse_dependencies(value)
            elif field == "source_id":
                task["_source_id"] = value
                source_id_to_idx[value] = len(parsed_tasks)
            elif field == "outline_level":
                task["_outline_level"] = int(value) if value.isdigit() else None
            elif field == "wbs":
                task["_wbs"] = value
            elif field == "effortRemaining":
                num = parse_number(value)
                if num is not None:
                    task["effortRemaining"] = num
            elif field == "effortCompleted":
                num = parse_number(value)
                if num is not None:
                    task["effortCompleted"] = num
            elif field == "costEstimate":
                num = parse_number(value)
                if num is not None:
                    task["costEstimate"] = num
            elif field == "costActual":
                num = parse_number(value)
                if num is not None:
                    task["costActual"] = num

        if "title" not in task:
            warnings.append(f"Row {row_num}: No title found, skipping")
            continue

        if "status" not in task:
            task["status"] = "Not Started"

        parsed_tasks.append(task)

    if not parsed_tasks:
        return {"error": "No valid tasks found in the file.", "warnings": warnings}

    # Build title-to-index map for resolving references
    title_to_idx = {}
    for i, t in enumerate(parsed_tasks):
        title_to_idx[t["title"].lower()] = i
        if t.get("_source_id"):
            source_id_to_idx[t["_source_id"]] = i

    # Also map by row number (1-indexed, but our rows start at 2 due to header)
    row_to_idx = {t["_row"]: i for i, t in enumerate(parsed_tasks)}

    # Resolve parent-child relationships
    for i, task in enumerate(parsed_tasks):
        ref = task.get("_parent_ref")
        if ref:
            parent_idx = _resolve_ref(ref, title_to_idx, source_id_to_idx, row_to_idx)
            if parent_idx is not None and parent_idx != i:
                task["parentId"] = parsed_tasks[parent_idx]["id"]
            else:
                warnings.append(f"Row {task['_row']}: Could not resolve parent '{ref}'")

    # Resolve outline-level hierarchy (MS Project style)
    if any(t.get("_outline_level") is not None for t in parsed_tasks):
        _resolve_outline_hierarchy(parsed_tasks)

    # Resolve dependencies
    for task in parsed_tasks:
        deps = []
        for ref in task.get("_depends_on_refs", []):
            dep_idx = _resolve_ref(ref, title_to_idx, source_id_to_idx, row_to_idx)
            if dep_idx is not None:
                deps.append({"taskId": parsed_tasks[dep_idx]["id"], "type": "blockedBy"})
            else:
                warnings.append(f"Row {task['_row']}: Could not resolve dependency '{ref}'")
        if deps:
            task["dependencies"] = deps

    # Summary for dry run
    if dry_run:
        print(f"\n  Dry Run — Import Preview")
        print(f"  ========================")
        print(f"  Source: {filepath}")
        print(f"  Project: {project_name}")
        print(f"  Tasks found: {len(parsed_tasks)}")
        print(f"  Column mapping:")
        for idx, field in sorted(col_map.items()):
            print(f"    {headers[idx]} → {field}")
        print(f"\n  Tasks:")
        for t in parsed_tasks:
            parent_str = f" (child of {t.get('parentId', '')[:8]}...)" if t.get("parentId") else ""
            dep_count = len(t.get("dependencies", []))
            dep_str = f" [{dep_count} deps]" if dep_count else ""
            print(f"    {t.get('status', '?'):15} | {t.get('priority', '-'):6} | {t['title']}{parent_str}{dep_str}")
        if warnings:
            print(f"\n  Warnings ({len(warnings)}):")
            for w in warnings:
                print(f"    ⚠ {w}")
        return {
            "tasks": len(parsed_tasks),
            "warnings": warnings,
            "dry_run": True,
        }

    # --- Write tasks ---
    # Load or create project
    sys.path.insert(0, str(Path(__file__).parent))
    from pp_manager import load_data, save_data, find_project, cmd_create_project, find_bucket

    data = load_data(vault_path)
    proj = find_project(data, project_name)
    if not proj:
        print(f"Creating project '{project_name}'...")
        # Collect unique bucket names from import
        bucket_names_from_import = sorted(set(
            t.get("_bucket_name") for t in parsed_tasks if t.get("_bucket_name")
        ))
        bucket_list = bucket_names_from_import if bucket_names_from_import else None
        proj = cmd_create_project(vault_path, project_name, bucket_names=bucket_list)
        # Reload data after project creation
        data = load_data(vault_path)
        proj = find_project(data, project_name)

    # Resolve bucket references
    for task in parsed_tasks:
        bucket_name = task.pop("_bucket_name", None)
        if bucket_name:
            bucket = find_bucket(proj, bucket_name)
            if bucket:
                task["bucketId"] = bucket["id"]
            else:
                warnings.append(f"Bucket '{bucket_name}' not found in project — skipping bucket assignment for '{task['title']}'")

    # Check if markdown sync is enabled
    settings = data.get("settings", {})
    sync_enabled = settings.get("enableMarkdownSync", False)

    tasks_written = 0

    if sync_enabled:
        # Write markdown files
        tasks_dir = Path(vault_path) / project_name / "Tasks"
        tasks_dir.mkdir(parents=True, exist_ok=True)

        for task in parsed_tasks:
            clean_task = _clean_task(task)
            md_content = _task_to_markdown(clean_task)
            # Sanitize filename
            safe_title = "".join(c for c in task["title"] if c not in r'\/:*?"<>|').strip()
            filepath = tasks_dir / f"{safe_title}.md"
            filepath.write_text(md_content, encoding="utf-8")
            tasks_written += 1
    else:
        # Write directly to data.json
        pid = proj["id"]
        for task in parsed_tasks:
            clean_task = _clean_task(task)
            data["tasksByProject"].setdefault(pid, []).append(clean_task)
            tasks_written += 1

        # Register new tags
        existing_tags = {t["name"].lower() for t in data.get("tags", [])}
        for task in parsed_tasks:
            for tag in task.get("tags", []):
                if tag.lower() not in existing_tags:
                    data.setdefault("tags", []).append({
                        "id": new_uuid(),
                        "name": tag,
                        "color": "#808080",
                    })
                    existing_tags.add(tag.lower())

        save_data(vault_path, data)

    n_parents = sum(1 for t in parsed_tasks if t.get("parentId"))
    n_deps = sum(len(t.get("dependencies", [])) for t in parsed_tasks)

    print(f"\n  Import Complete")
    print(f"  ===============")
    print(f"  Project: {project_name}")
    print(f"  Tasks imported: {tasks_written}")
    print(f"  Parent-child relationships: {n_parents}")
    print(f"  Dependencies: {n_deps}")
    if sync_enabled:
        print(f"  Written as: markdown files in {project_name}/Tasks/")
    else:
        print(f"  Written to: data.json (markdown sync is off)")
    if warnings:
        print(f"\n  Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"    ⚠ {w}")

    return {
        "tasks": tasks_written,
        "parents": n_parents,
        "dependencies": n_deps,
        "warnings": warnings,
    }


def _resolve_ref(
    ref: str,
    title_map: dict[str, int],
    id_map: dict[str, int],
    row_map: dict[int, int],
) -> int | None:
    """Resolve a reference (title, source ID, or row number) to a task index."""
    # Try source ID
    if ref in id_map:
        return id_map[ref]
    # Try title (case-insensitive)
    if ref.lower() in title_map:
        return title_map[ref.lower()]
    # Try row number
    try:
        row_num = int(ref)
        if row_num in row_map:
            return row_map[row_num]
        # Maybe 0-indexed or 1-indexed offset
        if row_num + 2 in row_map:
            return row_map[row_num + 2]
    except ValueError:
        pass
    return None


def _resolve_outline_hierarchy(tasks: list[dict]) -> None:
    """Resolve MS Project-style outline level hierarchy."""
    parent_stack = []  # Stack of (outline_level, task_id)
    for task in tasks:
        level = task.get("_outline_level")
        if level is None:
            continue
        # Pop stack until we find a parent at a lower level
        while parent_stack and parent_stack[-1][0] >= level:
            parent_stack.pop()
        if parent_stack:
            task["parentId"] = parent_stack[-1][1]
        parent_stack.append((level, task["id"]))


def _clean_task(task: dict) -> dict:
    """Remove internal fields (prefixed with _) from a task dict."""
    return {k: v for k, v in task.items() if not k.startswith("_")}


def _task_to_markdown(task: dict) -> str:
    """Convert a task dict to a markdown string with YAML frontmatter."""
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

    # Subtasks section placeholder
    if task.get("subtasks"):
        lines.append("## Subtasks")
        for st in task["subtasks"]:
            check = "x" if st.get("completed") else " "
            lines.append(f"- [{check}] {st['title']}")
        lines.append("")

    lines.append("---")
    lines.append("*Managed by Project Planner — do not remove the frontmatter.*")

    return "\n".join(lines) + "\n"


# --- CLI ---


def main():
    parser = argparse.ArgumentParser(description="Import CSV/TSV into Obsidian Project Planner")
    parser.add_argument("file", help="Path to CSV or TSV file")
    parser.add_argument("--vault", required=True, help="Path to Obsidian vault")
    parser.add_argument("--project", required=True, help="Target project name")
    parser.add_argument("--delimiter", help="Field delimiter (default: auto-detect)")
    parser.add_argument("--mapping", action="append", help="Column mapping COL=FIELD (repeatable)")
    parser.add_argument("--status-map", action="append", help="Status mapping SRC=DST (repeatable)")
    parser.add_argument("--priority-map", action="append", help="Priority mapping SRC=DST (repeatable)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")

    args = parser.parse_args()

    # Parse custom mappings
    custom_mapping = None
    if args.mapping:
        custom_mapping = {}
        for m in args.mapping:
            col, field = m.split("=", 1)
            custom_mapping[col] = field

    status_map = None
    if args.status_map:
        status_map = {}
        for m in args.status_map:
            src, dst = m.split("=", 1)
            status_map[src.lower()] = dst

    priority_map = None
    if args.priority_map:
        priority_map = {}
        for m in args.priority_map:
            src, dst = m.split("=", 1)
            priority_map[src.lower()] = dst

    result = import_csv(
        filepath=args.file,
        vault_path=args.vault,
        project_name=args.project,
        delimiter=args.delimiter,
        custom_mapping=custom_mapping,
        status_map=status_map,
        priority_map=priority_map,
        dry_run=args.dry_run,
    )

    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
