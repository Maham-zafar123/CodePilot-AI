"""Rule-based security scanner for CodePilot AI.
This is intentionally local/offline, so it works even before calling an LLM.
"""
from __future__ import annotations

import re
from typing import Dict, List

Finding = Dict[str, str | int]

SECURITY_RULES = [
    {
        "issue": "Possible exposed API key/token",
        "severity": "Critical",
        "pattern": re.compile(r"(?i)(api[_-]?key|secret|token|access[_-]?token)\s*[:=]\s*['\"][A-Za-z0-9_\-\.]{16,}['\"]"),
        "recommendation": "Move secrets to .env, rotate the leaked key, and never commit secrets to Git.",
    },
    {
        "issue": "Hardcoded password",
        "severity": "Critical",
        "pattern": re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{4,}['\"]"),
        "recommendation": "Use environment variables or a secret manager instead of hardcoding passwords.",
    },
    {
        "issue": "Unsafe eval() usage",
        "severity": "High",
        "pattern": re.compile(r"\beval\s*\("),
        "recommendation": "Avoid eval(). Use safe parsers such as json.loads, ast.literal_eval, or explicit logic.",
    },
    {
        "issue": "Unsafe exec() usage",
        "severity": "High",
        "pattern": re.compile(r"\bexec\s*\("),
        "recommendation": "Avoid exec(). Refactor to normal functions or controlled command dispatch.",
    },
    {
        "issue": "Possible SQL injection",
        "severity": "High",
        "pattern": re.compile(r"(?i)(execute|query)\s*\(.*(%|\.format\(|f['\"])"),
        "recommendation": "Use parameterized queries, prepared statements, or ORM-safe filters.",
    },
    {
        "issue": "Unsafe pickle deserialization",
        "severity": "High",
        "pattern": re.compile(r"\bpickle\.loads?\s*\("),
        "recommendation": "Never unpickle untrusted data. Use JSON or a signed/validated format.",
    },
    {
        "issue": "Shell command injection risk",
        "severity": "High",
        "pattern": re.compile(r"subprocess\.(call|run|Popen).*shell\s*=\s*True"),
        "recommendation": "Avoid shell=True. Pass commands as a list and validate all user input.",
    },
    {
        "issue": "Debug mode enabled",
        "severity": "Medium",
        "pattern": re.compile(r"(?i)(debug\s*=\s*True|app\.run\(.*debug\s*=\s*True)"),
        "recommendation": "Disable debug mode in production.",
    },
    {
        "issue": "CORS allows all origins",
        "severity": "Medium",
        "pattern": re.compile(r"(?i)(allow_origins\s*=\s*\[\s*['\"]\*['\"]|Access-Control-Allow-Origin.*\*)"),
        "recommendation": "Restrict CORS to trusted domains only.",
    },
]


def _masked_code(line: str) -> str:
    line = re.sub(r"(['\"])[A-Za-z0-9_\-\.]{12,}(['\"])", r"\1***masked***\2", line)
    return line.strip()[:220]


def scan_security(files: List[dict]) -> List[Finding]:
    findings: List[Finding] = []
    for file in files:
        for line_no, line in enumerate(file["content"].splitlines(), start=1):
            for rule in SECURITY_RULES:
                if rule["pattern"].search(line):
                    findings.append({
                        "file": file["path"],
                        "line": line_no,
                        "issue": rule["issue"],
                        "severity": rule["severity"],
                        "code": _masked_code(line),
                        "recommendation": rule["recommendation"],
                    })
    return findings


def security_score(findings: List[Finding]) -> int:
    score = 100
    weights = {"Critical": 25, "High": 15, "Medium": 8, "Low": 3}
    for finding in findings:
        score -= weights.get(str(finding.get("severity")), 5)
    return max(score, 0)
