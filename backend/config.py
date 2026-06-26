from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = ROOT_DIR / "uploads"
REPO_DIR = ROOT_DIR / "repositories"
VECTOR_DIR = ROOT_DIR / "vector_store"
REPORT_DIR = ROOT_DIR / "generated_reports"
DIAGRAM_DIR = ROOT_DIR / "diagrams"

for directory in [UPLOAD_DIR, REPO_DIR, VECTOR_DIR, REPORT_DIR, DIAGRAM_DIR]:
    directory.mkdir(exist_ok=True)

AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()
AI_MODEL = os.getenv("AI_MODEL", "gemini-1.5-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h", ".hpp",
    ".cs", ".go", ".rs", ".php", ".rb", ".html", ".css", ".json", ".yaml",
    ".yml", ".md", ".txt", ".sql", ".env", ".toml", ".ini"
}

IGNORE_DIRS = {
    ".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build", ".next",
    ".idea", ".vscode", "target", "vendor", "coverage"
}
