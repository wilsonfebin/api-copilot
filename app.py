import os
import time
import json
import threading
import requests
import streamlit as st

from utils.styles import load_css

# ========================
# CONFIG
# ========================
MAX_THREADS = 10
THREAD_FILE = "data/threads.json"
BACKEND_URL = "http://backend:8000"

st.set_page_config(page_title="API Copilot", page_icon="🚀", layout="wide")

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
# BACKEND
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
        return requests.get(f"{BACKEND_URL}/health", timeout=5).json()
    except:
        return None

def get_metrics():
    try:
        return requests.get(f"{BACKEND_URL}/metrics", timeout=5).json()
    except:
        return {"documents": "-", "chunks": "-"}

# ========================
# HELPERS
# ========================
def clean_answer(answer: str):
    lines = []
    for l in answer.split("\n"):
        if l.lower().startswith("## summary"):
            continue
        lines.append(l)
    return "\n".join(lines)

def metric(label, value):
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

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
    st.caption("API Copilot v0.7 Beta")

    st.markdown("### System Health")

    for label, status in [
        ("OpenAI API", "Healthy" if health and health["services"]["openai"] else "Missing"),
        ("Vector DB", "Active" if health and health["services"]["vector_db"] else "Down"),
        ("RAG Engine", "Online" if health and health["services"]["rag"] else "Down"),
    ]:
        c1, c2 = st.columns([2,1])
        c1.markdown(label)
        c2.markdown(f"{'🟢' if status in ['Healthy','Active','Online'] else '🔴'} {status}")

    st.markdown("### System Metrics")

    col1, col2 = st.columns(2)
    with col1:
        metric("Docs Indexed", metrics["documents"])
    with col2:
        metric("Chunks Created", metrics["chunks"])

    st.markdown("### Conversations")

    if st.session_state.threads:
        for i, t in enumerate(st.session_state.threads):
            c1, c2 = st.columns([5,1])

            if c1.button(t["title"][:30], key=f"t{i}", use_container_width=True):
                st.session_state.active_thread = i
                st.rerun()

            if c2.button("🗑", key=f"d{i}"):
                st.session_state.threads.pop(i)
                save_threads(st.session_state.threads)
                st.session_state.active_thread = None
                st.rerun()
    else:
        st.caption("No conversations yet.")

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
st.caption("RAG-powered assistant for debugging and integrating APIs")

# ========================
# EMPTY STATE
# ========================
if st.session_state.active_thread is None:
    st.markdown("### Suggested Questions")
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
    msgs = st.session_state.threads[st.session_state.active_thread]["messages"]

    for chat in msgs:
        with st.chat_message("user"):
            st.write(chat["question"])

        with st.chat_message("assistant"):
            st.markdown(f"""
            <div class="answer-box">
                <h3>Summary</h3>
                {clean_answer(chat["answer"])}
            </div>
            """, unsafe_allow_html=True)

            st.caption(f"{chat['response_time']}s • {chat['tokens']} tokens • ${chat['cost']:.5f}")

# ========================
# INPUT
# ========================
query = st.chat_input("Ask about authentication, payments, errors...")

if query:
    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        result = {}

        def run():
            result["data"] = call_backend(query)

        t = threading.Thread(target=run)
        t.start()

        start = time.time()
        while t.is_alive():
            placeholder.markdown(f"⏳ Thinking... {round(time.time()-start,2)}s")
            time.sleep(0.2)

        t.join()
        res = result["data"]
        placeholder.empty()

        st.markdown(f"""
        <div class="answer-box">
            <h3>Summary</h3>
            {clean_answer(res["answer"])}
        </div>
        """, unsafe_allow_html=True)

        st.caption(f"{res['response_time']}s • {res['tokens']} tokens • ${res['cost']:.5f}")

    payload = {
        "question": res["question"],
        "answer": res["answer"],
        "response_time": res["response_time"],
        "tokens": res["tokens"],
        "cost": res["cost"]
    }

    st.session_state.threads.insert(0, {
        "title": query,
        "messages": [payload]
    })

    st.session_state.active_thread = 0
    save_threads(st.session_state.threads[:MAX_THREADS])

    st.rerun()
