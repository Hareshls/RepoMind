import os
from pathlib import Path
from typing import List, Set

class Explorer:
    IGNORED_DIRS: Set[str] = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        ".venv",
        "venv",
        ".env",
        ".idea",
        ".vscode",
        "dist",
        "build",
        ".mypy_cache",
        ".eggs",
    }

    IGNORED_EXTENSIONS: Set[str] = {
        ".pyc", ".pyo", ".exe", ".dll", ".so", ".dylib",
        ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
        ".zip", ".tar", ".gz", ".7z", ".rar",
        ".pdf", ".docx", ".xlsx", ".sqlite", ".db", ".pack", ".idx",
        ".lock"
    }

    IGNORED_FILES: Set[str] = {
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "poetry.lock",
        "cargo.lock",
        "gemfile.lock",
        "go.sum",
        "composer.lock",
        "npm-debug.log",
        "yarn-debug.log",
        "yarn-error.log",
        ".ds_store",
        "thumbs.db"
    }

    def discover(self, repo_path: Path) -> List[Path]:
        """Walk through repository directory and discover relevant file paths relative to repo root."""
        repo_path = Path(repo_path).resolve()
        discovered: List[Path] = []
        
        if not repo_path.exists() or not repo_path.is_dir():
            return discovered

        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in self.IGNORED_DIRS and not d.endswith(".egg-info")]
            
            root_path = Path(root)
            for file_name in files:
                file_path = root_path / file_name
                if file_name.startswith(".") and file_name not in {".env.example", ".gitignore", ".dockerignore"}:
                    continue
                if file_name.lower() in self.IGNORED_FILES or file_path.suffix.lower() in self.IGNORED_EXTENSIONS:
                    continue
                
                try:
                    rel_path = file_path.relative_to(repo_path)
                    discovered.append(rel_path)
                except ValueError:
                    pass

        return sorted(discovered)
