#!/usr/bin/env python
"""
Quick test to verify Groq integration
"""
import sys
sys.path.insert(0, 'src')

from config import config

print("=" * 70)
print("🔍 Testing Groq Integration")
print("=" * 70)

# Test configuration
print(f"\n✓ LLM Provider: {config.LLM_PROVIDER}")
print(f"✓ Groq API Key: {'SET' if config.GROQ_API_KEY else 'NOT SET'}")
print(f"✓ Groq Model: {config.GROQ_MODEL}")

# Test LLM initialization
try:
    from rag.rag_chain import get_llm
    llm = get_llm()
    print(f"\n LLM initialized successfully!")
    print(f"   Type: {type(llm).__name__}")
    print(f"   Model: {llm.model}")
except Exception as e:
    print(f"\n LLM initialization failed:")
    print(f"   {e}")
    sys.exit(1)

# Test embeddings
try:
    from rag.vector_store import get_embeddings
    embeddings = get_embeddings()
    print(f"\n Embeddings initialized successfully!")
    print(f"   Type: {type(embeddings).__name__}")
except Exception as e:
    print(f"\n Embeddings initialization failed:")
    print(f"   {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✨ Groq integration is ready!")
print("=" * 70)
