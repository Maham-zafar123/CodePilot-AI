from __future__ import annotations

from pathlib import Path
from backend.config import REPORT_DIR


def save_markdown_report(project_name: str, title: str, content: str) -> Path:
    safe_title = title.lower().replace(" ", "_").replace("/", "_")
    path = REPORT_DIR / f"{project_name}_{safe_title}.md"
    path.write_text(f"# {title}\n\n{content}", encoding="utf-8")
    return path


def build_full_report(review: dict) -> str:
    return f"""# CodePilot AI Full Engineering Review

## Scores

- Code Quality Score: {review['quality_score']}/100
- Security Score: {review['security_score']}/100

## Project Overview

{review['overview']}

## Security Findings

{review['security_findings']}

## Bug / Quality Findings

{review['bug_findings']}

## Architecture Diagram

{review['diagram']}

## Refactoring Suggestions

{review['refactor_suggestions']}
"""
