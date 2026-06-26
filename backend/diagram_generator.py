from __future__ import annotations

import re
from collections import defaultdict
from backend.llm import call_llm


def build_dependency_edges(files):
    module_to_path = {}
    for f in files:
        if f["extension"] == ".py":
            module = f["path"].replace("/", ".").replace("\\", ".").removesuffix(".py")
            module_to_path[module] = f["path"]
            module_to_path[module.split(".")[-1]] = f["path"]

    edges = set()
    for f in files:
        if f["extension"] != ".py":
            continue
        for line in f["content"].splitlines():
            m1 = re.match(r"\s*import\s+([a-zA-Z0-9_\.]+)", line)
            m2 = re.match(r"\s*from\s+([a-zA-Z0-9_\.]+)\s+import", line)
            mod = (m1 or m2).group(1) if (m1 or m2) else None
            if mod:
                target = module_to_path.get(mod) or module_to_path.get(mod.split(".")[-1])
                if target and target != f["path"]:
                    edges.add((f["path"], target))
    return sorted(edges)


def generate_static_mermaid(files):
    edges = build_dependency_edges(files)
    if not edges:
        groups = defaultdict(list)
        for f in files[:60]:
            folder = f["path"].split("/")[0].split("\\")[0]
            groups[folder].append(f["path"])
        lines = ["```mermaid", "graph TD", "    A[Uploaded Project]"]
        for i, folder in enumerate(groups.keys()):
            node = f"F{i}"
            lines.append(f"    A --> {node}[{folder}]")
        lines.append("```")
        return "\n".join(lines)

    node_ids = {}
    def node(path):
        if path not in node_ids:
            node_ids[path] = f"N{len(node_ids)}"
        return node_ids[path]

    lines = ["```mermaid", "graph TD"]
    for source, target in edges[:80]:
        lines.append(f"    {node(source)}[{source}] --> {node(target)}[{target}]")
    lines.append("```")
    return "\n".join(lines)


def generate_mermaid_diagram(files):
    static = generate_static_mermaid(files)
    paths = "\n".join([f"{f['path']} - {f['lines']} lines" for f in files[:100]])
    prompt = f"""
Create a clean Mermaid architecture flowchart for this project.
Use the file list and dependency hints below.
Return only Mermaid code inside a mermaid code block.

Files:
{paths}

Dependency hints:
{static}
"""
    result = call_llm(prompt)
    if "Gemini API key is missing" in result or "OpenAI API key is missing" in result:
        return static
    return result
