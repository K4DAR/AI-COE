"""
RAG Chain module for RAG Bot
"""
import logging
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from config import config

logger = logging.getLogger(__name__)


def get_llm():
    """
    Get LLM based on configured provider
    
    Returns:
        LLM instance for the configured provider
    """
    provider = config.LLM_PROVIDER.lower()
    
    if provider == "openai":
        logger.debug("Using OpenAI LLM")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=config.OPENAI_MODEL,
            temperature=config.OPENAI_TEMPERATURE,
            api_key=config.OPENAI_API_KEY,
            max_retries=3
        )
    
    elif provider == "groq":
        logger.debug("Using Groq LLM")
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=config.GROQ_MODEL,
            temperature=config.OPENAI_TEMPERATURE,
            api_key=config.GROQ_API_KEY,
            max_retries=3
        )
    
    elif provider == "ollama":
        logger.debug("Using Ollama LLM")
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(
            model=config.OLLAMA_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=config.OPENAI_TEMPERATURE,
            top_p=0.9
        )
    
    else:
        logger.error(f"Unknown provider: {provider}")
        raise ValueError(f"Unknown LLM provider: {provider}")


class RAGChain:
    """Simple RAG Chain implementation"""

    def __init__(self, vectordb, llm):
        self.vectordb = vectordb
        self.llm = llm
        self.retriever = vectordb.as_retriever(
            search_kwargs={"k": config.RETRIEVER_K}
        )

    def invoke(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the RAG chain"""
        query = input_dict.get("query", "")

        # Retrieve documents
        docs = self.retriever.invoke(query)

        # Create context from retrieved documents
        context = "\n\n".join([doc.page_content for doc in docs])

        # Create prompt
        prompt_template = ChatPromptTemplate.from_template(
            """You are a helpful assistant. Use the following context to answer the question.

Context:
{context}

Question: {question}

Answer:"""
        )

        # Get answer from LLM
        chain = (
            RunnableParallel(
                context=lambda x: context,
                question=RunnablePassthrough()
            )
            | prompt_template
            | self.llm
        )

        response = chain.invoke(query)

        return {
            "result": response.content if hasattr(response, 'content') else str(response),
            "source_documents": docs
        }


def build_rag_chain(vectordb):
    """
    Build RAG chain from vector store
    
    Args:
        vectordb: Chroma vector store instance
        
    Returns:
        RAG chain instance
        
    Raises:
        Exception: If chain creation fails
    """
    if vectordb is None:
        logger.error("Vector store is None")
        raise ValueError("Vector store cannot be None")

    logger.info("Building RAG chain")

    try:
        logger.debug(f"Creating retriever with k={config.RETRIEVER_K}")

        logger.debug(f"Initializing LLM for provider: {config.LLM_PROVIDER}")
        llm = get_llm()

        logger.debug("Creating RAG chain")
        qa_chain = RAGChain(vectordb, llm)

        logger.info("RAG chain built successfully")

        return qa_chain

    except Exception as e:
        logger.error(f"Error building RAG chain: {str(e)}", exc_info=True)
        raise


def invoke_chain(qa_chain, question: str, timeout: int = 30):
    """
    Invoke RAG chain with question
    
    Args:
        qa_chain: RAG chain instance
        question: User question
        timeout: Timeout in seconds
        
    Returns:
        Dictionary with 'result' and 'source_documents'
        
    Raises:
        Exception: If chain invocation fails
    """
    logger.debug(f"Invoking chain with question: {question[:100]}...")

    try:
        response = qa_chain.invoke({"query": question})

        if not response:
            logger.error("Chain returned empty response")
            raise ValueError("Chain returned empty response")

        logger.debug(f"Chain response received with {len(response.get('source_documents', []))} sources")

        return response

    except Exception as e:
        logger.error(f"Error invoking chain: {str(e)}", exc_info=True)
        raise

