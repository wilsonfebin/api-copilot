import os
import time
import json
import threading
from datetime import datetime
from pathlib import Path
import streamlit as st

from backend.agents.workflow import run_agentic_flow
from backend.config import (
    DEFAULT_LLM_PROVIDER,
    SUPPORTED_MODELS,
    get_default_model,
)
from backend.enterprise.microsoft_graph import send_enterprise_notification
from backend.services.rag_service import run_query
from rag.vector_store import get_vector_stats
from utils.styles import load_css


# ========================
# CONFIG
# ========================
MAX_THREADS = 10
THREAD_FILE = "data/threads.json"
BASELINE_DIR = Path("evaluation/baselines")
ENTERPRISE_METADATA_FIELDS = [
    "workflow_type",
    "workflow_status",
    "hitl_required",
    "approval_status",
    "incident_payload",
    "notification_status",
]

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
def call_backend(
    query,
    llm_provider=DEFAULT_LLM_PROVIDER,
    model_name=None,
):

    try:

        frontend_start = time.time()

        agent_state = run_agentic_flow(
            query
        )

        model_name = model_name or get_default_model(
            llm_provider
        )

        data = run_query(
            question=query,
            intent=agent_state["intent"],
            tool=agent_state["tool"],
            llm_provider=llm_provider,
            model=model_name,
        )

        frontend_elapsed = round(
            time.time() - frontend_start,
            2
        )

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


def get_health():

    return {
        "services": {
            "openai": bool(
                os.getenv("OPENAI_API_KEY")
            ),
            "vector_db": True,
            "rag": True,
        }
    }


def get_metrics():

    try:
        return get_vector_stats()

    except:
        return {
            "documents": "-",
            "chunks": "-"
        }


def get_latest_baseline():

    baseline_files = sorted(
        BASELINE_DIR.glob(
            "evaluation_baseline_*.json"
        )
    )

    if not baseline_files:
        return None, None

    latest = baseline_files[-1]

    try:

        with open(latest, "r") as f:
            content = f.read()

        return latest, content

    except:
        return None, None


def get_latest_evaluation_log():

    log_files = sorted(
        BASELINE_DIR.glob(
            "evaluation_logs_*.txt"
        )
    )

    if not log_files:
        return None, None

    latest = log_files[-1]

    try:

        with open(latest, "r") as f:
            content = f.read()

        return latest, content

    except:
        return None, None


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


def add_enterprise_metadata(payload, response):

    for field in ENTERPRISE_METADATA_FIELDS:

        if field in response:
            payload[field] = response[field]

    return payload


def render_enterprise_status(message):

    if not message.get("workflow_type"):
        return

    notification_status = message.get(
        "notification_status",
        {}
    )

    st.markdown(
        f"""
**Enterprise Workflow Status**

Workflow: {message.get("workflow_type")}

Approval: {message.get("approval_status", "-")}

Notification: {notification_status.get("status", "-")}

Mode: {notification_status.get("mode", "-")}
"""
    )


def workflow_status_after_notification(result):

    if result.get("status") == "validation_failed":
        return "notification_validation_failed"

    if result.get("posted"):
        return "notification_executed"

    if result.get("mode") == "demo":
        return "notification_skipped_demo_mode"

    return "notification_failed"


def approve_enterprise_notification(
    thread_index,
    message_index,
):

    message = st.session_state.threads[
        thread_index
    ]["messages"][message_index]

    result = send_enterprise_notification(
        message.get("incident_payload", {}),
        approved=True,
    )

    message["approval_status"] = "approved"
    message["workflow_status"] = (
        workflow_status_after_notification(
            result
        )
    )
    message["notification_status"] = result

    st.session_state.threads[
        thread_index
    ]["updated_at"] = timestamp()

    save_threads(
        st.session_state.threads[:MAX_THREADS]
    )

    st.session_state.enterprise_notification_result = result

    pending = st.session_state.get(
        "pending_enterprise_approval"
    )

    if (
        pending
        and pending.get("thread_index") == thread_index
        and pending.get("message_index") == message_index
    ):
        del st.session_state.pending_enterprise_approval


