"""
Document loading module for RAG Bot
"""
import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import config
from validators import InputValidator, DocumentValidator, ValidationError

logger = logging.getLogger(__name__)


def load_documents(file_path: str):
    """
    Load and process documents from PDF file
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        List of document chunks
        
    Raises:
        ValidationError: If file path or content is invalid
        Exception: If document loading fails
    """
    logger.info(f"Starting document load from: {file_path}")

    # Validate file path
    is_valid, error_msg = InputValidator.validate_file_path(file_path)
    if not is_valid:
        logger.error(f"File validation failed: {error_msg}")
        raise ValidationError(f"Invalid file path: {error_msg}")

    try:
        # Load PDF
        logger.debug(f"Loading PDF from {file_path}")
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        if not docs:
            logger.error("No documents loaded from PDF")
            raise ValidationError("PDF file appears to be empty or invalid")

        logger.info(f"Successfully loaded {len(docs)} pages from PDF")

        # Split into chunks
        logger.debug(f"Splitting documents with chunk_size={config.PDF_CHUNK_SIZE}, "
                    f"overlap={config.PDF_CHUNK_OVERLAP}")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.PDF_CHUNK_SIZE,
            chunk_overlap=config.PDF_CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )

        chunks = splitter.split_documents(docs)

        if not chunks:
            logger.error("No chunks created from documents")
            raise ValidationError("Failed to create document chunks")

        # Validate chunks
        is_valid, error_msg = DocumentValidator.validate_chunks(chunks)
        if not is_valid:
            logger.error(f"Chunk validation failed: {error_msg}")
            raise ValidationError(f"Document chunk validation failed: {error_msg}")

        logger.info(f"Successfully created {len(chunks)} document chunks")
        logger.debug(f"Average chunk size: {sum(len(c.page_content) for c in chunks) // len(chunks)} characters")

        return chunks

    except Exception as e:
        logger.error(f"Error loading documents: {str(e)}", exc_info=True)
        raise