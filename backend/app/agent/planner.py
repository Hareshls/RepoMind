from pathlib import Path
from typing import List, Dict, Any

class Planner:
    PRIORITY_1_FILES = {
        "readme.md", "pyproject.toml", "requirements.txt", "package.json",
        "setup.py", "cargo.toml", "go.mod", "dockerfile", "docker-compose.yml",
        ".env.example"
    }

    PRIORITY_2_FILES = {
        "main.py", "app.py", "index.py", "manage.py", "server.py",
        "index.js", "index.ts", "app.js", "app.ts", "cli.py", "wsgi.py", "asgi.py"
    }

    def plan(self, files: List[Path], max_files: int = 50) -> List[Dict[str, Any]]:
        """Rank and select files to read based on priority rules."""
        planned: List[Dict[str, Any]] = []
        
        for file_path in files:
            path_str = str(file_path).replace("\\", "/")
            name_lower = file_path.name.lower()
            
            if name_lower in self.PRIORITY_1_FILES or (file_path.parent == Path(".") and "readme" in name_lower):
                planned.append({
                    "path": path_str,
                    "priority": 1,
                    "reason": "Project overview or configuration"
                })
            elif name_lower in self.PRIORITY_2_FILES or any(ep in path_str.lower() for ep in ["/main.", "/app.", "/index.", "/server.", "/cli."]):
                planned.append({
                    "path": path_str,
                    "priority": 2,
                    "reason": "Application entry point"
                })
            elif any(mod in path_str.lower() for mod in ["model", "route", "api", "service", "controller", "view", "schema", "config", "setting", "core", "client"]):
                planned.append({
                    "path": path_str,
                    "priority": 3,
                    "reason": "Core module or architecture"
                })
            elif file_path.suffix.lower() in {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".rb", ".php", ".cs", ".cpp", ".c", ".h"}:
                planned.append({
                    "path": path_str,
                    "priority": 4,
                    "reason": "Source code file"
                })
            else:
                planned.append({
                    "path": path_str,
                    "priority": 5,
                    "reason": "Supporting file"
                })

        planned.sort(key=lambda x: (x["priority"], len(x["path"]), x["path"]))
        return planned[:max_files]
