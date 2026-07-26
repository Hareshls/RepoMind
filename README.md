# 🧠 RepoMind — Autonomous AI Repository Understanding Agent

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Architecture-Custom%20Multi--Agent-8B5CF6?style=for-the-badge" alt="Custom Architecture">
  <img src="https://img.shields.io/badge/Frontend-Vanilla%20Glassmorphism-06B6D4?style=for-the-badge" alt="Frontend">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

---

## 🌟 Overview

**RepoMind** is an autonomous AI agent engineered to explore, analyze, and understand any public GitHub repository like a senior software engineer.

Unlike simple RAG wrappers or blind code generators, RepoMind prioritizes **repository understanding**. Instead of loading thousands of raw files into an LLM context window or relying on black-box frameworks (*LangGraph, CrewAI, AutoGen*), RepoMind implements a custom, decoupled multi-agent architecture where every component has one single responsibility.

---

## ✨ Key Features

- 🔍 **Intelligent Discovery (`Explorer`)**: Recursively traverses repositories while automatically filtering out build artifacts (`node_modules`, `venv`, `.git`, `__pycache__`) and binary files.
- 🎯 **Strategic Prioritization (`Planner`)**: Ranks files using a 5-tier rule-based hierarchy (prioritizing READMEs, config files, entry points, and architectural modules).
- 📖 **Safe Content Extraction (`Reader`)**: Extracts code with UTF-8 decoding and strict size limits (`100KB`) to protect memory integrity.
- 🏗️ **Structured Knowledge Synthesis (`KnowledgeBuilder`)**: Automatically detects programming languages, frameworks (*FastAPI, React, Django, Next.js, etc.*), entry points, clean dependency lists, and architectural layers.
- ⚡ **Vector Memory Indexing (`Memory`)**: Generates text chunks and embedding vectors, enabling fast semantic cosine similarity search boosted by keyword matching.
- 💬 **Grounded Question Answering (`Reporter`)**: Synthesizes accurate, codebase-grounded answers with Markdown and syntax-highlighted code snippets.
- 🎨 **Premium Glassmorphism Web Dashboard**: An obsidian/navy dark-mode web application served directly by FastAPI featuring real-time analysis progress animations, stats cards, dependency clouds, and an AI chat console.

---

## 🏛️ System Architecture Overview

RepoMind orchestrates six specialized sub-agents through a master orchestrator:

```text
                       +-------------------+
                       |    User / Web     |
                       +---------+---------+
                                 |
                                 v
                       +-------------------+
                       |    FastAPI API    |
                       +---------+---------+
                                 |
                                 v
                       +-------------------+
                       |     RepoMind      | (Master Orchestrator)
                       +---------+---------+
                                 |
         +-----------------------+-----------------------+
         |           |           |           |           |
         v           v           v           v           v
    [Explorer] -> [Planner] -> [Reader] -> [Knowledge] -> [Memory] <---> [Reporter]
    (Discover)    (Prioritize) (Extract)   (Synthesize)   (Index)        (Answer QA)
```

1. **`GitService`**: Dynamically clones repositories into `repositories/<repo_name>` and manages file permissions.
2. **`Explorer`**: Maps directory structures and filters noise.
3. **`Planner`**: Selects high-value target files for reading.
4. **`Reader`**: Safely opens and extracts text chunks.
5. **`KnowledgeBuilder`**: Derives tech stack, dependencies, and architecture.
6. **`Memory`**: Indexes vector embeddings and metadata.
7. **`Reporter`**: Retrieves relevant chunks from memory to answer queries.

---

## 🚀 Quickstart & Installation

### Prerequisites
- **Python 3.10** or higher
- **Git** installed and available on your PATH

### 1. Clone the Repository
```bash
git clone https://github.com/Hareshls/repomind.git
cd repomind
```

### 2. Set Up Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure AI Engine (Optional)
RepoMind supports a **Triple-Tier Hybrid AI Engine**! You can use OpenAI cloud models, 100% free local Ollama open-source models, or run offline with our deterministic local intelligence fallback:

