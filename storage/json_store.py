"""Storage module for JSON data."""

import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional, cast

import config


def ensure_directories() -> None:
    """Ensure all required directories exist."""
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.DAILY_DIR.mkdir(parents=True, exist_ok=True)
    config.HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def load_projects() -> Dict[str, Dict[str, Any]]:
    """Load projects data from JSON file.
    
    Returns:
        Dictionary mapping full_name to project data.
    """
    if not config.PROJECTS_FILE.exists():
        return {}
    
    with open(config.PROJECTS_FILE, "r", encoding="utf-8") as f:
        return cast(Dict[str, Dict[str, Any]], json.load(f))
        return json.load(f)


def save_projects(projects: Dict[str, Dict[str, Any]]) -> None:
    """Save projects data to JSON file.
    
    Args:
        projects: Dictionary mapping full_name to project data.
    """
    ensure_directories()
    with open(config.PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)


def update_project(full_name: str, data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Update a single project in the data store.
    
    Args:
        full_name: Project full name (e.g., "owner/repo").
        data: Project data to merge/update.
    
    Returns:
        Updated projects dictionary.
    """
    projects = load_projects()
    
    if full_name in projects:
        # Merge with existing data, preserving history
        existing = projects[full_name]
        if "history" not in existing:
            existing["history"] = []
        existing["history"].append({
            "date": str(date.today()),
            "stars": existing.get("stars", 0),
            "forks": existing.get("forks", 0),
        })
        projects[full_name] = {**existing, **data}
    else:
        projects[full_name] = data
    
    save_projects(projects)
    return projects


def get_daily_report_path(report_date: date) -> Path:
    """Get path for daily report file.
    
    Args:
        report_date: Date for the report.
    
    Returns:
        Path to the report file.
    """
    return config.DAILY_DIR / f"{report_date}.md"


def save_daily_report(content: str, report_date: Optional[date] = None) -> Path:
    """Save daily report to file.
    
    Args:
        content: Report content in Markdown format.
        report_date: Date for the report. Defaults to today.
    
    Returns:
        Path to the saved report file.
    """
    if report_date is None:
        report_date = date.today()
    
    ensure_directories()
    report_path = get_daily_report_path(report_date)
    report_path.write_text(content, encoding="utf-8")
    return report_path
