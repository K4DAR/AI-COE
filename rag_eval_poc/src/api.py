"""
Simple FastAPI server for RAG Bot
Provides REST API endpoints for web UI integration
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import logging
import time

from config import config
from demo import RAGBotDemo
from validators import InputValidator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="RAG Bot API",
    description="REST API for RAG Bot",
    version="1.0.0"
)

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global bot instance
bot: Optional[RAGBotDemo] = None


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class QuestionRequest(BaseModel):
    """Question request model"""
    question: str


class QuestionResponse(BaseModel):
    """Question response model"""
    answer: str
    sources: List[dict]
    response_time: float
    success: bool
    error: Optional[str] = None


class BotStatusResponse(BaseModel):
    """Bot status response"""
    initialized: bool
    ready: bool
    status: str


class ConfigResponse(BaseModel):
    """Configuration response"""
    model: str
    temperature: float
    chunk_size: int
    retriever_k: int
    max_question_length: int


# ============================================================================
# INITIALIZATION ENDPOINTS
# ============================================================================

@app.post("/api/init")
async def initialize_bot(pdf_path: Optional[str] = None) -> BotStatusResponse:
    """Initialize the RAG bot"""
    global bot
    try:
        logger.info("Initializing bot...")
        bot = RAGBotDemo(pdf_path=pdf_path or "data/document.pdf")
        
        if bot.setup():
            logger.info("Bot initialized successfully")
            return BotStatusResponse(
                initialized=True,
                ready=True,
                status=" Bot ready"
            )
        else:
            logger.error("Bot setup failed")
            return BotStatusResponse(
                initialized=False,
                ready=False,
                status=" Bot setup failed"
            )
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def get_status() -> BotStatusResponse:
    """Get bot status"""
    if bot is None:
        return BotStatusResponse(
            initialized=False,
            ready=False,
            status=" Bot not initialized"
        )
    
    return BotStatusResponse(
        initialized=True,
        ready=True,
        status=" Bot ready"
    )


# ============================================================================
# QUESTION & ANSWER ENDPOINTS
# ============================================================================

@app.post("/api/question")
async def ask_question(request: QuestionRequest) -> QuestionResponse:
    """Ask a question to the RAG bot"""
    if bot is None:
        raise HTTPException(status_code=400, detail="Bot not initialized. Call /api/init first")
    
    question = request.question.strip()
    
    # Validate question
    is_valid, error_msg = InputValidator.validate_question(question)
    if not is_valid:
        logger.warning(f"Invalid question: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    
    try:
        # Process question
        start_time = time.time()
        response = bot.process_question(question)
        elapsed_time = time.time() - start_time
        
        if response:
            answer = response.get("result", "")
            sources = response.get("source_documents", [])
            
            # Convert sources to simple format
            source_list = [
                {
                    "content": doc.page_content[:200],
                    "source": doc.metadata.get("source", "Unknown")
                }
                for doc in sources
            ]
            
            logger.info(f"Question answered in {elapsed_time:.2f}s")
            return QuestionResponse(
                answer=answer,
                sources=source_list,
                response_time=elapsed_time,
                success=True
            )
        else:
            logger.error("Failed to generate answer")
            raise HTTPException(status_code=500, detail="Failed to generate answer")
    
    except Exception as e:
        logger.error(f"Question processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================

@app.get("/api/config")
async def get_config() -> ConfigResponse:
    """Get current configuration"""
    return ConfigResponse(
        model=config.OPENAI_MODEL,
        temperature=config.OPENAI_TEMPERATURE,
        chunk_size=config.PDF_CHUNK_SIZE,
        retriever_k=config.RETRIEVER_K,
        max_question_length=config.MAX_QUESTION_LENGTH
    )


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "bot_initialized": bot is not None
    }


# ============================================================================
# ROOT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "RAG Bot API",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "init": "POST /api/init",
            "status": "GET /api/status",
            "question": "POST /api/question",
            "config": "GET /api/config"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
