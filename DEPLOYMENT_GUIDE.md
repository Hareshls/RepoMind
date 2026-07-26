# 🚀 RepoMind Production Deployment & Launch Guide

This document provides definitive instructions for deploying **RepoMind** to staging and production environments using **Docker**, **Nginx**, and local **systemd** services, along with guidelines for packaging the final GitHub release.

---

## Table of Contents
1. [Deployment Architecture](#1-deployment-architecture)
2. [Option A: Containerized Deployment (Docker & Docker Compose)](#2-option-a-containerized-deployment-docker--docker-compose)
3. [Option B: Bare-Metal / Virtual Machine Deployment (Systemd + Nginx)](#3-option-b-bare-metal--virtual-machine-deployment-systemd--nginx)
4. [Frontend Production Bundle Verification](#4-frontend-production-bundle-verification)
5. [GitHub Release Packaging Checklist](#5-github-release-packaging-checklist)

---

## 1. Deployment Architecture

In a production environment, RepoMind operates as a **unified decoupled application**:
- The React frontend is compiled into static HTML, CSS, and JS files located in `frontend/dist/`.
- The FastAPI server (`main.py`) serves these static assets directly from root `/` while exposing the REST API at `/analyze` and `/ask`.
- Persistent vector memory is written to `.repomind_memory.json` on the local disk or Docker volume.

---

## 2. Option A: Containerized Deployment (Docker & Docker Compose)

Docker is the recommended deployment method for cloud VPS instances (*e.g., AWS EC2, DigitalOcean Droplet, Hetzner Cloud*) and enterprise environments.

### **1. Create `Dockerfile`**
In the root repository directory, create a `Dockerfile`:
```dockerfile
# Stage 1: Build React Frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Python Backend Server
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Install system git required by GitService
RUN apt-get update && apt-get install -y --no-install-recommends git curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Copy compiled frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose server port
EXPOSE 8000

# Launch Uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **2. Create `docker-compose.yml`**
To link RepoMind with a local containerized Ollama instance:
```yaml
version: '3.8'

services:
  repomind:
    build: .
    container_name: repomind_app
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_MODEL=qwen2.5-coder:1.5b
      - OLLAMA_BASE_URL=http://ollama:11434/v1
    volumes:
      - repomind_memory:/app
      - repomind_repos:/app/repositories
    depends_on:
      - ollama
    restart: always

  ollama:
    image: ollama/ollama:latest
    container_name: repomind_ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_storage:/root/.ollama
    restart: always

volumes:
  repomind_memory:
  repomind_repos:
  ollama_storage:
```

### **3. Launch the Stack**
```bash
docker-compose up -d --build
```
After launch, pull the Qwen model into the Ollama container:
```bash
docker exec -it repomind_ollama ollama pull qwen2.5-coder:1.5b
```
Your containerized app is now live at `http://localhost:8000/`!

---

## 3. Option B: Bare-Metal / Virtual Machine Deployment (Systemd + Nginx)

If deploying to an existing Linux server without Docker, use Nginx as a reverse proxy in front of a systemd Uvicorn service.

### **1. Create Systemd Service File** (`/etc/systemd/system/repomind.service`)
```ini
[Unit]
Description=RepoMind AI Repository Intelligence Daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/repomind
Environment="PATH=/var/www/repomind/venv/bin:/usr/local/bin:/usr/bin"
Environment="OLLAMA_MODEL=qwen2.5-coder:1.5b"
ExecStart=/var/www/repomind/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
```

### **2. Enable and Start the Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable repomind
sudo systemctl start repomind
sudo systemctl status repomind
```

### **3. Configure Nginx Reverse Proxy** (`/etc/nginx/sites-available/repomind`)
```nginx
server {
    listen 80;
    server_name repomind.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Enable WebSocket and HTTP/1.1 support for long-running analyses
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 300s;
    }
}
```

---

## 4. Frontend Production Bundle Verification
Before deploying to any environment, always verify that your React frontend is cleanly built and synced:
```bash
cd frontend/
npm ci
npm run build
```
Verify that `frontend/dist/index.html` exists and that `main.py` is configured with `StaticFiles(directory="frontend/dist")`.

---

## 5. GitHub Release Packaging Checklist

When preparing to publish **RepoMind v1.0.0** on GitHub:

- [x] **Sanitize Secrets**: Ensure `.env` is listed in `.gitignore` and that no hardcoded API keys exist in the codebase.
- [x] **Verify Lockfile Exclusions**: Confirm that `app/agent/explorer.py` ignores `package-lock.json`, `poetry.lock`, and `.lock` files.
- [x] **Tag Release**: Create an annotated git tag:
  ```bash
  git tag -a v1.0.0 -m "Release v1.0.0: Full AI Repository Intelligence & RAG System"
  git push origin v1.0.0
  ```
- [x] **Draft GitHub Release Notes**: Include links to `README.md`, `ARCHITECTURE.md`, `API_DOCUMENTATION.md`, and attach screenshot demos!
