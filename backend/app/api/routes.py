from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from app.models.repository import RepositoryRequest, QuestionRequest
from app.agent.repoMind import RepoMind
from app.services.doc_generator import generate_docx, generate_html

router = APIRouter()
agent = RepoMind()

@router.post("/analyze")
def analyze_repository(request: RepositoryRequest):
    agent.memory._load_from_disk()
    return agent.analyse(str(request.repo_url))

@router.post("/ask")
def ask_question(request: QuestionRequest):
    return agent.ask(request.question, repo_url=request.repo_url)

@router.get("/repositories")
def get_repositories():
    agent.memory._load_from_disk()
    repos = []
    for url, mem in agent.memory.store.items():
        name = url.rstrip("/").split("/")[-1].replace(".git", "")
        parts = url.replace("https://github.com/", "").replace(".git", "").split("/")
        sub = f"{parts[0]} / {parts[1]}" if len(parts) >= 2 else name
        k = mem.get("knowledge", {})
        meta = k.get("metadata")
        if not meta:
            meta = {
                "name": name,
                "description": k.get("project_description", "An AI-analyzed GitHub repository codebase."),
                "owner": parts[0] if len(parts) >= 1 else "Unknown Owner",
                "stars": "N/A",
                "forks": "N/A",
                "primary_language": k.get("language", "N/A"),
                "license": "N/A",
                "default_branch": "N/A",
                "last_updated": "N/A",
                "size": "N/A",
                "size_bytes": 0
            }
        ts = k.get("tech_stack")
        if not ts or not isinstance(ts, dict) or not ts.get("languages"):
            lang_val = k.get("language")
            fw_val = k.get("framework")
            db_val = k.get("database")
            ts = {
                "languages": [lang_val] if lang_val else [],
                "frameworks": [fw_val] if fw_val else [],
                "databases": [db_val] if db_val else [],
                "cloud_devops": [],
                "package_managers": []
            }
        summary_doc = mem.get("summary_doc", "")
        repos.append({
            "url": url,
            "repo": url,
            "name": name,
            "sub": sub,
            "lang": k.get("language"),
            "language": k.get("language"),
            "framework": k.get("framework"),
            "database": k.get("database"),
            "authentication": k.get("authentication"),
            "entry": k.get("entry_point"),
            "entry_point": k.get("entry_point"),
            "files": str(len(mem.get("read_files", []))) if mem.get("read_files") else None,
            "files_analyzed": len(mem.get("read_files", [])) if mem.get("read_files") else None,
            "architecture": k.get("architecture"),
            "dependencies": k.get("dependencies", []),
            "metadata": meta,
            "tech_stack": ts,
            "summary_doc": summary_doc,
            "insights": k.get("insights", []),
            "api_endpoints": k.get("api_endpoints", []),
            "collections": k.get("collections", []),
            "env_variables": k.get("env_variables", []),
            "key_modules": k.get("key_modules", []),
            "security_detected": k.get("security_detected", [])
        })
    return {"repositories": repos, "last_active": agent.memory.last_repo_url}

@router.get("/export/doc")
def export_word_doc(repo_url: Optional[str] = None):
    knowledge = agent.memory.get_knowledge(repo_url)
    if not knowledge:
        raise HTTPException(status_code=404, detail="No analyzed repository knowledge found in memory.")
    doc_path = generate_docx(knowledge)
    return FileResponse(
        path=doc_path,
        filename=doc_path.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@router.get("/export/html")
def export_html_doc(repo_url: Optional[str] = None):
    knowledge = agent.memory.get_knowledge(repo_url)
    if not knowledge:
        raise HTTPException(status_code=404, detail="No analyzed repository knowledge found in memory.")
    html_path = generate_html(knowledge)
    return FileResponse(
        path=html_path,
        filename=html_path.name,
        media_type="text/html"
    )
