import os
from typing import Dict, Any, List

class LLMService:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.default_model = model

    def complete(self, prompt: str, system_prompt: str = "You are a helpful software engineering AI assistant.") -> str:
        """Call OpenAI or Ollama LLM if available, otherwise return empty to trigger local fallback."""
        ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")
        api_key = os.getenv("OPENAI_API_KEY")
        
        try:
            import openai
            if ollama_model:
                base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
                client = openai.OpenAI(api_key="ollama", base_url=base_url)
                response = client.chat.completions.create(
                    model=ollama_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2
                )
                return response.choices[0].message.content or ""
            elif api_key:
                client = openai.OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model=self.default_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2
                )
                return response.choices[0].message.content or ""
        except Exception as e:
            # Silently fall back to neat rule-based formatting if local LLM is offline or busy
            pass
        return ""