def render_enterprise_approval_button(
    message,
    thread_index,
    message_index,
    key_suffix,
):

    if not (
        message.get("hitl_required") is True
        and message.get("approval_status") == "pending"
        and message.get("incident_payload")
    ):
        return

    if st.button(
        "✅ Approve Teams Notification",
        key=f"approve_teams_{key_suffix}",
        use_container_width=True,
    ):
        approve_enterprise_notification(
            thread_index,
            message_index,
        )
        st.rerun()


def render_notification_result():

    result = st.session_state.pop(
        "enterprise_notification_result",
        None,
    )

    if not result:
        return

    message = (
        f"{result.get('status')} via "
        f"{result.get('mode')}: {result.get('reason')}"
    )

    if result.get("posted"):
        st.success(message)
    elif result.get("status") == "validation_failed":
        st.error(message)
    else:
        st.warning(message)


def should_show_baseline_download(question):

    q = question.lower()

    return any(
        keyword in q
        for keyword in [
            "evaluation",
            "metrics",
            "deepeval",
            "baseline",
            "faithfulness",
            "relevancy",
        ]
    )


def render_baseline_download(question, key):

    if (
        should_show_baseline_download(question)
        and baseline_content
    ):

        st.download_button(
            "Download Latest Baseline",
            data=baseline_content,
            file_name=baseline_path.name,
            mime="application/json",
            use_container_width=True,
            key=key
        )

        st.caption(
            baseline_path.name
        )


def render_top_download_buttons():

    spacer_left, content, spacer_right = st.columns(
        [1, 2, 1]
    )

    with content:

        metric_col, log_col = st.columns(2)

        with metric_col:

            st.download_button(
                "⬇️ DeepEval Evaluation Baseline",
                data=(
                    baseline_content
                    or ""
                ),
                file_name=(
                    baseline_path.name
                    if baseline_path
                    else "latest_evaluation_metrics.json"
                ),
                mime="application/json",
                type="primary",
                use_container_width=True,
                disabled=not baseline_content,
                key="download_top_metrics"
            )

        with log_col:

            st.download_button(
                "⬇️ DeepEval Evaluation logs",
                data=(
                    evaluation_log_content
                    or ""
                ),
                file_name=(
                    evaluation_log_path.name
                    if evaluation_log_path
                    else "evaluation_logs.txt"
                ),
                mime="text/plain",
                type="primary",
                use_container_width=True,
                disabled=not evaluation_log_content,
                key="download_top_logs"
            )


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
baseline_path, baseline_content = get_latest_baseline()
evaluation_log_path, evaluation_log_content = (
    get_latest_evaluation_log()
)

