from pathlib import Path
from git import Repo
from backend.config import REPO_DIR


def clone_repo(repo_url: str) -> Path:
    name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
    target = REPO_DIR / name
    if target.exists():
        return target
    Repo.clone_from(repo_url, target)
    return target
