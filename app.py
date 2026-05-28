import os
import time
import json
import queue
import threading
from datetime import datetime
import requests
import streamlit as st

from utils.styles import load_css

# ========================
# CONFIG
# ========================
MAX_THREADS = 10
THREAD_FILE = "data/threads.json"
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://backend:8000"
)

st.set_page_config(
    page_title="API Copilot",
    page_icon="🚀",
    layout="wide"
)

# ========================
# LOAD CSS
# ========================
st.markdown(
    load_css(),
    unsafe_allow_html=True
)

# ========================
# STORAGE
# ========================
def load_threads():

    if not os.path.exists(THREAD_FILE):
        return []

    try:

        with open(THREAD_FILE, "r") as f:

            content = f.read().strip()

            return (
                json.loads(content)
                if content
                else []
            )

    except:
        return []


def save_threads(threads):

    os.makedirs("data", exist_ok=True)

    with open(THREAD_FILE, "w") as f:
        json.dump(threads, f, indent=2)


def normalize_threads(threads):

    now = timestamp()

    for thread in threads:

        thread.setdefault(
            "created_at",
            now
        )

        thread.setdefault(
            "updated_at",
            thread["created_at"]
        )

        thread.setdefault(
            "messages",
            []
        )

    return threads


# ========================
# BACKEND
# ========================
def call_backend(query):

    try:

        frontend_start = time.time()

        res = requests.post(
            f"{BACKEND_URL}/query",
            json={"question": query},
            timeout=30
        )

        frontend_elapsed = round(
            time.time() - frontend_start,
            2
        )

        data = res.json()

        # ========================
        # FRONTEND LATENCY
        # ========================
        data["frontend_time"] = (
            frontend_elapsed
        )

        return data

    except Exception as e:

        return {
            "error": str(e)
        }


def stream_backend(query):

    frontend_start = time.time()

    with requests.post(
        f"{BACKEND_URL}/query/stream",
        json={"question": query},
        stream=True,
        timeout=60
    ) as res:

        res.raise_for_status()

        event = "message"

        for line in res.iter_lines(
            chunk_size=1,
            decode_unicode=True
        ):

            if line is None:
                continue

            if line.startswith("event: "):

                event = line.replace(
                    "event: ",
                    "",
                    1
                )

                continue

            if line.startswith("data: "):

                data = json.loads(
                    line.replace(
                        "data: ",
                        "",
                        1
                    )
                )

                data["event"] = event
                data["frontend_elapsed"] = round(
                    time.time() - frontend_start,
                    2
                )

                yield data

                event = "message"


def get_health():

    try:
        return requests.get(
            f"{BACKEND_URL}/health",
            timeout=5
        ).json()

    except:
        return None


def get_metrics():

    try:
        return requests.get(
            f"{BACKEND_URL}/metrics",
            timeout=5
        ).json()

    except:
        return {
            "documents": "-",
            "chunks": "-"
        }


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


def render_answer(answer):

    st.markdown(f"""
    <div class="answer-box">
        <h3>Summary</h3>
        {clean_answer(answer)}
    </div>
    """, unsafe_allow_html=True)


def render_answer_html(answer):

    return f"""
    <div class="answer-box">
        <h3>Summary</h3>
        {clean_answer(answer)}
    </div>
    """


def timestamp():

    return datetime.now().isoformat(
        timespec="seconds"
    )


# ========================
# INIT
# ========================
if "threads" not in st.session_state:
    st.session_state.threads = normalize_threads(
        load_threads()
    )

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

        (
            "OpenAI API",
            "Healthy"
            if health
            and health["services"]["openai"]
            else "Missing"
        ),

        (
            "Vector DB",
            "Active"
            if health
            and health["services"]["vector_db"]
            else "Down"
        ),

        (
            "RAG Engine",
            "Online"
            if health
            and health["services"]["rag"]
            else "Down"
        ),
    ]:

        c1, c2 = st.columns([2, 1])

        c1.markdown(label)

        c2.markdown(
            f"{'🟢' if status in ['Healthy','Active','Online'] else '🔴'} {status}"
        )

    st.markdown("### System Metrics")

    col1, col2 = st.columns(2)

    with col1:
        metric(
            "Docs Indexed",
            metrics["documents"]
        )

    with col2:
        metric(
            "Chunks Created",
            metrics["chunks"]
        )

    st.markdown("### Conversations")

    if st.session_state.threads:

        for i, t in enumerate(
            st.session_state.threads
        ):

            c1, c2 = st.columns([5, 1])

            if c1.button(
                t["title"][:30],
                key=f"t{i}",
                use_container_width=True
            ):

                st.session_state.active_thread = i
                st.rerun()

            if c2.button(
                "🗑",
                key=f"d{i}"
            ):

                st.session_state.threads.pop(i)

                save_threads(
                    st.session_state.threads
                )

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

st.caption(
    "RAG-powered assistant for debugging and integrating APIs"
)

# ========================
# DEMO QUERIES
# ========================
left, right = st.columns(2)

