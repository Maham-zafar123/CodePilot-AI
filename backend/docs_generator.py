from __future__ import annotations

from backend.llm import call_llm
from backend.parser import project_stats, folder_tree
from backend.config import REPORT_DIR


def _sample(files, limit=12, chars=1200):
    return "\n\n".join([f"FILE: {f['path']}\n{f['content'][:chars]}" for f in files[:limit]])


def generate_readme(project_name, project_path, files):
    prompt = f"""
Generate a professional README.md for this project.

Include:
- Title
- Overview
- Key features
- Tech stack
- Folder structure
- Installation
- Environment variables
- Usage
- Screenshots placeholder
- Future improvements

Project stats: {project_stats(files)}
Folder tree:\n{folder_tree(project_path)}
Sample files:\n{_sample(files)}
"""
    readme = call_llm(prompt)
    out = REPORT_DIR / f"{project_name}_README.md"
    out.write_text(readme, encoding="utf-8")
    return readme, out


def generate_developer_guide(project_name, project_path, files):
    prompt = f"""
Create a developer guide for a new engineer joining this project.
Explain:
- How the app starts
- Main modules and responsibilities
- Data flow
- Important functions/classes
- How to add a new feature
- How to debug common issues

Folder tree:\n{folder_tree(project_path)}
Sample files:\n{_sample(files, limit=15)}
"""
    guide = call_llm(prompt)
    out = REPORT_DIR / f"{project_name}_DEVELOPER_GUIDE.md"
    out.write_text(guide, encoding="utf-8")
    return guide, out