# ========================
# SIDEBAR
# ========================
with st.sidebar:

    st.header("System Overview")
    st.caption("API Copilot v2 Beta")

    llm_provider = st.selectbox(
        "LLM Provider",
        list(SUPPORTED_MODELS.keys()),
        index=list(SUPPORTED_MODELS.keys()).index(
            DEFAULT_LLM_PROVIDER
        )
    )

    model_name = st.selectbox(
        "Model",
        SUPPORTED_MODELS[llm_provider],
        index=0
    )

    st.markdown("### System Health")

    for label, status in [

        (
            "API",
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
        "### 💬 Suggested Queries"
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
        "### 🛠 MCP Tool Suggested Queries"
    )

    for q in mcp_suggestions:

        if st.button(
            q,
            key=f"mcp_suggestion_{q}",
            use_container_width=True
        ):

            st.session_state.user_query = q
            st.rerun()


st.markdown(
    "### 🏢 Enterprise Workflow - Microsoft Graph Integration (HITL)"
)

if st.button(
    "Investigate Razorpay webhook failures",
    key="enterprise_workflow_razorpay_webhooks",
    use_container_width=True
):

    st.session_state.user_query = (
        "Investigate Razorpay webhook failures"
    )
    st.rerun()


render_top_download_buttons()


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
current_thread_index = None
current_message_index = None


if query:

    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):

        placeholder = st.empty()

        result = {}
        start = time.time()
        res = None

        def run():

            result["data"] = call_backend(
                query,
                llm_provider=llm_provider,
                model_name=model_name,
            )

        worker_thread = threading.Thread(
            target=run,
            daemon=True
        )

        worker_thread.start()

        while worker_thread.is_alive():

            placeholder.markdown(
                f"⏳ Thinking... "
                f"{round(time.time()-start,2)}s"
            )

            time.sleep(0.2)

        worker_thread.join()

        res = result.get(
            "data",
            {
                "error": "Something went wrong"
            }
        )

        placeholder.empty()

        if res and "error" not in res:

            payload = {
                "question": res["question"],
                "answer": res["answer"],
                "response_time": res["response_time"],
                "frontend_time": res["frontend_time"],
                "tokens": res["tokens"],
                "cost": res["cost"],
                "llm_provider": res.get(
                    "llm_provider",
                    llm_provider
                ),
                "model": res.get(
                    "model",
                    model_name
                )
            }

            payload = add_enterprise_metadata(
                payload,
                res,
            )

            if st.session_state.active_thread is not None:

                current_thread_index = (
                    st.session_state.active_thread
                )

                st.session_state.threads[
                    current_thread_index
                ]["messages"].append(payload)

                current_message_index = (
                    len(
                        st.session_state.threads[
                            current_thread_index
                        ]["messages"]
                    )
                    - 1
                )

                st.session_state.threads[
                    current_thread_index
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
                current_thread_index = 0
                current_message_index = 0

            save_threads(
                st.session_state.threads[:MAX_THREADS]
            )

            if payload.get("approval_status") == "pending":
                st.session_state.pending_enterprise_approval = {
                    "thread_index": current_thread_index,
                    "message_index": current_message_index,
                }

            rendered_current_response = True

            placeholder.markdown(
                render_answer_html(
                    res["answer"]
                ),
                unsafe_allow_html=True
            )

            render_baseline_download(
                res["question"],
                key=(
                    "download_current_"
                    f"{int(time.time() * 1000)}"
                )
            )

            st.caption(
                f"Provider: {res.get('llm_provider', llm_provider)} • "
                f"Model: {res.get('model', model_name)} • "
                f"Backend: {res['response_time']}s • "
                f"Frontend: {res['frontend_time']}s • "
                f"{res['tokens']} tokens • "
                f"${res['cost']:.5f}"
            )

            render_enterprise_status(
                payload
            )

        else:

            st.error(
                (res or {}).get(
                    "error",
                    "Something went wrong"
                )
            )

render_notification_result()

pending_approval = st.session_state.get(
    "pending_enterprise_approval"
)

if pending_approval:
    pending_thread_index = pending_approval.get(
        "thread_index"
    )
    pending_message_index = pending_approval.get(
        "message_index"
    )

    try:
        pending_message = st.session_state.threads[
            pending_thread_index
        ]["messages"][pending_message_index]

        render_enterprise_approval_button(
            pending_message,
            pending_thread_index,
            pending_message_index,
            "pending_current",
        )

    except Exception:
        del st.session_state.pending_enterprise_approval


# ========================
# CHAT DISPLAY
# ========================
if st.session_state.active_thread is not None:

    msgs = st.session_state.threads[
        st.session_state.active_thread
    ]["messages"]

    visible_messages = list(
        reversed(
            list(enumerate(msgs))
        )
    )

    if (
        rendered_current_response
        and visible_messages
    ):
        visible_messages = visible_messages[1:]

    for message_index, chat in visible_messages:

        with st.chat_message("user"):
            st.write(chat["question"])

        with st.chat_message("assistant"):

            render_answer(
                chat["answer"]
            )

            render_baseline_download(
                chat["question"],
                key=(
                    "download_history_"
                    f"{chat['question']}_"
                    f"{chat.get('response_time')}"
                )
            )

            frontend_time = chat.get(
                "frontend_time",
                "-"
            )

            st.caption(
                f"Provider: {chat.get('llm_provider', DEFAULT_LLM_PROVIDER)} • "
                f"Model: {chat.get('model', get_default_model())} • "
                f"Backend: {chat['response_time']}s • "
                f"Frontend: {frontend_time}s • "
                f"{chat['tokens']} tokens • "
                f"${chat['cost']:.5f}"
            )

            render_enterprise_status(
                chat
            )

            render_enterprise_approval_button(
                chat,
                st.session_state.active_thread,
                message_index,
                (
                    "history_"
                    f"{st.session_state.active_thread}_"
                    f"{message_index}"
                ),
            )
