# 📖 RepoMind User Guide & Best Practices

Welcome to the **RepoMind User Guide**! This manual will teach you how to effectively use RepoMind's web dashboard, analyze GitHub repositories, leverage advanced prompting strategies, and manage your local RAG vector memory.

---

## Table of Contents
1. [Dashboard Overview](#1-dashboard-overview)
2. [Analyzing a New Repository](#2-analyzing-a-new-repository)
3. [Understanding the 7-Step Timeline](#3-understanding-the-7-step-timeline)
4. [Interactive Chat & Prompting Strategies](#4-interactive-chat--prompting-strategies)
5. [Memory Management & Export](#5-memory-management--export)
6. [Switching AI Engines (Local vs Cloud)](#6-switching-ai-engines-local-vs-cloud)
7. [Pro Tips & Best Practices](#7-pro-tips--best-practices)

---

## 1. Dashboard Overview

When you access RepoMind at `http://127.0.0.1:8000/`, you are presented with a unified, obsidian-themed repository intelligence interface composed of three main sections:

1. **Left Sidebar**: Displays your history of analyzed repositories (with green status dots indicating the currently active workspace), quick action shortcuts, and system settings.
2. **Top Analyzer Bar**: An input field where you paste GitHub URLs or local repository paths to initiate the automated AI analysis pipeline.
3. **Intelligence Workspace**: Displays 4 real-time metrics cards (*Language, Framework, Entry Point, Files Indexed*), an interactive Architecture Overview, Top Dependencies cloud, and the two-column **Ask RepoMind** chat console.

---

## 2. Analyzing a New Repository

To begin exploring a repository:
1. Locate the **Analyze New Repository** card at the top of the dashboard.
2. Paste any valid GitHub repository HTTPS URL (or local directory path):
   ```text
   https://github.com/openai/openai-python
   ```
3. Click the glowing purple **🚀 Analyze Repository** button.

---

## 3. Understanding the 7-Step Timeline

As soon as you click **Analyze Repository**, RepoMind's 6 specialist sub-agents initiate a sequential analysis lifecycle. You can watch their progress live via the animated horizontal timeline stepper:

| Step # | Stage Name | Agent Responsible | What Happens Under the Hood |
| :---: | :--- | :--- | :--- |
| **0** | **Cloning** | `GitService` | Clones the remote repository into local workspace `repositories/<repo_name>/`. |
| **1** | **Exploring** | `Explorer` | Scans the directory tree while filtering out lockfiles (`package-lock.json`), `.git`, and `node_modules`. |
| **2** | **Planning** | `Planner` | Ranks files by priority, identifying entry points (`main.py`), manifests (`package.json`), and core logic. |
| **3** | **Reading** | `Reader` | Reads file contents up to safety thresholds, formatting source code for embedding. |
| **4** | **Building Knowledge**| `KnowledgeBuilder` | Detects primary languages, web frameworks, and extracts clean module summaries. |
| **5** | **Indexing Memory** | `Memory` | Computes semantic vector embeddings and persists them to `.repomind_memory.json` on disk. |
| **6** | **Completed** | *System* | Workspace is ready! The dashboard metrics populate automatically. |

---

## 4. Interactive Chat & Prompting Strategies

The bottom half of the dashboard features the **Ask RepoMind** console. You can click any of the 5 quick action prompts on the left or type custom natural language queries on the right.

### **How Citations Work**
Every AI response is backed by **grounded file citations**. Below the AI bubble, you will see badges pointing directly to the exact source files and line ranges that contributed to the answer:
```text
📄 openai/_client.py (L1-L50)   📄 openai/_auth.py (L1-L50)
```

### **Effective Prompting Patterns**

#### 1. Architectural Queries
Ask about high-level system design and data flow:
- *"Explain the overall architecture and layer separation."*
- *"What are the primary modules and how do they communicate?"*
- *"How is state management structured across frontend components?"*

#### 2. Security & Authentication
Investigate security practices and access control:
- *"How does authentication work in this repository?"*
- *"Where are API keys or JWT tokens validated?"*
- *"Show how environment variables and secrets are handled."*

#### 3. Error Handling & Resilience
Examine fault tolerance and exception guardrails:
- *"Show the error handling approach across API endpoints."*
- *"How are database connection failures caught and logged?"*
- *"What custom exception classes are defined in this codebase?"*

#### 4. Implementation How-Tos
Ask for practical integration guidance:
- *"How to make an authenticated API request using this library?"*
- *"Show a code snippet for initializing the database client."*
- *"Where do I add a new API endpoint in this project?"*

---

## 5. Memory Management & Export

RepoMind automatically saves all repository knowledge and vector embeddings to disk (`.repomind_memory.json`). You can manage this memory from the left sidebar:

- **Switching Repositories**: Click any repository name in the sidebar list to instantly switch the active workspace and load its stored knowledge without re-cloning!
- **Clear Current Memory**: Click **Trash2 Clear Current Memory** to wipe the active session history and vector store if you want to start fresh.
- **Export Knowledge**: Click **DownloadCloud Export Knowledge** to download a clean, structured JSON file containing all metadata, architecture summaries, and dependencies for your own reporting tools.

---

## 6. Switching AI Engines (Local vs Cloud)

By default, RepoMind runs offline using your local **Qwen 2.5 Coder** model via Ollama. You can switch engines at any time by editing your environment or `.env` file:

### **Running 100% Offline (Default)**
Ensure Ollama is running and set:
```ini
OLLAMA_MODEL=qwen2.5-coder:1.5b
OLLAMA_BASE_URL=http://localhost:11434/v1
```

### **Switching to OpenAI Cloud Models**
If you want to use cloud-based GPT-4o for complex reasoning, add your API key:
```ini
OPENAI_API_KEY=sk-proj-YourOpenAIApiKeyHere
```
When an OpenAI API key is detected, `LLMService` automatically prioritizes cloud completion while keeping local embeddings fast and free.

---

## 7. Pro Tips & Best Practices

1. **Avoid Giant Monoliths**: For optimal vector search accuracy, analyze modular repositories or specific microservices rather than multi-gigabyte monorepos.
2. **Use Quick Prompts as Starting Points**: Click *"Explain the architecture"* first when exploring an unfamiliar codebase to build mental context before diving into specific line-level questions.
3. **Check Your Ollama Service**: If chat responses feel instant and fallback to structured bullet points without generating conversational paragraphs, check your terminal to ensure the Ollama application hasn't gone to sleep!
