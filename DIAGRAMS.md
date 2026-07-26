# 📊 RepoMind Architecture & Workflow Diagrams

This document compiles standalone, professional **Mermaid.js** diagrams illustrating the system architecture, automated analysis lifecycle, RAG vector pipeline, and frontend state machine of **RepoMind**.

---

## 1. High-Level System Architecture
This diagram illustrates the decoupling between the client browser, the FastAPI server, the 6 specialist AI sub-agents, and the persistent vector memory layer.

```mermaid
graph TD
    subgraph Client Layer ["🖥️ Client Layer (Browser)"]
        UI["Vite React JSX Web App<br/>(Obsidian Glassmorphism UI)"]
    end

    subgraph API Layer ["⚡ FastAPI Backend Server"]
        Router["API Router<br/>(POST /analyze, POST /ask)"]
        Orchestrator["RepoMind Orchestrator<br/>(Agent Controller)"]
    end

    subgraph Specialist Agents ["🤖 6 Specialist Sub-Agents"]
        Git["GitService<br/>(Cloning & Remote Access)"]
        Exp["Explorer Agent<br/>(Directory & File Discovery)"]
        Plan["Planner Agent<br/>(Priority Scoring & Filtering)"]
        Read["Reader Agent<br/>(Code Extraction & Formatting)"]
        KB["KnowledgeBuilder<br/>(AST & Dependency Parsing)"]
        Mem["Memory Agent<br/>(RAG Indexing & Vector Store)"]
    end

    subgraph AI Engine & Storage ["🧠 Hybrid AI Engine & Persistent Memory"]
        Embed["EmbeddingService<br/>(Cosine Similarity & Chunking)"]
        LLM["LLMService<br/>(Local Qwen 2.5 / OpenAI Cloud)"]
        Disk[".repomind_memory.json<br/>(Disk Persistence Layer)"]
    end

    UI -->|"HTTP POST /analyze<br/>HTTP POST /ask"| Router
    Router --> Orchestrator
    Orchestrator --> Git & Exp & Plan & Read & KB & Mem
    Mem <--> Embed
    KB <--> LLM
    Mem <-->|"JSON Serialization"| Disk
```

---

## 2. The 7-Step Repository Analysis Lifecycle
This sequence diagram details the exact order of execution from the moment a user submits a GitHub URL to when the repository is fully indexed in memory.

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 Developer
    participant UI as 🖥️ React Dashboard
    participant API as ⚡ FastAPI Server
    participant Git as 📦 GitService
    participant Exp as 🔍 Explorer
    participant Plan as 📋 Planner
    participant Read as 📖 Reader
    participant KB as 🧠 KnowledgeBuilder
    participant Mem as 💾 Memory Agent

    User->>UI: Pastes GitHub URL & Clicks "Analyze"
    UI->>API: POST /analyze { "repo_url": "..." }
    API->>Git: Step 0: Clone Repository to local disk
    Git-->>API: Repository cloned successfully
    API->>Exp: Step 1: Discover files (ignore .lock, node_modules)
    Exp-->>API: Returns list of clean source files
    API->>Plan: Step 2: Rank files by priority (Entry points first)
    Plan-->>API: Returns top 50 prioritized files to read
    API->>Read: Step 3: Read file contents safely
    Read-->>API: Returns raw code strings
    API->>KB: Step 4: Detect language, framework & dependencies
    KB->>KB: Generate code chunks (500 chars, 80 char overlap)
    KB-->>API: Returns structured knowledge metadata
    API->>Mem: Step 5: Compute embedding vectors & store knowledge
    Mem->>Mem: Save vector store to .repomind_memory.json
    Mem-->>API: Memory indexing complete
    API-->>UI: Step 6: Return AnalysisResponse JSON (Status 200 OK)
    UI-->>User: Dashboard metrics update & 7-step timeline lights up!
