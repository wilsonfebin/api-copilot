import os
import time
import json
import threading
import requests
import streamlit as st

from rag.vector_store import get_vector_stats
from utils.styles import load_css


# ========================
# CONFIG
# ========================
MAX_THREADS = 10
THREAD_FILE = "data/threads.json"
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="API Copilot", page_icon="🚀", layout="wide")


# ========================
# STORAGE
# ========================
def load_threads():
    if not os.path.exists(THREAD_FILE):
        return []
    try:
        with open(THREAD_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except:
        return []


def save_threads(threads):
    os.makedirs("data", exist_ok=True)
    tmp = THREAD_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(threads, f, indent=2)
    os.replace(tmp, THREAD_FILE)


# ========================
# BACKEND CALLS
# ========================
def call_backend(query):
    try:
        res = requests.post(
            f"{BACKEND_URL}/query",
            json={"question": query},
            timeout=30
        )
        return res.json()
    except Exception as e:
        return {"error": str(e)}


def get_health():
    try:
        res = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return res.json()
    except:
        return None


# ========================
# INIT
# ========================
st.markdown(load_css(), unsafe_allow_html=True)

vector_stats = get_vector_stats()
health = get_health()

if "threads" not in st.session_state:
    st.session_state.threads = load_threads()

if "active_thread" not in st.session_state:
    st.session_state.active_thread = None


# ========================
# HEALTH STATUS
# ========================
if health:
    openai_status = "Healthy" if health["services"]["openai"] else "Missing"
    vector_status = "Active" if health["services"]["vector_db"] else "Down"
    rag_status = "Online" if health["services"]["rag"] else "Down"
else:
    openai_status = "Down"
    vector_status = "Down"
    rag_status = "Down"


# ========================
# HEADER
# ========================
st.title("🚀 API Copilot")
st.subheader("API Integration Copilot")
st.caption(
    "RAG-powered assistant for debugging, integrating, and understanding APIs using indexed documentation."
)


# ========================
# SIDEBAR
# ========================
with st.sidebar:

    st.header("System Overview")
    st.caption("API Copilot v0.7 Beta")

    st.markdown("### System Health")

    for label, status in [
        ("OpenAI API", openai_status),
        ("Vector DB", vector_status),
        ("RAG Engine", rag_status)
    ]:
        c1, c2 = st.columns([2, 1])
        c1.markdown(label)

        if status in ["Healthy", "Active", "Online"]:
            c2.markdown(f"🟢 {status}")
        else:
            c2.markdown(f"🔴 {status}")

    st.markdown("")

    st.markdown("### System Metrics")
    m1, m2 = st.columns(2)
    m1.metric("Docs Indexed", vector_stats["documents"])
    m2.metric("Chunks Created", vector_stats["chunks"])

    st.markdown("")

    st.markdown("### Supported Modules")
    st.markdown("""
🔐 Authentication  
💳 Payments  
⚠️ Errors  
🔔 Webhooks
""")

    st.markdown("")

    # Conversations
    st.markdown("### Conversations")

    if st.session_state.threads:
        for idx, thread in enumerate(st.session_state.threads):

            title = thread["title"]
            title = title[:36] + "..." if len(title) > 36 else title

            if idx == st.session_state.active_thread:
                title = f"• {title}"

            c1, c2 = st.columns([5, 1])

            if c1.button(title, key=f"thread_{idx}", use_container_width=True):
                t = st.session_state.threads.pop(idx)
                st.session_state.threads.insert(0, t)
                st.session_state.active_thread = 0
                save_threads(st.session_state.threads)
                st.rerun()

            if c2.button("🗑", key=f"del_{idx}"):
                st.session_state.threads.pop(idx)
                save_threads(st.session_state.threads)
                st.session_state.active_thread = None
                st.rerun()
    else:
        st.caption("No conversations yet.")

    st.markdown("")

    c1, c2 = st.columns(2)
    if c1.button("New Chat", use_container_width=True):
        st.session_state.active_thread = None
        st.rerun()

    if c2.button("Clear All", use_container_width=True):
        st.session_state.threads = []
        save_threads([])
        st.session_state.active_thread = None
        st.rerun()


# ========================
# EMPTY STATE
# ========================
if st.session_state.active_thread is None:

    st.markdown("### Ask a question")
    st.caption("Start by asking anything about API integrations")

    st.markdown("---")

    st.markdown("#### Suggested Questions")
    st.markdown("""
- How does Razorpay authentication work?
- How do I capture payments?
- What causes invalid OTP?
- How do webhooks work?
- Explain Razorpay payments in 150 words.
""")


# ========================
# CHAT DISPLAY
# ========================
if st.session_state.active_thread is not None:

    messages = st.session_state.threads[
        st.session_state.active_thread
    ]["messages"]

    for chat in messages:

        with st.chat_message("user"):
            st.write(chat["question"])

        with st.chat_message("assistant"):
            st.write(chat["answer"])
            st.caption(
                f"{chat['response_time']}s • "
                f"{chat['tokens']} tokens • "
                f"${chat['cost']:.5f}"
            )


# ========================
# INPUT
# ========================
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

user_query = st.chat_input(
    "Ask about authentication, payments, errors, or webhooks..."
)


# ========================
# QUERY EXECUTION
# ========================
if user_query:

    with st.chat_message("user"):
        st.write(user_query)

    with st.chat_message("assistant"):

        placeholder = st.empty()
        start = time.time()
        result_container = {}

        def run_query():
            result_container["data"] = call_backend(user_query)

        thread = threading.Thread(target=run_query)
        thread.start()

        while thread.is_alive():
            elapsed = round(time.time() - start, 1)
            placeholder.markdown(f"⏳ Thinking... {elapsed}s")
            time.sleep(0.2)

        thread.join()

        result = result_container["data"]

        if "error" in result:
            placeholder.empty()
            st.error("Backend error: " + result["error"])
            st.stop()

        placeholder.empty()

        st.write(result["answer"])

        st.caption(
            f"{result['response_time']}s • "
            f"{result['tokens']} tokens • "
            f"${result['cost']:.5f}"
        )

    payload = {
        "question": result["question"],
        "answer": result["answer"],
        "sources": result["sources"],
        "response_time": result["response_time"],
        "tokens": result["tokens"],
        "cost": result["cost"]
    }

    if st.session_state.active_thread is None:
        st.session_state.threads.insert(0, {
            "title": user_query,
            "messages": [payload]
        })
        st.session_state.active_thread = 0
    else:
        idx = st.session_state.active_thread
        t = st.session_state.threads.pop(idx)
        t["messages"].append(payload)
        st.session_state.threads.insert(0, t)
        st.session_state.active_thread = 0

    st.session_state.threads = st.session_state.threads[:MAX_THREADS]
    save_threads(st.session_state.threads)

    st.rerun()
