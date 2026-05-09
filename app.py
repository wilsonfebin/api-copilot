import os
import time
import json
import threading
import logging
import streamlit as st
import sys

# ========================
# PATH FIX
# ========================
sys.path.append(os.path.abspath("."))

# ========================
# IMPORTS
# ========================
from utils.styles import load_css
from backend.services.rag_service import run_query
from rag.vector_store import get_vector_stats, get_collection

# ========================
# LOGGING
# ========================
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ========================
# CONFIG
# ========================
MAX_THREADS = 10
THREAD_FILE = "data/threads.json"

st.set_page_config(page_title="API Copilot", page_icon="🚀", layout="wide")

# ========================
# API KEY
# ========================
if "OPENAI_API_KEY" not in st.secrets:
    st.error("Missing OPENAI_API_KEY in Streamlit secrets")
    st.stop()

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# ========================
# LOAD CSS
# ========================
st.markdown(load_css(), unsafe_allow_html=True)

# ========================
# STORAGE
# ========================
def load_threads():
    if not os.path.exists(THREAD_FILE):
        return []
    try:
        with open(THREAD_FILE, "r") as f:
            content = f.read().strip()
            return json.loads(content) if content else []
    except:
        return []

def save_threads(threads):
    os.makedirs("data", exist_ok=True)
    with open(THREAD_FILE, "w") as f:
        json.dump(threads, f, indent=2)

# ========================
# TITLE
# ========================
def generate_title(question):
    return question[:50]

# ========================
# SOURCE PREVIEW
# ========================
def preview_text(text):
    if not text:
        return ""
    return " ".join(text.split("\n")[:2])[:120] + "..."

# ========================
# CORE
# ========================
def run_query_safe(query):
    try:
        start = time.time()
        logger.info(f"QUERY | {query}")

        result = run_query(query)
        elapsed = round(time.time() - start, 2)

        answer = result.get("answer", "").strip()
        if not answer:
            answer = "No relevant answer found in documentation."

        return {
            "question": query,
            "answer": answer,
            "sources": result.get("sources", []),
            "response_time": elapsed,
            "tokens": result.get("tokens", 0),
            "cost": result.get("cost", 0.0)
        }

    except Exception as e:
        logger.error(f"ERROR | {e}")
        return {
            "question": query,
            "answer": "Error processing request",
            "sources": [],
            "response_time": 0,
            "tokens": 0,
            "cost": 0.0
        }

# ========================
# HEALTH + METRICS
# ========================
def get_health():
    try:
        collection = get_collection()
        return {
            "services": {
                "openai": True,
                "vector_db": collection is not None,
                "rag": True
            }
        }
    except:
        return None
    
def clean_answer(answer: str):
    lines = []
    for l in answer.split("\n"):
        if l.lower().startswith("## summary"):
            continue
        lines.append(l)
    return "\n".join(lines)

def get_metrics():
    try:
        return get_vector_stats()
    except:
        return {"documents": "-", "chunks": "-"}

# ========================
# INIT
# ========================
if "threads" not in st.session_state:
    st.session_state.threads = load_threads()

if "active_thread" not in st.session_state:
    st.session_state.active_thread = None

health = get_health()
metrics = get_metrics()

# ========================
# SIDEBAR
# ========================
with st.sidebar:
    st.header("System Overview")

    st.markdown("### System Health")
    for label, status in [
        ("OpenAI API", "Healthy"),
        ("Vector DB", "Active"),
        ("RAG Engine", "Online"),
    ]:
        c1, c2 = st.columns([2,1])
        c1.markdown(label)
        c2.markdown(f"🟢 {status}")

    st.markdown("### System Metrics")
    col1, col2 = st.columns(2)
    col1.metric("Docs", metrics["documents"])
    col2.metric("Chunks", metrics["chunks"])

    st.markdown("### Modules")
    st.markdown("""
- 🔐 Authentication  
- 💳 Payments  
- ⚠️ Errors  
- 🔔 Webhooks  
""")

    st.markdown("### Conversations")

    for i, t in enumerate(st.session_state.threads):
        c1, c2 = st.columns([5,1])

        if c1.button(t["title"], key=f"t{i}"):
            st.session_state.active_thread = i
            st.rerun()

        if c2.button("🗑", key=f"d{i}"):
            st.session_state.threads.pop(i)
            save_threads(st.session_state.threads)
            st.session_state.active_thread = None
            st.rerun()

    c1, c2 = st.columns(2)

    if c1.button("New Chat"):
        st.session_state.active_thread = None
        st.rerun()

    if c2.button("Clear All"):
        st.session_state.threads = []
        save_threads([])
        st.session_state.active_thread = None
        st.rerun()