```

---

## 3. Hybrid RAG Vector Pipeline (`/ask`)
This flowchart maps how natural language queries are embedded, boosted, retrieved from disk memory, and synthesized into citation-backed answers.

```mermaid
flowchart TD
    Start(["💬 User Submits Query<br/>'How does authentication work?'"]) --> EmbedQuery["EmbeddingService.compute_embedding()<br/>(Convert query text to vector float array)"]
    
    EmbedQuery --> LoadDisk["Memory Agent Checks RAM<br/>(If empty, load .repomind_memory.json from disk)"]
    LoadDisk --> SimSearch["Cosine Similarity Calculation<br/>(Compare query vector against stored code chunks)"]
    
    SimSearch --> KeyBoost["Keyword Boosting Algorithm<br/>(+0.15 score boost for matching terms like 'auth', 'jwt')"]
    KeyBoost --> TopK["Select Top-K Relevant Chunks<br/>(Retrieve 3-4 highest scoring source snippets)"]
    
    TopK --> BuildPrompt["Construct Grounded Prompt<br/>(Inject repo metadata + raw code chunks + user question)"]
    BuildPrompt --> CheckEngine{"Which LLM Engine<br/>is Active?"}
    
    CheckEngine -->|"Ollama Running<br/>(OLLAMA_MODEL)"| LocalQwen["🦙 Local Qwen 2.5 Coder (1.5B)<br/>(100% Offline & Private Inference)"]
    CheckEngine -->|"API Key Present<br/>(OPENAI_API_KEY)"| CloudOpenAI["☁️ OpenAI GPT-4o<br/>(Cloud High-Reasoning Completion)"]
    CheckEngine -->|"LLM Offline / Busy"| Heuristics["🛡️ Rule-Based Heuristic Fallback<br/>(Structured Markdown Headers & Bullet Points)"]
    
    LocalQwen --> FormatAns["Format Markdown Answer & Attach Citations<br/>[e.g., openai/_client.py (L1-L50)]"]
    CloudOpenAI --> FormatAns
    Heuristics --> FormatAns
    
    FormatAns --> End(["✅ Return QuestionResponse JSON to Frontend"])
```

---

## 4. Frontend Component Hierarchy & State Flow
This diagram breaks down the Vite React JSX web application architecture, illustrating how state flows down from `App.jsx` to individual components and how API actions trigger visual updates.

```mermaid
graph TD
    subgraph Root ["⚛️ Vite React Root"]
        App["App.jsx<br/>(Main State Orchestrator & API Action Controller)"]
    end

    subgraph Components ["🧱 Presentation Components"]
        Sidebar["Sidebar.jsx<br/>(Repo History, Active Status Dots, Pro Card)"]
        Header["Header.jsx<br/>(System Online Pill, Theme Toggle, User Profile)"]
        Analyzer["Analyzer.jsx<br/>(URL Input Form & 7-Step Horizontal Stepper)"]
        Dashboard["Dashboard.jsx<br/>(4 Stats Cards, Arch Flow Diagram, Dep Grid)"]
        Chat["Chat.jsx<br/>(Ask RepoMind Console, Quick Prompts, Citations)"]
    end

    subgraph Services ["🔌 Services & Storage"]
        API["api.js<br/>(fetch /analyze, fetch /ask)"]
        Local["localStorage<br/>('repomind_react_history')"]
    end

    App -->|"repositories, activeRepoUrl"| Sidebar
    App -->|"isDarkTheme, onToggleTheme"| Header
    App -->|"onAnalyze, isAnalyzing, currentStep"| Analyzer
    App -->|"repoData, archDescription, dependencies"| Dashboard
    App -->|"messages, onSendMessage, isWaiting"| Chat

    Sidebar -->|"onSelectRepo(), onClearMemory()"| App
    Analyzer -->|"handleSubmit(url)"| App
    Chat -->|"handleSend(query)"| App

    App <-->|"analyzeRepositoryAPI()<br/>askQuestionAPI()"| API
    App <-->|"JSON.parse() / JSON.stringify()"| Local
```
