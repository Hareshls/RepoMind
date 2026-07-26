# 🏛️ RepoMind System Architecture & Design Specification

This document provides a comprehensive technical deep-dive into the internal design, agent lifecycle, memory indexing algorithms, and hybrid AI engine powering **RepoMind**.

---

## 1. Core Architectural Philosophy

Most AI coding tools focus on **code generation**—attempting to write snippets or auto-complete functions. RepoMind is engineered for a fundamentally different challenge: **repository understanding**.

### Design Principles:
1. **Decoupled Multi-Agent Specialization**: Instead of a single monolithic prompt attempting to read an entire repository, RepoMind decomposes repository comprehension into six specialized sub-agents. Each sub-agent adheres strictly to the **Single Responsibility Principle**.
2. **Zero Black-Box Frameworks**: Built entirely from scratch in modern Python without heavy, opaque agent orchestration libraries (*LangGraph, CrewAI, AutoGen*). This ensures transparent execution traces, deterministic error handling, and zero hidden prompt bloat.
3. **Memory & RAG First**: Repositories can contain thousands of files. RepoMind uses strategic file prioritization and vector similarity memory indexing so that answering queries requires retrieving small, highly relevant code chunks rather than reloading entire files from disk.
4. **Triple-Tier Hybrid Intelligence**: Designed to operate cleanly across three intelligence layers: cloud LLMs (OpenAI), local open-source LLMs (Ollama / Qwen / Llama), and zero-config deterministic local heuristics.

---

## 2. High-Level System Workflow & RAG Pipeline

When a user submits a repository URL, RepoMind executes a sequential, multi-phase comprehension pipeline:

```text
+-----------------------------------------------------------------------------------+
|                                 USER / WEB CLIENT                                 |
+-----------------------------------------------------------------------------------+
                                          |
                                          | POST /analyze  |  POST /ask
                                          v
+-----------------------------------------------------------------------------------+
|                           FASTAPI ROUTER (api/routes.py)                          |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        REPOMIND ORCHESTRATOR (repoMind.py)                        |
+-----------------------------------------------------------------------------------+
       |              |              |              |              |              ^
       | 1. Clone     | 2. Discover  | 3. Prioritize| 4. Read      | 5. Synthesize| 6. Query
       v              v              v              v              v              |
+--------------+ +--------------+ +--------------+ +--------------+ +--------------+  |
|  GitService  | |   Explorer   | |   Planner    | |    Reader    | |  Knowledge   |  |
| (github.py)  | | (explorer.py)| | (planner.py) | | (reader.py)  | |  Builder     |  |
+--------------+ +--------------+ +--------------+ +--------------+ +--------------+  |
       |                                                                   |          |
       +---------------------------------+---------------------------------+          |
                                         |                                            |
                                         v                                            |
                         +-------------------------------+                            |
                         |            Memory             |                            |
                         | (Metadata & Vector Chunks Index)|                          |
                         +---------------+---------------+                            |
                                         ^                                            |
                                         | Retrieve Chunks                            |
                                         v                                            |
                         +-------------------------------+                            |
                         |           Reporter            |----------------------------+
                         |     (Grounded RAG QA Engine)  |
                         +-------------------------------+
```

---

## 3. Specialist Agents Deep-Dive

### 🔍 1. `Explorer` (`app/agent/explorer.py`)
- **Responsibility**: Map the local repository filesystem and filter out noise.
- **Implementation**: Recursively walks directory trees while pruning common build artifacts, dependency directories, and version control metadata (`.git`, `node_modules`, `venv`, `.next`, `__pycache__`, `.pytest_cache`, `dist`, `build`). It also automatically inspects file extensions to exclude binary assets (`.png`, `.exe`, `.dll`, `.pdf`, `.zip`).
- **Output**: A structured list of clean, human-readable source file paths.

### 🎯 2. `Planner` (`app/agent/planner.py`)
- **Responsibility**: Develop a strategic reading plan without exceeding memory budgets.
- **Implementation**: Evaluates discovered files against a 5-tier rule-based hierarchy:
  - **Tier 1 (Priority 100)**: Core Documentation (`README.md`, `ARCHITECTURE.md`)
  - **Tier 2 (Priority 90)**: Dependency & Build Manifests (`pyproject.toml`, `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`)
  - **Tier 3 (Priority 85)**: Primary Entry Points (`main.py`, `app.py`, `index.js`, `index.ts`, `server.py`, `cli.py`)
  - **Tier 4 (Priority 70)**: Core Logic & Architecture Modules (`*service*`, `*manager*`, `*model*`, `*route*`, `*controller*`)
  - **Tier 5 (Priority 50)**: Standard source modules and utilities.
- **Output**: A sorted execution plan capping reading volume at the top 50 most critical files.

### 📖 3. `Reader` (`app/agent/reader.py`)
- **Responsibility**: Extract textual file contents safely.
- **Implementation**: Opens planned file paths using `utf-8` encoding with `errors="replace"` to prevent crashing on malformed characters. Enforces a strict memory safeguard (`max_file_bytes = 100_000`); files exceeding this threshold have their opening 100KB extracted and appended with a truncation notice.
- **Output**: List of dictionaries containing relative file paths and extracted code contents.

