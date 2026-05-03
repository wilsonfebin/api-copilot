import os
import time
import streamlit as st
from rag.retrieve import answer_query
from rag.vector_store import get_vector_stats
from utils.metrics import estimate_tokens, estimate_cost


st.set_page_config(
    page_title="API Copilot",
    page_icon="🚀",
    layout="wide"
)


@st.cache_data(show_spinner=False)
def cached_query(query):
    return answer_query(query, top_k=2)


# Dynamic system stats
vector_stats = get_vector_stats()
api_status = "Healthy" if os.getenv("OPENAI_API_KEY") else "Missing Key"


# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "thread_title" not in st.session_state:
    st.session_state.thread_title = None


# Premium typography + layout system
st.markdown("""
<style>

/* ===== GLOBAL LAYOUT ===== */
.block-container {
    max-width: 1000px;
    padding-top: 1.5rem;
    padding-bottom: 1.2rem;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] > div:first-child {
    height: 100vh;
    overflow-y: auto;
    padding-top: 0.45rem;
    padding-bottom: 0.45rem;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 0rem;
    padding-bottom: 0rem;
    padding-left: 0.65rem;
    padding-right: 0.65rem;
}

/* Sidebar headers */
section[data-testid="stSidebar"] h1 {
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    margin-bottom: 0.28rem !important;
}

section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    margin-top: 0.5rem !important;
    margin-bottom: 0.18rem !important;
}

/* Sidebar text */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] div {
    font-size: 0.78rem !important;
    line-height: 1.22 !important;
}

/* Sidebar captions */
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    font-size: 0.72rem !important;
    line-height: 1.18rem !important;
    margin-bottom: 0.08rem !important;
}

/* Sidebar metric cards */
[data-testid="metric-container"] {
    padding: 0.35rem 0.5rem !important;
    border-radius: 10px !important;
    background-color: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.04);
}

/* Sidebar buttons */
section[data-testid="stSidebar"] button {
    padding-top: 0.24rem !important;
    padding-bottom: 0.24rem !important;
    font-size: 0.76rem !important;
}

/* Remove dividers */
section[data-testid="stSidebar"] hr {
    display: none !important;
}

/* Sidebar lists */
section[data-testid="stSidebar"] ul,
section[data-testid="stSidebar"] ol {
    margin-top: 0rem !important;
    margin-bottom: 0rem !important;
    padding-left: 1rem !important;
}

section[data-testid="stSidebar"] li {
    margin-bottom: 0.08rem !important;
}

/* ===== MAIN HEADER ===== */
h1 {
    font-size: 2.9rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em;
    margin-bottom: 0.25rem !important;
}

h2 {
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    margin-bottom: 0.45rem !important;
}

h3 {
    font-size: 1.22rem !important;
    font-weight: 650 !important;
    margin-top: 1rem !important;
    margin-bottom: 0.6rem !important;
}

/* ===== BODY ===== */
p, li {
    font-size: 0.98rem !important;
    line-height: 1.65 !important;
}

/* ===== CAPTIONS ===== */
[data-testid="stCaptionContainer"] {
    font-size: 0.8rem !important;
    opacity: 0.78;
}

/* ===== CHAT ===== */
div[data-testid="stChatMessage"] {
    padding-top: 0.45rem;
    padding-bottom: 0.45rem;
}

/* ===== RESPONSE CARD ===== */
.response-container {
    padding: 1.35rem;
    border-radius: 16px;
    background-color: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.05);
    margin-top: 0.55rem;
    margin-bottom: 1rem;
    line-height: 1.7;
    font-size: 0.98rem;
}

/* Response headings */
.response-container h1 {
    font-size: 1.55rem !important;
    font-weight: 700 !important;
}

.response-container h2 {
    font-size: 1.28rem !important;
    font-weight: 680 !important;
}

.response-container h3 {
    font-size: 1.1rem !important;
    font-weight: 650 !important;
}

.response-container p,
.response-container li {
    font-size: 0.98rem !important;
    line-height: 1.72 !important;
}

/* ===== CODE ===== */
pre {
    font-size: 0.88rem !important;
    border-radius: 10px !important;
    padding: 0.9rem !important;
}

/* ===== CHAT INPUT ===== */
div[data-testid="stChatInput"] {
    max-width: 780px;
    margin: auto;
}

div[data-testid="stChatInput"] > div {
    padding-top: 0.15rem !important;
    padding-bottom: 0.15rem !important;
}

div[data-testid="stChatInput"] textarea {
    font-size: 0.92rem !important;
    padding-top: 0.38rem !important;
    padding-bottom: 0.38rem !important;
    min-height: 44px !important;
    border-radius: 12px !important;
}

/* ===== BUTTONS ===== */
button {
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
}

</style>
""", unsafe_allow_html=True)