#### Option A: Local Open-Source LLMs via Ollama (100% Free & Private)
If you have [Ollama](https://ollama.com/) running locally:
```bash
# Windows (PowerShell)
$env:OLLAMA_MODEL="llama3"                # or mistral, qwen2.5-coder, codellama
$env:OLLAMA_EMBEDDING_MODEL="nomic-embed-text"  # optional local embeddings

# macOS / Linux
export OLLAMA_MODEL="llama3"
export OLLAMA_EMBEDDING_MODEL="nomic-embed-text"
```

#### Option B: Cloud LLMs via OpenAI
```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-your-openai-api-key"

# macOS / Linux
export OPENAI_API_KEY="sk-your-openai-api-key"
```

*Note: If neither is set, RepoMind automatically uses its built-in deterministic local intelligence and hashing vectorizer!*


---

## 💻 Running Locally

Start the application server using Uvicorn:
```bash
uvicorn main:app --reload
```

### 🌐 1. Web Application UI
Open your web browser and navigate to:
**👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

Paste any public GitHub repository URL into the top Analyzer Bar to watch RepoMind explore and understand the codebase in real-time, or chat with previously analyzed repositories from the left sidebar!

### 🔌 2. Interactive API Swagger UI
Access the auto-generated interactive OpenAPI documentation at:
**👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## 📖 API Reference

### Analyze Repository
- **Endpoint**: `POST /analyze`
- **Description**: Clones, explores, builds knowledge, and indexes vector memory for a repository.
- **Request Body**:
  ```json
  {
    "repo_url": "https://github.com/openai/openai-python"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "repo": "https://github.com/openai/openai-python",
    "language": "Python",
    "framework": "Standard Library / SDK",
    "entry_point": "README.md",
    "files_analyzed": 50
  }
  ```

### Ask Question
- **Endpoint**: `POST /ask`
- **Description**: Retrieves relevant code chunks from memory and synthesizes grounded answers.
- **Request Body**:
  ```json
  {
    "question": "What are the core dependencies?",
    "repo_url": "https://github.com/openai/openai-python"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "question": "What are the core dependencies?",
    "answer": "The repository relies on: `httpx`, `pydantic`, `anyio`, `pytest`...\n\n**From `pyproject.toml`**:\n...",
    "repo_url": "https://github.com/openai/openai-python"
  }
  ```

---

## 📁 Project Structure

```text
repomind/
├── app/
│   ├── agent/                 # The 6 Specialist Agents & Master Orchestrator
│   │   ├── explorer.py        # Recursive file discovery & filtering
│   │   ├── planner.py         # 5-tier file ranking & reading strategy
│   │   ├── reader.py          # Safe content extraction & truncation
│   │   ├── knowledge_builder.py # Tech stack, dependency & architecture synthesis
│   │   ├── memory.py          # Vector store & cosine similarity indexing
│   │   ├── reporter.py        # Grounded QA & code chunk synthesis
│   │   └── repoMind.py        # Master workflow orchestrator
│   ├── api/
│   │   └── routes.py          # Decoupled FastAPI route handlers (/analyze, /ask)
│   ├── models/
│   │   └── repository.py      # Pydantic validation & pipeline communication schemas
│   └── services/
│       ├── github.py          # Git clone management & permission cleanup
│       ├── embeddings.py      # Chunking, OpenAI embeddings & local hash fallback
│       └── llm.py             # OpenAI completion wrapper & rule-based fallback
├── frontend/                  # Vanilla Glassmorphism Web Application
│   ├── index.html             # Dashboard & chat console layout
│   ├── styles.css             # Obsidian dark mode & micro-animations
│   └── app.js                 # Async API communication & state persistence
├── repositories/              # Dynamic storage for cloned target repositories
├── main.py                    # FastAPI server entry point & static UI mounting
├── requirements.txt           # Python package dependencies
└── README.md                  # Project entry point & documentation
```

---

## 🗺️ Final Roadmap

- [x] **Project Setup**: Clean decoupled directory structure and type-safe schemas.
- [x] **Backend & AI Pipeline**: 6 specialized sub-agents with custom orchestration.
- [x] **Vector Memory**: In-memory embedding storage with cosine similarity and keyword boosting.
- [x] **Frontend Dashboard**: Premium obsidian dark-mode UI with live animated feedback.
- [x] **Testing & Verification**: Verified against real-world repositories (`openai-python`, `Portfolio`).
- [ ] **Comprehensive Documentation**: Architectural deep-dive, API docs, and guides.
- [ ] **Architecture Diagrams**: Professional Mermaid & visual flow diagrams.
- [ ] **Deployment**: Production packaging for backend, frontend, and live demo.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE). Developed as an advanced demonstration of autonomous agentic architecture and codebase comprehension.
