from pathlib import Path
from collections import Counter
from backend.config import ALLOWED_EXTENSIONS, IGNORE_DIRS


def is_valid_file(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return False
    return path.suffix.lower() in ALLOWED_EXTENSIONS and path.is_file()


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def collect_code_files(project_path: Path):
    files = []
    for path in project_path.rglob("*"):
        if is_valid_file(path):
            text = read_file(path)
            if text.strip():
                files.append({
                    "path": str(path.relative_to(project_path)),
                    "absolute_path": str(path),
                    "extension": path.suffix.lower(),
                    "content": text,
                    "lines": len(text.splitlines()),
                })
    return files


def project_stats(files):
    ext_counter = Counter(f["extension"] for f in files)
    total_lines = sum(f["lines"] for f in files)
    return {
        "total_files": len(files),
        "total_lines": total_lines,
        "languages": dict(ext_counter.most_common()),
    }


def folder_tree(project_path: Path, max_items: int = 250) -> str:
    lines = []
    count = 0
    for path in sorted(project_path.rglob("*")):
        if count >= max_items:
            lines.append("... tree truncated ...")
            break
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        rel = path.relative_to(project_path)
        depth = len(rel.parts) - 1
        lines.append("  " * depth + ("📁 " if path.is_dir() else "📄 ") + path.name)
        count += 1
    return "\n".join(lines)
