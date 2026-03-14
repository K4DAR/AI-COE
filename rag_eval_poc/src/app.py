"""
Enterprise RAG Intelligence Platform
Professional Streamlit UI for Document AI Systems
"""

import streamlit as st
import json
import time
from datetime import datetime
from pathlib import Path
import logging

from config import config
from validators import InputValidator
from demo import RAGBotDemo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="RAG Intelligence Platform",
    page_icon="🚀",
    layout="wide",
)

# =========================================================
# PROFESSIONAL UI STYLING
# =========================================================

def apply_professional_styling():

    st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: Inter, system-ui, -apple-system;
}

.main {
    background: #f6f8fb;
}


/* HERO HEADER */

.hero {
    padding: 30px;
    border-radius: 14px;
    background: linear-gradient(135deg,#1e3a8a,#2563eb);
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 34px;
}

.hero p {
    opacity: 0.9;
}


/* KPI CARDS */

.metric-card {
    background: white;
    padding: 22px;
    border-radius: 12px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.05);
}


/* CHAT WINDOW */

.chat-window {
    background: white;
    padding: 30px;
    border-radius: 14px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.06);
    margin-top: 15px;
}


/* USER MESSAGE */

.user-msg {
    background:#eff6ff;
    border-left:4px solid #2563eb;
    padding:15px;
    border-radius:8px;
    margin-bottom:10px;
}


/* AI MESSAGE */

.ai-msg {
    background:#ecfdf5;
    border-left:4px solid #059669;
    padding:15px;
    border-radius:8px;
    margin-bottom:10px;
}


/* SOURCE DOC PANEL */

.source-card {
    background:white;
    border-radius:10px;
    padding:15px;
    border:1px solid #e5e7eb;
    margin-bottom:10px;
}


/* SIDEBAR */

section[data-testid="stSidebar"]{
    background:#111827;
}

section[data-testid="stSidebar"] *{
    color:white;
}


/* BUTTON */

.stButton button {
    background:#2563eb;
    border-radius:8px;
    border:none;
}

.stButton button:hover{
    background:#1d4ed8;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================

def initialize_session():

    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    if "bot" not in st.session_state:
        st.session_state.bot = None

    if "bot_initialized" not in st.session_state:
        st.session_state.bot_initialized = False

    if "stats" not in st.session_state:
        st.session_state.stats = {
            "total_questions": 0,
            "total_time": 0,
            "errors": 0
        }

# =========================================================
# HEADER
# =========================================================

def display_header():

    st.markdown("""
    <div class="hero">

    <h1>🚀 RAG Intelligence Platform</h1>

    <p>
    Enterprise Document AI powered by Retrieval-Augmented Generation.
    Ask questions and retrieve knowledge from your documents instantly.
    </p>

    </div>
    """, unsafe_allow_html=True)

# =========================================================
# KPI BAR
# =========================================================

def display_kpis():

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Queries", st.session_state.stats["total_questions"])

    with col2:
        success = st.session_state.stats["total_questions"] - st.session_state.stats["errors"]
        st.metric("Successful Answers", success)

    with col3:

        avg_time = (
            st.session_state.stats["total_time"] /
            max(st.session_state.stats["total_questions"], 1)
        )

        st.metric("Avg Latency", f"{avg_time:.2f}s")

    with col4:
        st.metric("Errors", st.session_state.stats["errors"])

# =========================================================
# BOT INITIALIZATION
# =========================================================

def init_bot():

    try:

        with st.spinner("Initializing RAG System..."):

            bot = RAGBotDemo()

            if bot.setup():

                st.session_state.bot = bot
                st.session_state.bot_initialized = True

                return True

    except Exception as e:

        st.error(f"Initialization failed: {str(e)}")
        logger.error(e)

    return False

# =========================================================
# CHAT WINDOW
# =========================================================

def display_chat():

    st.markdown('<div class="chat-window">', unsafe_allow_html=True)

    for msg in st.session_state.conversation_history:

        if msg["role"] == "user":

            st.markdown(
                f'<div class="user-msg"><b>You</b><br>{msg["content"]}</div>',
                unsafe_allow_html=True
            )

        elif msg["role"] == "assistant":

            st.markdown(
                f'<div class="ai-msg"><b>AI Assistant</b><br>{msg["content"]}</div>',
                unsafe_allow_html=True
            )

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# SOURCE DOCUMENT VIEW
# =========================================================

def display_sources(sources):

    if not sources:
        return

    st.subheader("Retrieved Document Context")

    for doc in sources[:3]:

        st.markdown(
            f"""
            <div class="source-card">

            <b>Source:</b> {doc.metadata.get("source","Document")}

            <hr>

            {doc.page_content[:400]}

            </div>
            """,
            unsafe_allow_html=True
        )

# =========================================================
# MAIN APPLICATION
# =========================================================

def main():

    apply_professional_styling()

    initialize_session()

    display_header()

    display_kpis()

    col_main, col_side = st.columns([4,1])

    # -----------------------------------------------------

    with col_side:

        st.title("AI Control Center")

        st.write("---")

        if st.session_state.bot_initialized:

            st.success("System Online")

        else:

            st.warning("System Offline")

            if st.button("Initialize AI"):

                if init_bot():
                    st.rerun()

        st.write("---")

        st.subheader("Session Tools")

        if st.button("Clear Conversation"):

            st.session_state.conversation_history = []
            st.rerun()

        st.write("---")

        st.subheader("System Info")

        st.write("Model: Groq LLM")
        st.write("Vector DB: Chroma")

    # -----------------------------------------------------

    with col_main:

        st.subheader("Ask Questions")

        display_chat()

        question = st.text_input(
            "Ask something about your documents",
            placeholder="Example: What is Python used for?"
        )

        if st.button("Ask") and question:

            valid, error = InputValidator.validate_question(question)

            if not valid:

                st.error(error)
                st.session_state.stats["errors"] += 1
                return

            st.session_state.conversation_history.append({
                "role": "user",
                "content": question
            })

            start = time.time()

            with st.spinner("Generating answer..."):

                response = st.session_state.bot.process_question(question)

            elapsed = time.time() - start

            if response:

                answer = response.get("result", "")
                sources = response.get("source_documents", [])

                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": answer
                })

                display_sources(sources)

                st.session_state.stats["total_questions"] += 1
                st.session_state.stats["total_time"] += elapsed

            else:

                st.error("Failed to generate answer")
                st.session_state.stats["errors"] += 1

            st.rerun()

# =========================================================

if __name__ == "__main__":
    main()