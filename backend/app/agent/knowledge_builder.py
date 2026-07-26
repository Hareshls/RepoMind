import json
import re
from typing import List, Dict, Any, Optional
from app.services.llm import LLMService
from app.services.embeddings import EmbeddingService

class KnowledgeBuilder:
    def __init__(self, llm_service: Optional[LLMService] = None, embedding_service: Optional[EmbeddingService] = None):
        self.llm = llm_service or LLMService()
        self.embedder = embedding_service or EmbeddingService()

    def build_knowledge(self, repo_url: str, read_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Transform raw file contents into structured knowledge and searchable chunks."""
        language = self._detect_language(read_results)
        dependencies = self._extract_dependencies(read_results)
        framework = self._detect_framework(read_results, dependencies)
        entry_point = self._detect_entry_point(read_results)
        architecture = self._determine_architecture(read_results, framework)
        key_modules = self._extract_key_modules(read_results)
        chunks = self._generate_chunks(read_results)

        # Optional LLM refinement if API key is available
        prompt = (
            f"Analyze this repository: {repo_url}.\n"
            f"Detected Language: {language}\n"
            f"Detected Framework: {framework}\n"
            f"Dependencies: {', '.join(dependencies[:20])}\n"
            f"Entry Point: {entry_point}\n"
            f"Please return a brief 1-2 sentence architecture description if you can improve upon: '{architecture}'."
        )
        llm_arch = self.llm.complete(prompt)
        if llm_arch and len(llm_arch.strip()) > 10:
            architecture = llm_arch.strip()

        return {
            "repo_url": str(repo_url),
            "language": language,
            "framework": framework,
            "entry_point": entry_point,
            "dependencies": dependencies,
            "architecture": architecture,
            "key_modules": key_modules,
            "chunks": chunks
        }

    def _detect_language(self, files: List[Dict[str, Any]]) -> str:
        ext_counts: Dict[str, int] = {}
        for f in files:
            path = f["path"]
            if "." in path:
                ext = path.rsplit(".", 1)[-1].lower()
                ext_counts[ext] = ext_counts.get(ext, 0) + 1
        
        if ext_counts.get("py", 0) >= ext_counts.get("js", 0) and "py" in ext_counts:
            return "Python"
        elif ext_counts.get("ts", 0) > 0 or ext_counts.get("js", 0) > 0:
            return "JavaScript/TypeScript"
        elif "go" in ext_counts:
            return "Go"
        elif "rs" in ext_counts:
            return "Rust"
        elif "java" in ext_counts:
            return "Java"
        return "Python" if not ext_counts else f"Multi-language ({', '.join(list(ext_counts.keys())[:3])})"

    def _extract_dependencies(self, files: List[Dict[str, Any]]) -> List[str]:
        deps: set = set()
        for f in files:
            path = f["path"].lower()
            content = f["content"]
            if "requirements" in path and path.endswith(".txt"):
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        dep = re.split(r"[=><~]", line)[0].strip()
                        if dep:
                            deps.add(dep)
            elif "pyproject.toml" in path:
                dep_blocks = re.findall(r'(?:dependencies|requires)\s*=\s*\[(.*?)\]', content, re.DOTALL)
                for block in dep_blocks:
                    items = re.findall(r'[\'"]([a-zA-Z0-9_\-]+)[^\'"]*[\'"]', block)
                    for item in items:
                        if len(item) > 1 and not item.startswith("-"):
                            deps.add(item)
                if "[tool.poetry.dependencies]" in content:
                    poetry_section = content.split("[tool.poetry.dependencies]")[1].split("[")[0]
                    for line in poetry_section.splitlines():
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            pkg = line.split("=")[0].strip()
                            if pkg != "python":
                                deps.add(pkg)

            elif "package.json" in path:
                try:
                    data = json.loads(content)
                    for key in ["dependencies", "devDependencies", "peerDependencies"]:
                        if key in data and isinstance(data[key], dict):
                            deps.update(data[key].keys())
                except Exception:
                    pass
            elif "go.mod" in path:
                for line in content.splitlines():
                    if "/" in line and not line.strip().startswith("module"):
                        parts = line.strip().split()
                        if parts:
                            deps.add(parts[0])
        return sorted(list(deps))

    def _detect_framework(self, files: List[Dict[str, Any]], dependencies: List[str]) -> str:
        deps_lower = {d.lower() for d in dependencies}
        combined_text = " ".join([f["content"][:2000].lower() for f in files[:10]])
        
        if "fastapi" in deps_lower or "fastapi" in combined_text:
            return "FastAPI"
        elif "django" in deps_lower or "django" in combined_text:
            return "Django"
        elif "flask" in deps_lower or "flask" in combined_text:
            return "Flask"
        elif "next" in deps_lower or "next.js" in combined_text:
            return "Next.js"
        elif "react" in deps_lower or "react" in combined_text:
            return "React"
        elif "express" in deps_lower or "express" in combined_text:
            return "Express"
        elif "spring" in combined_text or "spring-boot" in deps_lower:
            return "Spring Boot"
        elif "gin" in deps_lower or "fiber" in deps_lower:
            return "Go Web Framework (Gin/Fiber)"
        return "Standard Library / General Purpose SDK"

    def _detect_entry_point(self, files: List[Dict[str, Any]]) -> str:
        candidates = ["main.py", "app.py", "server.py", "index.py", "cli.py", "manage.py", "index.js", "index.ts", "src/main.py", "src/app.py"]
        file_paths = [f["path"] for f in files]
        
        for cand in candidates:
            for fp in file_paths:
                if fp.lower().endswith(cand):
                    return fp
        
        for f in files:
            content = f["content"]
            if "__main__" in content or "FastAPI()" in content or "app.listen(" in content:
                return f["path"]
        
        return file_paths[0] if file_paths else "Unknown"

    def _determine_architecture(self, files: List[Dict[str, Any]], framework: str) -> str:
        file_paths = [f["path"].lower() for f in files]
        has_models = any("model" in p or "schema" in p for p in file_paths)
        has_routes = any("route" in p or "api" in p or "controller" in p or "view" in p for p in file_paths)
        has_services = any("service" in p or "core" in p or "manager" in p for p in file_paths)
        
        if has_models and has_routes and has_services:
            return f"{framework} layered architecture with separated models, API routes, and business services."
        elif has_routes and has_models:
            return f"{framework} API architecture with route controllers and data models."
        elif any("cli" in p for p in file_paths):
            return f"Command-Line Interface (CLI) application."
        elif any("test" in p for p in file_paths) and not has_routes:
            return f"Library or SDK package with unit tests."
        return f"Modular {framework} software project."

    def _extract_key_modules(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        modules = []
        for f in files[:15]:
            path = f["path"]
            name = path.rsplit("/", 1)[-1] if "/" in path else path
            if name.endswith(".py"):
                role = "Python module handling logic, routing, or services."
            elif name.endswith((".js", ".jsx", ".ts", ".tsx")):
                role = "JavaScript/React frontend application module or component."
            elif name.endswith(".html"):
                role = "HTML structure and UI layout definition."
            elif name.endswith(".css"):
                role = "Stylesheet defining styling tokens and visual aesthetics."
            elif name.lower() in {"package.json", "pyproject.toml", "requirements.txt", "go.mod", "cargo.toml"}:
                role = "Project configuration and dependency manifest."
            else:
                role = "Core project source file."
            modules.append({
                "path": path,
                "summary": role
            })
        return modules

    def _generate_chunks(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        for f in files:
            path = f["path"]
            text = f["content"]
            split_chunks = self.embedder.chunk_text(text, max_size=500, overlap=80)
            for idx, chunk_text in enumerate(split_chunks):
                chunks.append({
                    "id": f"{path}_chunk_{idx}",
                    "path": path,
                    "text": chunk_text
                })
        return chunks
