# 🛠️ RepoMind Installation & Setup Guide

Welcome to the **RepoMind** installation guide! This document provides step-by-step instructions for getting RepoMind up and running on your local machine across **Windows**, **macOS**, and **Linux**.

---

## Table of Contents
1. [System Requirements](#1-system-requirements)
2. [Step 1: Clone the Repository](#step-1-clone-the-repository)
3. [Step 2: Backend Setup (Python & FastAPI)](#step-2-backend-setup-python--fastapi)
4. [Step 3: Frontend Setup (Vite React JSX)](#step-3-frontend-setup-vite-react-jsx)
5. [Step 4: Local AI Engine Setup (Ollama & Qwen 2.5 Coder)](#step-4-local-ai-engine-setup-ollama--qwen-25-coder)
6. [Step 5: Environment Configuration](#step-5-environment-configuration)
7. [Step 6: Running the Full Application](#step-6-running-the-full-application)
8. [Troubleshooting & FAQ](#troubleshooting--faq)

---

## 1. System Requirements
Before starting, ensure your system meets the following minimum requirements:
- **Operating System**: Windows 10/11, macOS 11+, or Linux (Ubuntu 20.04+ recommended).
- **Python**: Version **3.10** or higher (`python --version`).
- **Node.js & npm**: Version **18.0** or higher (`node --version`).
- **Git**: Installed and added to system PATH (`git --version`).
- **RAM**: Minimum 8GB (16GB recommended if running local 7B+ LLM models).
- **Disk Space**: ~3GB free space (includes Python virtualenv, Node modules, and local Qwen LLM weights).

---

## Step 1: Clone the Repository
Open your terminal or command prompt and clone the RepoMind repository to your local workspace:

```bash
git clone https://github.com/Hareshls/repomind.git
cd repomind
```

---

## Step 2: Backend Setup (Python & FastAPI)

We recommend creating an isolated Python virtual environment to manage dependencies without conflicting with system packages.

### **Windows (PowerShell / CMD)**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### **macOS / Linux (Bash / Zsh)**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 3: Frontend Setup (Vite React JSX)

RepoMind features a modern, obsidian-themed React web application located in the `frontend/` directory.

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies (including Lucide icons and Vite)
npm install

# Build the production static bundle into frontend/dist/
npm run build

# Return to root directory
cd ..
```

> [!TIP]
> When `npm run build` completes, the FastAPI backend will automatically serve your compiled React application directly at root `http://127.0.0.1:8000/`. No secondary frontend dev server is required!

---

## Step 4: Local AI Engine Setup (Ollama & Qwen 2.5 Coder)

RepoMind is designed to run **100% locally and free** using open-source LLMs via **Ollama**. We recommend the **Qwen 2.5 Coder (1.5B)** model for lightning-fast repository reasoning and code understanding.

### **1. Install Ollama**
- **Windows / macOS**: Download the installer directly from [https://ollama.com/download](https://ollama.com/download) and run it.
- **Linux**: Run the official install script:
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

### **2. Pull the Qwen 2.5 Coder Model**
Open a terminal and pull the model weights (~1GB):
```bash
ollama pull qwen2.5-coder:1.5b
```

### **3. Verify Ollama is Running**
Verify the Ollama background service is active:
```bash
ollama list
```
You should see `qwen2.5-coder:1.5b` listed in your available models.

---

## Step 5: Environment Configuration

RepoMind works out-of-the-box with zero configuration required. However, you can customize engine behavior by creating a `.env` file in the root directory:

```bash
# Copy example configuration (optional)
cp .env.example .env
```

### **Sample `.env` Configuration**
```ini
# --- Local AI Engine (Default) ---
OLLAMA_MODEL=qwen2.5-coder:1.5b
OLLAMA_BASE_URL=http://localhost:11434/v1

# --- Cloud AI Engine (Optional) ---
# If you prefer OpenAI GPT-4o, uncomment and add your API key below:
# OPENAI_API_KEY=sk-proj-YourOpenAIApiKeyHere
```

---

## Step 6: Running the Full Application

With dependencies installed and Ollama ready, start the unified Uvicorn server:

```bash
# Ensure virtual environment is active
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

You will see output indicating the server has started:
```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process using WatchFiles
INFO:     Application startup complete.
```

### 🎉 Open Your Dashboard!
Open your web browser and navigate to:
### 👉 **http://127.0.0.1:8000/**

You can also access the interactive API documentation at:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Troubleshooting & FAQ

### ❌ `ModuleNotFoundError: No module named 'fastapi'`
- **Cause**: You did not activate the Python virtual environment before starting Uvicorn.
- **Fix**: Run `.\venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux) and try again.

### ❌ `[ERROR] Connection refused to http://localhost:11434`
- **Cause**: The Ollama background application is not running.
- **Fix**: Launch the Ollama desktop app from your system tray or run `ollama serve` in a separate terminal window.

### ❌ `Address already in use: 127.0.0.1:8000`
- **Cause**: Another application or previous Uvicorn instance is using port 8000.
- **Fix**: Either kill the old process or launch RepoMind on a different port:
  ```bash
  uvicorn main:app --reload --port 8080
  ```

### ❌ React Dashboard Shows Blank Page or 404
- **Cause**: You forgot to build the frontend production bundle.
- **Fix**: Navigate to `cd frontend/`, run `npm run build`, and refresh your browser tab (`Ctrl + F5`).
