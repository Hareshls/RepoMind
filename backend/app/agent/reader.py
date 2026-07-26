from pathlib import Path
from typing import List, Dict, Any

class Reader:
    def __init__(self, max_file_bytes: int = 100_000):
        self.max_file_bytes = max_file_bytes

    def read_files(self, repo_path: Path, planned_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Open selected files and extract text content."""
        repo_path = Path(repo_path).resolve()
        results: List[Dict[str, Any]] = []
        
        for item in planned_files:
            rel_path = item["path"]
            full_path = repo_path / rel_path
            
            if not full_path.exists() or not full_path.is_file():
                continue
            
            try:
                if full_path.stat().st_size > self.max_file_bytes:
                    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read(self.max_file_bytes) + "\n...[TRUNCATED]"
                else:
                    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                
                results.append({
                    "path": rel_path,
                    "content": content
                })
            except Exception:
                continue

        return results
