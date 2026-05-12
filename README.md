API Copilot — Agentic RAG Platform

AI-powered API Integration Copilot built using FastAPI, Streamlit, OpenAI APIs, ChromaDB, and Dockerized microservices.

The platform combines Retrieval-Augmented Generation (RAG), agentic retrieval workflows, intent-aware routing, vector search, and structured observability to provide grounded, developer-focused API assistance.

⸻

🚀 Features

Core AI Features

* Retrieval-Augmented Generation (RAG)
* Semantic vector search using embeddings
* Intent-based retrieval routing
* Agentic workflow orchestration
* Metadata-filtered document retrieval
* Source-grounded LLM responses
* Context-aware answer generation
* Word-limit aware response compression

⸻

Agentic Workflow Features

* Query intent classification
* Retrieval tool selection
* Source-filtered vector retrieval
* Workflow orchestration layer
* Retrieval tracing and observability
* Structured agent logging

Supported intents:

* AUTH
* PAYMENTS
* ERRORS
* WEBHOOKS
* GENERAL

⸻

Platform Features

* Dockerized frontend/backend architecture
* FastAPI backend services
* Streamlit interactive UI
* Conversation persistence
* Source visibility
* Frontend/backend latency tracking
* Token and cost monitoring
* Health monitoring APIs
* Metrics APIs
* Structured logging

⸻

🏗 Architecture

                    ┌────────────────────┐
                    │   Streamlit UI     │
                    │    (Frontend)      │
                    └─────────┬──────────┘
                              │ HTTP
                              ▼
                    ┌────────────────────┐
                    │     FastAPI        │
                    │      Backend       │
                    └─────────┬──────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │ Agentic Workflow Layer │
                  │                        │
                  │ • Intent Router        │
                  │ • Tool Registry        │
                  │ • Workflow Engine      │
                  └─────────┬──────────────┘
                            │
                            ▼
                  ┌────────────────────────┐
                  │      RAG Pipeline      │
                  │                        │
                  │ • Embeddings           │
                  │ • Retrieval            │
                  │ • Prompting            │
                  │ • Compression          │
                  └─────────┬──────────────┘
                            │
          ┌─────────────────┴─────────────────┐
          ▼                                   ▼
┌────────────────────┐             ┌────────────────────┐
│     ChromaDB       │             │     OpenAI API     │
│    Vector Store    │             │   LLM + Embedding  │
└────────────────────┘             └────────────────────┘

🧠 Agentic Workflow

The platform uses a modular agentic retrieval workflow instead of a simple chatbot pipeline.

Flow

User Query
→ Intent Classification
→ Tool Selection
→ Metadata-based Retrieval Filtering
→ Context Retrieval
→ LLM Response Generation
→ Structured Logging & Metrics

📂 Project Structure

api-copilot/
│
├── app.py                         # Streamlit frontend
│
├── backend/
│   ├── main.py                    # FastAPI entrypoint
│   │
│   ├── agents/
│   │   ├── intent_router.py       # Query intent classification
│   │   ├── tool_registry.py       # Retrieval tool mapping
│   │   └── workflow.py            # Agent orchestration layer
│   │
│   ├── routes/
│   │   ├── query.py               # Main query endpoint
│   │   ├── health.py              # Health API
│   │   └── metrics.py             # Metrics API
│   │
│   ├── services/
│   │   └── rag_service.py         # Core RAG service layer
│   │
│   ├── utils/
│   │   └── logger.py              # Structured logging
│   │
│   └── config.py                  # Backend config
│
├── rag/
│   ├── ingest.py                  # Document ingestion
│   ├── chunk.py                   # Text chunking
│   ├── embed.py                   # Embedding generation
│   ├── retrieve.py                # Retrieval pipeline
│   └── vector_store.py            # ChromaDB integration
│
├── llm/
│   └── client.py                  # OpenAI client wrapper
│
├── utils/
│   ├── metrics.py                 # Token & cost estimation
│   ├── styles.py                  # Streamlit styling
│   └── storage.py                 # Persistence helpers
│
├── data/
│   ├── razorpay_auth.txt
│   ├── razorpay_payments.txt
│   ├── razorpay_errors.txt
│   └── razorpay_webhooks.txt
│
├── chroma_db/                     # Persistent vector DB
│
├── logs/
│   └── app.log
│
├── docker-compose.yml
├── Dockerfile.ui
├── requirements_backend.txt
├── requirements_ui.txt
└── README.md

⚙️ Tech Stack

Frontend: Streamlit
Backend: FastAPI
LLM: OpenAI GPT APIs
Embeddings: OpenAI Embeddings
Vector Database: ChromaDB
Architecture: Retrieval-Augmented Generation (RAG)
Agentic Layer: Intent Routing + Retrieval Orchestration
Observability: Structured Logging + Latency Metrics
Deployment: Docker + Docker Compose
Language: Python


🔍 Observability & Metrics

The platform includes structured observability for debugging and tracing LLM workflows.

Tracked Metrics

* Backend latency
* Frontend latency
* Token usage
* Cost estimation
* Retrieval sources
* Intent routing
* Workflow state
* Request tracing

⸻

📊 Example Workflow Logs

api-backend  | 2026-05-12 07:37:18,446 | INFO | RATE STATUS | 172.18.0.3 | 0/20
api-backend  | 2026-05-12 07:37:18,450 | INFO | QUERY START | How does Razorpay authentication work?
api-backend  | 2026-05-12 07:37:18,450 | INFO | AGENT ROUTER | intent=Intent.AUTH | tool={'collection': 'auth'}
api-backend  | 2026-05-12 07:37:18,451 | INFO | RAG START | intent=Intent.AUTH | question=How does Razorpay authentication work?
api-backend  | 2026-05-12 07:37:20,942 | INFO | RETRIEVAL START | intent=Intent.AUTH | source_filter=None
api-backend  | 2026-05-12 07:37:20,966 | INFO | RETRIEVAL SOURCES | ['razorpay_auth.txt', 'razorpay_auth.txt']
api-backend  | 2026-05-12 07:37:30,780 | INFO | RAG DONE | intent=Intent.AUTH | 6.93s | tokens=246
api-backend  | 2026-05-12 07:37:30,782 | INFO | QUERY DONE | 6.93s | tokens=246 | cost=0.000144

🚀 Future Enhancements

* LangGraph orchestration
* Hybrid search (BM25 + vector)
* Redis caching
* Streaming responses
* OpenTelemetry tracing
* Evaluation pipelines
* Hallucination scoring
* Kubernetes deployment
* RBAC and guardrails
* Multi-step agent workflows

📌 Key Engineering Concepts Implemented

* Retrieval-Augmented Generation (RAG)
* Agentic retrieval orchestration
* Intent-aware routing
* Vector similarity search
* Metadata-based filtering
* Source-grounded responses
* Structured observability
* Frontend/backend separation
* Dockerized microservices
* Modular backend architecture

