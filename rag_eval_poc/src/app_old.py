"""
Professional Streamlit Web UI for RAG Bot
A modern, feature-rich interface for document Q&A
"""
import streamlit as st
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="RAG Bot - AI Document Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import RAG components
from config import config
from validators import InputValidator, OutputValidator, ValidationError
from demo import RAGBotDemo

# Configure styling
def configure_styling():
    """Apply custom CSS styling"""
    st.markdown("""
        <style>
        /* Main theme colors */
        :root {
            --primary: #0066cc;
            --secondary: #f0f4f8;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
        }
        
        /* Custom sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        }
        
        /* Chat messages styling */
        .chat-message {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            gap: 1rem;
        }
        
        .chat-message.user {
            background-color: #e0e7ff;
            border-left: 4px solid #0066cc;
        }
        
        .chat-message.assistant {
            background-color: #f0fdf4;
            border-left: 4px solid #10b981;
        }
        
        .chat-message.error {
            background-color: #fef2f2;
            border-left: 4px solid #ef4444;
        }
        
        /* Info boxes */
        .info-box {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .info-box.success {
            background-color: #f0fdf4;
            border-left: 4px solid #10b981;
            color: #065f46;
        }
        
        .info-box.warning {
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            color: #92400e;
        }
        
        .info-box.error {
            background-color: #fef2f2;
            border-left: 4px solid #ef4444;
            color: #7f1d1d;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 0.5rem;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        /* Header styling */
        h1 {
            color: #0f172a;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 0.5rem;
        }
        
        h2 {
            color: #1e293b;
            margin-top: 1.5rem;
        }
        
        /* Source documents styling */
        .source-doc {
            padding: 1rem;
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        /* Stats cards */
        .stat-card {
            padding: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 0.5rem;
            text-align: center;
        }
        
        .stat-card h3 {
            margin: 0 0 0.5rem 0;
            font-size: 0.875rem;
            opacity: 0.9;
        }
        
        .stat-card .value {
            font-size: 2rem;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state"""
    if "bot" not in st.session_state:
        st.session_state.bot = None
        st.session_state.bot_initialized = False
        st.session_state.conversation_history = []
        st.session_state.stats = {
            "total_questions": 0,
            "total_time": 0.0,
            "errors": 0
        }
        st.session_state.current_pdf = None
        st.session_state.vector_store_loaded = False


def init_bot(pdf_path: Optional[str] = None) -> bool:
    """Initialize RAG bot"""
    try:
        with st.spinner("🤖 Initializing RAG Bot..."):
            # Use document.txt as default document
            bot_path = pdf_path or "src/data/document.txt"
            bot = RAGBotDemo(pdf_path=bot_path)
            if bot.setup():
                st.session_state.bot = bot
                st.session_state.bot_initialized = True
                st.session_state.vector_store_loaded = True
                st.session_state.current_pdf = pdf_path
                return True
    except Exception as e:
        st.error(f" Failed to initialize bot: {str(e)}")
        logger.error(f"Bot initialization error: {e}", exc_info=True)
    return False


def display_chat_message(role: str, content: str, sources: Optional[List] = None):
    """Display a formatted chat message"""
    message_class = f"chat-message {role}"
    
    if role == "user":
        emoji = "👤"
        st.markdown(f"""
            <div class='{message_class}'>
                <div style='flex: 1;'>
                    <div style='font-weight: bold; color: #0066cc;'>{emoji} You</div>
                    <div style='margin-top: 0.5rem;'>{content}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    elif role == "assistant":
        emoji = "🤖"
        st.markdown(f"""
            <div class='{message_class}'>
                <div style='flex: 1;'>
                    <div style='font-weight: bold; color: #10b981;'>{emoji} RAG Bot</div>
                    <div style='margin-top: 0.5rem;'>{content}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if sources:
            with st.expander(f"📚 {len(sources)} Source Document(s)"):
                for i, doc in enumerate(sources, 1):
                    st.markdown(f"""
                        <div class='source-doc'>
                            <strong>Source {i}</strong><br>
                            <small>📄 {doc.metadata.get('source', 'Unknown')}</small><br>
                            {doc.page_content[:300]}...
                        </div>
                    """, unsafe_allow_html=True)
    
    elif role == "error":
        st.markdown(f"""
            <div class='chat-message error'>
                <div style='flex: 1;'>
                    <div style='font-weight: bold; color: #ef4444;'> Error</div>
                    <div style='margin-top: 0.5rem;'>{content}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)


def display_stats():
    """Display statistics dashboard"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "📊 Questions Asked",
            st.session_state.stats["total_questions"],
            delta=None,
            help="Total number of questions processed"
        )
    
    with col2:
        avg_time = (
            st.session_state.stats["total_time"] / max(st.session_state.stats["total_questions"], 1)
            if st.session_state.stats["total_questions"] > 0
            else 0
        )
        st.metric(
            "⏱️ Avg Response Time",
            f"{avg_time:.2f}s",
            delta=None,
            help="Average time to generate answers"
        )
    
    with col3:
        st.metric(
            " Errors",
            st.session_state.stats["errors"],
            delta=None,
            help="Number of errors encountered"
        )


def sidebar_settings():
    """Sidebar settings panel"""
    st.sidebar.markdown("## ⚙️ Settings")
    
    # Model settings
    with st.sidebar.expander("🧠 Model Configuration", expanded=False):
        st.sidebar.markdown("### LLM Settings")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.markdown("**Temperature** (Creativity)")
            temp = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=float(config.OPENAI_TEMPERATURE),
                step=0.1,
                label_visibility="collapsed"
            )
        with col2:
            st.markdown("**Retrieval K** (Documents)")
            k = st.slider(
                "Retriever K",
                min_value=1,
                max_value=10,
                value=config.RETRIEVER_K,
                label_visibility="collapsed"
            )
        
        st.info(f"ℹ️ Current: Temperature={temp}, K={k}")
    
    # Document settings
    with st.sidebar.expander("📄 Document Settings", expanded=False):
        st.sidebar.markdown("### Chunk Configuration")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.markdown("**Chunk Size**")
            chunk_size = st.number_input(
                "Chunk Size",
                min_value=200,
                max_value=2000,
                value=config.PDF_CHUNK_SIZE,
                step=100,
                label_visibility="collapsed"
            )
        with col2:
            st.markdown("**Chunk Overlap**")
            overlap = st.number_input(
                "Overlap",
                min_value=0,
                max_value=500,
                value=config.PDF_CHUNK_OVERLAP,
                step=50,
                label_visibility="collapsed"
            )
    
    # Logging settings
    with st.sidebar.expander("📋 Logging", expanded=False):
        log_level = st.selectbox(
            "Log Level",
            ["DEBUG", "INFO", "WARNING", "ERROR"],
            index=1,
            help="Set the logging level for debugging"
        )
        st.info(f"ℹ️ Current: {log_level}")


def sidebar_about():
    """Sidebar about section"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("## ℹ️ About")
    
    st.sidebar.markdown("""
    **RAG Bot - AI Document Assistant**
    
    A professional Retrieval-Augmented Generation system for intelligent document Q&A.
    
    **Version:** 1.0  
    **Status:** Production Ready 
    
    ### Features
    -  Fast semantic search
    - 🧠 Powered by GPT-4o
    - 📊 Real-time analytics
    - 🎯 High accuracy answers
    
    ### Documentation
    - [Quick Start](START_HERE.md)
    - [Full Reference](README.md)
    - [Architecture](ARCHITECTURE.md)
    """)


def main():
    """Main application"""
    configure_styling()
    initialize_session_state()
    
    # Header
    st.markdown("# 🤖 RAG Bot - AI Document Assistant")
    st.markdown(
        "Ask questions about your documents and get intelligent answers powered by AI",
        help="This is a Retrieval-Augmented Generation system"
    )
    
    # Main layout
    col_main, col_sidebar = st.columns([3, 1], gap="large")
    
    with col_sidebar:
        # Bot status
        st.markdown("### 📊 Bot Status")
        
        if st.session_state.bot_initialized and st.session_state.vector_store_loaded:
            st.success("✅ Bot Ready")
            if st.session_state.current_pdf:
                st.caption(f"📄 {Path(st.session_state.current_pdf).name}")
        else:
            st.warning("⚠️ Bot Not Ready")
            if st.button("🚀 Initialize Bot", width='stretch'):
                if init_bot():
                    st.rerun()
        
        st.markdown("---")
        
        # Settings
        sidebar_settings()
        
        # About
        sidebar_about()
    
    with col_main:
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(
            ["💬 Chat", "📊 Analytics", "⚙️ Settings", "📚 Help"]
        )
        
        # Chat Tab
        with tab1:
            st.markdown("### Start a Conversation")
            
            if not st.session_state.bot_initialized:
                st.error("""
                    ###  Bot Not Initialized
                    
                    Click the **Initialize Bot** button in the sidebar to get started.
                """)
            else:
                # Display conversation history
                if st.session_state.conversation_history:
                    st.markdown("### Conversation History")
                    for msg in st.session_state.conversation_history:
                        if msg["role"] == "user":
                            display_chat_message("user", msg["content"])
                        elif msg["role"] == "assistant":
                            display_chat_message("assistant", msg["content"], msg.get("sources"))
                        elif msg["role"] == "error":
                            display_chat_message("error", msg["content"])
                else:
                    st.info("💡 Start typing your question below to begin!")
                
                # Question input
                st.markdown("### Ask a Question")
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    question = st.text_input(
                        "Your question:",
                        placeholder="What is electricity load forecasting?",
                        label_visibility="collapsed"
                    )
                
                with col2:
                    submit = st.button("🔍 Ask", width='stretch')
                
                if submit and question:
                    # Validate input
                    is_valid, error_msg = InputValidator.validate_question(question)
                    
                    if not is_valid:
                        st.error(f" Invalid question: {error_msg}")
                        st.session_state.stats["errors"] += 1
                        st.session_state.conversation_history.append({
                            "role": "error",
                            "content": error_msg
                        })
                    else:
                        # Add to history and process
                        st.session_state.conversation_history.append({
                            "role": "user",
                            "content": question
                        })
                        
                        start_time = time.time()
                        with st.spinner("🤔 Thinking..."):
                            response = st.session_state.bot.process_question(question)
                        elapsed_time = time.time() - start_time
                        
                        if response:
                            answer = response.get("result", "")
                            sources = response.get("source_documents", [])
                            
                            # Validate output
                            is_valid, _ = OutputValidator.validate_answer(answer)
                            
                            st.session_state.conversation_history.append({
                                "role": "assistant",
                                "content": answer,
                                "sources": sources
                            })
                            
                            st.session_state.stats["total_questions"] += 1
                            st.session_state.stats["total_time"] += elapsed_time
                        else:
                            error_content = "Failed to generate answer. Please try again."
                            st.session_state.conversation_history.append({
                                "role": "error",
                                "content": error_content
                            })
                            st.session_state.stats["errors"] += 1
                        
                        st.rerun()
                
                # Clear history button
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Clear History", width='stretch'):
                        st.session_state.conversation_history = []
                        st.rerun()
                
                with col2:
                    if st.button("💾 Export Chat", width='stretch'):
                        # Export to JSON
                        export_data = {
                            "timestamp": datetime.now().isoformat(),
                            "messages": st.session_state.conversation_history,
                            "stats": st.session_state.stats
                        }
                        st.download_button(
                            label="📥 Download JSON",
                            data=json.dumps(export_data, indent=2),
                            file_name=f"rag_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
        
        # Analytics Tab
        with tab2:
            st.markdown("### 📊 Performance Analytics")
            
            if st.session_state.stats["total_questions"] == 0:
                st.info("💡 No questions asked yet. Start a conversation to see analytics!")
            else:
                display_stats()
                
                st.markdown("---")
                st.markdown("### 📈 Conversation Metrics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "Success Rate",
                        f"{((st.session_state.stats['total_questions'] - st.session_state.stats['errors']) / st.session_state.stats['total_questions'] * 100):.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "Total Questions",
                        st.session_state.stats["total_questions"]
                    )
        
        # Settings Tab
        with tab3:
            st.markdown("### ⚙️ Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### LLM Settings")
                st.info(f"""
                - **Model:** {config.OPENAI_MODEL}
                - **Temperature:** {config.OPENAI_TEMPERATURE}
                - **Max Retries:** 3
                """)
            
            with col2:
                st.markdown("#### Document Settings")
                st.info(f"""
                - **Chunk Size:** {config.PDF_CHUNK_SIZE}
                - **Chunk Overlap:** {config.PDF_CHUNK_OVERLAP}
                - **Retriever K:** {config.RETRIEVER_K}
                """)
            
            st.markdown("---")
            
            st.markdown("#### Validation Rules")
            st.info(f"""
            - **Min Question Length:** {config.MIN_QUESTION_LENGTH} chars
            - **Max Question Length:** {config.MAX_QUESTION_LENGTH} chars
            - **Min Answer Length:** {config.MIN_ANSWER_LENGTH} chars
            - **Max Answer Length:** {config.MAX_ANSWER_LENGTH} chars
            """)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Restart Bot", width='stretch'):
                    st.session_state.bot = None
                    st.session_state.bot_initialized = False
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Reset Stats", width='stretch'):
                    st.session_state.stats = {
                        "total_questions": 0,
                        "total_time": 0.0,
                        "errors": 0
                    }
                    st.rerun()
        
        # Help Tab
        with tab4:
            st.markdown("### 📚 Help & Documentation")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Getting Started")
                st.markdown("""
                1. **Initialize Bot** - Click in the sidebar
                2. **Ask Questions** - Type naturally about your documents
                3. **View Sources** - Expand to see source documents
                4. **Export Chat** - Save conversations as JSON
                """)
            
            with col2:
                st.markdown("#### Tips & Tricks")
                st.markdown("""
                - Ask specific, clear questions
                - Questions should be 3-500 characters
                - Use natural language
                - Check source documents for accuracy
                - Adjust model temperature for different styles
                """)
            
            st.markdown("---")
            
            st.markdown("#### Features")
            st.markdown("""
             **Input Validation** - Questions are validated for quality  
             **Source Tracking** - See which documents were used  
             **Error Handling** - Clear error messages  
             **Analytics** - Track conversation metrics  
             **Export** - Save conversations for later  
             **Configuration** - Customize behavior  
            """)
            
            st.markdown("---")
            
            st.markdown("#### About RAG Bot")
            st.markdown("""
            **Retrieval-Augmented Generation (RAG)** is a technique that:
            1. Retrieves relevant documents
            2. Passes them to an LLM with your question
            3. Generates accurate, source-backed answers
            
            This ensures answers are grounded in your actual documents!
            """)


if __name__ == "__main__":
    main()
