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
    return agent.analyse(str(request.repo_url))

@router.post("/ask")
def ask_question(request: QuestionRequest):
    return agent.ask(request.question, repo_url=request.repo_url)

@router.get("/repositories")
def get_repositories():
    repos = []
    for url, k in agent.memory.knowledge_store.items():
        name = url.rstrip("/").split("/")[-1].replace(".git", "")
        parts = url.replace("https://github.com/", "").replace(".git", "").split("/")
        sub = f"{parts[0]} / {parts[1]}" if len(parts) >= 2 else name
        repos.append({
            "url": url,
            "name": name,
            "sub": sub,
            "lang": k.get("language", "Python"),
            "framework": k.get("framework", "General Purpose"),
            "entry": k.get("entry_point", "README.md"),
            "files": str(len(k.get("key_modules", [])) * 4 or 25)
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
