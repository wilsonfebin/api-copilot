import os
import time
import json
import threading
import streamlit as st
from rag.retrieve import answer_query
from rag.vector_store import get_vector_stats
from utils.metrics import estimate_tokens, estimate_cost
from utils.styles import load_css


# ========================
# CONFIG
# ========================
MAX_THREADS = 10
THREAD_FILE = "data/threads.json"

st.set_page_config(page_title="API Copilot", page_icon="🚀", layout="wide")


# ========================
# STORAGE (fail-safe)
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
# HELPERS
# ========================
@st.cache_data(show_spinner=False)
def cached_query(query):
    return answer_query(query, top_k=2)


# ========================
# INIT
# ========================
st.markdown(load_css(), unsafe_allow_html=True)

vector_stats = get_vector_stats()
api_status = "Healthy" if os.getenv("OPENAI_API_KEY") else "Missing Key"

if "threads" not in st.session_state:
    st.session_state.threads = load_threads()

if "active_thread" not in st.session_state:
    st.session_state.active_thread = None


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
        ("OpenAI API", api_status),
        ("Vector DB", "Active"),
        ("RAG Engine", "Online")
    ]:
        c1, c2 = st.columns([2, 1])
        c1.markdown(label)
        c2.markdown(f"🟢 {status}")

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

    # ---- Conversations
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
                f"{chat['response_time']}s · "
                f"{chat['tokens']} tokens · "
                f"${chat['cost']:.5f}"
            )


# ========================
# INPUT
# ========================
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
            result_container["data"] = cached_query(user_query)

        thread = threading.Thread(target=run_query)
        thread.start()

        while thread.is_alive():
            elapsed = round(time.time() - start, 1)
            placeholder.markdown(f"⏳ Thinking... {elapsed}s")
            time.sleep(0.2)

        thread.join()

        result = result_container["data"]
        elapsed = round(time.time() - start, 2)

        placeholder.empty()

        answer = result["answer"]

        in_tokens = estimate_tokens(user_query)
        out_tokens = estimate_tokens(answer)

        payload = {
            "question": user_query,
            "answer": answer,
            "sources": list(set([s["source"] for s in result["sources"]])),
            "response_time": elapsed,
            "tokens": in_tokens + out_tokens,
            "cost": estimate_cost(in_tokens, out_tokens)
        }

        st.write(answer)

        st.caption(
            f"{elapsed}s · "
            f"{payload['tokens']} tokens · "
            f"${payload['cost']:.5f}"
        )

    # ---- Save thread
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
