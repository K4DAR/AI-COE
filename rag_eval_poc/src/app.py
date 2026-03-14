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
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from config import config
from validators import InputValidator
from demo import RAGBotDemo
from evaluation import UIEvaluator, TestCaseManager

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

    # Evaluation-related session state
    if "evaluation_test_cases" not in st.session_state:
        st.session_state.evaluation_test_cases = []

    if "evaluation_results" not in st.session_state:
        st.session_state.evaluation_results = []

    if "evaluator" not in st.session_state:
        st.session_state.evaluator = None

    if "evaluation_loaded" not in st.session_state:
        st.session_state.evaluation_loaded = False

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
# EVALUATION UI FUNCTIONS
# =========================================================

def display_metric_card(metric_name: str, score: float, threshold: float, passed: bool):
    """Display individual metric card"""
    color = "#10b981" if passed else "#ef4444"  # Green or Red
    status = "✓ PASS" if passed else "✗ FAIL"
    
    st.markdown(f"""
    <div style="background: white; padding: 20px; border-radius: 10px; 
                border-left: 4px solid {color}; margin-bottom: 10px;">
        <b>{metric_name}</b><br>
        Score: <span style="font-size: 20px; font-weight: bold;">{score:.2f}</span> {status}
    </div>
    """, unsafe_allow_html=True)


def display_evaluation_test_cases():
    """Display test case loader and selector"""
    st.subheader("📋 Test Case Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Load Default Test Cases"):
            try:
                test_manager = TestCaseManager()
                test_manager.load_test_cases()
                st.session_state.evaluation_test_cases = test_manager.test_cases
                st.session_state.evaluation_loaded = True
                st.success(f"✓ Loaded {len(test_manager.test_cases)} test cases")
            except Exception as e:
                st.error(f"✗ Error loading test cases: {str(e)}")
    
    with col2:
        if st.session_state.evaluation_loaded:
            st.success(f"✓ {len(st.session_state.evaluation_test_cases)} test cases loaded")
    
    # Show test case breakdown
    if st.session_state.evaluation_test_cases:
        st.write("---")
        col1, col2, col3 = st.columns(3)
        
        categories = {}
        for tc in st.session_state.evaluation_test_cases:
            cat = tc.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        with col1:
            st.metric("Total Cases", len(st.session_state.evaluation_test_cases))
        
        for idx, (cat, count) in enumerate(categories.items(), 1):
            if idx == 2:
                with col2:
                    st.metric(f"{cat.title()}", count)
            elif idx == 3:
                with col3:
                    st.metric(f"{cat.title()}", count)


def display_single_test_evaluation():
    """Display single test case evaluation interface"""
    st.subheader("🧪 Single Test Evaluation")
    
    if not st.session_state.evaluation_test_cases:
        st.warning("⚠ Load test cases first")
        return
    
    if not st.session_state.bot_initialized:
        st.warning("⚠ Initialize RAG bot first")
        return
    
    # Check if LLM judge is configured
    llm_configured, llm_msg = UIEvaluator._check_llm_for_metrics()
    if not llm_configured:
        st.error(f"⚠️ LLM Judge Configuration Required\n\n{llm_msg}")
        return
    
    # Select test case
    test_ids = [f"Q#{tc['id']}: {tc['question'][:50]}..." 
                for tc in st.session_state.evaluation_test_cases]
    selected_idx = st.selectbox("Select Test Case", range(len(test_ids)), 
                                format_func=lambda i: test_ids[i])
    
    selected_test = st.session_state.evaluation_test_cases[selected_idx]
    
    # Display test case details
    st.write("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Category:** {selected_test.get('category', 'N/A')}")
        st.write(f"**Difficulty:** {selected_test.get('difficulty', 'N/A')}")
    
    with col2:
        st.write(f"**ID:** {selected_test['id']}")
        st.write(f"**Notes:** {selected_test.get('notes', 'N/A')}")
    
    st.write("---")
    st.write(f"**Question:** {selected_test['question']}")
    st.write(f"**Expected Answer:** {selected_test['expected_answer']}")
    
    # Run evaluation
    if st.button("▶ Evaluate This Test", key="single_test_eval"):
        if st.session_state.evaluator is None:
            st.session_state.evaluator = UIEvaluator(st.session_state.bot.qa_chain)
        
        with st.spinner("Evaluating..."):
            result = st.session_state.evaluator.evaluate_single_test(selected_test)
        
        # Display result
        st.write("---")
        st.subheader("📊 Evaluation Results")
        
        if "error" in result and result["error"]:
            st.error(f"✗ Error: {result['error']}")
        else:
            # Show actual answer
            st.write(f"**Actual Answer:** {result['actual_answer']}")
            
            # Show metrics
            st.write("---")
            st.write("**Metric Scores:**")
            
            cols = st.columns(2)
            metrics = result.get("metrics", {})
            
            for idx, (metric_name, metric_data) in enumerate(metrics.items()):
                with cols[idx % 2]:
                    score = metric_data.get("score")
                    if score is not None:
                        passed = metric_data.get("passed", False)
                        display_metric_card(metric_name, score, 
                                          metric_data.get("threshold", 0), passed)
                    else:
                        error_msg = metric_data.get("error", "Unknown error")
                        st.warning(f"{metric_name}: {error_msg}")
            
            # Show retrieved context
            st.write("---")
            with st.expander("📄 Retrieved Context"):
                st.text_area("Context", result.get("context", "No context"), 
                           height=200, disabled=True)