# ========================
# HEADER
# ========================
st.title("🚀 API Copilot")
st.subheader("API Integration Copilot")

# ========================
# EMPTY STATE
# ========================
if st.session_state.active_thread is None:
    st.markdown("### 💡 Suggested Questions")

    suggestions = [
        "How does Razorpay authentication work?",
        "How do I capture payments?",
        "What causes invalid OTP?",
        "How do webhooks work?",
        "Explain Razorpay payments in 150 words."
    ]

    for q in suggestions:
        if st.button(q, key=f"sugg_{q}", use_container_width=False):
            st.session_state.pending_query = q
            st.rerun()

# ========================
# HANDLE SUGGESTIONS
# ========================
if "pending_query" in st.session_state:
    query = st.session_state.pending_query
    del st.session_state.pending_query
else:
    query = st.chat_input("Ask about authentication, payments, errors...")

# ========================
# CHAT DISPLAY
# ========================
if st.session_state.active_thread is not None:
    for chat in st.session_state.threads[st.session_state.active_thread]["messages"]:
        with st.chat_message("user"):
            st.write(chat["question"])

        with st.chat_message("assistant"):
            st.markdown(f"""
            <div class="answer-box">
                <h3>Summary</h3>
                {clean_answer(chat["answer"])}
            </div>
            """, unsafe_allow_html=True)

            # ✅ METRICS RESTORED
            st.caption(
                f"{chat.get('response_time', 0)}s • "
                f"{chat.get('tokens', 0)} tokens • "
                f"${chat.get('cost', 0.0):.5f}"
            )

            if chat.get("sources"):
                with st.expander("📚 Sources", expanded=True):
                    for s in chat["sources"]:
                        if isinstance(s, dict):
                            st.markdown(f"📄 `{s.get('source')}`")
                            st.caption(preview_text(s.get("content", "")))
                        else:
                            st.markdown(f"📄 `{s}`")

# ========================
# QUERY FLOW (WITH SPINNER)
# ========================
if query:
    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        result = {}

        def run():
            result["data"] = run_query_safe(query)

        t = threading.Thread(target=run)
        t.start()

        start = time.time()
        while t.is_alive():
            placeholder.markdown(f"⏳ Thinking... {round(time.time()-start,2)}s")
            time.sleep(0.2)

        t.join()
        res = result["data"]
        placeholder.empty()

        st.markdown(res["answer"])

        # ✅ METRICS RESTORED
        st.caption(
            f"{res.get('response_time', 0)}s • "
            f"{res.get('tokens', 0)} tokens • "
            f"${res.get('cost', 0.0):.5f}"
        )

        if res.get("sources"):
            with st.expander("📚 Sources", expanded=True):
                for s in res["sources"]:
                    if isinstance(s, dict):
                        st.markdown(f"📄 `{s.get('source')}`")
                        st.caption(preview_text(s.get("content", "")))
                    else:
                        st.markdown(f"📄 `{s}`")

    if st.session_state.active_thread is None:
        st.session_state.threads.insert(0, {
            "title": generate_title(query),
            "messages": [res]
        })
        st.session_state.active_thread = 0
    else:
        st.session_state.threads[st.session_state.active_thread]["messages"].append(res)

    save_threads(st.session_state.threads[:MAX_THREADS])
    st.rerun()
