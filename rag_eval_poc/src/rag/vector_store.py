"""
Vector store management module for RAG Bot
"""
import logging
import numpy as np
from pathlib import Path
from langchain_community.vectorstores import Chroma
from config import config

logger = logging.getLogger(__name__)


class VectorStore:
    """Wrapper class for vector store operations"""
    pass


def get_embeddings():
    """
    Get embeddings using simple TF-IDF (no torch needed)
    Lightweight and works offline
    
    Returns:
        Embeddings instance
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from langchain_core.embeddings import Embeddings
    
    class SimpleEmbeddings(Embeddings):
        """Simple TF-IDF embeddings using sklearn"""
        
        def __init__(self):
            self.vectorizer = TfidfVectorizer(max_features=384, min_df=1)
            self.fitted = False
        
        def embed_documents(self, texts):
            """Embed documents"""
            if not self.fitted:
                vectors = self.vectorizer.fit_transform(texts).toarray()
                self.fitted = True
            else:
                vectors = self.vectorizer.transform(texts).toarray()
            return vectors.tolist()
        
        def embed_query(self, text):
            """Embed query"""
            if not self.fitted:
                self.vectorizer.fit([text])
                self.fitted = True
            vector = self.vectorizer.transform([text]).toarray()[0]
            return vector.tolist()
    
    logger.info("Using lightweight TF-IDF embeddings (no torch needed)")
    return SimpleEmbeddings()


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
