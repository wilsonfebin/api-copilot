import time
import streamlit as st
from rag.retrieve import answer_query


st.set_page_config(
    page_title="API Copilot",
    page_icon="🚀",
    layout="wide"
)

# Header
st.title("🚀 API Copilot")
st.subheader("AI-Powered API Integration Assistant")

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_thread" not in st.session_state:
    st.session_state.current_thread = []

# Sidebar
with st.sidebar:
    st.header("About")
    st.write(
        "API Copilot is a Retrieval-Augmented Generation (RAG) assistant built on real-world Razorpay API documentation to help developers"
    )

    st.markdown("---")

    # Status badges
    st.success("RAG System Active")
    st.caption("Docs Indexed: 4 | Chunks: 21")

    st.markdown("---")

    st.markdown("### Supported Modules")
    st.markdown("- Authentication")
    st.markdown("- Payments")
    st.markdown("- Errors")
    st.markdown("- Webhooks")

    st.markdown("---")

    # Thread history (one thread per session)
    st.markdown("### Current Chat")
    if st.session_state.current_thread:
        for idx, item in enumerate(st.session_state.current_thread, start=1):
            st.caption(f"{idx}. {item}")
    else:
        st.caption("No conversation yet.")

    st.markdown("---")

    # New thread
    if st.button("New Chat"):
        st.session_state.chat_history = []
        st.session_state.current_thread = []
        st.rerun()

    # Clear thread
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.current_thread = []
        st.rerun()

    st.markdown("---")
    st.caption("Built with OpenAI + Chroma + Streamlit")

# Empty state
if not st.session_state.chat_history:
    st.info(
        "Ask API Copilot about authentication, payments, errors, or webhooks."
    )

    st.markdown("### Try asking:")
    st.markdown("- How does Razorpay authentication work?")
    st.markdown("- How do I capture payments?")
    st.markdown("- What causes invalid OTP?")
    st.markdown("- How do webhooks work?")

    st.markdown("---")

# Display chat history
for chat in st.session_state.chat_history:

    with st.chat_message("user"):
        st.markdown(chat["question"])

    with st.chat_message("assistant"):

        with st.container():
            st.markdown(chat["answer"])

            st.caption(
                f"Answer generated from indexed Razorpay API documentation "
                f"in {chat['response_time']}s."
            )

        with st.expander("📚 View Sources"):
            for source in chat["sources"]:
                st.markdown(f"📄 {source}")

# Chat input
user_query = st.chat_input("Ask an API question...")

# Process query
if user_query:
    start_time = time.time()

    with st.spinner("Thinking..."):
        result = answer_query(user_query, top_k=2)

    elapsed_time = round(time.time() - start_time, 2)

    # Store full chat
    st.session_state.chat_history.append({
        "question": user_query,
        "answer": result["answer"],
        "sources": list(set([source["source"] for source in result["sources"]])),
        "response_time": elapsed_time
    })

    # Store thread-only question list
    st.session_state.current_thread.append(user_query)

    st.rerun()
