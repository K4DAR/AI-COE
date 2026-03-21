"""
Configuration module for RAG Bot
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from config folder
config_path = Path(__file__).parent.parent / "config" / ".env"
if config_path.exists():
    load_dotenv(config_path)
else:
    load_dotenv()


class Config:
    """Main configuration class"""

    # Paths
    BASE_DIR = Path(__file__).parent
    PROJECT_ROOT = BASE_DIR.parent
    DATA_DIR = BASE_DIR / "data"
    DOCUMENTS_DIR = DATA_DIR / "documents"
    CHROMA_DB_DIR = BASE_DIR / "chroma_db"
    EVALUATION_DIR = PROJECT_ROOT / "tests" / "evaluation"

    # LLM Provider Configuration (supports multiple providers)
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
    
    # Groq Configuration (FREE - RECOMMENDED)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")  # Fast & free model
    
    # Temperature for all providers
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", 0.7))

    # Document Loading Configuration
    PDF_CHUNK_SIZE = 800
    PDF_CHUNK_OVERLAP = 100
    ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}

    # Vector Store Configuration
    VECTOR_STORE_TYPE = "chroma"
    RETRIEVER_K = 1  # Number of documents to retrieve

    # Validation Configuration
    MIN_QUESTION_LENGTH = 3
    MAX_QUESTION_LENGTH = 500
    MIN_ANSWER_LENGTH = 10
    MAX_ANSWER_LENGTH = 5000

    # Logging Configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Evaluation Configuration
    EVAL_TEST_CASES_PATH = EVALUATION_DIR / "test_cases.yaml"
    MIN_CONFIDENCE_SCORE = 0.5

    @staticmethod
    def validate():
        """Validate configuration"""
        provider = Config.LLM_PROVIDER
        
        # Validate based on selected provider
        if provider == "groq":
            if not Config.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY environment variable is not set. Get a free key at: https://console.groq.com")
        else:
            raise ValueError(f"Invalid LLM_PROVIDER: {provider}. Use: openai, groq, or ollama")

        # Create required directories
        Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        Config.DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        Config.EVALUATION_DIR.mkdir(parents=True, exist_ok=True)

        return True


# Create config instance
config = Config()
