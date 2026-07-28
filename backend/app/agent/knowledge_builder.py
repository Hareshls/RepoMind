import json
import re
from typing import List, Dict, Any, Optional
from app.services.llm import LLMService
from app.services.embeddings import EmbeddingService

CONFIDENCE_THRESHOLD = 0.75


class KnowledgeBuilder:
    """
    Knowledge Agent — learns incrementally from one file at a time.
    LLM-First: all technology intelligence (frameworks, databases, auth, architecture,
    security, improvements, module summaries) is delegated to the LLM.
    Python code only reads files, extracts raw structural data, and validates JSON.
    Returns (knowledge, confidence, open_questions) after every file read.
    """

    def __init__(self, llm_service: Optional[LLMService] = None,
                 embedding_service: Optional[EmbeddingService] = None):
        self.llm = llm_service or LLMService()
        self.embedder = embedding_service or EmbeddingService()

    # ─────────────────────────────────────────────
    # Public: called once per file during the agent loop
    # ─────────────────────────────────────────────

    def learn_from_file(
        self,
        file: Dict[str, Any],
        current_knowledge: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Incrementally update raw structural knowledge from a single file.
        Technology-specific fields (framework, database, auth, architecture,
        security, improvements, module layer/summary) are left for the LLM
        to populate later in Phase 4 via analyze_repository_with_llm().
        Returns: { knowledge, confidence, open_questions }
        """
        updated = dict(current_knowledge)

        # ── Language detection: purely extension-based, no tech knowledge ──
        if not updated.get("language") or updated.get("language") in ["Unknown", "None"]:
            lang_val = self._detect_language([file])
            if lang_val and lang_val != "Unknown":
                updated["language"] = lang_val

        # ── Dependency extraction: format-aware manifest parsing ──
        new_deps = self._extract_dependencies([file])
        if new_deps:
            combined = list(set(updated.get("dependencies", []) + new_deps))
            updated["dependencies"] = sorted(combined)

        # ── Accumulate key modules: just record the path for LLM context ──
        module_entry = {"path": file["path"], "layer": "", "summary": ""}
        existing_modules = updated.get("key_modules", [])
        paths_seen = {m["path"] for m in existing_modules}
        if file["path"] not in paths_seen:
            existing_modules.append(module_entry)
        updated["key_modules"] = existing_modules[:20]

        # ── Structural data accumulation (regex-based, no tech knowledge) ──
        new_endpoints = self._detect_api_endpoints([file])
        if new_endpoints:
            seen = {(e["method"], e["path"]) for e in updated.get("api_endpoints", [])}
            combined_ep = list(updated.get("api_endpoints", []))
            for ep in new_endpoints:
                if (ep["method"], ep["path"]) not in seen:
                    combined_ep.append(ep)
                    seen.add((ep["method"], ep["path"]))
            updated["api_endpoints"] = combined_ep[:30]

        env_vars = self._detect_env_variables([file])
        if env_vars:
            updated["env_variables"] = sorted(list(set(updated.get("env_variables", []) + env_vars)))

        config_files = self._detect_config_files([file])
        if config_files:
            updated["config_files"] = sorted(list(set(updated.get("config_files", []) + config_files)))

        collections = self._detect_collections([file])
        if collections:
            updated["collections"] = sorted(list(set(updated.get("collections", []) + collections)))

        # ── Package manager detection: filename-only, zero tech knowledge ──
        p_lower = file["path"].lower()
        pm = ""
        if "package.json" in p_lower or "package-lock.json" in p_lower:
            pm = "npm"
        elif "pnpm-lock.yaml" in p_lower:
            pm = "pnpm"
        elif "yarn.lock" in p_lower:
            pm = "yarn"
        elif "requirements.txt" in p_lower or "pipfile" in p_lower:
            pm = "pip"
        elif "pyproject.toml" in p_lower or "poetry.lock" in p_lower:
            pm = "poetry"
        elif "pom.xml" in p_lower:
            pm = "maven"
        elif "build.gradle" in p_lower:
            pm = "gradle"
        elif "cargo.toml" in p_lower:
            pm = "cargo"
        elif "go.mod" in p_lower:
            pm = "go modules"
        elif "gemfile" in p_lower:
            pm = "bundler"
        elif "composer.json" in p_lower:
            pm = "composer"
        if pm:
            ts = updated.get("tech_stack", {})
            existing_pms = ts.get("package_managers", [])
            if pm not in existing_pms:
                existing_pms.append(pm)
            ts["package_managers"] = existing_pms
            ts["package_manager"] = pm
            updated["tech_stack"] = ts

        # ── Score confidence on raw structural data ──
        confidence = self._score_confidence(updated)
        open_questions = self._generate_open_questions(confidence)

        return {
            "knowledge": updated,
            "confidence": confidence,
            "open_questions": open_questions,
        }

    # ─────────────────────────────────────────────
    # Public: build knowledge from ALL files at once (full-pass fallback)
    # ─────────────────────────────────────────────

    def build_knowledge_from_all(
        self, repo_url: str, read_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Full-pass knowledge build — used if the agent loop is skipped."""
        knowledge: Dict[str, Any] = {}
        for file in read_results:
            result = self.learn_from_file(file, knowledge)
            knowledge = result["knowledge"]

        knowledge["language"] = self._detect_language(read_results)

        readme_content = self._get_readme_content(read_results)
        knowledge = self._llm_enrich(repo_url, knowledge, readme_content, read_results)

        if not knowledge.get("project_description"):
            knowledge["project_description"] = self._extract_fallback_description(
                read_results, knowledge.get("entry_point", "")
            )

        knowledge["chunks"] = self.generate_chunks(read_results)
        knowledge["suggested_improvements"] = self.generate_suggested_improvements(knowledge)
        knowledge["repo_url"] = str(repo_url)
        return knowledge

    # ─────────────────────────────────────────────
    # LLM-First Primary Analyzer
    # ─────────────────────────────────────────────

    def _llm_enrich(
        self, repo_url: str, knowledge: Dict[str, Any], readme_content: str,
        read_files: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        return self.analyze_repository_with_llm(repo_url, knowledge, readme_content, read_files)

    def analyze_repository_with_llm(
        self, repo_url: str, knowledge: Dict[str, Any], readme_content: str,
        read_files: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Primary LLM-first repository analyzer. Sends full repository context to the LLM
        and extracts a structured JSON object covering all technology intelligence:
        languages, frameworks, libraries, database, authentication, deployment,
        architecture, entry point, APIs, security, suggested improvements,
        and per-module layer/summary descriptions.
        Rule-based data (dependencies, file paths) is used only as context input.
        """
        dependencies = knowledge.get("dependencies", [])
        key_modules = knowledge.get("key_modules", [])

        folder_tree: set = set()
        file_paths: List[str] = []
        config_files_snippets = ""
        api_arch_snippets = ""
        entry_point_snippet = ""

        if read_files:
            file_paths = [f["path"] for f in read_files[:60]]
            for f in read_files:
                parts = f["path"].replace("\\", "/").split("/")
                if len(parts) > 1:
                    folder_tree.add(parts[0])

                p_lower = f["path"].lower()
                # Config / Manifest files — critical for LLM context
                if any(cfg in p_lower for cfg in [
                    "package.json", "pyproject.toml", "requirements.txt", "pom.xml",
                    "vite.config", "dockerfile", ".env.example", "tsconfig", "cargo.toml",
                    "go.mod", "build.gradle", "composer.json", "gemfile"
                ]):
                    config_files_snippets += f"--- CONFIG: {f['path']} ---\n{f['content'][:600]}\n\n"
                # Entry point files
                elif any(ep in p_lower for ep in [
                    "main.py", "index.js", "app.py", "app.tsx", "server.js",
                    "index.ts", "main.go", "main.rs", "main.java", "program.cs"
                ]):
                    if not entry_point_snippet:
                        entry_point_snippet = f"--- ENTRY POINT: {f['path']} ---\n{f['content'][:800]}\n\n"
                # Architecture / API files
                elif any(arch in p_lower for arch in [
                    "route", "view", "controller", "service", "model", "api", "handler",
                    "schema", "auth", "middleware", "database", "db"
                ]):
                    if len(api_arch_snippets) < 3000:
                        api_arch_snippets += f"--- ARCH/API: {f['path']} ---\n{f['content'][:600]}\n\n"

        module_paths = [m["path"] for m in key_modules[:20]]

        prompt = (
            f"You are analyzing this repository: {repo_url}\n\n"
            f"--- 1. FOLDER TREE & FILE STRUCTURE ---\n"
            f"Root Folders: {', '.join(sorted(list(folder_tree))) or 'Root directory'}\n"
            f"Discovered Files ({len(file_paths)}): {', '.join(file_paths[:60])}\n\n"
            f"--- 2. CONFIGURATION & MANIFESTS ---\n"
            f"Raw Dependencies Extracted: {', '.join(dependencies[:40])}\n"
            f"{config_files_snippets[:2000]}\n"
            f"--- 3. README ---\n"
            f"{readme_content[:2000] if readme_content else 'No README provided.'}\n\n"
            f"--- 4. ENTRY POINT ---\n"
            f"{entry_point_snippet or 'No explicit entry point file sampled.'}\n\n"
            f"--- 5. KEY MODULES ---\n"
            f"{', '.join(module_paths)}\n\n"
            f"--- 6. ARCHITECTURE, API & SCHEMA CODE ---\n"
            f"{api_arch_snippets[:3000]}\n\n"
        )

        prompt += (
            "INSTRUCTIONS: You are an authoritative Senior Staff Software Engineer. "
            "Analyze the repository above using ONLY the provided context. "
            "Do NOT fall back to generic templates. Be specific to THIS codebase. "
            "Detect any framework, database, auth method, or cloud platform — including "
            "modern ones like Hono, Elysia, Fresh, Nitro, Bun, Deno, Axum, Gleam, etc.\n\n"
            "Return ONLY a single valid JSON object with EXACTLY this structure:\n"
            "{\n"
            '  "project_description": "4-6 sentence executive summary specific to this codebase — what it does, its core logic, key features, and tech stack.",\n'
            '  "languages": ["list of programming languages detected"],\n'
            '  "frameworks": ["list of frameworks and runtimes"],\n'
            '  "libraries": ["list of key third-party libraries"],\n'
            '  "database": "primary database or ORM, e.g. MongoDB / Motor, PostgreSQL / SQLAlchemy",\n'
            '  "authentication": "authentication mechanism, e.g. JWT Bearer Token + bcrypt",\n'
            '  "deployment": "deployment platform/tools, e.g. Docker, Vercel, AWS Lambda",\n'
            '  "architecture": "2-3 sentence description of the architectural pattern",\n'
            '  "entry_point": "relative path to the primary application entry point file",\n'
            '  "environment_variables": ["list of env var names the project uses"],\n'
            '  "security_detected": ["list of security practices found, e.g. JWT Authentication, bcrypt, CORS, Rate Limiting, HTTPS"],\n'
            '  "security_missing": ["list of recommended security practices NOT found in the code"],\n'
            '  "suggested_improvements": ["3-6 specific, actionable improvement suggestions for this exact codebase"],\n'
            '  "module_details": {\n'
            '    "path/to/file.py": {"layer": "concise layer name e.g. Backend API Entry Point", "summary": "1-2 sentence specific description"}\n'
            "  }\n"
            "}\n"
            "Output ONLY valid JSON. No markdown, no explanation, no code fences."
        )

        llm_response = self.llm.complete(
            prompt,
            system_prompt=(
                "You are a Senior Staff Software Engineer and authoritative AI repository analyzer. "
                "You output ONLY valid JSON. Never output explanations or markdown."
            ),
        )

        try:
            if llm_response:
                clean = llm_response.strip()
                if clean.startswith("```"):
                    clean = re.sub(r"^```[a-z]*\n?", "", clean).rstrip("` \n")
                data = json.loads(clean)

                # ── 1. Project description & architecture ──
                if data.get("project_description"):
                    knowledge["project_description"] = data["project_description"]
                if data.get("architecture"):
                    knowledge["architecture"] = data["architecture"]
                if data.get("entry_point") and data["entry_point"] not in ("Unknown", "", None):
                    knowledge["entry_point"] = data["entry_point"]

                # ── 2. Full tech stack (LLM is authoritative) ──
                ts = knowledge.get("tech_stack", {})
                if not isinstance(ts, dict):
                    ts = {}

                if data.get("languages") and isinstance(data["languages"], list):
                    ts["languages"] = data["languages"]
                    if data["languages"]:
                        knowledge["language"] = data["languages"][0]

                if data.get("frameworks") and isinstance(data["frameworks"], list):
                    ts["frameworks"] = data["frameworks"]
                    if data["frameworks"]:
                        knowledge["framework"] = data["frameworks"][0]

                if data.get("libraries") and isinstance(data["libraries"], list):
                    ts["libraries"] = data["libraries"]

                null_values = {"none", "not detected", "null", "none detected", "n/a", ""}
                if data.get("database") and str(data["database"]).lower().strip() not in null_values:
                    knowledge["database"] = data["database"]
                    ts["databases"] = [data["database"]]

                if data.get("authentication") and str(data["authentication"]).lower().strip() not in null_values:
                    knowledge["authentication"] = data["authentication"]

                if data.get("deployment") and str(data["deployment"]).lower().strip() not in null_values:
                    ts["cloud_devops"] = [data["deployment"]]

                knowledge["tech_stack"] = ts

                # ── 3. Environment variables ──
                if data.get("environment_variables") and isinstance(data["environment_variables"], list):
                    existing_evs = set(knowledge.get("env_variables", []))
                    for ev in data["environment_variables"]:
                        if isinstance(ev, str) and ev.strip():
                            existing_evs.add(ev.strip())
                    knowledge["env_variables"] = sorted(list(existing_evs))

                # ── 4. Security (LLM-detected) ──
                if data.get("security_detected") and isinstance(data["security_detected"], list):
                    knowledge["security_detected"] = data["security_detected"]
                if data.get("security_missing") and isinstance(data["security_missing"], list):
                    knowledge["security_missing"] = data["security_missing"]

                # ── 5. Suggested improvements (LLM-generated) ──
                if data.get("suggested_improvements") and isinstance(data["suggested_improvements"], list):
                    knowledge["suggested_improvements"] = [
                        s for s in data["suggested_improvements"] if isinstance(s, str) and s.strip()
                    ][:6]

                # ── 6. Module layer + summary (LLM-generated per file) ──
                mod_details = data.get("module_details", {})
                if isinstance(mod_details, dict):
                    for m in knowledge.get("key_modules", []):
                        detail = mod_details.get(m["path"])
                        if detail and isinstance(detail, dict):
                            m["layer"] = detail.get("layer", m.get("layer", "Core Module"))
                            m["summary"] = detail.get("summary", m.get("summary", ""))

        except Exception as e:
            print(f"[KnowledgeBuilder] LLM analysis parse error — raw structural data preserved: {e}")

        # ── Structural fallback: populate fields from raw file structure ──
        # Runs when LLM is offline/unconfigured OR returned incomplete data.
        # Philosophy: Python knows NOTHING about specific technologies here.
        # It can only observe: file extensions, dependency names, URL patterns
        # in source code, and directory/filename conventions.
        # Fields that require technology intelligence (auth, security) are left
        # empty — the LLM is the only correct source for those.

        if read_files:
            deps = knowledge.get("dependencies", [])
            deps_lower = {d.lower() for d in deps}

            # ── Framework: report top non-trivial dependencies as the tech stack ──
            # Dependency names ARE framework names. We don't categorize them —
            # we just filter out known generic infrastructure packages that are
            # never frameworks (build tools, transport layers, type stubs, linters).
            # This skip-list contains ONLY packages that are definitively
            # infrastructure/utility and never the primary application framework.
            INFRA_SKIP_PREFIXES = (
                "@types/",        # TypeScript type definitions only
                "@typescript-eslint/",  # TS linter plugins
                "@babel/",        # JS transpiler plugins
                "@vitejs/plugin", # Vite build plugins
                "@eslint/",       # ESLint config packages
            )
            INFRA_SKIP_EXACT = {
                # Python build/transport/typing infrastructure
                "pip", "setuptools", "wheel", "six", "certifi", "urllib3",
                "charset-normalizer", "idna", "typing-extensions", "annotated-types",
                "anyio", "sniffio", "h11", "click", "httpx", "httpcore",
                # JS build/lint infrastructure
                "eslint", "eslint-plugin-react-hooks", "eslint-plugin-react-refresh",
                "prettier", "typescript",
                # Test runners (not frameworks)
                "jest", "vitest", "mocha", "chai", "jasmine", "pytest", "unittest2",
            }

            if not knowledge.get("framework"):
                tech_deps = [
                    d for d in deps
                    if d.lower() not in INFRA_SKIP_EXACT
                    and not any(d.lower().startswith(p) for p in INFRA_SKIP_PREFIXES)
                ]
                if tech_deps:
                    # Present all non-infrastructure deps — the LLM decides primary;
                    # without LLM we just report the top candidates
                    knowledge["framework"] = tech_deps[0]
                    ts = knowledge.get("tech_stack", {})
                    ts["frameworks"] = tech_deps[:5]
                    knowledge["tech_stack"] = ts

            # ── Database: detect from URL protocol strings in source code ──
            # These are literal connection strings, not package-name heuristics.
            # A URL protocol string like "mongodb://" is a factual observation
            # of what the code connects to, not a technology assumption.
            if not knowledge.get("database"):
                content_sample = " ".join(f["content"][:1200].lower() for f in read_files[:15])
                db = ""
                if "mongodb://" in content_sample or "mongodb+srv://" in content_sample:
                    db = "MongoDB"
                elif "postgresql://" in content_sample or "postgres://" in content_sample:
                    db = "PostgreSQL"
                elif "mysql://" in content_sample or "mysql+aiomysql://" in content_sample:
                    db = "MySQL"
                elif "sqlite:///" in content_sample:
                    db = "SQLite"
                elif "redis://" in content_sample or "rediss://" in content_sample:
                    db = "Redis"
                if db:
                    knowledge["database"] = db
                    ts = knowledge.get("tech_stack", {})
                    ts["databases"] = [db]
                    knowledge["tech_stack"] = ts

            # ── Authentication & Security: left empty without LLM ──
            # Cannot classify auth mechanisms without technology-specific knowledge.
            # The LLM is the only correct source. No guessing here.

            # ── Entry point: common file naming conventions ──
            # These are universal software conventions (main, index, app, server),
            # not framework-specific names. Approved by user as structural fallback.
            if not knowledge.get("entry_point"):
                ep_candidates = {
                    "main.py", "app.py", "server.py", "run.py",
                    "index.js", "index.ts", "index.jsx", "index.tsx",
                    "app.js", "app.ts", "server.js", "server.ts",
                    "main.go", "main.rs", "main.java", "main.cs",
                    "program.cs", "manage.py",
                }
                for f in read_files:
                    fname = f["path"].rsplit("/", 1)[-1].rsplit("\\", 1)[-1].lower()
                    if fname in ep_candidates:
                        knowledge["entry_point"] = f["path"]
                        break

            # ── Architecture: pure directory/file structure observation ──
            # Detects layering from folder names — approved by user as structural.
            # Folder names like "routes", "services", "models" are structural
            # conventions, not technology-specific knowledge.
            if not knowledge.get("architecture"):
                fps = [f["path"].lower() for f in read_files]
                has_routes   = any("route" in p or "api"        in p or "controller" in p for p in fps)
                has_models   = any("model" in p or "schema"     in p or "entit"      in p for p in fps)
                has_services = any("service" in p or "manager" in p or "core"       in p for p in fps)
                endpoint_count = len(knowledge.get("api_endpoints", []))
                schema_count   = len(knowledge.get("collections", []))
                if has_routes and has_models and has_services:
                    knowledge["architecture"] = (
                        "Layered architecture with separated API routes, data models, and business service logic."
                    )
                elif has_routes and has_models:
                    knowledge["architecture"] = (
                        "API architecture with route handlers and data model definitions."
                    )
                elif endpoint_count > 0:
                    knowledge["architecture"] = (
                        f"Web API application with {endpoint_count} detected endpoints"
                        + (f" and {schema_count} data schemas." if schema_count else ".")
                    )
                else:
                    knowledge["architecture"] = (
                        f"Software project using {knowledge.get('language', 'the detected language')}."
                    )

        return knowledge

    # ─────────────────────────────────────────────
    # Confidence Scoring (structural presence — no tech knowledge)
    # ─────────────────────────────────────────────

    def _score_confidence(self, knowledge: Dict[str, Any]) -> Dict[str, float]:
        lang = knowledge.get("language", "")
        fw = knowledge.get("framework", "")
        ep = knowledge.get("entry_point", "")
        arch = knowledge.get("architecture", "")
        db = knowledge.get("database", "")
        auth = knowledge.get("authentication", "")
        return {
            "language":       1.0 if lang and lang not in ("Unknown", "") else 0.0,
            "framework":      0.95 if fw and fw not in ("", "Unknown") else 0.15,
            "entry_point":    1.0 if ep and ep not in ("Unknown", "") else 0.0,
            "architecture":   0.9 if arch and len(arch) > 20 else (0.4 if arch else 0.0),
            "database":       1.0 if db and db.lower() not in ("none detected", "not detected", "none", "") else 0.85,
            "authentication": 1.0 if auth and auth.lower() not in ("none detected", "not detected", "none", "") else 0.85,
        }

    def _generate_open_questions(self, confidence: Dict[str, float]) -> List[str]:
        thresholds = {
            "database":       (0.5, "Which database or ORM is used?"),
            "authentication": (0.5, "How is authentication implemented?"),
            "architecture":   (0.5, "What is the main architectural pattern?"),
            "framework":      (0.5, "Which framework or runtime is used?"),
            "entry_point":    (0.5, "Where does the application start?"),
            "language":       (0.5, "What is the primary programming language?"),
        }
        return [q for dim, (t, q) in thresholds.items() if confidence.get(dim, 0.0) < t]

    def average_confidence(self, confidence: Dict[str, float]) -> float:
        return sum(confidence.values()) / len(confidence) if confidence else 0.0

    # ─────────────────────────────────────────────
    # Raw structural extractors (no tech knowledge)
    # ─────────────────────────────────────────────

    def _detect_language(self, files: List[Dict[str, Any]]) -> str:
        """Detects primary language from file extension counts — no hardcoded framework names."""
        ext_counts: Dict[str, int] = {}
        ignore_exts = {
            "json", "toml", "txt", "md", "lock", "mod", "yaml", "yml", "env",
            "html", "css", "scss", "less", "svg", "png", "jpg", "jpeg", "gif",
            "ico", "gitignore", "dockerfile", "csv", "tsv", "pdf", "docx",
            "config", "log", "map", "woff", "woff2", "ttf", "eot",
        }
        for f in files:
            path = f["path"]
            if "." in path:
                ext = path.rsplit(".", 1)[-1].lower()
                if ext not in ignore_exts:
                    ext_counts[ext] = ext_counts.get(ext, 0) + 1

        if not ext_counts:
            return "Unknown"

        # Map common extensions to display names
        ext_display = {
            "py": "Python", "pyw": "Python", "ipynb": "Jupyter Notebook (Python)",
            "js": "JavaScript", "mjs": "JavaScript", "cjs": "JavaScript",
            "ts": "TypeScript", "tsx": "TypeScript", "jsx": "JavaScript",
            "go": "Go", "rs": "Rust", "java": "Java", "cs": "C#",
            "cpp": "C++", "cc": "C++", "cxx": "C++", "c": "C",
            "rb": "Ruby", "php": "PHP", "kt": "Kotlin", "swift": "Swift",
            "scala": "Scala", "r": "R", "dart": "Dart", "lua": "Lua",
            "vue": "Vue (JavaScript)", "svelte": "Svelte (JavaScript)",
        }

        top_ext = sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)[0][0]
        return ext_display.get(top_ext, top_ext.upper() if len(top_ext) <= 4 else top_ext.capitalize())

    def _extract_dependencies(self, files: List[Dict[str, Any]]) -> List[str]:
        """Parses dependency manifests. Format-aware but not technology-specific."""
        deps: set = set()
        for f in files:
            path = f["path"].lower()
            content = f["content"]
            if "requirements" in path and path.endswith(".txt"):
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        dep = re.split(r"[=><~;#\[]", line)[0].strip()
                        if dep:
                            deps.add(dep)
            elif "pyproject.toml" in path:
                dep_blocks = re.findall(r'(?:dependencies|requires)\s*=\s*\[(.*?)\]', content, re.DOTALL)
                for block in dep_blocks:
                    items = re.findall(r'[\'"]([a-zA-Z0-9_\-]+)[^\'\"]*[\'"]', block)
                    for item in items:
                        if len(item) > 1 and not item.startswith("-"):
                            deps.add(item)
                if "[tool.poetry.dependencies]" in content:
                    section = content.split("[tool.poetry.dependencies]")[1].split("[")[0]
                    for line in section.splitlines():
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
                    line = line.strip()
                    if "/" in line and not line.startswith("module") and not line.startswith("go "):
                        parts = line.split()
                        if parts:
                            deps.add(parts[0])
            elif "cargo.toml" in path:
                in_deps = False
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("[dependencies") or line.startswith("[dev-dependencies"):
                        in_deps = True
                        continue
                    if line.startswith("[") and in_deps:
                        in_deps = False
                    if in_deps and "=" in line:
                        pkg = line.split("=")[0].strip()
                        if pkg:
                            deps.add(pkg)
            elif "pom.xml" in path:
                for m in re.finditer(r"<artifactId>([^<]+)</artifactId>", content):
                    deps.add(m.group(1).strip())
        return sorted(list(deps))

    def _detect_api_endpoints(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extracts API endpoint definitions using structural regex — no tech-specific keyword lists."""
        endpoints = []
        for f in files:
            content = f["content"]
            p_lower = f["path"].lower()
            # Skip binary/asset files
            if p_lower.endswith((".png", ".jpg", ".svg", ".ico", ".woff", ".ttf", ".lock", ".css", ".pdf")):
                continue
            # Python decorators: @app.get("/path"), @router.post("/path"), @api_v1.delete("/path")
            for m in re.finditer(
                r'@([a-zA-Z0-9_]+)\.(get|post|put|delete|patch|route|head|options)\s*\(\s*["\']([^"\']+)["\']',
                content, re.IGNORECASE
            ):
                p = m.group(3)
                method = m.group(2).upper() if m.group(2).lower() != "route" else "GET/POST"
                endpoints.append({"method": method, "path": p, "summary": self._format_endpoint_summary(p, method)})
            # JS/TS: anyRouter.get('/path', handler) — only paths starting with /
            for m in re.finditer(
                r'\b([a-zA-Z0-9_]+)\.(get|post|put|delete|patch|all)\s*\(\s*["\'](/[^"\']*)["\']',
                content, re.IGNORECASE
            ):
                obj = m.group(1).lower()
                if obj in ("os", "path", "sys", "dict", "list", "str", "re", "json", "np", "pd", "df"):
                    continue
                p = m.group(3)
                method = m.group(2).upper()
                endpoints.append({"method": method, "path": p, "summary": self._format_endpoint_summary(p, method)})
            # Django / Spring / ASP.NET
            for m in re.finditer(
                r'(?:re_path|GetMapping|PostMapping|PutMapping|DeleteMapping)\s*\(\s*["\']([^"\']+)["\']',
                content
            ):
                p = "/" + m.group(1).lstrip("^/").rstrip("$")
                endpoints.append({"method": "GET/POST", "path": p, "summary": self._format_endpoint_summary(p, "GET/POST")})
        seen: set = set()
        deduped = []
        for ep in endpoints:
            key = (ep["method"], ep["path"])
            if key not in seen:
                seen.add(key)
                deduped.append(ep)
        return deduped[:30]

    def _format_endpoint_summary(self, path: str, method: str) -> str:
        """Generic structural summary from path segments — no hardcoded domain-specific keywords."""
        clean = path.strip("/").replace("/", " ").replace("-", " ").replace("_", " ").strip()
        if not clean:
            clean = "root"
        return f"{method} endpoint for {clean} operations."

    def _detect_env_variables(self, files: List[Dict[str, Any]]) -> List[str]:
        """Extracts env variable names from .env files — format parsing only."""
        vars_found: set = set()
        for f in files:
            p = f["path"].lower()
            if not any(kw in p for kw in [".env", "env.example", "env.sample", "env.local"]):
                continue
            for line in f["content"].splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    var_name = line.split("=")[0].strip()
                    if var_name and var_name.replace("_", "").isupper():
                        vars_found.add(var_name)
        return sorted(list(vars_found))

    def _detect_config_files(self, files: List[Dict[str, Any]]) -> List[str]:
        """Identifies configuration files by their well-known filenames."""
        config_names = {
            "package.json", "pyproject.toml", "requirements.txt", "go.mod", "cargo.toml",
            "pom.xml", "build.gradle", "dockerfile", "docker-compose.yml", ".env.example",
            "tsconfig.json", "vite.config.js", "vite.config.ts", "webpack.config.js",
            "tailwind.config.js", "eslint.config.js", ".eslintrc", ".gitignore", "readme.md",
            "setup.py", "jest.config.js", "babel.config.js", "next.config.js", ".prettierrc",
            "deno.json", "bun.lockb", "composer.json", "gemfile",
        }
        found = []
        for f in files:
            name = f["path"].rsplit("/", 1)[-1].lower() if "/" in f["path"] else f["path"].lower()
            if name in config_names:
                found.append(f["path"])
        return found

    def _detect_collections(self, files: List[Dict[str, Any]]) -> List[str]:
        """Detects database schema/model/collection names using structural regex patterns."""
        SKIP_BASE_NAMES = {
            "BaseModel", "Model", "SQLModel", "Base", "Config", "Enum",
            "Exception", "Error", "Mixin", "ABC", "Protocol",
        }
        collections: set = set()
        for f in files:
            content = f["content"]
            p_lower = f["path"].lower()

            # Python ORMs: SQLAlchemy, Django, SQLModel, Beanie, Tortoise
            for m in re.finditer(
                r'class\s+([A-Z][a-zA-Z0-9_]*)\s*\([^)]*(?:Base|db\.Model|models\.Model|Document|SQLModel|DeclarativeBase|DeclarativeMeta)[^)]*\):',
                content
            ):
                name = m.group(1)
                if name not in SKIP_BASE_NAMES:
                    collections.add(name)

            # Pydantic schemas: class X(BaseModel):
            for m in re.finditer(r'class\s+([A-Z][a-zA-Z0-9_]*)\s*\([^)]*BaseModel[^)]*\):', content):
                name = m.group(1)
                if name not in SKIP_BASE_NAMES:
                    collections.add(name)

            # Schema/model files: grab all class names
            if any(kw in p_lower for kw in ["model", "schema", "entit", "collection"]):
                for m in re.finditer(r'class\s+([A-Z][a-zA-Z0-9_]*)\s*(?:\([^)]*\))?:', content):
                    name = m.group(1)
                    if name not in SKIP_BASE_NAMES:
                        collections.add(name)

            # MongoDB Motor / PyMongo: database.get_collection('name')
            for m in re.finditer(r'get_collection\s*\(\s*["\']([a-zA-Z0-9_]+)["\']', content):
                collections.add(m.group(1))

            # Mongoose / Prisma / TypeORM / Sequelize
            for m in re.finditer(
                r'(?:mongoose\.model|sequelize\.define|@Entity)\s*\(\s*["\']([A-Za-z0-9_]+)["\']',
                content, re.IGNORECASE
            ):
                collections.add(m.group(1))
            for m in re.finditer(r'(?:^|\n)\s*(?:model|type)\s+([A-Z][a-zA-Z0-9_]*)\s*\{', content):
                collections.add(m.group(1))

            # SQL DDL
            for m in re.finditer(
                r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`"]?([a-zA-Z0-9_]+)[`"]?',
                content, re.IGNORECASE
            ):
                name = m.group(1)
                if name.upper() not in ("TABLE", "EXISTS"):
                    collections.add(name)

        return sorted(list(collections))

    # ─────────────────────────────────────────────
    # README & fallback helpers
    # ─────────────────────────────────────────────

    def _get_readme_content(self, files: List[Dict[str, Any]]) -> str:
        readme = next((f for f in files if "readme.md" in f["path"].lower()), None)
        return readme["content"][:4000] if readme else ""

    def _extract_fallback_description(self, files: List[Dict[str, Any]], entry_point: str) -> str:
        readme = next((f for f in files if "readme.md" in f["path"].lower()), None)
        # Skip boilerplate README files
        if readme and any(bp in readme["content"].lower() for bp in [
            "react + vite", "minimal setup to get react working",
            "create react app", "next.js boilerplate", "this template provides",
        ]):
            readme = None
        if readme:
            cleaned = []
            for line in readme["content"].splitlines():
                s = line.strip()
                if s.startswith(("<", "!", "---", "```", "| ")) or s == "|":
                    continue
                if s.startswith("#"):
                    text = s.lstrip("# ").strip()
                    if text:
                        cleaned.append(text + (":" if not text.endswith(":") else ""))
                    continue
                cleaned.append(s)
            full = " ".join(p for p in cleaned if p).strip()
            return full[:2000] if full else ""
        entry = next((f for f in files if f["path"] == entry_point), None)
        if entry:
            match = re.search(r'"""(.*?)"""', entry["content"], re.DOTALL)
            if match and match.group(1).strip():
                return " ".join(match.group(1).strip().splitlines())[:500]
            return f"This project's execution begins at {entry_point}."
        return ""

    # ─────────────────────────────────────────────
    # Chunk generation (Phase 4) — pure utility
    # ─────────────────────────────────────────────

    def generate_chunks(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        for f in files:
            path = f["path"]
            text = f["content"]
            for idx, chunk_text in enumerate(self.embedder.chunk_text(text, max_size=500, overlap=80)):
                chunks.append({"id": f"{path}_chunk_{idx}", "path": path, "text": chunk_text})
        return chunks

    # ─────────────────────────────────────────────
    # Suggested improvements — thin LLM-output wrapper
    # ─────────────────────────────────────────────

    def generate_suggested_improvements(self, knowledge: Dict[str, Any]) -> List[str]:
        """
        Returns LLM-generated improvements stored during analyze_repository_with_llm().
        Falls back to generic structural checks if the LLM didn't provide any.
        No technology-specific keyword lists.
        """
        # Use LLM-generated improvements if available
        llm_improvements = knowledge.get("suggested_improvements", [])
        if llm_improvements:
            return llm_improvements[:6]

        # Generic structural fallback — no tech knowledge
        fallback = []
        if not knowledge.get("env_variables"):
            fallback.append("Use environment variables (.env) to separate configuration secrets from source code.")
        if not knowledge.get("tech_stack", {}).get("containerization"):
            fallback.append("Add Docker containerization for reproducible, isolated deployments.")
        if knowledge.get("api_endpoints") and not knowledge.get("security_detected"):
            fallback.append("Implement authentication and authorization on API endpoints.")
        if not knowledge.get("collections") and not knowledge.get("database"):
            fallback.append("Consider adding persistent data storage appropriate for your use case.")
        fallback.append("Set up a CI/CD pipeline (GitHub Actions / GitLab CI) for automated testing and deployment.")
        fallback.append("Add structured logging for better observability and debugging across services.")
        return fallback[:6]

    # ─────────────────────────────────────────────
    # Folder tree builder — pure filesystem utility
    # ─────────────────────────────────────────────

    def build_folder_tree(self, read_files: List[str]) -> str:
        """Builds an ASCII folder tree from a list of file paths."""
        if not read_files:
            return ""
        dirs: dict = {}
        for path in read_files:
            parts = path.replace("\\", "/").split("/")
            node = dirs
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = None

        def render(node, prefix=""):
            lines = []
            items = list(node.items())
            for i, (name, children) in enumerate(items):
                connector = "└── " if i == len(items) - 1 else "├── "
                lines.append(prefix + connector + name)
                if isinstance(children, dict):
                    ext = "    " if i == len(items) - 1 else "│   "
                    lines.extend(render(children, prefix + ext))
            return lines

        root_name = read_files[0].split("/")[0] if "/" in read_files[0] else "."
        lines = [root_name + "/"]
        lines.extend(render(dirs.get(root_name, dirs)))
        return "\n".join(lines[:60])
