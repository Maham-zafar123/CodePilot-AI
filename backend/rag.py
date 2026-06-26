from backend.vector_db import search_project
from backend.llm import call_llm


def ask_codebase(project_name: str, question: str) -> str:
    results = search_project(project_name, question)
    context_parts = []
    for text, meta in results:
        context_parts.append(f"FILE: {meta.get('path')}\nCODE:\n{text}")
    context = "\n\n---\n\n".join(context_parts)
    prompt = f"""
Answer the question using the code context.

Question:
{question}

Code context:
{context}

Answer with:
1. Direct answer
2. Relevant files
3. Explanation
4. Suggested next step if useful
"""
    return call_llm(prompt)
