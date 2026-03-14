"""
Evaluation module for RAG Bot
"""
import yaml
import logging
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm

from config import config
from validators import InputValidator, ValidationError
from rag.vector_store import load_vector_store
from rag.rag_chain import build_rag_chain

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

try:
    from deepeval import evaluate
    from deepeval.metrics import (
        HallucinationMetric,
        FaithfulnessMetric,
        AnswerRelevancyMetric,
        ContextualRecallMetric
    )
    from deepeval.test_case import LLMTestCase
    DEEPEVAL_AVAILABLE = True
except ImportError:
    DEEPEVAL_AVAILABLE = False
    logger.warning("DeepEval not installed. Using basic evaluation only.")


class TestCaseLoader:
    """Load and validate test cases from YAML"""

    @staticmethod
    def load_test_cases(filepath: str = None) -> List[Dict[str, Any]]:
        """
        Load test cases from YAML file
        
        Args:
            filepath: Path to test cases YAML file
            
        Returns:
            List of test case dictionaries
            
        Raises:
            ValidationError: If file or test cases are invalid
        """
        if filepath is None:
            filepath = str(config.EVAL_TEST_CASES_PATH)

        logger.info(f"Loading test cases from {filepath}")

        is_valid, error_msg = InputValidator.validate_file_path(filepath)
        if not is_valid:
            logger.error(f"File validation failed: {error_msg}")
            raise ValidationError(f"Invalid test cases file: {error_msg}")

        try:
            with open(filepath, "r") as f:
                test_cases = yaml.safe_load(f)

            if not isinstance(test_cases, list):
                logger.error("Test cases must be a list")
                raise ValidationError("Test cases must be a YAML list")

            if not test_cases:
                logger.error("Test cases list is empty")
                raise ValidationError("Test cases list is empty")

            # Validate test cases
            required_fields = ["question", "expected_answer"]
            for i, tc in enumerate(test_cases):
                if not isinstance(tc, dict):
                    logger.error(f"Test case {i} is not a dictionary")
                    raise ValidationError(f"Test case {i} must be a dictionary")

                for field in required_fields:
                    if field not in tc:
                        logger.error(f"Test case {i} missing field: {field}")
                        raise ValidationError(f"Test case {i} missing field: {field}")

            logger.info(f"Loaded {len(test_cases)} test cases")
            return test_cases

        except Exception as e:
            logger.error(f"Error loading test cases: {e}", exc_info=True)
            raise


