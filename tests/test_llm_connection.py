"""
Task 4: Verify LLM connection test script.

Run with:  python -m tests.test_llm_connection
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


def test_groq_connection():
    """Verify we can reach the Groq API with the configured model."""
    from langchain_groq import ChatGroq

    print(f"[1/3] Initialising Groq LLM: model={settings.llm_model_name}")
    llm = ChatGroq(
        model=settings.llm_model_name,
        api_key=settings.groq_api_key,
        temperature=0,
        max_tokens=64,
    )

    print("[2/3] Sending test prompt …")
    response = llm.invoke("Say 'connection successful' and nothing else.")
    content = response.content.strip()
    print(f"[3/3] Response: {content}")
    assert "successful" in content.lower(), f"Unexpected response: {content}"
    print("✅  Groq LLM connection verified!\n")


def test_embedding_model():
    """Verify the embedding model loads and produces vectors."""
    from langchain_huggingface import HuggingFaceEmbeddings

    print(f"[1/2] Loading embedding model: {settings.embedding_model_name}")
    embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model_name)

    print("[2/2] Generating test embedding …")
    vector = embeddings.embed_query("Hello world")
    dim = len(vector)
    print(f"✅  Embedding model works! Vector dimension = {dim}\n")
    assert dim > 0, "Empty embedding vector"


def test_qdrant_connection():
    """Verify we can reach the Qdrant instance."""
    from qdrant_client import QdrantClient

    print(f"[1/2] Connecting to Qdrant at {settings.qdrant_url}")
    client = QdrantClient(url=settings.qdrant_url)

    print("[2/2] Fetching collections …")
    collections = client.get_collections()
    print(f"✅  Qdrant connected! Existing collections: {[c.name for c in collections.collections]}\n")


if __name__ == "__main__":
    print("=" * 50)
    print(" EnterpriseRAG — Connection Verification")
    print("=" * 50 + "\n")

    passed = 0
    failed = 0

    # Qdrant (no API key needed)
    try:
        test_qdrant_connection()
        passed += 1
    except Exception as e:
        print(f"❌  Qdrant connection failed: {e}\n")
        failed += 1

    # Embedding model (local, no API key needed)
    try:
        test_embedding_model()
        passed += 1
    except Exception as e:
        print(f"❌  Embedding model failed: {e}\n")
        failed += 1

    # Groq LLM (requires API key)
    if settings.groq_api_key and settings.groq_api_key != "your_groq_api_key_here":
        try:
            test_groq_connection()
            passed += 1
        except Exception as e:
            print(f"❌  Groq LLM connection failed: {e}\n")
            failed += 1
    else:
        print("⚠️  Skipping Groq LLM test — GROQ_API_KEY not configured in .env\n")

    print("=" * 50)
    print(f" Results: {passed} passed, {failed} failed")
    print("=" * 50)
    sys.exit(1 if failed > 0 else 0)
