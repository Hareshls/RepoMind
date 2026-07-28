import os
from typing import Dict, Any, List

class LLMService:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.default_model = model

    def complete(self, prompt: str, system_prompt: str = "You are a helpful software engineering AI assistant.") -> str:
        ollama_model = os.getenv("OLLAMA_MODEL")
        api_key = os.getenv("OPENAI_API_KEY")
        import json, urllib.request
        if not ollama_model and not api_key:
            # Try to auto-detect local Ollama models if no env var is set
            try:
                req = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2.0)
                data = json.loads(req.read().decode())
                models = [m["name"] for m in data.get("models", [])]
                if models:
                    for preferred in ["qwen2.5-coder:1.5b", "qwen2.5-coder", "llama3.2:latest", "llama3:latest"]:
                        if any(preferred in m for m in models):
                            ollama_model = next(m for m in models if preferred in m)
                            break
                    if not ollama_model:
                        ollama_model = models[0]
                    print(f"[LLMService] Auto-detected local Ollama model: {ollama_model}")
            except Exception:
                pass

        import openai
        
        # 1. Try Ollama if model is configured
        if ollama_model:
            try:
                base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
                client = openai.OpenAI(api_key="ollama", base_url=base_url, timeout=120.0)
                response = client.chat.completions.create(
                    model=ollama_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                print(f"[LLMService] Ollama connection failed ({e}), falling back if possible...")

        # 2. Fall back to OpenAI / Groq if API key is provided
        if api_key:
            try:
                base_url = os.getenv("OPENAI_BASE_URL")
                client = openai.OpenAI(api_key=api_key, base_url=base_url, timeout=120.0)
                
                # Automatically use a Groq model if the base URL points to Groq
                model_to_use = self.default_model
                if base_url and "groq" in base_url.lower():
                    model_to_use = "llama-3.3-70b-versatile"
                    
                response = client.chat.completions.create(
                    model=model_to_use,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                print(f"[LLMService] OpenAI fallback error: {type(e).__name__}: {e}")

        return ""


