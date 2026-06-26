from __future__ import annotations

from backend.llm import call_llm


def generate_tests(files, framework="pytest", max_files=8):
    selected = [f for f in files if f["extension"] in [".py", ".js", ".ts", ".jsx", ".tsx"]][:max_files]
    if not selected:
        return "No Python/JavaScript/TypeScript files found for test generation."

    sample = "\n\n".join([f"FILE: {f['path']}\n```{f['extension']}\n{f['content'][:2200]}\n```" for f in selected])
    prompt = f"""
You are a senior QA automation engineer.
Generate useful unit tests using {framework} for the code below.

Requirements:
- Return suggested test file paths.
- Include complete runnable test code blocks.
- Cover normal cases, edge cases, and error cases.
- Use mocks where external APIs, files, databases, or network calls are used.
- Do not invent dependencies unless necessary.
- Add a short command for running the tests.

Code:
{sample}
"""
    return call_llm(prompt)


def generate_test_plan(files):
    paths = "\n".join(f"- {f['path']} ({f['lines']} lines)" for f in files[:80])
    prompt = f"""
Create a practical testing strategy for this project.
Include:
- Most important files to test first
- Unit test ideas
- Integration test ideas
- Edge cases
- Suggested test folder structure

Files:
{paths}
"""
    return call_llm(prompt)
