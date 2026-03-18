"""
RAG Bot Evaluation Module
Integrated evaluation logic for Streamlit UI
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import yaml
import os
from dotenv import load_dotenv

# Ensure environment is loaded before importing config
config_path = Path(__file__).parent.parent / "config" / ".env"
if config_path.exists():
    load_dotenv(config_path, override=True)
else:
    load_dotenv(override=True)

from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    HallucinationMetric,
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualRecallMetric
)

from config import config

logger = logging.getLogger(__name__)


def _get_groq_llm():
    """
    Lazy-load Groq LLM for metrics (on-demand, not at import time)
    This ensures environment variables are loaded before configuration
    """
    try:
        from langchain_groq import ChatGroq
        from deepeval.models import DeepEvalBaseLLM
        
        # Reload environment variables to ensure they're fresh in Streamlit context
        config_path = Path(__file__).parent.parent / "config" / ".env"
        if config_path.exists():
            load_dotenv(config_path, override=True)
        
        # Try to get API key from environment or config
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            try:
                groq_key = config.GROQ_API_KEY
            except:
                groq_key = None
        
        if not groq_key:
            logger.warning("GROQ_API_KEY not found in environment or config")
            return None
        
        
        # Create custom DeepEval-compatible Groq wrapper
        class GroqModel(DeepEvalBaseLLM):
            def __init__(self, api_key: str, model_name: str = "mixtral-8x7b-32768"):
                self.api_key = api_key
                self.model_name = model_name
                self.groq_client = ChatGroq(
                    api_key=api_key,
                    model=model_name,
                    temperature=0.0
                )
            
            def load_model(self):
                return self.groq_client
            
            def get_model_name(self) -> str:
                return self.model_name
            
            def generate(self, prompt: str) -> str:
                try:
                    response = self.groq_client.invoke(prompt)
                    return response.content
                except Exception as e:
                    logger.error(f"Groq generation error: {str(e)}")
                    raise
            
            async def a_generate(self, prompt: str) -> str:
                try:
                    response = await self.groq_client.ainvoke(prompt)
                    return response.content
                except Exception as e:
                    logger.error(f"Groq async generation error: {str(e)}")
                    raise
        
        # Create instance
        groq_model = GroqModel(api_key=groq_key, model_name=config.GROQ_MODEL)
        logger.info(f"✓ Configured Groq ({config.GROQ_MODEL}) as metric judge")
        return groq_model
        
    except Exception as e:
        logger.error(f"Failed to configure Groq for metrics: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

# Lazy-load Groq - don't configure at module import time
_groq_llm = None
_groq_llm_initialized = False

def _ensure_groq_configured():
    """Ensure Groq is configured, doing it lazily on first call"""
    global _groq_llm, _groq_llm_initialized
    if not _groq_llm_initialized:
        _groq_llm = _get_groq_llm()
        _groq_llm_initialized = True
    return _groq_llm


class EvaluationMetrics:
    """Helper class for metric evaluation"""
    
    METRIC_THRESHOLDS = {
        "Hallucination": {"value": 0.0, "operator": "=="},  # Should be 0
        "Faithfulness": {"value": 0.7, "operator": ">="},   # At least 70%
        "AnswerRelevancy": {"value": 0.7, "operator": ">="},  # At least 70%
        "ContextualRecall": {"value": 0.6, "operator": ">="}  # At least 60%
    }

    def evaluate_response_single_pass(question: str, actual_answer: str, expected_answer: str, retrieval_context: List[str]) -> Dict[str, Any]:
        groq_llm = _ensure_groq_configured()
        
        if not groq_llm:
            return {"error": "Groq not configured", "overall_passed": False}

        context_text = "\n\n".join(retrieval_context)

        prompt = f"""
                You are an expert evaluator for RAG systems.

                Evaluate the response based on the following:

                QUESTION:
                {question}

                EXPECTED ANSWER:
                {expected_answer}

                ACTUAL ANSWER:
                {actual_answer}

                RETRIEVED CONTEXT:
                {context_text}

                Return STRICT JSON ONLY (no explanation outside JSON):

                {{
                "hallucination": <float between 0 and 1>,
                "faithfulness": <float between 0 and 1>,
                "answer_relevancy": <float between 0 and 1>,
                "contextual_recall": <float between 0 and 1>,
                "reasoning": "short explanation"
                }}

                Scoring rules:
                - hallucination = 0 means no hallucination
                - faithfulness = grounded in context
                - answer_relevancy = answers the question
                - contextual_recall = uses retrieved context properly
                """

        try:
            raw_output = groq_llm.generate(prompt)

            # Extract JSON safely
            import json
            import re

            json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
            if not json_match:
                raise ValueError("No valid JSON found in LLM output")

            parsed = json.loads(json_match.group())

            metrics = {
                "Hallucination": {
                    "score": parsed["hallucination"],
                    "passed": parsed["hallucination"] == 0.0
                },
                "Faithfulness": {
                    "score": parsed["faithfulness"],
                    "passed": parsed["faithfulness"] >= 0.7
                },
                "AnswerRelevancy": {
                    "score": parsed["answer_relevancy"],
                    "passed": parsed["answer_relevancy"] >= 0.7
                },
                "ContextualRecall": {
                    "score": parsed["contextual_recall"],
                    "passed": parsed["contextual_recall"] >= 0.6
                }
            }

            overall_passed = all(m["passed"] for m in metrics.values())

            return {
                "metrics": metrics,
                "overall_passed": overall_passed,
                "reason": parsed.get("reasoning", "")
            }

        except Exception as e:
            logger.error(f"Single-pass evaluation failed: {str(e)}")
            
            return {
                "metrics": {
                    "Hallucination": {"error": str(e), "passed": False},
                    "Faithfulness": {"error": str(e), "passed": False},
                    "AnswerRelevancy": {"error": str(e), "passed": False},
                    "ContextualRecall": {"error": str(e), "passed": False}
                },
                "overall_passed": False,
                "error": str(e)
            }
    
    @staticmethod
    def _check_llm_configured() -> Tuple[bool, str]:
        """
        Check if Groq is configured for metrics
        Returns (is_configured, message)
        """
        # Reload environment variables to ensure they're fresh in Streamlit context
        config_path = Path(__file__).parent.parent / "config" / ".env"
        if config_path.exists():
            load_dotenv(config_path, override=True)
        
        groq_key = os.getenv("GROQ_API_KEY") or config.GROQ_API_KEY
        if groq_key:
            return True, f"✓ Using Groq ({config.GROQ_MODEL}) for evaluation metrics"
        
        return False, (
            "Groq API Key Not Configured!\n\n"
            "Evaluation metrics require GROQ_API_KEY.\n\n"
            "To fix:\n"
            "1. Set GROQ_API_KEY in config/.env\n"
            "2. Get a free key from: https://console.groq.com\n\n"
            "Groq is used for both RAG bot AND evaluation metrics."
        )
    
    @staticmethod
    def evaluate_response(question: str, actual_answer: str, expected_answer: str, 
                         retrieval_context: List[str]) -> Dict[str, Any]:
        """
        Evaluate a single response against all metrics
        
        Args:
            question: The question asked
            actual_answer: The bot's answer
            expected_answer: The expected/reference answer
            retrieval_context: Retrieved document contexts
            
        Returns:
            Dict with metric scores and pass/fail status
        """
        # Ensure Groq LLM is configured (lazy-load on first use)
        groq_llm = _ensure_groq_configured()
        
        if not groq_llm:
            error_msg = (
                "Groq API Key Not Configured!\n\n"
                "Evaluation metrics require GROQ_API_KEY.\n\n"
                "To fix:\n"
                "1. Set GROQ_API_KEY in config/.env\n"
                "2. Get a free key from: https://console.groq.com\n\n"
                "Groq is used for both RAG bot AND evaluation metrics."
            )
            return {
                "metrics": {
                    "Hallucination": {"error": error_msg, "passed": False},
                    "Faithfulness": {"error": error_msg, "passed": False},
                    "AnswerRelevancy": {"error": error_msg, "passed": False},
                    "ContextualRecall": {"error": error_msg, "passed": False}
                },
                "overall_passed": False,
                "error": error_msg
            }
        
        # Create test case for DeepEval
        llm_test_case = LLMTestCase(
            input=question,
            actual_output=actual_answer,
            expected_output=expected_answer,
            context=retrieval_context if retrieval_context else ["No context available"],
            retrieval_context=retrieval_context if retrieval_context else ["No context available"]
        )
                
        metrics_results = {}
        
        # 1. Hallucination Metric
        try:
            metric = HallucinationMetric(model=groq_llm)
            metric.measure(llm_test_case)
            metrics_results["Hallucination"] = {
                "score": metric.score,
                "reason": metric.reason,
                "threshold": 0.0,
                "passed": metric.score == 0.0
            }
            logger.debug(f"Hallucination: {metric.score:.2f}")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Hallucination metric failed: {error_msg}")
            metrics_results["Hallucination"] = {
                "error": f"Error: {error_msg[:100]}",
                "passed": False
            }
        
        # 2. Faithfulness Metric
        try:
            metric = FaithfulnessMetric(model=groq_llm)
            metric.measure(llm_test_case)
            metrics_results["Faithfulness"] = {
                "score": metric.score,
                "reason": metric.reason,
                "threshold": 0.7,
                "passed": metric.score >= 0.7
            }
            logger.debug(f"Faithfulness: {metric.score:.2f}")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Faithfulness metric failed: {error_msg}")
            metrics_results["Faithfulness"] = {
                "error": f"Error: {error_msg[:100]}",
                "passed": False
            }
        
        # 3. Answer Relevancy Metric
        try:
            metric = AnswerRelevancyMetric(model=groq_llm)
            metric.measure(llm_test_case)
            metrics_results["AnswerRelevancy"] = {
                "score": metric.score,
                "reason": metric.reason,
                "threshold": 0.7,
                "passed": metric.score >= 0.7
            }
            logger.debug(f"Answer Relevancy: {metric.score:.2f}")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Answer Relevancy metric failed: {error_msg}")
            metrics_results["AnswerRelevancy"] = {
                "error": f"Error: {error_msg[:100]}",
                "passed": False
            }
        
        # 4. Contextual Recall Metric
        try:
            metric = ContextualRecallMetric(model=groq_llm)
            metric.measure(llm_test_case)
            metrics_results["ContextualRecall"] = {
                "score": metric.score,
                "reason": metric.reason,
                "threshold": 0.6,
                "passed": metric.score >= 0.6
            }
            logger.debug(f"Contextual Recall: {metric.score:.2f}")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Contextual Recall metric failed: {error_msg}")
            metrics_results["ContextualRecall"] = {
                "error": f"Error: {error_msg[:100]}",
                "passed": False
            }
        
        # Overall pass status
        overall_passed = True

        for m in metrics_results.values():
            if m.get("score") is None:
                overall_passed = False
            elif not m.get("passed", False):
                overall_passed = False
        
        return {
            "metrics": metrics_results,
            "overall_passed": overall_passed
        }


class TestCaseManager:
    """Manage test cases loaded from YAML"""
    
    def __init__(self):
        """Initialize test case manager"""
        self.test_cases = []
        self.default_file = Path(__file__).parent.parent / "tests" / "evaluation" / "test_cases.yaml"
    
    def load_test_cases(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load test cases from YAML file
        
        Args:
            file_path: Path to YAML test cases file
            
        Returns:
            List of test cases
        """
        yaml_file = Path(file_path) if file_path else self.default_file
        
        if not yaml_file.exists():
            raise FileNotFoundError(f"Test cases file not found: {yaml_file}")
        
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
            
            self.test_cases = data.get("test_cases", [])
            logger.info(f"Loaded {len(self.test_cases)} test cases")
            return self.test_cases
            
        except Exception as e:
            logger.error(f"Error loading test cases: {str(e)}")
            raise
    
    def get_test_cases(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get test cases, optionally filtered by category
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of test cases
        """
        if category:
            return [tc for tc in self.test_cases if tc.get("category") == category]
        return self.test_cases
    
    def get_test_case_by_id(self, test_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific test case by ID"""
        for tc in self.test_cases:
            if tc.get("id") == test_id:
                return tc
        return None


class UIEvaluator:
    """Evaluator designed for Streamlit UI integration"""
    
    def __init__(self, qa_chain):
        """
        Initialize evaluator
        
        Args:
            qa_chain: The RAG chain to evaluate
        """
        self.qa_chain = qa_chain
        self.results = []
        self.test_case_manager = TestCaseManager()
    
    @staticmethod
    def _check_llm_for_metrics() -> Tuple[bool, str]:
        """Check if LLM judge is configured for metrics"""
        return EvaluationMetrics._check_llm_configured()
    
    def evaluate_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single test case
        
        Args:
            test_case: Test case dict with question, expected_answer, etc.
            
        Returns:
            Evaluation result with metrics
        """
        question = test_case.get("question", "")
        expected_answer = test_case.get("expected_answer", "")
        
        logger.info(f"Evaluating Q#{test_case['id']}: {question[:50]}...")
        
        # Get RAG bot answer
        try:
            result = self.qa_chain.invoke({"query": question})
            actual_answer = result.get("result", "")
            source_docs = result.get("source_documents", [])
            
            # Extract context from source documents
            retrieval_context = [
                doc.page_content for doc in source_docs
            ] if source_docs else ["No context retrieved"]
            
        except Exception as e:
            logger.error(f"Error getting RAG answer: {str(e)}")
            return {
                "test_id": test_case["id"],
                "question": question,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        
        # Evaluate metrics
        eval_result = EvaluationMetrics.evaluate_response_single_pass(
            question, actual_answer, expected_answer, retrieval_context
        )
        
        # Compile result
        result_data = {
            "test_id": test_case["id"],
            "category": test_case.get("category", "unknown"),
            "question": question,
            "expected_answer": expected_answer,
            "actual_answer": actual_answer,
            "context": "\n\n".join(retrieval_context),
            "num_retrieved_docs": len(source_docs),
            "metrics": eval_result["metrics"],
            "overall_passed": eval_result["overall_passed"],
            "timestamp": datetime.now().isoformat()
        }
        
        self.results.append(result_data)
        return result_data
    
    def evaluate_batch(self, test_cases: List[Dict[str, Any]], 
                      progress_callback=None) -> List[Dict[str, Any]]:
        """
        Evaluate multiple test cases
        
        Args:
            test_cases: List of test cases to evaluate
            progress_callback: Optional callback function for progress updates
                             Receives (current, total) as arguments
            
        Returns:
            List of evaluation results
        """
        results = []
        
        for idx, test_case in enumerate(test_cases):
            result = self.evaluate_single_test(test_case)
            results.append(result)
            
            if progress_callback:
                progress_callback(idx + 1, len(test_cases))
        
        return results
    
    def get_results_summary(self, results: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Generate summary statistics from results
        
        Args:
            results: Optional list of results (uses self.results if not provided)
            
        Returns:
            Summary dict with statistics
        """
        eval_results = results if results is not None else self.results
        
        if not eval_results:
            return {}
        
        summary = {
            "total_tests": len(eval_results),
            "passed_tests": sum(1 for r in eval_results if r.get("overall_passed", False)),
            "failed_tests": sum(1 for r in eval_results if not r.get("overall_passed", True)),
            "metrics": {}
        }
        
        # Calculate per-metric statistics
        for metric_name in ["Hallucination", "Faithfulness", "AnswerRelevancy", "ContextualRecall"]:
            scores = []
            passed_count = 0
            
            for result in eval_results:
                if "metrics" in result:
                    metric = result["metrics"].get(metric_name, {})
                    if metric.get("score") is not None:
                        scores.append(metric["score"])
                        if metric.get("passed"):
                            passed_count += 1
            
            if scores:
                summary["metrics"][metric_name] = {
                    "avg_score": sum(scores) / len(scores),
                    "min_score": min(scores),
                    "max_score": max(scores),
                    "passed": passed_count,
                    "total": len(scores)
                }
        
        # Category breakdown
        summary["by_category"] = {}
        for category in set(r.get("category") for r in eval_results if "category" in r):
            category_results = [r for r in eval_results if r.get("category") == category]
            summary["by_category"][category] = {
                "count": len(category_results),
                "passed": sum(1 for r in category_results if r.get("overall_passed", False))
            }
        
        return summary
    
    def export_results_json(self, output_file: Optional[str] = None, 
                           results: Optional[List[Dict]] = None) -> str:
        """
        Export results to JSON file
        
        Args:
            output_file: Path to save JSON (auto-generated if not provided)
            results: Optional list of results (uses self.results if not provided)
            
        Returns:
            Path to output file
        """
        eval_results = results if results is not None else self.results
        
        if output_file is None:
            output_dir = Path(__file__).parent.parent / "tests" / "evaluation"
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = str(output_dir / f"evaluation_results_{timestamp}.json")
        
        with open(output_file, 'w') as f:
            json.dump(eval_results, f, indent=2, default=str)
        
        logger.info(f"Results saved to {output_file}")
        return output_file