suggestions = [
    "How does Razorpay authentication work?",
    "How do I capture payments?",
    "What causes invalid OTP?",
    "How do webhooks work?",
    "Explain Razorpay payments in 150 words."
]

mcp_suggestions = [
    "How many documents and chunks are indexed?",
    "Show latest evaluation metrics",
    "Is the vector database healthy?",
    "What did we discuss earlier?",
    "Show system diagnostics",
]

with left:

    st.markdown(
        "### Suggested Questions"
    )

    for q in suggestions:

        if st.button(
            q,
            key=f"suggestion_{q}",
            use_container_width=True
        ):

            st.session_state.user_query = q
            st.rerun()

with right:

    st.markdown(
        "### 🛠 MCP Tool Demo"
    )

    for q in mcp_suggestions:

        if st.button(
            q,
            key=f"mcp_suggestion_{q}",
            use_container_width=True
        ):

            st.session_state.user_query = q
            st.rerun()


# ========================
# INPUT
# ========================
query = st.chat_input(
    "Ask about authentication, payments, errors..."
)

if "user_query" in st.session_state:

    query = st.session_state.user_query

    del st.session_state.user_query


rendered_current_response = False


if query:

    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):

        placeholder = st.empty()

        start = time.time()
        answer = ""
        res = None
        status_text = "Thinking"
        events = queue.Queue()

        def consume_stream():

            try:

                for event in stream_backend(query):
                    events.put(event)

            except Exception as exc:

                events.put({
                    "event": "exception",
                    "error": str(exc)
                })

            finally:

                events.put({
                    "event": "stream_complete"
                })

        stream_thread = threading.Thread(
            target=consume_stream,
            daemon=True
        )

        stream_thread.start()

        try:

            while True:

                try:

                    event = events.get(
                        timeout=0.1
                    )

                except queue.Empty:

                    if answer:

                        placeholder.markdown(
                            render_answer_html(answer),
                            unsafe_allow_html=True
                        )

                    else:

                        placeholder.markdown(
                            f"⏳ {status_text}... "
                            f"{round(time.time()-start,2)}s"
                        )

                    continue

                if event["event"] == "status":

                    status_text = event["message"]

                    if not answer:

                        placeholder.markdown(
                            f"⏳ {status_text}... "
                            f"{event['frontend_elapsed']}s"
                        )

                elif event["event"] == "chunk":

                    answer += event["text"]

                    placeholder.markdown(
                        render_answer_html(answer),
                        unsafe_allow_html=True
                    )

                elif event["event"] == "done":

                    res = event
                    res["frontend_time"] = event[
                        "frontend_elapsed"
                    ]

                elif event["event"] == "error":

                    res = {
                        "error": event.get(
                            "error",
                            "Streaming request failed"
                        )
                    }

                elif event["event"] == "exception":

                    raise RuntimeError(
                        event.get(
                            "error",
                            "Streaming request failed"
                        )
                    )

                elif event["event"] == "stream_complete":

                    break

        except Exception:

            res = call_backend(query)

            answer = res.get(
                "answer",
                ""
            )

            placeholder.markdown(
                render_answer_html(answer),
                unsafe_allow_html=True
            )

        if res and "error" not in res:

            st.caption(
                f"Backend: {res['response_time']}s • "
                f"Frontend: {res['frontend_time']}s • "
                f"{res['tokens']} tokens • "
                f"${res['cost']:.5f}"
            )

        else:

            st.error(
                (res or {}).get(
                    "error",
                    "Something went wrong"
                )
            )

    if res and "error" not in res:

        payload = {
            "question": res["question"],
            "answer": res["answer"],
            "response_time": res["response_time"],
            "frontend_time": res["frontend_time"],
            "tokens": res["tokens"],
            "cost": res["cost"]
        }

        if st.session_state.active_thread is not None:

            active_thread = st.session_state.active_thread

            st.session_state.threads[
                active_thread
            ]["messages"].append(payload)

            st.session_state.threads[
                active_thread
            ]["updated_at"] = timestamp()

        else:

            now = timestamp()

            st.session_state.threads.insert(0, {
                "title": query,
                "created_at": now,
                "updated_at": now,
                "messages": [payload]
            })

            st.session_state.active_thread = 0

        save_threads(
            st.session_state.threads[:MAX_THREADS]
        )

        rendered_current_response = True


# ========================
# CHAT DISPLAY
# ========================
if st.session_state.active_thread is not None:

    msgs = st.session_state.threads[
        st.session_state.active_thread
    ]["messages"]

    visible_messages = list(
        reversed(msgs)
    )

    if (
        rendered_current_response
        and visible_messages
    ):
        visible_messages = visible_messages[1:]

    for chat in visible_messages:

        with st.chat_message("user"):
            st.write(chat["question"])

        with st.chat_message("assistant"):

            render_answer(
                chat["answer"]
            )

            frontend_time = chat.get(
                "frontend_time",
                "-"
            )

            st.caption(
                f"Backend: {chat['response_time']}s • "
                f"Frontend: {frontend_time}s • "
                f"{chat['tokens']} tokens • "
                f"${chat['cost']:.5f}"
            )
