# API Copilot

API Copilot is a Retrieval-Augmented Generation (RAG) based assistant for understanding, debugging, and integrating APIs using indexed documentation.

---

## Overview

This project enables users to ask natural language questions about APIs and receive structured, context-aware responses powered by:

- Vector search over API documentation  
- LLM-based response generation  
- A decoupled backend service architecture  

---

## Architecture

Streamlit (UI)     ↓ FastAPI (Backend)     ↓ RAG Service Layer     ↓ Vector Database (ChromaDB)

---

## Features

### Core
- RAG-based question answering  
- Context retrieval from indexed documents  
- Structured responses (summary, steps, best practices)  

### UI (Streamlit)
- Chat-based interface  
- Multi-thread conversations (persistent)  
- Real-time response timing  
- Token and cost estimation  
- Suggested queries  
- Subtle, developer-focused UI design  

### Backend (FastAPI)
- /query endpoint for inference  
- /health endpoint for system status  
- Service-layer abstraction for RAG logic  
- Clean API contract  

### System
- Vector store using ChromaDB  
- Token + cost estimation  
- JSON-based thread persistence  

---

## Caching

- Implemented using functools.lru_cache  
- Caches last 50 unique queries  
- Reduces latency for repeated queries  

First query   → full RAG (~5–10s) Repeat query  → near-instant response

---

## Health Monitoring

Backend exposes:

GET /health

Example response:

json {   "status": "ok",   "services": {     "openai": true,     "vector_db": true,     "rag": true   } } 

UI consumes this endpoint to reflect real system state.

---

## Project Structure

api-copilot/
│
├── app.py                      # Streamlit UI
│
├── backend/
│   ├── main.py                # FastAPI entry point
│   ├── routes/
│   │   ├── query.py
│   │   └── health.py
│   ├── services/
│   │   └── rag_service.py
│
├── rag/
│   ├── retrieve.py
│   └── vector_store.py
│
├── utils/
│   ├── styles.py
│   ├── metrics.py
│   └── storage.py
│
├── data/
│   └── threads.json
---

## Running the Project

### 1. Activate virtual environment

source venv/bin/activate

---

### 2. Start backend

python -m uvicorn backend.main:app --reload

Backend runs at:

http://127.0.0.1:8000

---

### 3. Start UI

streamlit run app.py

---

## API Endpoints

### POST /query

Request:

json {   "question": "How do webhooks work?" } 

Response:

json {   "question": "...",   "answer": "...",   "sources": ["..."],   "response_time": 6.2,   "tokens": 210,   "cost": 0.00012 } 

---

### GET /health

Returns system health status.

---

## Design Decisions

- Decoupled architecture  
  UI does not directly call RAG logic; all inference goes through FastAPI  

- Service layer abstraction  
  RAG logic is isolated in rag_service.py  

- In-memory caching  
  Reduces repeated query latency without external dependencies  

- Minimal state persistence  
  Threads stored locally using JSON  

- Backend-driven system status  
  UI reflects actual backend health via /health  

---

## Notes

- Cache is in-memory and resets on restart  
- Cache key is exact query string match  
- No external database used for conversations  
- System is designed for clarity and extensibility  

---

## Next Steps

- Containerization (Docker)  
- Logging and monitoring  
- Improved cache strategy (TTL / distributed)  
- API hardening (timeouts, retries)
