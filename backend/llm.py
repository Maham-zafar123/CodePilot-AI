from backend.config import AI_PROVIDER, AI_MODEL, GEMINI_API_KEY, OPENAI_API_KEY

SYSTEM_PROMPT = """You are CodePilot AI, an expert software engineer. Be accurate, practical, and concise.
When code context is provided, answer only using that context unless clearly stated otherwise.
Give file names and actionable steps when possible.
"""


def call_llm(prompt: str, temperature: float = 0.2) -> str:
    """Call Gemini or OpenAI. Falls back to a helpful message if no key is configured."""
    if AI_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            return "OpenAI API key is missing. Add OPENAI_API_KEY in .env."
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=AI_MODEL or "gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    if not GEMINI_API_KEY:
        return "Gemini API key is missing. Add GEMINI_API_KEY in .env."
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(AI_MODEL or "gemini-2.5-flash", system_instruction=SYSTEM_PROMPT)
    response = model.generate_content(prompt, generation_config={"temperature": temperature})
    return getattr(response, "text", "") or "No response generated."
