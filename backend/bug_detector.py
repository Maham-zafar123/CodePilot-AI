"""Static bug and maintainability scanner."""
from __future__ import annotations

import ast
import re
from collections import Counter
from typing import Dict, List

Issue = Dict[str, str | int]


def _issue(file: str, line: int, issue: str, severity: str, details: str) -> Issue:
    return {"file": file, "line": line, "issue": issue, "severity": severity, "details": details}


def scan_python_ast(file: dict) -> List[Issue]:
    issues: List[Issue] = []
    try:
        tree = ast.parse(file["content"])
    except SyntaxError as e:
        return [_issue(file["path"], e.lineno or 1, "Python syntax error", "High", str(e))]

    imports: Dict[str, int] = {}
    used_names = set()
    function_names = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used_names.add(node.id)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports[alias.asname or alias.name.split(".")[0]] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports[alias.asname or alias.name] = node.lineno
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_names.append(node.name)
            length = (getattr(node, "end_lineno", node.lineno) or node.lineno) - node.lineno + 1
            if length > 80:
                issues.append(_issue(file["path"], node.lineno, "Large function", "Medium", f"Function '{node.name}' has {length} lines. Split it into smaller functions."))
            if len(node.args.args) > 6:
                issues.append(_issue(file["path"], node.lineno, "Too many parameters", "Low", f"Function '{node.name}' has many parameters. Consider a config object/dataclass."))
            has_try = any(isinstance(child, ast.Try) for child in ast.walk(node))
            risky_calls = [n for n in ast.walk(node) if isinstance(n, ast.Call) and getattr(getattr(n, "func", None), "attr", "") in {"open", "read", "write", "request", "get", "post"}]
            if risky_calls and not has_try:
                issues.append(_issue(file["path"], node.lineno, "Missing error handling", "Low", f"Function '{node.name}' appears to do I/O/network work without try/except."))

        elif isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append(_issue(file["path"], node.lineno, "Bare except", "Medium", "Catch specific exception classes instead of using bare except."))

    for name, line in imports.items():
        if name not in used_names and name != "__future__":
            issues.append(_issue(file["path"], line, "Possibly unused import", "Low", f"'{name}' is imported but not used in this file."))

    duplicates = [name for name, count in Counter(function_names).items() if count > 1]
    for name in duplicates:
        issues.append(_issue(file["path"], 1, "Duplicate function name", "Medium", f"Function '{name}' is defined more than once."))

    return issues


def scan_bugs(files: List[dict]) -> List[Issue]:
    issues: List[Issue] = []
    for file in files:
        content = file["content"]
        ext = file["extension"]
        if ext == ".py":
            issues.extend(scan_python_ast(file))

        for line_no, line in enumerate(content.splitlines(), start=1):
            if "TODO" in line or "FIXME" in line:
                issues.append(_issue(file["path"], line_no, "TODO/FIXME found", "Low", "Unfinished work marker found."))
            if re.search(r"print\s*\(.+(password|token|secret|key)", line, re.I):
                issues.append(_issue(file["path"], line_no, "Sensitive value may be logged", "High", "Avoid printing secrets or credentials."))
            if ext in {".js", ".ts", ".jsx", ".tsx"} and "console.log" in line:
                issues.append(_issue(file["path"], line_no, "Console log left in code", "Low", "Remove debug console logs before production."))
            if len(line) > 140:
                issues.append(_issue(file["path"], line_no, "Very long line", "Low", "Long lines reduce readability."))
    return issues


def bug_score(issues: List[Issue]) -> int:
    score = 100
    weights = {"High": 12, "Medium": 7, "Low": 2}
    for item in issues:
        score -= weights.get(str(item.get("severity")), 3)
    return max(score, 0)
