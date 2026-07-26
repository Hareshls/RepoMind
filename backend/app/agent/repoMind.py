from pathlib import Path
from typing import Dict, Any, Optional
from app.services.github import GitService
from app.agent.explorer import Explorer
from app.agent.planner import Planner
from app.agent.reader import Reader
from app.agent.knowledge_builder import KnowledgeBuilder
from app.agent.memory import Memory
from app.agent.reporter import Reporter

class RepoMind:
    def __init__(self):
        self.git_service = GitService()
        self.explorer = Explorer()
        self.planner = Planner()
        self.reader = Reader()
        self.knowledge_builder = KnowledgeBuilder()
        self.memory = Memory()
        self.reporter = Reporter()

    def analyse(self, repo_url: str) -> Dict[str, Any]:
        """Orchestrate full repository analysis workflow."""
        repo_url = str(repo_url)
        print(f"Starting analysis for {repo_url}")

        repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
        destination = Path("repositories") / repo_name

        self.git_service.clone_repository(repo_url, str(destination))
        discovered_files = self.explorer.discover(destination)
        read_plan = self.planner.plan(discovered_files)
        read_results = self.reader.read_files(destination, read_plan)
        knowledge = self.knowledge_builder.build_knowledge(repo_url, read_results)
        self.memory.store(repo_url, knowledge)

        print(f"Analysis complete for {repo_url}: {knowledge['language']}, {knowledge['framework']}")
        return {
            "status": "success",
            "repo": repo_url,
            "language": knowledge["language"],
            "framework": knowledge["framework"],
            "entry_point": knowledge["entry_point"],
            "files_analyzed": len(read_results)
        }

    def ask(self, question: str, repo_url: Optional[str] = None) -> Dict[str, Any]:
        """Answer user questions grounded in stored repository knowledge."""
        print(f"Answering question: {question}")
        answer_text = self.reporter.answer(question, self.memory, repo_url=repo_url)
        chunks = self.memory.search(question, repo_url=repo_url, top_k=3)
        sources = [{"file": ch["path"], "range": "L1-L50"} for ch in chunks] if chunks else []
        return {
            "status": "success",
            "question": question,
            "answer": answer_text,
            "sources": sources,
            "repo_url": repo_url or self.memory.last_repo_url
        }