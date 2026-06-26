"""Optional multi-agent workflow.
If LangGraph is not installed, this module still provides a simple sequential fallback.
"""
from __future__ import annotations

from backend.analyzer import summarize_project
from backend.bug_detector import scan_bugs, bug_score
from backend.security_scan import scan_security, security_score
from backend.diagram_generator import generate_mermaid_diagram
from backend.refactor import suggest_refactoring


def run_engineer_review(project_name, project_path, files):
    security = scan_security(files)
    bugs = scan_bugs(files)
    diagram = generate_mermaid_diagram(files)
    refactor = suggest_refactoring(files)
    overview = summarize_project(project_path, files)

    return {
        "project_name": project_name,
        "quality_score": bug_score(bugs),
        "security_score": security_score(security),
        "security_findings": security,
        "bug_findings": bugs,
        "diagram": diagram,
        "overview": overview,
        "refactor_suggestions": refactor,
    }
