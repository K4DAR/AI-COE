#!/usr/bin/env python3
"""
Complete system testing script
Tests all components to ensure everything works
"""
import sys
import time
import requests
import logging
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_section(title):
    """Print a section header"""
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}{title}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")

def test_pass(message):
    """Print pass message"""
    print(f"{GREEN}✓ PASS{RESET}: {message}")

def test_fail(message):
    """Print fail message"""
    print(f"{RED}✗ FAIL{RESET}: {message}")

def test_info(message):
    """Print info message"""
    print(f"{YELLOW}ℹ INFO{RESET}: {message}")

# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

def test_environment():
    """Test environment setup"""
    print_section("1. ENVIRONMENT TESTS")
    
    try:
        from config import config
        test_pass("config.py imports successfully")
        
        # Check required attributes
        assert hasattr(config, 'OPENAI_API_KEY'), "Missing OPENAI_API_KEY"
        test_pass(f"OPENAI_API_KEY configured: {config.OPENAI_API_KEY[:10]}...")
        
        assert hasattr(config, 'OPENAI_MODEL'), "Missing OPENAI_MODEL"
        test_pass(f"OPENAI_MODEL: {config.OPENAI_MODEL}")
        
        assert hasattr(config, 'PDF_CHUNK_SIZE'), "Missing PDF_CHUNK_SIZE"
        test_pass(f"PDF_CHUNK_SIZE: {config.PDF_CHUNK_SIZE}")
        
        return True
    except Exception as e:
        test_fail(f"Environment test failed: {e}")
        return False

# ============================================================================
# IMPORT TESTS
# ============================================================================

def test_imports():
    """Test all imports work"""
    print_section("2. IMPORT TESTS")
    
    imports = {
        'config': 'from config import config',
        'validators': 'from validators import InputValidator, OutputValidator',
        'demo': 'from demo import RAGBotDemo',
        'rag.loader': 'from rag.loader import load_documents',
        'rag.vector_store': 'from rag.vector_store import build_vector_store',
        'rag.rag_chain': 'from rag.rag_chain import build_rag_chain',
    }
    
    results = {}
    for name, import_stmt in imports.items():
        try:
            exec(import_stmt)
            test_pass(f"{name} imports successfully")
            results[name] = True
        except Exception as e:
            test_fail(f"{name} import failed: {e}")
            results[name] = False
    
    return all(results.values())

# ============================================================================
# VALIDATION TESTS
# ============================================================================

def test_validators():
    """Test input/output validators"""
    print_section("3. VALIDATION TESTS")
    
    from validators import InputValidator, OutputValidator
    
    test_cases = [
        ("What is AI?", True, "Valid question"),
        ("a", False, "Too short"),
        ("x" * 600, False, "Too long"),
        ("", False, "Empty question"),
    ]
    
    passed = 0
    for question, should_pass, description in test_cases:
        is_valid, msg = InputValidator.validate_question(question)
        if is_valid == should_pass:
            test_pass(f"'{description}': {msg}")
            passed += 1
        else:
            test_fail(f"'{description}': Expected {should_pass}, got {is_valid}")
    
    return passed == len(test_cases)

# ============================================================================
# FILE STRUCTURE TESTS
# ============================================================================

def test_file_structure():
    """Test required files and directories exist"""
    print_section("4. FILE STRUCTURE TESTS")
    
    required_files = [
        'config.py',
        'validators.py',
        'demo.py',
        'app.py',
        'api.py',
        'requirements.txt',
        '.env',
        'rag/loader.py',
        'rag/vector_store.py',
        'rag/rag_chain.py',
    ]
    
    required_dirs = [
        'data/documents',
        'rag',
        'evaluation',
    ]
    
    passed = 0
    
    for file in required_files:
        if Path(file).exists():
            test_pass(f"File exists: {file}")
            passed += 1
        else:
            test_fail(f"File missing: {file}")
    
    for dir in required_dirs:
        if Path(dir).exists():
            test_pass(f"Directory exists: {dir}")
            passed += 1
        else:
            test_fail(f"Directory missing: {dir}")
    
    total = len(required_files) + len(required_dirs)
    return passed == total

