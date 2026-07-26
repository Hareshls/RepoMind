# 🔌 RepoMind REST API Documentation

This document provides complete technical specifications, request/response schemas, error handling patterns, and integration examples for the **RepoMind REST API**. 

After reading this guide, developers can integrate RepoMind's AI repository intelligence and RAG capabilities into their own applications, CI/CD pipelines, IDE extensions, or custom dashboards **without needing to inspect the underlying Python source code**.

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [Base URL](#2-base-url)
3. [Authentication](#3-authentication)
4. [Analyze Repository (`POST /analyze`)](#4-analyze-repository)
5. [Ask Repository (`POST /ask`)](#5-ask-repository)
6. [Request Models](#6-request-models)
7. [Response Models](#7-response-models)
8. [HTTP Status Codes](#8-http-status-codes)
9. [Error Responses](#9-error-responses)
10. [Example Requests](#10-example-requests)
11. [Example Responses](#11-example-responses)
12. [OpenAPI / Swagger](#12-openapi--swagger)
13. [Rate Limits (Future)](#13-rate-limits-future)
14. [Version History](#14-version-history)

---

## 1. Introduction
The RepoMind API is a modern, high-performance RESTful web service built with **FastAPI**. It exposes two primary asynchronous workflows:
1. **Repository Analysis (`/analyze`)**: Clones a remote or local Git repository, explores its structure, prioritizes core files, reads code contents, builds structured knowledge, and indexes semantic vector embeddings to disk memory.
2. **Repository Question Answering (`/ask`)**: Queries stored vector memory using cosine similarity and keyword boosting, passing grounded code chunks to a local (**Qwen 2.5 Coder**) or cloud (**OpenAI**) LLM to generate accurate, citation-backed answers.

---

## 2. Base URL
All API requests should be directed to the base URL of your running Uvicorn or production FastAPI server instance.

```http
# Local Development Server
http://127.0.0.1:8000

# Production Deployment (Example)
https://api.repomind.example.com/v1
```

---

## 3. Authentication
In **v1.0.0**, the API operates in **unauthenticated open-access mode** designed for local developer workstations, self-hosted internal networks, and private container deployments. 

> [!NOTE]
> If deploying to a public-facing cloud environment, it is recommended to place an API Gateway or reverse proxy (*e.g., Nginx, Traefik, AWS API Gateway*) in front of Uvicorn to enforce standard `Authorization: Bearer <token>` or API key validation.

---

## 4. Analyze Repository
Initiates the 7-step repository analysis pipeline for a specified GitHub or local repository URL.

### **Endpoint**
```http
POST /analyze
```

### **Headers**
| Header | Value | Description |
| :--- | :--- | :--- |
| `Content-Type` | `application/json` | **Required**. Indicates the payload is JSON formatted. |

### **Request Body**
```json
{
  "repo_url": "https://github.com/openai/openai-python"
}
```

### **Behavior & Lifecycle**
1. Clones or accesses the target repository into `repositories/<repo_name>/`.
2. Scans files while ignoring noisy directories (`node_modules`, `.git`, `venv`) and lockfiles (`package-lock.json`, `poetry.lock`).
3. Prioritizes entry points and core architecture modules.
4. Generates vector embeddings for all code chunks and persists them to `.repomind_memory.json`.

---

## 5. Ask Repository
Queries the vector memory of an analyzed repository and returns a grounded natural language answer with precise file citations.

### **Endpoint**
```http
POST /ask
```

### **Headers**
| Header | Value | Description |
| :--- | :--- | :--- |
| `Content-Type` | `application/json` | **Required**. Indicates the payload is JSON formatted. |

### **Request Body**
```json
{
  "question": "How does API key authentication work in this SDK?",
  "repo_url": "https://github.com/openai/openai-python"
}
```

### **Behavior & Lifecycle**
1. Computes an embedding vector for the submitted `question`.
2. Performs cosine similarity search across the vector store corresponding to `repo_url` (or auto-falls back to the most recently analyzed repository if `repo_url` is omitted).
3. Synthesizes a response using the active AI engine (Local Qwen / OpenAI / Rule Heuristics).
4. Returns the answer along with matching source file citations.

---

## 6. Request Models

### `RepositoryRequest`
Used by `POST /analyze`.
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RepositoryRequest",
  "type": "object",
  "properties": {
    "repo_url": {
      "type": "string",
      "format": "uri",
      "description": "The HTTP/HTTPS or local path URI of the Git repository to analyze."
    }
  },
  "required": ["repo_url"],
  "additionalProperties": false
}
```

### `QuestionRequest`
Used by `POST /ask`.
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "QuestionRequest",
  "type": "object",
  "properties": {
    "question": {
      "type": "string",
      "minLength": 3,
      "description": "The natural language query regarding the repository architecture, code, or logic."
    },
    "repo_url": {
      "type": "string",
      "format": "uri",
      "description": "Optional URI of the target repository. Defaults to last analyzed repository if omitted."
    }
  },
  "required": ["question"],
  "additionalProperties": false
}
```

---

## 7. Response Models

### `AnalysisResponse`
Returned upon successful completion of `POST /analyze`.
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AnalysisResponse",
  "type": "object",
  "properties": {
    "status": { "type": "string", "enum": ["success"] },
    "repo": { "type": "string", "format": "uri" },
    "language": { "type": "string", "example": "Python" },
    "framework": { "type": "string", "example": "FastAPI" },
    "entry_point": { "type": "string", "example": "main.py" },
    "files_analyzed": { "type": "integer", "minimum": 0, "example": 45 }
  },
  "required": ["status", "repo", "language", "framework", "entry_point", "files_analyzed"]
}
```

### `QuestionResponse`
Returned upon successful completion of `POST /ask`.
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "QuestionResponse",
  "type": "object",
  "properties": {
    "status": { "type": "string", "enum": ["success"] },
    "question": { "type": "string" },
    "answer": { "type": "string", "description": "Markdown-formatted response grounded in RAG context." },
    "sources": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "file": { "type": "string", "example": "app/auth/jwt.py" },
          "range": { "type": "string", "example": "L1-L50" }
        },
        "required": ["file", "range"]
      }
    },
    "repo_url": { "type": "string", "format": "uri" }
  },
  "required": ["status", "question", "answer", "sources", "repo_url"]
}
```

---

## 8. HTTP Status Codes
RepoMind adheres to standard REST HTTP status code conventions:

| Status Code | Message | Description |
| :---: | :--- | :--- |
| **`200 OK`** | Success | The request was processed successfully and a JSON payload is returned. |
| **`400 Bad Request`** | Client Error | Malformed JSON, missing required fields, or invalid repository URL syntax. |
| **`404 Not Found`** | Not Found | The endpoint URI does not exist or the target repository could not be found/cloned. |
| **`422 Unprocessable Entity`** | Validation Error | Pydantic validation failed (*e.g., passing an integer where a URL string was expected*). |
| **`500 Internal Server Error`** | Server Error | Unhandled backend exception during embedding calculation, git cloning, or LLM inference. |

---

## 9. Error Responses
When an error occurs (status codes `400`, `404`, `422`, `500`), the API returns a structured JSON error object:

### Standard Error Schema
```json
{
  "detail": "Detailed explanation of why the request failed."
}
```

### Example `422 Unprocessable Entity` (Missing Required Field)
```json
{
  "detail": [
    {
      "loc": ["body", "repo_url"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Example `500 Internal Server Error` (Git Clone Failure)
```json
{
  "detail": "Git clone failed for https://github.com/invalid/repo.git: Repository not found or access denied."
}
```

---

## 10. Example Requests

### **cURL Examples**

#### 1. Analyze a Repository
```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/openai/openai-python"
  }'
```

#### 2. Ask a Question
```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the architecture and dependencies?",
    "repo_url": "https://github.com/openai/openai-python"
  }'
```

---

### **Python (`httpx` / `requests`) Integration Example**
```python
import httpx

BASE_URL = "http://127.0.0.1:8000"
REPO_URL = "https://github.com/openai/openai-python"

# 1. Trigger Analysis
print("Analyzing repository...")
analyze_res = httpx.post(
    f"{BASE_URL}/analyze",
    json={"repo_url": REPO_URL},
    timeout=60.0
)
print("Analysis Result:", analyze_res.json())

# 2. Ask a Question
print("\nAsking question...")
ask_res = httpx.post(
    f"{BASE_URL}/ask",
    json={
        "question": "How does authentication work in this SDK?",
        "repo_url": REPO_URL
    },
    timeout=30.0
)
data = ask_res.json()
print(f"\nAnswer:\n{data['answer']}")
print(f"\nSources Cited: {data['sources']}")
```

---

### **JavaScript / TypeScript (`fetch`) Integration Example**
```javascript
const BASE_URL = 'http://127.0.0.1:8000';

async function runRepoMindWorkflow(repoUrl) {
  // Step 1: Analyze
  console.log(`[API] Starting analysis for ${repoUrl}...`);
  const analyzeRes = await fetch(`${BASE_URL}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ repo_url: repoUrl })
  });
  const analyzeData = await analyzeRes.json();
  console.log('[API] Analysis Complete:', analyzeData);

  // Step 2: Ask
  console.log('[API] Querying repository intelligence...');
  const askRes = await fetch(`${BASE_URL}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: 'Explain the error handling approach',
      repo_url: repoUrl
    })
  });
  const askData = await askRes.json();
  
  console.log('\n--- AI Response ---');
  console.log(askData.answer);
  console.log('\n--- Citations ---', askData.sources);
}

runRepoMindWorkflow('https://github.com/openai/openai-python');
```

---

## 11. Example Responses

### Successful `/analyze` Response
```json
{
  "status": "success",
  "repo": "https://github.com/openai/openai-python",
  "language": "Python",
  "framework": "Standard Library / General Purpose SDK",
  "entry_point": "openai/__init__.py",
  "files_analyzed": 50
}
```

### Successful `/ask` Response
```json
{
  "status": "success",
  "question": "How does authentication work in this SDK?",
  "answer": "### 🔐 Authentication & Security Model\nThe OpenAI Python SDK authenticates requests via API keys provided by the developer.\n\n- **API Key Initialization**: You can pass `api_key` explicitly when instantiating `OpenAI(api_key='...')`.\n- **Environment Variable**: If omitted, the client automatically attempts to load `OPENAI_API_KEY` from the system environment variables.\n- **Header Injection**: The HTTP client injects `Authorization: Bearer <api_key>` into the outbound HTTP headers for all API requests.",
  "sources": [
    { "file": "openai/_client.py", "range": "L1-L50" },
    { "file": "openai/_auth.py", "range": "L1-L50" },
    { "file": "README.md", "range": "L1-L50" }
  ],
  "repo_url": "https://github.com/openai/openai-python"
}
```

---

## 12. OpenAPI / Swagger
FastAPI automatically generates interactive, browser-based API documentation directly from the type hints and Pydantic schemas. When your server is running, you can explore and test the endpoints interactively:

- **Swagger UI (Interactive Console)**:  
  👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc (Alternative API Reference)**:  
  👉 [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI JSON Schema Specification**:  
  👉 [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## 13. Rate Limits (Future)
Currently, RepoMind imposes **no artificial rate limits** or request quotas on local API endpoints. 

In future enterprise or multi-tenant cloud releases (**v1.5+**), the following rate limiting headers and quotas are planned for `/analyze` and `/ask`:
- `X-RateLimit-Limit`: Maximum requests allowed per hour (*e.g., `100`*).
- `X-RateLimit-Remaining`: Remaining requests in the current window (*e.g., `95`*).
- `X-RateLimit-Reset`: UTC epoch timestamp when the quota window resets.
- Exceeding quotas will return HTTP **`429 Too Many Requests`**.

---

## 14. Version History

| Version | Release Date | Summary of Changes |
| :---: | :---: | :--- |
| **`v1.0.0`** | July 2026 | **Initial Public Release**. Added `/analyze` and `/ask` REST endpoints, Pydantic validation schemas, disk memory persistence (`.repomind_memory.json`), dynamic source citations, and local Qwen 2.5 Coder integration. |
| **`v0.9.0-beta`**| July 2026 | Internal prototype with in-memory storage and basic heuristic response formatting. |
