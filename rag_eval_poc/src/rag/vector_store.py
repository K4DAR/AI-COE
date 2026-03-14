"""
Vector store management module for RAG Bot
"""
import logging
import numpy as np
from pathlib import Path
from langchain_community.vectorstores import Chroma
from config import config

logger = logging.getLogger(__name__)


def get_embeddings():
    """
    Get embeddings based on configured provider.
    Uses offline models by default (no API key needed).
    
    Tries in order:
    1. langchain-huggingface (if installed)
    2. sentence-transformers (if installed)  
    3. Simple TF-IDF fallback (always works, no dependencies)
    
    Returns:
        Embeddings instance for the configured provider
    """
    provider = config.LLM_PROVIDER.lower()
    
    # Try 1: HuggingFace through langchain (most optimized)
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        logger.info("✓ Using LangChain HuggingFace embeddings")
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
    except (ImportError, Exception) as e:
        logger.debug(f"LangChain HuggingFace not available: {type(e).__name__}")
    
    # Try 2: Direct sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
        from langchain_core.embeddings import Embeddings
        
        logger.info("✓ Using sentence-transformers embeddings")
        
        class SentenceTransformerEmbeddings(Embeddings):
            """Offline embeddings using sentence-transformers - completely free"""
            
            def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
                self.model = SentenceTransformer(model_name)
            
            def embed_documents(self, texts):
                """Embed search docs"""
                return self.model.encode(texts, convert_to_numpy=True).tolist()
            
            def embed_query(self, text):
                """Embed query text"""
                return self.model.encode(text, convert_to_numpy=True).tolist()
        
        return SentenceTransformerEmbeddings()
    except (ImportError, Exception) as e:
        logger.debug(f"sentence-transformers not available: {type(e).__name__}")
    
    # Try 3: Simpler approach - use sklearn's TfidfVectorizer wrapped for LangChain
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from langchain_core.embeddings import Embeddings
        
        logger.warning("  Using TF-IDF fallback embeddings (simpler, works offline)")
        
        class TfidfEmbeddings(Embeddings):
            """Simple TF-IDF embeddings - pure Python, no ML dependencies"""
            
            def __init__(self, max_features=300):
                self.vectorizer = TfidfVectorizer(max_features=max_features)
                self.fitted = False
                self.vocabulary = {}
            
            def embed_documents(self, texts):
                """Embed documents with TF-IDF"""
                if not self.fitted:
                    # First time: fit vectorizer
                    vectors = self.vectorizer.fit_transform(texts).toarray()
                    self.fitted = True
                    self.vocabulary = self.vectorizer.vocabulary_
                    return vectors.tolist()
                else:
                    # Subsequent calls: use fitted vectorizer
                    vectors = self.vectorizer.transform(texts).toarray()
                    return vectors.tolist()
            
            def embed_query(self, text):
                """Embed single query"""
                if not self.fitted:
                    # Need at least one doc to fit
                    self.vectorizer.fit([text])
                    self.fitted = True
                    self.vocabulary = self.vectorizer.vocabulary_
                
                vector = self.vectorizer.transform([text]).toarray()[0]
                return vector.tolist()
        
        logger.info("✓ Using TF-IDF embeddings (fallback)")
        return TfidfEmbeddings()
    except (ImportError, Exception) as e:
        logger.debug(f"TF-IDF not available: {e}")
    
    # Last resort: Check if OpenAI key is available
    if config.OPENAI_API_KEY:
        try:
            from langchain_openai import OpenAIEmbeddings
            logger.warning("  Using OpenAI embeddings (requires API key - will cost money)")
            return OpenAIEmbeddings(
                model="text-embedding-3-small",
                api_key=config.OPENAI_API_KEY
            )
        except Exception as e:
            logger.error(f"OpenAI embeddings failed: {e}")
    
    # If absolutely nothing works, raise error
    error_msg = (
        "No embeddings model available!\n"
        "Please install one of:\n"
        "  pip install langchain-huggingface sentence-transformers\n"
        "or:\n"
        "  pip install scikit-learn\n"
        "For OpenAI (paid): add OPENAI_API_KEY to config/.env"
    )
    logger.error(error_msg)
    raise RuntimeError(error_msg)


def build_vector_store(chunks):
    """
    Build and persist vector store from document chunks
    
    Args:
        chunks: List of document chunks
        
    Returns:
        Chroma vector store instance
        
    Raises:
        Exception: If vector store creation fails
    """
    if not chunks:
        logger.error("No chunks provided for vector store")
        raise ValueError("Cannot build vector store from empty chunks")

    logger.info(f"Building vector store with {len(chunks)} chunks")

    try:
        logger.debug(f"Initializing embeddings for provider: {config.LLM_PROVIDER}")
        embeddings = get_embeddings()

        logger.debug(f"Creating Chroma database at {config.CHROMA_DB_DIR}")
        vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(config.CHROMA_DB_DIR),
            collection_name="rag_documents"
        )

        logger.info("Vector database created successfully")
        logger.debug(f"Persisting database to {config.CHROMA_DB_DIR}")

        return vectordb

    except Exception as e:
        logger.error(f"Error building vector store: {str(e)}", exc_info=True)
        raise


def load_vector_store():
    """
    Load existing vector store from disk
    
    Returns:
        Chroma vector store instance
        
    Raises:
        Exception: If vector store cannot be loaded
    """
    logger.info(f"Loading vector store from {config.CHROMA_DB_DIR}")

    if not Path(config.CHROMA_DB_DIR).exists():
        logger.error(f"Vector store not found at {config.CHROMA_DB_DIR}")
        raise FileNotFoundError(
            f"Vector store not found. Please run document loading first. "
            f"Expected at: {config.CHROMA_DB_DIR}"
        )

    try:
        logger.debug(f"Initializing embeddings for provider: {config.LLM_PROVIDER}")
        embeddings = get_embeddings()

        logger.debug(f"Loading Chroma database from {config.CHROMA_DB_DIR}")
        vectordb = Chroma(
            persist_directory=str(config.CHROMA_DB_DIR),
            embedding_function=embeddings,
            collection_name="rag_documents"
        )

        # Test if vector store has documents
        try:
            count = vectordb._collection.count()
            logger.info(f"Vector store loaded successfully with {count} documents")
        except Exception as e:
            logger.warning(f"Could not verify document count: {e}")

        return vectordb

    except Exception as e:
        logger.error(f"Error loading vector store: {str(e)}", exc_info=True)
        raise


def delete_vector_store():
    """Delete existing vector store"""
    import shutil

    if Path(config.CHROMA_DB_DIR).exists():
        logger.warning(f"Deleting vector store at {config.CHROMA_DB_DIR}")
        shutil.rmtree(config.CHROMA_DB_DIR)
        logger.info("Vector store deleted successfully")
    else:
        logger.info("Vector store does not exist")
