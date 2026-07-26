from typing import Optional, List, Dict, Any
from pydantic import field_validator, HttpUrl, BaseModel

class RepositoryRequest(BaseModel):
    repo_url: HttpUrl

    @field_validator("repo_url")
    @classmethod
    def validate_git_url(cls, value):
        if value.host != "github.com":
            raise ValueError("only github.com url allowed")
        return value

class QuestionRequest(BaseModel):
    question: str
    repo_url: Optional[str] = None

class FilePlan(BaseModel):
    path: str
    priority: int
    reason: str

class FileContent(BaseModel):
    path: str
    content: str

class RepoKnowledge(BaseModel):
    repo_url: str
    language: str
    framework: str
    entry_point: str
    dependencies: List[str]
    architecture: str
    key_modules: List[Dict[str, Any]]
    chunks: List[Dict[str, Any]] = []