class RAGEvaluator:
    """Evaluate RAG Bot performance"""

    def __init__(self, rag_chain):
        """
        Initialize evaluator
        
        Args:
            rag_chain: RAG chain instance
        """
        self.rag_chain = rag_chain
        self.results = []

    def run_inference(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Run RAG chain on test cases
        
        Args:
            test_cases: List of test cases
            
        Returns:
            List of results with answers
        """
        logger.info(f"Running inference on {len(test_cases)} test cases...")

        results = []

        for i, tc in enumerate(tqdm(test_cases, desc="Processing test cases")):
            try:
                question = tc["question"]

                # Validate question
                is_valid, error_msg = InputValidator.validate_question(question)
                if not is_valid:
                    logger.warning(f"Test case {i}: Invalid question - {error_msg}")
                    results.append({
                        "test_case": tc,
                        "answer": None,
                        "sources": [],
                        "error": error_msg
                    })
                    continue

                # Invoke chain
                logger.debug(f"Processing test case {i}: {question[:50]}...")
                response = self.rag_chain.invoke({"query": question})

                answer = response.get("result", "")
                sources = response.get("source_documents", [])

                results.append({
                    "test_case": tc,
                    "answer": answer,
                    "sources": sources,
                    "error": None
                })

            except Exception as e:
                logger.error(f"Error processing test case {i}: {e}")
                results.append({
                    "test_case": tc,
                    "answer": None,
                    "sources": [],
                    "error": str(e)
                })

        self.results = results
        logger.info(f"Inference completed. Successful: {sum(1 for r in results if r['error'] is None)}/{len(results)}")

        return results

    def run_deepeval_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run DeepEval metrics
        
        Args:
            results: List of inference results
            
        Returns:
            Dictionary with evaluation metrics
        """
        if not DEEPEVAL_AVAILABLE:
            logger.warning("DeepEval not available. Skipping deep evaluation.")
            return {}

        logger.info("Running DeepEval metrics...")

        # Filter valid results
        valid_results = [r for r in results if r["error"] is None]

        if not valid_results:
            logger.warning("No valid results to evaluate")
            return {}

        # Create test cases
        test_cases = []
        for r in valid_results:
            try:
                test_case = LLMTestCase(
                    input=r["test_case"]["question"],
                    actual_output=r["answer"],
                    expected_output=r["test_case"]["expected_answer"]
                )
                test_cases.append(test_case)
            except Exception as e:
                logger.warning(f"Could not create test case: {e}")

        if not test_cases:
            logger.warning("No valid test cases for evaluation")
            return {}

        try:
            metrics = [
                HallucinationMetric(),
                FaithfulnessMetric(),
                AnswerRelevancyMetric(),
                ContextualRecallMetric()
            ]

            logger.debug(f"Running {len(metrics)} metrics on {len(test_cases)} test cases")
            evaluate(test_cases=test_cases, metrics=metrics)
            logger.info("DeepEval metrics completed")

            return {"status": "completed"}

        except Exception as e:
            logger.error(f"Error running DeepEval metrics: {e}", exc_info=True)
            return {"error": str(e)}

    def print_results_summary(self, results: List[Dict[str, Any]]):
        """Print summary of results"""
        print("\n" + "=" * 80)
        print("EVALUATION RESULTS SUMMARY")
        print("=" * 80)

        total = len(results)
        successful = sum(1 for r in results if r["error"] is None)
        failed = total - successful

        print(f"\nTotal test cases: {total}")
        print(f"Successful: {successful} ({successful/total*100:.1f}%)")
        print(f"Failed: {failed} ({failed/total*100:.1f}%)")

        if failed > 0:
            print(f"\nFailed test cases:")
            for i, r in enumerate(results):
                if r["error"]:
                    print(f"  {i+1}. Question: {r['test_case']['question'][:50]}...")
                    print(f"     Error: {r['error']}")

        print("\n" + "=" * 80)

    def save_results(self, output_path: str = None):
        """Save results to JSON file"""
        if output_path is None:
            output_path = config.EVALUATION_DIR / "evaluation_results.json"

        logger.info(f"Saving results to {output_path}")

        try:
            # Convert to JSON-serializable format
            json_results = []
            for r in self.results:
                json_results.append({
                    "question": r["test_case"].get("question", ""),
                    "expected_answer": r["test_case"].get("expected_answer", ""),
                    "actual_answer": r["answer"],
                    "error": r["error"],
                    "source_count": len(r["sources"])
                })

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w") as f:
                json.dump(json_results, f, indent=2)

            logger.info(f"Results saved to {output_path}")

        except Exception as e:
            logger.error(f"Error saving results: {e}", exc_info=True)


def main():
    """Main evaluation entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate RAG Bot performance")
    parser.add_argument(
        "--test-cases",
        type=str,
        help="Path to test cases YAML file",
        default=None
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Path to save evaluation results",
        default=None
    )
    parser.add_argument(
        "--skip-deepeval",
        action="store_true",
        help="Skip DeepEval metrics"
    )

    args = parser.parse_args()

    try:
        # Load configuration
        config.validate()

        # Load test cases
        loader = TestCaseLoader()
        test_cases = loader.load_test_cases(args.test_cases)

        # Load vector store and build chain
        logger.info("Setting up RAG chain...")
        vectordb = load_vector_store()
        rag_chain = build_rag_chain(vectordb)

        # Run evaluation
        evaluator = RAGEvaluator(rag_chain)
        results = evaluator.run_inference(test_cases)

        # Print summary
        evaluator.print_results_summary(results)

        # Save results
        evaluator.save_results(args.output)

        # Run DeepEval if available
        if not args.skip_deepeval and DEEPEVAL_AVAILABLE:
            evaluator.run_deepeval_metrics(results)

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
