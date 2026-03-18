"""
DeepEval Integration for RAG Bot Evaluation

This module runs structured LLM evaluations using DeepEval metrics:
- Hallucination: Did the bot make up facts?
- Faithfulness: Did the bot stick to the source documents?
- Answer Relevancy: Did the bot answer the actual question?
- Contextual Recall: Did the bot retrieve relevant context?
"""

import os
import sys
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import time
from groq_model import GroqModel
from dotenv import load_dotenv

# Ensure environment is loaded before importing config
config_path = Path(__file__).parent.parent / "config" / ".env"
if config_path.exists():
    load_dotenv(config_path, override=True)
else:
    load_dotenv(override=True)

# Add src to path - handle different working directories
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# DeepEval imports
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    HallucinationMetric,
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualRecallMetric
)

# RAG Bot imports
from config import config
from rag.loader import load_documents
from rag.vector_store import build_vector_store, get_embeddings
from rag.rag_chain import build_rag_chain

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

DEEPEVAL_AVAILABLE = True


class TestCaseLoader:
    """Load and validate test cases from YAML"""

class RAGEvaluator:
    """Evaluate RAG bot using DeepEval metrics"""
    
    def __init__(self, documents_dir: str = None):
        """Initialize evaluator with RAG bot and metrics"""
        self.documents_dir = documents_dir or str(config.DOCUMENTS_DIR)
        self.results = []
        self.metrics_summary = {}
        self.qa_chain = None
        self._setup_rag_bot()
        self.groq_llm = GroqModel(
            api_key=os.getenv("GROQ_API_KEY") or config.GROQ_API_KEY,
            model_name=os.getenv("GROQ_MODEL") or config.GROQ_MODEL
        )
    
    def _setup_rag_bot(self):
        """Initialize RAG bot with documents"""
        logger.info("Setting up RAG bot...")
        
        try:
            # Find all text and PDF files
            doc_files = []
            doc_path = Path(self.documents_dir)
            
            if not doc_path.exists():
                logger.error(f"Documents directory not found: {self.documents_dir}")
                raise FileNotFoundError(f"Documents directory not found: {self.documents_dir}")
            
            # Get all TXT files
            doc_files.extend(doc_path.glob("*.txt"))
            # Get all PDF files
            doc_files.extend(doc_path.glob("*.pdf"))
            
            if not doc_files:
                logger.error(f"No documents found in {self.documents_dir}")
                raise FileNotFoundError(f"No documents found in {self.documents_dir}")
            
            logger.info(f"Found {len(doc_files)} documents")
            
            # Load and chunk documents
            all_chunks = []
            for doc_file in doc_files:
                logger.info(f"Loading {doc_file.name}...")
                try:
                    if doc_file.suffix.lower() == '.pdf':
                        from langchain_community.document_loaders import PyPDFLoader
                        loader = PyPDFLoader(str(doc_file))
                        docs = loader.load()
                    else:  # TXT files
                        from langchain_community.document_loaders import TextLoader
                        loader = TextLoader(str(doc_file))
                        docs = loader.load()
                    
                    # Chunk documents
                    from langchain_text_splitters import RecursiveCharacterTextSplitter
                    splitter = RecursiveCharacterTextSplitter(
                        chunk_size=config.PDF_CHUNK_SIZE,
                        chunk_overlap=config.PDF_CHUNK_OVERLAP,
                        separators=["\n\n", "\n", " ", ""]
                    )
                    chunks = splitter.split_documents(docs)
                    all_chunks.extend(chunks)
                    logger.info(f"  ✓ Loaded {len(chunks)} chunks from {doc_file.name}")
                    
                except Exception as e:
                    logger.error(f"  ✗ Error loading {doc_file}: {str(e)}")
                    continue
            
            if not all_chunks:
                raise ValueError("No document chunks created")
            
            logger.info(f"Total chunks loaded: {len(all_chunks)}")
            
            # Build vector store
            logger.info("Building vector store...")
            embeddings = get_embeddings()
            vectordb = build_vector_store(all_chunks)
            logger.info("✓ Vector store built")
            
            # Build RAG chain
            logger.info("Building RAG chain...")
            self.qa_chain = build_rag_chain(vectordb)
            logger.info("✓ RAG chain built successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup RAG bot: {str(e)}")
            raise
    
    def get_rag_answer(self, question: str) -> tuple:
        """
        Get answer from RAG bot
        
        Returns:
            (answer, context, source_docs)
        """
        try:
            result = self.qa_chain.invoke({"query": question})
            answer = result.get("result", "")
            source_docs = result.get("source_documents", [])
            
            # Extract context from source documents
            context = [doc.page_content for doc in source_docs]
                     
            return answer, context, source_docs
            
        except Exception as e:
            logger.error(f"Error getting RAG answer: {str(e)}")
            return "", "", []
    
    def evaluate_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single test case with all metrics
        
        Args:
            test_case: Dict with id, question, expected_answer, source_context
            
        Returns:
            Dict with metric scores and details
        """
        question = test_case.get("question", "")
        expected_answer = test_case.get("expected_answer", "")
        
        logger.info(f"Evaluating Q#{test_case['id']}: {question[:50]}...")
        
        # Get RAG bot answer
        actual_answer, context, source_docs = self.get_rag_answer(question)
        
        # Prepare retrieval context
        retrieval_context = [doc.page_content for doc in source_docs] if source_docs else ["No context retrieved"]
        
        # Create test case for DeepEval
        llm_test_case = LLMTestCase(
            input=question,
            actual_output=actual_answer,
            expected_output=expected_answer,
            context=context,
            retrieval_context=retrieval_context
        )
        
        # Run metrics with error handling
        metrics_results = {}
        
        # 1. Hallucination Metric (Lower is better, 0 is perfect)
        try:
            hallucination_metric = HallucinationMetric(model=self.groq_llm)
            #hallucination_metric = HallucinationMetric()
            hallucination_metric.measure(llm_test_case)
            time.sleep(1.1)  # Add small delay to avoid rate limiting
            metrics_results["Hallucination"] = {
                "score": hallucination_metric.score,
                "reason": hallucination_metric.reason,
                "threshold": 0.0,
                "passed": hallucination_metric.score == 0.0
            }
            logger.debug(f"  Hallucination: {hallucination_metric.score:.2f}")
        except Exception as e:
            logger.warning(f"  Hallucination metric failed: {str(e)}")
            metrics_results["Hallucination"] = {"score": None, "error": str(e), "passed": False}
        
        # 2. Faithfulness Metric (Higher is better, 0-1 scale)
        try:
            faithfulness_metric = FaithfulnessMetric(model=self.groq_llm)
            #faithfulness_metric = FaithfulnessMetric()
            faithfulness_metric.measure(llm_test_case)
            time.sleep(1.1) # Add small delay to avoid rate limiting
            metrics_results["Faithfulness"] = {
                "score": faithfulness_metric.score,
                "reason": faithfulness_metric.reason,
                "threshold": 0.7,
                "passed": faithfulness_metric.score >= 0.7
            }
            logger.debug(f"  Faithfulness: {faithfulness_metric.score:.2f}")
        except Exception as e:
            logger.warning(f"  Faithfulness metric failed: {str(e)}")
            metrics_results["Faithfulness"] = {"score": None, "error": str(e), "passed": False}
        
        # 3. Answer Relevancy Metric (Higher is better, 0-1 scale)
        try:
            relevancy_metric = AnswerRelevancyMetric(model=self.groq_llm)
            #relevancy_metric = AnswerRelevancyMetric()
            relevancy_metric.measure(llm_test_case)
            time.sleep(1.1) # Add small delay to avoid rate limiting

            metrics_results["AnswerRelevancy"] = {
                "score": relevancy_metric.score,
                "reason": relevancy_metric.reason,
                "threshold": 0.7,
                "passed": relevancy_metric.score >= 0.7
            }
            logger.debug(f"  Answer Relevancy: {relevancy_metric.score:.2f}")
        except Exception as e:
            logger.warning(f"  Answer Relevancy metric failed: {str(e)}")
            metrics_results["AnswerRelevancy"] = {"score": None, "error": str(e), "passed": False}
        
        # 4. Contextual Recall Metric (Higher is better, 0-1 scale)
        try:
            contextual_recall_metric = ContextualRecallMetric(model=self.groq_llm)
            #contextual_recall_metric = ContextualRecallMetric()
            contextual_recall_metric.measure(llm_test_case)
            time.sleep(1.1) # Add small delay to avoid rate limiting

            metrics_results["ContextualRecall"] = {
                "score": contextual_recall_metric.score,
                "reason": contextual_recall_metric.reason,
                "threshold": 0.6,
                "passed": contextual_recall_metric.score >= 0.6
            }
            logger.debug(f"  Contextual Recall: {contextual_recall_metric.score:.2f}")
        except Exception as e:
            logger.warning(f"  Contextual Recall metric failed: {str(e)}")
            metrics_results["ContextualRecall"] = {"score": None, "error": str(e), "passed": False}
        
        # Compile results
        valid_metrics = [
            m for m in metrics_results.values()
            if m.get("score") is not None
        ]

        passed_metrics = [
            m for m in valid_metrics
            if m.get("passed")
        ]

        overall_passed = len(passed_metrics) >= 2   # majority pass

        logger.info(f"Hallucination Score: {metrics_results['Hallucination']}")
        logger.info(f"Faithfulness Score: {metrics_results['Faithfulness']}")
        logger.info(f"Answer Relevancy Score: {metrics_results['AnswerRelevancy']}")
        logger.info(f"Contextual Recall Score: {metrics_results['ContextualRecall']}")

        result = {
            "test_id": test_case["id"],
            "category": test_case.get("category", "unknown"),
            "question": question,
            "expected_answer": expected_answer,
            "actual_answer": actual_answer,
            "context": context,
            "num_retrieved_docs": len(source_docs),
            "metrics": metrics_results,
            "overall_passed": overall_passed,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def run_evaluation(self, test_cases_file: str = None) -> List[Dict[str, Any]]:
        """
        Run evaluation on all test cases
        
        Args:
            test_cases_file: Path to YAML file with test cases
            
        Returns:
            List of evaluation results
        """
        if test_cases_file is None:
            test_cases_file = str(Path(__file__).parent / "test_cases.yaml")
        
        logger.info(f"Loading test cases from {test_cases_file}...")
        
        # Load test cases
        with open(test_cases_file, 'r') as f:
            data = yaml.safe_load(f)
        
        test_cases = data.get("test_cases", [])
        logger.info(f"Loaded {len(test_cases)} test cases")
        
        # Run evaluation on each test case
        for test_case in test_cases:
            try:
                result = self.evaluate_test_case(test_case)
                self.results.append(result)
            except Exception as e:
                logger.error(f"Error evaluating test case {test_case['id']}: {str(e)}")
                self.results.append({
                    "test_id": test_case["id"],
                    "question": test_case.get("question", ""),
                    "expected_answer": test_case.get("expected_answer", ""),  # ✅ ADD
                    "actual_answer": "",
                    "metrics": {},
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        logger.info(f"\n✓ Evaluation complete: {len(self.results)} test cases processed")
        return self.results
    
    def save_results(self, output_file: str = None) -> str:
        """Save evaluation results to JSON file"""
        if output_file is None:
            output_dir = Path(__file__).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = str(output_dir / f"evaluation_results_{timestamp}.json")
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info(f"✓ Results saved to {output_file}")
        return output_file
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics from evaluation results"""
        if not self.results:
            return {}
        
        summary = {
            "total_tests": len(self.results),
            "passed_tests": sum(1 for r in self.results if r.get("overall_passed", False)),
            "failed_tests": sum(1 for r in self.results if not r.get("overall_passed", True)),
            "metrics": {}
        }
        
        # Calculate per-metric statistics
        for metric_name in ["Hallucination", "Faithfulness", "AnswerRelevancy", "ContextualRecall"]:
            scores = []
            for result in self.results:
                if "metrics" in result:
                    metric = result["metrics"].get(metric_name, {})
                    if metric.get("score") is not None:
                        scores.append(metric["score"])
            
            if scores:
                summary["metrics"][metric_name] = {
                    "avg_score": sum(scores) / len(scores),
                    "min_score": min(scores),
                    "max_score": max(scores),
                    "passed": sum(1 for s in scores if (
                        (metric_name == "Hallucination" and s == 0.0) or
                        (metric_name != "Hallucination" and s >= 0.7)
                    ))
                }
        
        # Category breakdown
        summary["by_category"] = {}
        for category in set(r.get("category") for r in self.results if "category" in r):
            category_results = [r for r in self.results if r.get("category") == category]
            summary["by_category"][category] = {
                "count": len(category_results),
                "passed": sum(1 for r in category_results if r.get("overall_passed", False))
            }
        
        return summary
    
    def print_summary(self):
        """Print evaluation summary to console"""
        summary = self.generate_summary()
        
        print("\n" + "="*80)
        print("RAG BOT EVALUATION SUMMARY")
        print("="*80)
        
        print(f"\nOverall: {summary['passed_tests']}/{summary['total_tests']} tests passed")
        
        print("\nMetric Performance:")
        for metric, stats in summary.get("metrics", {}).items():
            print(f"  {metric}:")
            print(f"    Avg Score: {stats['avg_score']:.2f}")
            print(f"    Range: {stats['min_score']:.2f} - {stats['max_score']:.2f}")
            print(f"    Passed: {stats['passed']}/{summary['total_tests']}")
        
        print("\nResults by Category:")
        for category, stats in summary.get("by_category", {}).items():
            print(f"  {category}: {stats['passed']}/{stats['count']} passed")
        
        print("="*80 + "\n")
        
        return summary
    
    def export_detailed_report(self, output_file: str = None) -> str:
        """Export detailed report in markdown format"""
        if output_file is None:
            output_dir = Path(__file__).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = str(output_dir / f"evaluation_report_{timestamp}.md")
        
        summary = self.generate_summary()
        
        with open(output_file, 'w') as f:
            f.write("# RAG Bot Evaluation Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary stats
            f.write(" Summary Statistics\n\n")
            f.write(f"- **Total Tests**: {summary['total_tests']}\n")
            f.write(f"- **Passed**: {summary['passed_tests']}\n")
            f.write(f"- **Failed**: {summary['failed_tests']}\n")
            f.write(f"- **Pass Rate**: {(summary['passed_tests']/summary['total_tests']*100):.1f}%\n\n")
            
            # Metric performance
            f.write(" Metric Performance\n\n")
            for metric, stats in summary.get("metrics", {}).items():
                f.write(f"# {metric}\n")
                f.write(f"- Average Score: {stats['avg_score']:.2f}\n")
                f.write(f"- Min: {stats['min_score']:.2f}, Max: {stats['max_score']:.2f}\n")
                f.write(f"- Passed: {stats['passed']}/{summary['total_tests']}\n\n")
            
            # Category breakdown
            f.write(" Results by Category\n\n")
            for category, stats in summary.get("by_category", {}).items():
                f.write(f"- **{category}**: {stats['passed']}/{stats['count']} passed\n")
            
            f.write("\n Detailed Results\n\n")
            for result in self.results:
                f.write(f"# Test #{result['test_id']}\n")
                f.write(f"**Category**: {result.get('category', 'unknown')}\n")
                f.write(f"**Question**: {result['question']}\n\n")
                f.write(f"**Expected**: {result['expected_answer']}\n\n")
                f.write(f"**Actual**: {result['actual_answer']}\n\n")
                
                if "metrics" in result:
                    f.write("**Metrics**:\n")
                    for metric, m_data in result["metrics"].items():
                        score = m_data.get("score")
                        if score is not None:
                            passed = "PASS" if m_data.get("passed") else "FAIL"
                            f.write(f"- {metric}: {score:.2f} {passed}\n")
                            if m_data.get("reason"):
                                f.write(f"  - Reason: {m_data['reason']}\n")
                f.write("\n---\n\n")
        
        logger.info(f"✓ Report saved to {output_file}")
        return output_file


def main():
    """Main evaluation runner"""
    # Set up GROQ API key for DeepEval metrics
    if config.GROQ_API_KEY:
        os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY
    else:
        logger.error("❌ GROQ_API_KEY not found in environment or config!")
        logger.error("Please set GROQ_API_KEY in config/.env")
        sys.exit(1)
    
    logger.info("Starting RAG Bot Evaluation with DeepEval")
    logger.info(f"LLM Provider: {config.LLM_PROVIDER}")
    
    try:
        # Initialize evaluator
        evaluator = RAGEvaluator()
        
        # Run evaluation
        test_cases_file = str(Path(__file__).parent / "test_cases.yaml")
        evaluator.run_evaluation(test_cases_file)
        
        # Save results
        json_file = evaluator.save_results()
        
        # Print summary
        evaluator.print_summary()
        
        # Export detailed report
        report_file = evaluator.export_detailed_report()
        
        logger.info(f"\n✓ Evaluation complete!")
        logger.info(f"  - JSON Results: {json_file}")
        logger.info(f"  - Markdown Report: {report_file}")
        
    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
