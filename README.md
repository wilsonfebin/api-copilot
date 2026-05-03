# 🚀 API Copilot

**AI-powered API Integration Assistant for developer support, troubleshooting, and contextual documentation retrieval — built using OpenAI, Chroma, and Retrieval-Augmented Generation (RAG).**

---

## 🎯 Overview

API Copilot is a production-style AI developer assistant that helps engineers:

- Understand API documentation
- Debug authentication and payment issues
- Retrieve contextual answers from real-world technical docs
- Troubleshoot webhook and payment workflows
- Accelerate API integrations with grounded AI responses

This project simulates a practical AI deployment engineering workflow, progressing from foundational LLM integration into a full semantic retrieval and RAG-powered support system.

---

## 🧠 Current Project Status

### ✅ Day 1 — Foundation
- OpenAI LLM integration (`gpt-4o-mini`)
- Embedding generation (`text-embedding-3-small`)
- Secure API key configuration
- Modular Python architecture

---

### ✅ Day 2 — RAG Preparation
- Multi-document ingestion
- Chunking engine
- Curated Razorpay production documentation:
  - Authentication
  - Payments
  - Errors
  - Webhooks

---

### ✅ Day 3 — Semantic Retrieval
- OpenAI embedding pipeline
- Chroma vector database
- Persistent local vector storage
- Semantic search
- Metadata tracking

---

### ✅ Day 4 — Full RAG System
- Query embedding
- Semantic retrieval
- Context injection
- Grounded answer generation
- Source attribution
- Developer-focused API support assistant

---

# ⚙️ Tech Stack

- **Language:** Python 3.11  
- **LLM:** OpenAI `gpt-4o-mini`  
- **Embeddings:** `text-embedding-3-small`  
- **Vector DB:** ChromaDB  
- **Environment Management:** `python-dotenv`  
- **Version Control:** Git + GitHub  

---

# 📁 Project Structure

```text
api-copilot/
├── main.py
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
Grounded API Answers + Sources
```

---

# 🔐 Security Practices

- `.env` for secret management
- `.gitignore` for credential protection
- Real-world API key workflows
- Webhook secret validation
- Production-style authentication coverage

---

# 📚 Documentation Corpus

## Razorpay Authentication
- Basic Auth
- API key management
- Test/Live environments
- Security best practices

---

## Razorpay Payments
- Payment capture
- Payment retrieval
- Orders integration
- Payment lifecycle management

---

## Razorpay Errors
- Structured API failure diagnostics
- Retry scenarios
- Customer troubleshooting
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

### Authentication
```text
How does Razorpay API authentication work?
```

### Payments
```text
How do I capture an authorized payment?
```

### Errors
```text
What does invalid OTP mean in Razorpay?
```

### Webhooks
```text
How do I validate Razorpay webhooks?
```

---

# 📊 Current Capabilities

### Retrieval:
- Semantic search
- Multi-document knowledge retrieval
- Metadata-aware chunking

### Answer Generation:
- Grounded technical responses
- Reduced hallucination risk
- Source attribution
- Developer-grade explanations

### Business Value:
- Developer productivity
- Faster integrations
- API troubleshooting
- Customer support enablement

---

# 🔒 Engineering Best Practices Applied

- Modular architecture
- Clean code separation
- Persistent storage
- Source transparency
- Low-temperature prompt design
- Production-style system progression
- Real-world documentation curation

---

# 🚀 Sample Day 4 Output

```text
Question:
How does Razorpay API authentication work?

Answer:
Razorpay API authentication is based on Basic Authentication using Key ID and Key Secret...

Sources:
- razorpay_auth.txt
- razorpay_errors.txt
```

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

## Phase 2 — Productization
- [ ] Streamlit UI
- [ ] Chat interface
- [ ] Query history
- [ ] Better citations
- [ ] UX improvements

## Phase 3 — Production Hardening
- [ ] Retry logic
- [ ] Monitoring
- [ ] Analytics
- [ ] Deployment
- [ ] Scaling infrastructure

---

# 🌍 Practical Impact

API Copilot demonstrates how modern AI systems can enhance:

- Developer productivity
- API troubleshooting
- Technical documentation accessibility
- Payment system integrations
- Event-driven support workflows

By combining semantic retrieval with grounded answer generation, the platform reduces time spent navigating fragmented documentation and improves technical execution efficiency.

---

# 📌 Current Status

## 🟢 Day 4 Complete  
## 🔜 Day 5: UI + Productization

---

# 👤 Author

**Febin Wilson**  
Engineering leader transitioning into AI deployment, startup technical architecture, and applied LLM systems.

---

# 🚀 Long-Term Vision

To evolve API Copilot into a production-grade AI platform capable of:

- API support
- Integration guidance
- Debugging
- Developer productivity
- Startup deployment advisor