def display_batch_evaluation():
    """Display batch evaluation interface"""
    st.subheader("⚡ Batch Evaluation")
    
    if not st.session_state.evaluation_test_cases:
        st.warning("⚠ Load test cases first")
        return
    
    if not st.session_state.bot_initialized:
        st.warning("⚠ Initialize RAG bot first")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All"] + list(set(tc.get("category") for tc in st.session_state.evaluation_test_cases))
        )
    
    with col2:
        if category_filter == "All":
            test_cases_to_run = st.session_state.evaluation_test_cases
        else:
            test_cases_to_run = [tc for tc in st.session_state.evaluation_test_cases 
                                if tc.get("category") == category_filter]
        
        st.metric("Tests to Run", len(test_cases_to_run))
    
    with col3:
        pass
    
    if st.button("▶ Run Batch Evaluation", key="batch_eval"):
        if st.session_state.evaluator is None:
            st.session_state.evaluator = UIEvaluator(st.session_state.bot.qa_chain)
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()
        
        def progress_callback(current, total):
            progress_bar.progress(current / total)
            status_text.text(f"Running: {current}/{total} tests...")
        
        # Run evaluation
        with st.spinner("Running batch evaluation..."):
            batch_results = st.session_state.evaluator.evaluate_batch(
                test_cases_to_run,
                progress_callback=progress_callback
            )
        
        # Store results
        st.session_state.evaluation_results = batch_results
        
        progress_bar.progress(1.0)
        status_text.text("✓ Evaluation complete!")
        
        # Display summary
        st.write("---")
        st.subheader("📈 Batch Results Summary")
        
        summary = st.session_state.evaluator.get_results_summary(batch_results)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tests", summary["total_tests"])
        with col2:
            st.metric("Passed", summary["passed_tests"])
        with col3:
            st.metric("Failed", summary["failed_tests"])
        with col4:
            pass_rate = (summary["passed_tests"] / summary["total_tests"] * 100) if summary["total_tests"] > 0 else 0
            st.metric("Pass Rate", f"{pass_rate:.1f}%")


def display_evaluation_results():
    """Display evaluation results and metrics"""
    st.subheader("📊 Evaluation Results")
    
    if not st.session_state.evaluation_results:
        st.info("ℹ Run batch evaluation to see results here")
        return
    
    # Get summary
    if st.session_state.evaluator is None:
        st.session_state.evaluator = UIEvaluator(st.session_state.bot.qa_chain)
    
    summary = st.session_state.evaluator.get_results_summary(st.session_state.evaluation_results)
    
    # Display metrics summary
    st.write("**Overall Performance:**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tests", summary["total_tests"])
    with col2:
        st.metric("Passed", summary["passed_tests"])
    with col3:
        st.metric("Failed", summary["failed_tests"])
    with col4:
        pass_rate = (summary["passed_tests"] / summary["total_tests"] * 100) if summary["total_tests"] > 0 else 0
        st.metric("Pass Rate", f"{pass_rate:.1f}%")
    
    st.write("---")
    
    # Metrics visualization
    st.write("**Metric Performance:**")
    
    metric_cols = st.columns(2)
    for idx, (metric_name, metric_stats) in enumerate(summary.get("metrics", {}).items()):
        with metric_cols[idx % 2]:
            st.write(f"**{metric_name}:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average", f"{metric_stats['avg_score']:.2f}")
            with col2:
                st.metric("Min-Max", f"{metric_stats['min_score']:.2f} - {metric_stats['max_score']:.2f}")
            with col3:
                st.metric("Passed", f"{metric_stats['passed']}/{metric_stats['total']}")
    
    st.write("---")
    
    # Category breakdown
    if summary.get("by_category"):
        st.write("**Results by Category:**")
        category_data = summary["by_category"]
        
        df_category = pd.DataFrame([
            {
                "Category": cat.title(),
                "Total": stats["count"],
                "Passed": stats["passed"],
                "Failed": stats["count"] - stats["passed"]
            }
            for cat, stats in category_data.items()
        ])
        
        st.dataframe(df_category, use_container_width=True)
    
    st.write("---")
    
    # Detailed results table
    st.write("**Detailed Test Results:**")
    
    # Prepare data for table
    results_data = []
    for result in st.session_state.evaluation_results:
        if "error" not in result:
            metrics = result.get("metrics", {})
            passed_count = sum(1 for m in metrics.values() if m.get("passed", False))
            total_metrics = len([m for m in metrics.values() if m.get("score") is not None])
            
            results_data.append({
                "ID": result["test_id"],
                "Category": result.get("category", "N/A").title(),
                "Question": result["question"][:60] + "...",
                "Status": "✓ PASS" if result["overall_passed"] else "✗ FAIL",
                "Metrics": f"{passed_count}/{total_metrics}"
            })
    
    if results_data:
        df_results = pd.DataFrame(results_data)
        st.dataframe(df_results, use_container_width=True)
    
    st.write("---")
    
    # Export results
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Export Results as JSON"):
            try:
                json_file = st.session_state.evaluator.export_results_json(
                    results=st.session_state.evaluation_results
                )
                with open(json_file, 'r') as f:
                    st.download_button(
                        label="Download JSON",
                        data=f.read(),
                        file_name=Path(json_file).name,
                        mime="application/json"
                    )
                st.success(f"✓ Results exported to {json_file}")
            except Exception as e:
                st.error(f"✗ Error exporting: {str(e)}")


