import os
import math
import re
from typing import List

class EmbeddingService:
    def __init__(self, dim: int = 128):
        self.dim = dim
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.ollama_embed_model = os.getenv("OLLAMA_EMBEDDING_MODEL")
        self.use_openai = bool(self.api_key)
        self.use_ollama = bool(self.ollama_embed_model)

    def chunk_text(self, text: str, max_size: int = 600, overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks for memory indexing."""
        if not text.strip():
            return []
        lines = text.splitlines()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for line in lines:
            line_len = len(line) + 1
            if current_length + line_len > max_size and current_chunk:
                chunk_str = "\n".join(current_chunk).strip()
                if chunk_str:
                    chunks.append(chunk_str)
                overlap_len = 0
                new_chunk = []
                for rev_line in reversed(current_chunk):
                    if overlap_len + len(rev_line) <= overlap:
                        new_chunk.insert(0, rev_line)
                        overlap_len += len(rev_line) + 1
                    else:
                        break
                current_chunk = new_chunk
                current_length = overlap_len
            current_chunk.append(line)
            current_length += line_len
            
        if current_chunk:
            chunk_str = "\n".join(current_chunk).strip()
            if chunk_str:
                chunks.append(chunk_str)
        return chunks

    def compute_embedding(self, text: str) -> List[float]:
        """Compute embedding vector using OpenAI, Ollama, or fallback hashing vectorizer."""
        if self.use_openai or self.use_ollama:
            try:
                import openai
                base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1") if self.use_ollama else None
                api_key = "ollama" if self.use_ollama else self.api_key
                model_name = self.ollama_embed_model if self.use_ollama else "text-embedding-3-small"

                client = openai.OpenAI(api_key=api_key, base_url=base_url)
                res = client.embeddings.create(input=text, model=model_name)
                return res.data[0].embedding
            except Exception as e:
                print(f"[EmbeddingService] Error computing embedding ({'Ollama' if self.use_ollama else 'OpenAI'}): {e}")
        return self._hash_embedding(text)


    def _hash_embedding(self, text: str) -> List[float]:
        """Deterministic TF-style hashing vectorizer for in-memory cosine similarity."""
        vec = [0.0] * self.dim
        words = re.findall(r"\w+", text.lower())
        if not words:
            return vec
        for word in words:
            idx = hash(word) % self.dim
            sign = 1.0 if (hash(word) // self.dim) % 2 == 0 else -1.0
            vec[idx] += sign
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two embedding vectors."""
        if len(vec1) != len(vec2) or not vec1 or not vec2:
            return 0.0
        return sum(a * b for a, b in zip(vec1, vec2))