# Header
st.title("🚀 API Copilot")
st.subheader("AI-Powered API Integration Assistant")
st.caption(
    "Premium developer support for API integrations, payments, errors, and webhooks."
)


# Sidebar
with st.sidebar:

    # Overview
    st.header("System Overview")
    st.caption("API Copilot v0.6 Beta")

    # Health
    st.markdown("### System Health")

    health_items = [
        ("OpenAI API", f"🟢 {api_status}"),
        ("Vector DB", "🟢 Active"),
        ("RAG Engine", "🟢 Online")
    ]

    for label, status in health_items:
        col1, col2 = st.columns([2.2, 1])

        with col1:
            st.markdown(f"**{label}**")

        with col2:
            st.markdown(status)

    st.markdown("")

    # Metrics
    st.markdown("### System Metrics")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Docs", vector_stats["documents"])

    with col2:
        st.metric("Chunks", vector_stats["chunks"])

    st.markdown("")

    # Modules
    st.markdown("### Supported Modules")
    st.markdown("""
🔐 Authentication  
💳 Payments  
⚠️ Errors  
🔔 Webhooks
""")

    st.markdown("")

    # Session thread
    st.markdown("### Session Thread")

    if st.session_state.thread_title:
        trimmed = (
            st.session_state.thread_title[:42] + "..."
            if len(st.session_state.thread_title) > 42
            else st.session_state.thread_title
        )
        st.markdown(f"• {trimmed}")
    else:
        st.caption("No active conversation.")

    st.markdown("")

    # Controls
    col1, col2 = st.columns(2)

    with col1:
        if st.button("New Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.thread_title = None
            st.rerun()

    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.thread_title = None
            st.rerun()


# Empty state
if not st.session_state.chat_history:
    st.info(
        "Ask API Copilot about authentication, payments, errors, or webhooks."
    )

    st.markdown("### Suggested Questions")
    st.markdown("""
- How does Razorpay authentication work?
- How do I capture payments?
- What causes invalid OTP?
- How do webhooks work?
- Explain Razorpay payments in 150 words.
""")


# Chat history
for chat in st.session_state.chat_history:

    with st.chat_message("user"):
        st.markdown(chat["question"])

    with st.chat_message("assistant"):

        st.markdown(
            f"""
            <div class="response-container">
            {chat["answer"]}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            f"{chat['response_time']}s · "
            f"{chat['tokens']} tokens · "
            f"${round(chat['cost'], 5)}"
        )

        if len(chat["sources"]) == 1:
            st.caption(f"📄 Source: {chat['sources'][0]}")
        else:
            with st.expander("📄 Sources", expanded=True):
                for source in chat["sources"]:
                    st.caption(f"📄 {source}")


# Chat input
user_query = st.chat_input("Message API Copilot...")


# Query execution
if user_query:

    # Set thread title only for first query in active chat
    if not st.session_state.thread_title:
        st.session_state.thread_title = user_query

    start_time = time.time()

    with st.spinner("Thinking..."):
        result = cached_query(user_query)

    elapsed_time = round(time.time() - start_time, 2)

    input_tokens = estimate_tokens(user_query)
    output_tokens = estimate_tokens(result["answer"])
    total_tokens = input_tokens + output_tokens
    total_cost = estimate_cost(input_tokens, output_tokens)

    st.session_state.chat_history.append({
        "question": user_query,
        "answer": result["answer"],
        "sources": list(set([source["source"] for source in result["sources"]])),
        "response_time": elapsed_time,
        "tokens": total_tokens,
        "cost": total_cost
    })

    st.rerun()
