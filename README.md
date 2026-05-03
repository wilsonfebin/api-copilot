# 🚀 API Copilot

**AI-powered API Integration Assistant for developer support, troubleshooting, and contextual documentation retrieval — built using OpenAI, Chroma, Streamlit, and Retrieval-Augmented Generation (RAG).**

---

## 🎯 Overview

API Copilot is a production-style AI developer assistant designed to help engineers:

- Understand API documentation
- Debug authentication and payment issues
- Retrieve contextual answers from real-world technical documentation
- Troubleshoot webhook workflows
- Accelerate API integrations with grounded AI responses
- Interact through a productized chat-based developer support interface

This project simulates a modern AI deployment engineering workflow, progressing from foundational LLM integration into a full-stack RAG-powered developer productivity platform.

---

## 🧠 Current Project Status

### ✅ Day 1 — Foundation
- OpenAI LLM integration (`gpt-4o-mini`)
- Embedding generation (`text-embedding-3-small`)
- Secure API key management
- Modular Python architecture

---

### ✅ Day 2 — RAG Preparation
- Multi-document ingestion
- Chunking pipeline
- Curated Razorpay production documentation:
  - Authentication
  - Payments
  - Errors
  - Webhooks

---

### ✅ Day 3 — Semantic Retrieval
- Embedding pipeline
- Chroma vector database
- Persistent vector storage
- Metadata tracking
- Semantic search

---

### ✅ Day 4 — Full RAG System
- Query embedding
- Semantic retrieval
- Context injection
- Grounded answer generation
- Source attribution

---

### ✅ Day 5 — Productization
- Streamlit UI
- ChatGPT-style conversational interface
- Sidebar architecture
- Thread-aware session history
- Suggested prompts
- Status badges
- Source expanders
- Performance timing
- Product-grade UX polish

---

# ⚙️ Tech Stack

- **Language:** Python 3.11  
- **LLM:** OpenAI `gpt-4o-mini`  
- **Embeddings:** `text-embedding-3-small`  
- **Vector Database:** ChromaDB  
- **Frontend/UI:** Streamlit  
- **Environment Management:** `python-dotenv`  
- **Version Control:** Git + GitHub  

---

# 📁 Project Structure

```text
api-copilot/
├── main.py
├── app.py
├── .env
├── .gitignore
├── requirements.txt
│
├── llm/
│   └── client.py
│
├── rag/
│   ├── ingest.py
│   ├── chunk.py
│   ├── embed.py
│   ├── vector_store.py
│   └── retrieve.py
│
├── chroma_db/
│
└── data/
    ├── razorpay_auth.txt
    ├── razorpay_payments.txt
    ├── razorpay_errors.txt
    └── razorpay_webhooks.txt
```

---

# 🧠 Full System Architecture

```text
Real API Docs
   │
   ▼
Document Ingestion
   │
   ▼
Chunking Pipeline
   │
   ▼
OpenAI Embeddings
   │
   ▼
Chroma Vector DB
   │
   ▼
Semantic Retrieval
   │
   ▼
Context Injection
   │
   ▼
OpenAI LLM
   │
   ▼
Grounded API Answers
   │
   ▼
Streamlit Chat Interface
```

---

# 💻 Core Interfaces

## CLI RAG Pipeline (`main.py`)
```text
User Query
   │
   ▼
Retrieve Context
   │
   ▼
Generate Grounded Answer
   │
   ▼
Display Sources
```

---

## Product UI (`app.py`)
```text
User Chat Input
   │
   ▼
Semantic Retrieval
   │
   ▼
LLM Answer
   │
   ▼
Chat Thread
   │
   ▼
Source Display + Session History
```

---

# 🔐 Security Practices

- `.env` for secret management
- `.gitignore` for credential protection
- Secure API key workflows
- Webhook secret validation
- Authentication best practices
- Production-style credential hygiene

---

# 📚 Documentation Corpus

## Razorpay Authentication
- Basic Auth
- Key management
- Live/Test modes
- Security workflows

---

## Razorpay Payments
- Payment capture
- Payment retrieval
- Orders integration
- Lifecycle management

---

## Razorpay Errors
- Error diagnostics
- Failure reasons
- Retry scenarios
- Monitoring workflows

---

## Razorpay Webhooks
- Event subscriptions
- Signature validation
- Refunds
- Partner onboarding
- Event-driven architecture

---

# 🧪 Example Supported Queries

```text
How does Razorpay API authentication work?
How do I capture payments?
What causes invalid OTP?
How do webhooks work?
Explain Razorpay payments in 150 words.
```

---

# 📊 Current Capabilities

### Retrieval:
- Semantic search
- Multi-document indexing
- Metadata-aware retrieval
- Source attribution

---

### Answer Generation:
- Grounded technical responses
- Reduced hallucination risk
- Developer-focused guidance
- Context-aware API troubleshooting

---

### Product UX:
- Chat-style interface
- Session threads
- Suggested prompts
- Response timing
- Expandable sources
- Sidebar module navigation

---

### Business Value:
- Developer productivity
- API support
- Integration acceleration
- Troubleshooting automation
- Startup deployment readiness

---

# 🚀 Sample Product Output

```text
Question:
How does Razorpay authentication work?

Answer:
Razorpay authentication uses Basic Authentication with Key ID and Key Secret
encoded into the Authorization header...

Sources:
📄 razorpay_auth.txt
📄 razorpay_errors.txt

Response Time:
7.2s
```

---

# 🔒 Engineering Best Practices Applied

- Modular architecture
- Product-first iteration
- Persistent vector storage
- Source transparency
- Session-aware UX
- Prompt optimization
- Real-world documentation curation
- Clean deployment structure

---

# 🌍 Practical Impact

API Copilot demonstrates how modern AI systems can improve:

- Developer productivity
- API troubleshooting
- Technical support automation
- Payment system integrations
- Event-driven support workflows
- Startup technical enablement

By combining semantic retrieval with grounded generation and user-facing productization, API Copilot reduces technical friction and accelerates operational execution.

---

# 🗺️ Roadmap

## Phase 1 — Complete
- [x] LLM integration
- [x] Embeddings
- [x] Document ingestion
- [x] Chunking
- [x] Chroma vector storage
- [x] Semantic retrieval
- [x] Full RAG answering
- [x] Streamlit UI
- [x] Product-grade chat UX

---

## Phase 2 — Production Hardening
- [ ] Retry logic
- [ ] Rate limiting
- [ ] Query caching
- [ ] Monitoring
- [ ] Performance optimization
- [ ] Deployment

---

## Phase 3 — Scaling
- [ ] Multi-doc expansion
- [ ] Advanced citation system
- [ ] Observability
- [ ] Team workflows
- [ ] Enterprise integrations

---

# 📌 Current Status

## 🟢 Day 5 Complete  
## 🔜 Day 6: Production Hardening + Deployment Readiness

---

# 👤 Author

**Febin Wilson**  
Engineering leader transitioning into AI deployment, startup technical architecture, and applied LLM systems.

---

# 🚀 Long-Term Vision

To evolve API Copilot into a production-grade AI developer platform capable of:

- API support
- Integration guidance
- Technical troubleshooting
- Developer productivity
- Startup enablement
- Enterprise deployment advisor