def display_metrics_dashboard():
    """Display comprehensive metrics dashboard"""
    st.subheader("📈 Metrics Dashboard")
    
    if not st.session_state.evaluation_results:
        st.info("ℹ Run batch evaluation to see dashboard")
        return
    
    if st.session_state.evaluator is None:
        st.session_state.evaluator = UIEvaluator(st.session_state.bot.qa_chain)
    
    summary = st.session_state.evaluator.get_results_summary(st.session_state.evaluation_results)
    
    # Create metric score visualization
    if summary.get("metrics"):
        metric_names = list(summary["metrics"].keys())
        avg_scores = [summary["metrics"][m]["avg_score"] for m in metric_names]
        
        fig_metrics = go.Figure()
        fig_metrics.add_trace(go.Bar(
            x=metric_names,
            y=avg_scores,
            marker=dict(
                color=avg_scores,
                colorscale="RdYlGn",
                showscale=True,
                colorbar=dict(title="Score")
            )
        ))
        fig_metrics.update_layout(
            title="Average Metric Scores",
            xaxis_title="Metrics",
            yaxis_title="Average Score",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_metrics, use_container_width=True)
    
    # Create pass/fail pie chart
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = go.Figure(data=[go.Pie(
            labels=["Passed", "Failed"],
            values=[summary["passed_tests"], summary["failed_tests"]],
            marker=dict(colors=["#10b981", "#ef4444"])
        )])
        fig_pie.update_layout(
            title="Pass/Fail Distribution",
            height=400
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Category pass rates
        if summary.get("by_category"):
            category_names = [cat.title() for cat in summary["by_category"].keys()]
            pass_rates = [
                (summary["by_category"][cat]["passed"] / summary["by_category"][cat]["count"] * 100)
                for cat in summary["by_category"].keys()
            ]
            
            fig_category = go.Figure()
            fig_category.add_trace(go.Bar(
                x=category_names,
                y=pass_rates,
                marker=dict(
                    color=pass_rates,
                    colorscale="RdYlGn",
                    showscale=True,
                    colorbar=dict(title="Pass Rate %")
                )
            ))
            fig_category.update_layout(
                title="Pass Rate by Category",
                xaxis_title="Category",
                yaxis_title="Pass Rate (%)",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig_category, use_container_width=True)



# =========================================================
# MAIN APPLICATION
# =========================================================

def main():

    apply_professional_styling()

    initialize_session()

    display_header()

    display_kpis()

    # Create tabs for Chat and Evaluation
    tab_chat, tab_evaluation = st.tabs(["💬 Chat", "🧪 Evaluation"])

    with tab_chat:

        col_main, col_side = st.columns([4, 1])

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

            if st.button("🔄 Reset Vector Database"):
                """Reset the vector store if there are embedding mismatches"""
                import shutil
                from pathlib import Path
                db_path = Path("src/chroma_db")
                if db_path.exists():
                    try:
                        shutil.rmtree(db_path)
                        st.success("✓ Vector database reset. Please reload documents.")
                    except Exception as e:
                        st.error(f"Failed to reset database: {str(e)}")
                else:
                    st.info("No database found to reset")

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

    # ========================================================
    # EVALUATION TAB
    # ========================================================

    with tab_evaluation:

        if not st.session_state.bot_initialized:
            st.warning("⚠️ Initialize RAG bot in the Chat tab first!")
        else:

            # Evaluation sub-tabs
            eval_tab1, eval_tab2, eval_tab3, eval_tab4 = st.tabs(
                ["📋 Test Cases", "🧪 Single Test", "⚡ Batch Run", "📊 Results & Dashboard"]
            )

            with eval_tab1:
                display_evaluation_test_cases()

            with eval_tab2:
                display_single_test_evaluation()

            with eval_tab3:
                display_batch_evaluation()

            with eval_tab4:

                col_res, col_dash = st.columns([1, 1])

                with col_res:
                    display_evaluation_results()

                with col_dash:
                    display_metrics_dashboard()

# =========================================================

if __name__ == "__main__":
    main()