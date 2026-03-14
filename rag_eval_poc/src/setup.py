"""
Setup script for RAG Bot
"""
import subprocess
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup Python environment and install dependencies"""
    
    logger.info("=" * 70)
    logger.info("RAG BOT SETUP")
    logger.info("=" * 70)
    
    # Check Python version
    logger.info(f"\n1. Checking Python version...")
    version = sys.version_info
    logger.info(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        logger.error(f"   Python 3.9+ required!")
        return False
    
    logger.info("   ✓ Python version OK")
    
    # Install requirements
    logger.info(f"\n2. Installing dependencies from requirements.txt...")
    
    try:
        requirements_file = Path("requirements.txt")
        if not requirements_file.exists():
            logger.error("   requirements.txt not found!")
            return False
        
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"   Error installing requirements: {result.stderr}")
            return False
        
        logger.info("   ✓ Dependencies installed successfully")
        
    except Exception as e:
        logger.error(f"   Error: {e}")
        return False
    
    # Create data directory if needed
    logger.info(f"\n3. Creating data directories...")
    
    try:
        Path("data/documents").mkdir(parents=True, exist_ok=True)
        Path("evaluation").mkdir(parents=True, exist_ok=True)
        Path("notebooks").mkdir(parents=True, exist_ok=True)
        logger.info("   ✓ Directories created")
    except Exception as e:
        logger.error(f"   Error creating directories: {e}")
        return False
    
    # Check .env file
    logger.info(f"\n4. Checking .env file...")
    
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            content = f.read()
            has_key = "OPENAI_API_KEY" in content
        
        if has_key:
            logger.info("   ✓ .env file found with OPENAI_API_KEY")
        else:
            logger.warning("   ⚠ .env file exists but OPENAI_API_KEY might be missing")
    else:
        logger.warning("   ⚠ .env file not found. Please create it with your API keys")
    
    logger.info("\n" + "=" * 70)
    logger.info("✓ SETUP COMPLETED!")
    logger.info("=" * 70)
    
    logger.info("\nNext steps:")
    logger.info("1. Ensure your API keys are in .env file:")
    logger.info("   OPENAI_API_KEY=your-key-here")
    logger.info("")
    logger.info("2. Run validation:")
    logger.info("   python validate_system.py")
    logger.info("")
    logger.info("3. Run the bot:")
    logger.info("   python demo.py")
    
    return True

if __name__ == "__main__":
    success = setup_environment()
    sys.exit(0 if success else 1)
