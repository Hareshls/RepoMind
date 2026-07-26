# 🎬 RepoMind Demo Video & Presentation Script

This document provides a professional, step-by-step presentation script and recording guide for creating a 3-minute video demonstration of **RepoMind**. This script is designed to showcase your project to prospective employers, open-source reviewers, and technical audiences.

---

## 📽️ Video Recording Checklist
- **Screen Resolution**: Record in 1080p (1920x1080) or 4K at 60 FPS.
- **Browser Window**: Maximize your browser tab at `http://127.0.0.1:8000/`. Close unneeded tabs and bookmarks bars for a clean look.
- **Terminal Readiness**: Keep a terminal open in the background with Uvicorn and Ollama running so you can show live server logs if desired.
- **Theme**: Ensure the **Dark Obsidian Theme** is active for maximum visual impact.

---

## 🕒 Section 1: The Hook & Introduction (0:00 - 0:30)

**[Visual Action]**: Start on the main RepoMind dashboard with the glowing background orbs visible. Slowly move your mouse over the header and sidebar.

> **[Voiceover]**:  
> *"Hello everyone! Today I'm excited to present **RepoMind**, an autonomous AI repository intelligence and interactive RAG system.  
> Modern codebases can contain thousands of files, making it difficult for developers to onboard, understand architectural layers, or locate critical security routines. RepoMind solves this by combining a specialized 6-agent analysis pipeline with local vector memory and open-source LLMs to transform any Git repository into an interactive, citation-backed knowledge base—all running 100% locally and free."*

---

## 🕒 Section 2: Automated 7-Step Repository Analysis (0:30 - 1:15)

**[Visual Action]**:  
1. Copy a GitHub repository URL (*e.g., `https://github.com/openai/openai-python`*).
2. Paste it into the top **Analyze New Repository** input box.
3. Click the glowing purple **🚀 Analyze Repository** button.
4. Point your cursor to the horizontal timeline stepper as it lights up from Step 0 to Step 6.

> **[Voiceover]**:  
> *"Let's see it in action. I'll paste the official OpenAI Python SDK repository URL and initiate analysis.  
> Notice our real-time 7-step execution timeline. Under the hood, RepoMind orchestrates 6 specialist sub-agents:
> First, our GitService clones the repository. Next, the Explorer agent scans directory trees while automatically filtering out noisy lockfiles and dependencies. Our Planner agent ranks source files by architectural importance, while the Reader and KnowledgeBuilder extract AST syntax and module summaries. Finally, our Memory agent computes semantic embedding vectors and saves the indexed knowledge directly to persistent disk memory."*

---

## 🕒 Section 3: Intelligence Workspace & Architecture Overview (1:15 - 1:45)

**[Visual Action]**:  
1. When analysis finishes, show the 4 top metric cards (*Language: Python, Framework: SDK, Entry Point: __init__.py, Files Indexed: 50*).
2. Scroll down to highlight the **Architecture Flow Diagram** box and the **Top Dependencies** cloud grid.

> **[Voiceover]**:  
> *"Within seconds, the analysis is complete! The dashboard populates our core metrics, identifying the primary language, framework, and entry points.  
> Below, RepoMind maps out an interactive Architecture Overview, breaking down the separation between client modules, HTTP request routing, and authentication layers, alongside a complete dependency matrix."*

---

## 🕒 Section 4: Grounded RAG Chat & File Citations (1:45 - 2:30)

**[Visual Action]**:  
1. Scroll down to the **Ask RepoMind** console.
2. Click the quick prompt button: **"How does authentication work?"**
3. While the AI is typing, mention local inference.
4. Point to the markdown headers (`### 🔐 Authentication & Security Model`) and highlight the clickable citation badges at the bottom: `📄 openai/_client.py (L1-L50)`.

> **[Voiceover]**:  
> *"Now for the most powerful feature: interactive repository reasoning. Let's ask RepoMind how authentication is handled in this codebase.  
> Right now, our query is converted into an embedding vector, performing a cosine similarity search across our indexed disk memory with keyword boosting. The retrieved code chunks are sent to our local **Qwen 2.5 Coder** model running offline via Ollama.  
> Look at the response: a structured, beautifully formatted breakdown of API key initialization and authorization headers. Best of all, notice the grounded citations at the bottom! RepoMind tells us exactly which file and line range contributed to this answer, eliminating AI hallucinations and allowing us to jump straight to the source."*

---

## 🕒 Section 5: Memory Persistence & Conclusion (2:30 - 3:00)

**[Visual Action]**:  
1. Click the **sidebar repository list**, showing how switching between `openai-python` and `Fitness_monitor` loads stored memory instantly without re-cloning.
2. Click the **DownloadCloud Export Knowledge** button to show the downloaded JSON report.

> **[Voiceover]**:  
> *"Because RepoMind features auto-syncing disk persistence, all analyzed repositories remain in memory across server restarts. You can seamlessly switch between repositories in your sidebar or export the full intelligence report as JSON.  
> Whether you're onboarding new engineers, auditing security models, or navigating unfamiliar codebases, RepoMind delivers instant, citation-backed repository mastery. Thank you for watching!"*
