import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.services.embeddings import EmbeddingService

class Memory:
    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        self.embedder = embedding_service or EmbeddingService()
        self.knowledge_store: Dict[str, Dict[str, Any]] = {}
        self.vector_store: Dict[str, List[Dict[str, Any]]] = {}
        self.last_repo_url: Optional[str] = None
        self.persist_file = Path(".repomind_memory.json")
        self._load_from_disk()

    def _load_from_disk(self):
        try:
            if self.persist_file.exists():
                data = json.loads(self.persist_file.read_text(encoding="utf-8"))
                self.knowledge_store = data.get("knowledge_store", {})
                self.vector_store = data.get("vector_store", {})
                self.last_repo_url = data.get("last_repo_url")
        except Exception as e:
            print(f"[Memory] Could not load persisted memory: {e}")

    def _save_to_disk(self):
        try:
            data = {
                "knowledge_store": self.knowledge_store,
                "vector_store": self.vector_store,
                "last_repo_url": self.last_repo_url
            }
            self.persist_file.write_text(json.dumps(data), encoding="utf-8")
        except Exception as e:
            print(f"[Memory] Could not persist memory to disk: {e}")

    def store(self, repo_url: str, knowledge: Dict[str, Any]):
        """Store repository knowledge and index text chunks with embedding vectors."""
        repo_url = str(repo_url)
        self.knowledge_store[repo_url] = knowledge
        self.last_repo_url = repo_url

        chunks = knowledge.get("chunks", [])
        indexed_chunks = []
        for ch in chunks:
            vec = self.embedder.compute_embedding(ch["text"])
            indexed_chunks.append({
                "id": ch["id"],
                "path": ch["path"],
                "text": ch["text"],
                "vector": vec
            })
        self.vector_store[repo_url] = indexed_chunks
        self._save_to_disk()

    def get_knowledge(self, repo_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve stored repository metadata knowledge."""
        self._load_from_disk()
        target_url = str(repo_url) if repo_url else self.last_repo_url
        if not target_url or target_url not in self.knowledge_store:
            if self.knowledge_store:
                target_url = list(self.knowledge_store.keys())[-1]
            else:
                return None
        return self.knowledge_store[target_url]

    def search(self, query: str, repo_url: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search stored chunk vectors using cosine similarity and keyword boosting."""
        self._load_from_disk()
        target_url = str(repo_url) if repo_url else self.last_repo_url
        if not target_url or target_url not in self.vector_store:
            if self.vector_store:
                target_url = list(self.vector_store.keys())[-1]
            else:
                return []

        query_vec = self.embedder.compute_embedding(query)
        indexed_chunks = self.vector_store[target_url]
        
        scored = []
        for ch in indexed_chunks:
            score = self.embedder.cosine_similarity(query_vec, ch["vector"])
            query_words = [w.lower() for w in query.split() if len(w) > 2]
            text_lower = ch["text"].lower()
            keyword_boost = sum(0.15 for w in query_words if w in text_lower)
            
            scored.append({
                "id": ch["id"],
                "path": ch["path"],
                "text": ch["text"],
                "score": score + keyword_boost
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
