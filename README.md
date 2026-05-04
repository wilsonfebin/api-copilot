# 🚀 API Copilot — RAG-powered API Assistant

A full-stack AI application that answers API-related questions using Retrieval-Augmented Generation (RAG), with cost tracking, caching, and a hardened backend.

---

## 🧠 Overview

API Copilot enables users to query API documentation and receive contextual, intelligent answers powered by LLMs and vector search.

### Key capabilities:
- Context-aware answers using RAG
- Token, cost, and latency tracking
- Chat-based multi-thread UI
- Dockerized full-stack system

---

## 🏗️ Architecture
~~~
Streamlit UI (Frontend)
        ↓
FastAPI Backend
        ↓
RAG Pipeline
        ↓
ChromaDB (Vector Store)
        ↓
OpenAI LLM
~~~
### Design Principles
- Separation of concerns (UI / API / RAG)
- Stateless backend (except cache)
- Modular and extensible
- Config-driven behavior

---

## ⚙️ Tech Stack

### Backend
- FastAPI
- Uvicorn
- Python 3.11

### Frontend
- Streamlit

### AI / RAG
- OpenAI API
- ChromaDB

### Infrastructure
- Docker
- Docker Compose

---

## 🧠 RAG Pipeline

User Query → Retrieve (Top-K) → Context Injection → LLM → Answer

### Features
- Configurable Top-K retrieval
- Context-aware generation
- Source extraction
- Deterministic outputs (low temperature)
- Token & cost estimation

---

## ⚡ Performance Optimizations

### Caching
- LRU cache for repeated queries
- Instant responses for identical inputs
- Reduced API usage cost

### Latency Tracking
- Per-query response time
- Displayed in UI and logs

---

## 🔐 API Hardening

- Rate limiting (per-IP, window-based, /query endpoint)
- Retry logic for transient failures
- Timeout enforcement for long-running requests
- Concurrency control using semaphore
- Graceful error handling

---

## 📊 Logging & Observability

### Logs include:
- Request logs (method, path, latency)
- Query lifecycle (start/end)
- RAG execution details
- Error logging
- Rate limit tracking

### Outputs:
- Console (stdout)
- File logs (logs/app.log)
- Docker volume persistence

---

## 🎛️ Configuration

Centralized configuration for:

- Rate limits
- Retry and timeout settings
- Cache size
- Retrieval parameters (top_k)
- LLM parameters (tokens, temperature)
- Concurrency limits

Supports environment variable overrides.

---

## 🎨 UI / UX

### Chat Interface
- Conversational UI (user + assistant)
- Structured answer containers
- Token, cost, and latency display

### Sidebar Features
- System health indicators (OpenAI, Vector DB, RAG)
- Metrics (documents, chunks)
- Conversation history
- Active thread selection
- Delete / clear actions
- New chat creation

### Conversation System
- Multi-thread support
- Persistent storage (JSON)
- Recency-based ordering

---

## 🐳 Docker Setup

### Services
- api-backend (FastAPI)
- api-ui (Streamlit)

### Features
- Multi-container orchestration
- Shared network
- Volume mounts (logs, DB, data)
- Hot reload for development

---

## 📁 Project Structure
~~~
├── app.py                  # Streamlit UI
├── backend/               # FastAPI backend
│   ├── main.py
│   ├── routes/
│   ├── services/
│   └── utils/
├── rag/                   # Retrieval + generation logic
├── utils/                 # UI styles, metrics
├── data/                  # Conversation storage
├── chroma_db/             # Vector DB persistence
├── docker-compose.yml
├── requirements.txt
├── requirements_backend.txt
├── requirements_ui.txt
└── README.md
~~~
---

## 🚀 Running Locally

### Without Docker

bash # Backend uvicorn backend.main:app --reload  # UI streamlit run app.py 

---

### With Docker

bash docker compose up --build 

Access:
- UI → http://localhost:8501
- Backend → http://localhost:8000

---

## 🔑 Environment Variables

Create .env or configure:

OPENAI_API_KEY=your_api_key

---

## ⚖️ Scope & Design Choices

- Minimal, focused architecture
- No unnecessary infra (Kubernetes, Redis, etc.)
- Designed for clarity, performance, and extensibility

---

## 🏁 Summary

A full-stack, Dockerized RAG-based API assistant with:

- Intelligent retrieval + generation
- Performance optimizations (caching)
- Hardened backend (rate limiting, retry, timeout, concurrency)
- Structured logging and observability
- Clean, chat-based UI
