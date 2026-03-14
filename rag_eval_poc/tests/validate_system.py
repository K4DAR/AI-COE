"""
Quick system validation script
"""
import sys
import logging
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def validate_environment():
    """Validate project structure and environment"""
    
    logger.info("=" * 70)
    logger.info("RAG BOT VALIDATION")
    logger.info("=" * 70)
    
    project_root = Path(__file__).parent.parent
    checks = {
        "config.py": project_root / "src" / "config.py",
        "validators.py": project_root / "src" / "validators.py",
        "demo.py": project_root / "src" / "demo.py",
        "requirements.txt": project_root / "requirements.txt",
        ".env": project_root / "config" / ".env",
        "Sample PDF": project_root / "src" / "data" / "documents" / "sample_doc.pdf",
        "rag/loader.py": project_root / "src" / "rag" / "loader.py",
        "rag/vector_store.py": project_root / "src" / "rag" / "vector_store.py",
        "rag/rag_chain.py": project_root / "src" / "rag" / "rag_chain.py",
        "evaluation/run_eval.py": project_root / "tests" / "evaluation" / "run_eval.py",
        "evaluation/test_cases.yaml": project_root / "tests" / "evaluation" / "test_cases.yaml",
    }
    
    logger.info("\n1. Checking file structure:")
    all_exist = True
    for name, path in checks.items():
        exists = path.exists()
        status = "✓" if exists else "✗"
        logger.info(f"   {status} {name:<35} {'OK' if exists else 'MISSING'}")
        if not exists:
            all_exist = False
    
    if not all_exist:
        logger.error("\n   Some files are missing!")
        return False
    
    # Check imports
    logger.info("\n2. Checking imports:")
    
    try:
        logger.info("   Importing config...")
        import config
        logger.info("   ✓ config.py imported successfully")
    except Exception as e:
        logger.error(f"   ✗ Error importing config: {e}")
        return False
    
    try:
        logger.info("   Importing validators...")
        import validators
        logger.info("   ✓ validators.py imported successfully")
    except Exception as e:
        logger.error(f"   ✗ Error importing validators: {e}")
        return False
    
    try:
        logger.info("   Importing RAG modules...")
        from rag import loader, vector_store, rag_chain
        logger.info("   ✓ RAG modules imported successfully")
    except Exception as e:
        logger.error(f"   ✗ Error importing RAG modules: {e}")
        return False
    
    # Check environment
    logger.info("\n3. Checking environment configuration:")
    
    try:
        config.config.validate()
        logger.info("   ✓ Configuration validated")
    except Exception as e:
        logger.error(f"   ✗ Configuration error: {e}")
        return False
    
    # Check PDF
    logger.info("\n4. Checking sample document:")
    pdf_path = Path("data/documents/sample_doc.pdf")
    if pdf_path.exists():
        size_mb = pdf_path.stat().st_size / (1024 * 1024)
        logger.info(f"   ✓ Sample PDF found ({size_mb:.2f} MB)")
    else:
        logger.error("   ✗ Sample PDF not found")
        return False
    
    logger.info("\n" + "=" * 70)
    logger.info("✓ ALL VALIDATION CHECKS PASSED!")
    logger.info("=" * 70)
    
    logger.info("\nYou can now run:")
    logger.info("  python demo.py              # Interactive mode")
    logger.info("  python demo.py --question \"Your question here\"")
    logger.info("  python evaluation/run_eval.py  # Run evaluation")
    
    return True

if __name__ == "__main__":
    success = validate_environment()
    sys.exit(0 if success else 1)