# ============================================================================
# API TESTS
# ============================================================================

def test_api():
    """Test API endpoints"""
    print_section("5. API TESTS")
    
    BASE_URL = 'http://localhost:8000'
    
    try:
        # Health check
        response = requests.get(f'{BASE_URL}/health', timeout=5)
        if response.status_code == 200:
            test_pass("API health check")
        else:
            test_fail("API health check failed")
            return False
        
        # Init bot
        response = requests.post(f'{BASE_URL}/api/init', timeout=10)
        if response.status_code == 200:
            test_pass("Bot initialization")
        else:
            test_fail(f"Bot initialization failed: {response.text}")
            return False
        
        # Get status
        response = requests.get(f'{BASE_URL}/api/status', timeout=5)
        if response.status_code == 200:
            test_pass("Get status endpoint")
        else:
            test_fail("Get status endpoint failed")
            return False
        
        # Ask question
        response = requests.post(
            f'{BASE_URL}/api/question',
            json={'question': 'What is AI?'},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if 'answer' in data and 'response_time' in data:
                test_pass(f"Ask question (response time: {data['response_time']:.2f}s)")
            else:
                test_fail("Invalid question response format")
                return False
        else:
            test_fail(f"Ask question failed: {response.text}")
            return False
        
        # Get config
        response = requests.get(f'{BASE_URL}/api/config', timeout=5)
        if response.status_code == 200:
            test_pass("Get config endpoint")
        else:
            test_fail("Get config endpoint failed")
            return False
        
        return True
    
    except requests.exceptions.ConnectionError:
        test_fail("Cannot connect to API. Make sure: python api.py is running")
        return False
    except Exception as e:
        test_fail(f"API test error: {e}")
        return False

# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

def test_performance():
    """Test performance metrics"""
    print_section("6. PERFORMANCE TESTS")
    
    BASE_URL = 'http://localhost:8000'
    
    try:
        # Test response time
        start = time.time()
        response = requests.post(
            f'{BASE_URL}/api/question',
            json={'question': 'What is technology?'},
            timeout=10
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            test_pass(f"Question answered in {elapsed:.2f}s")
            if elapsed < 5:
                test_info("Excellent response time!")
            elif elapsed < 10:
                test_info("Good response time")
            else:
                test_info("Response is slower than expected")
        else:
            test_fail("Performance test question failed")
            return False
        
        return True
    
    except Exception as e:
        test_fail(f"Performance test error: {e}")
        return False

# ============================================================================
# DOCUMENTATION TESTS
# ============================================================================

def test_documentation():
    """Test documentation files exist"""
    print_section("7. DOCUMENTATION TESTS")
    
    doc_files = [
        'README.md',
        'SIMPLE_GUIDE.md',
        'API_GUIDE.md',
        'DEPLOYMENT.md',
        'TESTING_GUIDE.md',
        'QUICK_START_WEB_UI.md',
    ]
    
    passed = 0
    for doc in doc_files:
        if Path(doc).exists():
            size = Path(doc).stat().st_size
            test_pass(f"{doc} ({size} bytes)")
            passed += 1
        else:
            test_fail(f"{doc} missing")
    
    return passed == len(doc_files)

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests"""
    print(f"\n{BOLD}{GREEN}RAG BOT - COMPLETE SYSTEM TEST{RESET}\n")
    
    tests = [
        ("Environment", test_environment),
        ("Imports", test_imports),
        ("Validators", test_validators),
        ("File Structure", test_file_structure),
        ("Documentation", test_documentation),
        ("API", test_api),
        ("Performance", test_performance),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            test_fail(f"Test error: {e}")
            results[test_name] = False
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{status}: {test_name}")
    
    print(f"\n{BOLD}Results: {passed}/{total} tests passed{RESET}\n")
    
    if passed == total:
        print(f"{GREEN}{BOLD}✓ ALL TESTS PASSED!{RESET}")
        print(f"{GREEN}Your RAG Bot is working perfectly!{RESET}\n")
        return 0
    else:
        print(f"{RED}{BOLD}✗ SOME TESTS FAILED{RESET}")
        print(f"{RED}Please review the errors above{RESET}\n")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
