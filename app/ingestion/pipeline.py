"""
Full ingestion pipeline.

Orchestrates:  parse → chunk → embed → upsert

Run with:  python -m app.ingestion.pipeline
"""

import sys
import time

from app.ingestion.parser import load_all_documents
from app.ingestion.chunker import chunk_documents
from app.ingestion.vector_store import upsert_documents, get_collection_info


def run_ingestion(data_dir: str = "data") -> dict:
    """
    Execute the full document ingestion pipeline.

    Parameters
    ----------
    data_dir : str
        Root data directory.

    Returns
    -------
    dict
        Summary of the ingestion run.
    """
    print("=" * 55)
    print(" EnterpriseRAG — Document Ingestion Pipeline")
    print("=" * 55)

    start = time.time()

    # Step 1: Parse
    print("\n📄  Step 1/3: Parsing documents …")
    documents = load_all_documents(data_dir)

    # Step 2: Chunk
    print("\n✂️   Step 2/3: Chunking documents …")
    chunks = chunk_documents(documents)

    # Step 3: Embed + Upsert
    print("\n📤  Step 3/3: Embedding & upserting into Qdrant …")
    total = upsert_documents(chunks)

    elapsed = time.time() - start

    # Summary
    info = get_collection_info()
    print("\n" + "=" * 55)
    print(f" ✅  Ingestion complete in {elapsed:.1f}s")
    print(f"    Documents parsed : {len(documents)}")
    print(f"    Chunks created   : {len(chunks)}")
    print(f"    Points in Qdrant : {info['points_count']}")
    print(f"    Collection status: {info['status']}")
    print("=" * 55)

    return {
        "documents_parsed": len(documents),
        "chunks_created": len(chunks),
        "points_upserted": total,
        "elapsed_seconds": round(elapsed, 2),
    }


if __name__ == "__main__":
    data_directory = sys.argv[1] if len(sys.argv) > 1 else "data"
    run_ingestion(data_directory)
