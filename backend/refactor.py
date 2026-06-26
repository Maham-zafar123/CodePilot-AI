from __future__ import annotations

from backend.bug_detector import scan_bugs
from backend.llm import call_llm


def suggest_refactoring(files):
    issues = scan_bugs(files)[:30]
    sample = "\n\n".join([f"FILE: {f['path']}\n{f['content'][:1600]}" for f in files[:12]])
    prompt = f"""
You are a senior software architect. Review this codebase and suggest refactoring improvements.

Focus on:
- Project structure
- Readability
- Duplicate code
- Large functions/classes
- Error handling
- Performance
- Clean architecture
- Maintainability

Static scan issues:
{issues}

Code sample:
{sample}

Return prioritized suggestions with file names, reason, and concrete fix.
"""
    return call_llm(prompt)