### 🏗️ 4. `KnowledgeBuilder` (`app/agent/knowledge_builder.py`)
- **Responsibility**: Transform raw file contents into structured architectural knowledge and searchable code chunks.
- **Implementation**:
  - **Language Detection**: Calculates file extension frequency distributions across read files.
  - **Framework Classification**: Scans dependency lists and code contents against signatures for web frameworks (*FastAPI, Django, Flask, React, Next.js, Express, Spring Boot, Gin*).
  - **Dependency Extraction**: Runs targeted regular expression engines over `pyproject.toml`, `package.json`, and `requirements.txt` while filtering out linter flags or license strings.
  - **Entry Point & Architecture Synthesis**: Derives project structure (*e.g., "Layered MVC with separated models and API routes"*). If connected to an LLM (*OpenAI or Ollama*), it sends a structured summary prompt to generate an expert natural language overview.
  - **Chunking**: Passes raw code through `EmbeddingService.chunk_text(max_size=500, overlap=80)` to generate discrete, searchable code blocks.
- **Output**: A unified `RepoKnowledge` schema.

### ⚡ 5. `Memory` (`app/agent/memory.py`)
- **Responsibility**: Persist repository metadata and index code vectors for Retrieval-Augmented Generation (RAG).
- **Implementation**: Maintains a dual-store in-memory architecture:
  1. `knowledge_store`: Maps repository URLs to metadata dictionaries.
  2. `vector_store`: Stores individual text chunks alongside their computed high-dimensional embedding vectors.
- **Search Algorithm**: When queried via `search(query, top_k=5)`, it calculates the dot product / cosine similarity between the query embedding vector and stored chunk vectors. It applies a **keyword boosting multiplier** (`+0.15` per matching query term) to ensure exact method names or variable searches surface instantly.

### 💬 6. `Reporter` (`app/agent/reporter.py`)
- **Responsibility**: Synthesize accurate, codebase-grounded answers to natural language questions.
- **Implementation**: Receives user questions, retrieves the top 4 most relevant code/documentation chunks from `Memory`, and formats an exhaustive RAG context window. It prompts the active LLM engine to generate an accurate response grounded strictly in the provided code snippets.
- **Fallback Engine**: If no LLM is configured, it activates an intelligent keyword-parsing rule engine that constructs detailed Markdown answers using stored dependency trees, architecture summaries, and formatted code chunks.

---

## 4. Triple-Tier Hybrid AI Engine

RepoMind’s AI layer (`app/services/llm.py` & `app/services/embeddings.py`) is designed for maximum versatility:

```text
+-------------------------------------------------------------------------------+
|                             REPOMIND AI LAYER                                 |
+-------------------------------------------------------------------------------+
                                        |
          +-----------------------------+-----------------------------+
          | (Option 1: Local)           | (Option 2: Cloud)           | (Option 3: Offline)
          v                             v                             v
+--------------------+        +--------------------+        +--------------------+
|   Ollama / Qwen    |        |   OpenAI Models    |        |  Local Heuristics  |
|  (100% Free/Local) |        |  (gpt-4o-mini /    |        | (Zero Config / TF- |
|  qwen2.5-coder     |        |   embeddings-3)    |        |  Hashing Vector)   |
+--------------------+        +--------------------+        +--------------------+
```

1. **Tier 1: Local Open-Source LLMs (Ollama / Qwen / Llama)**:
   - When `OLLAMA_MODEL` (*e.g., `qwen2.5-coder:1.5b` or `llama3.2`*) is set in environment variables, RepoMind connects to `http://localhost:11434/v1` using OpenAI-compatible HTTP schemas.
   - All architectural reasoning and RAG chat completions run locally on the user's hardware at zero cost and complete privacy.
2. **Tier 2: Cloud LLMs (OpenAI)**:
   - When `OPENAI_API_KEY` is provided, RepoMind routes completion requests to `gpt-4o-mini` and vector calculations to `text-embedding-3-small`.
3. **Tier 3: Zero-Config Deterministic Heuristics**:
   - If neither cloud nor local models are running, RepoMind activates its custom TF-style hashing vectorizer (`_hash_embedding`) and rule-based response synthesis. The application never crashes and remains 100% functional offline.

---

## 5. Vanilla Glassmorphism Frontend Architecture

The web dashboard (`frontend/`) is engineered to be served directly by FastAPI via `StaticFiles(directory="frontend", html=True)` mounted at root (`/`):
- **Design System**: An obsidian/navy dark mode aesthetic (`#090a0f`) using glowing neon purple/cyan gradients (`#8b5cf6`, `#06b6d4`), glassmorphism backdrop blur (`backdrop-filter: blur(20px)`), and animated floating background glow orbs.
- **State & Storage**: Pure Vanilla JavaScript (`app.js`) managing asynchronous `fetch()` API calls to `/analyze` and `/ask`. It maintains a persistent repository history in browser `localStorage` (`repomind_history`), enabling users to switch between analyzed codebases instantly without re-cloning.
- **Real-Time Visual Feedback**: Features a step-by-step progress animation overlay during analysis (*"Cloning...", "Exploring...", "Building knowledge...", "Indexing vector memory..."*) to provide immediate visual feedback during backend processing.
