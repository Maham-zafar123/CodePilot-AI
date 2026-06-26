from backend.llm import call_llm
from backend.parser import project_stats, folder_tree


def summarize_project(project_path, files):
    sample = "\n\n".join([f"FILE: {f['path']}\n{f['content'][:1200]}" for f in files[:12]])
    stats = project_stats(files)
    tree = folder_tree(project_path)
    prompt = f"""
Analyze this software project.

Stats: {stats}

Folder tree:
{tree}

Sample files:
{sample}

Return:
- Project purpose
- Tech stack
- Main entry points
- Important folders
- Architecture explanation
- How a new developer should start
"""
    return call_llm(prompt)
