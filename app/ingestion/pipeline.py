"""
Full ingestion pipeline.

Orchestrates:  parse → chunk → embed → upsert
Supports incremental ingestion via document versioning.

Run with:  python -m app.ingestion.pipeline [--full]
"""

import sys
import time

from app.ingestion.parser import load_all_documents, parse_document
from app.ingestion.chunker import chunk_documents
from app.ingestion.vector_store import upsert_documents, get_collection_info
from app.ingestion.versioning import get_changed_files, register_ingestion


async def run_ingestion(data_dir: str = "data", full: bool = False) -> dict:
    """
    Execute the full document ingestion pipeline.

    Parameters
    ----------
    data_dir : str
        Root data directory.
    full : bool
        If True, re-ingest all documents regardless of version state.
        If False, only ingest new or modified files.

    Returns
    -------
    dict
        Summary of the ingestion run.
    """
    print("=" * 55)
    print(" EnterpriseRAG — Document Ingestion Pipeline")
    print("=" * 55)

    start = time.time()

    if full:
        # Full ingestion — parse everything
        print("\n📄  Step 1/4: Parsing ALL documents …")
        documents = await load_all_documents(data_dir)
        ingested_files = [d.metadata["source_path"] for d in documents]
        # Deduplicate (CSV rows share same source_path)
        ingested_files = list(set(ingested_files))
    else:
        # Incremental ingestion — only changed files
        print("\n🔍  Step 1/4: Checking for new or modified documents …")
        changed = get_changed_files(data_dir)
        if not changed:
            print("   No changes detected — nothing to ingest.")
            print("   Use --full to force a complete re-ingestion.")
            return {"documents_parsed": 0, "chunks_created": 0, "points_upserted": 0}

        print(f"   Found {len(changed)} changed file(s):")
        for f in changed:
            print(f"     • {f}")

        documents = []
        for fp in changed:
            docs = await parse_document(fp)
            documents.extend(docs)
        ingested_files = changed

    # Step 2: Chunk
    print(f"\n✂️   Step 2/4: Chunking {len(documents)} document(s) …")
    chunks = chunk_documents(documents)

    # Step 3: Embed + Upsert
    print("\n📤  Step 3/4: Embedding & upserting into Qdrant …")
    total = upsert_documents(chunks)

    # Step 4: Update version registry
    print("\n📋  Step 4/4: Updating version registry …")
    register_ingestion(ingested_files)

    elapsed = time.time() - start

    # Summary
    info = get_collection_info()
    print("\n" + "=" * 55)
    print(f" ✅  Ingestion complete in {elapsed:.1f}s")
    print(f"    Files processed  : {len(ingested_files)}")
    print(f"    Chunks created   : {len(chunks)}")
    print(f"    Points in Qdrant : {info['points_count']}")
    print(f"    Collection status: {info['status']}")
    print("=" * 55)

    return {
        "files_processed": len(ingested_files),
        "documents_parsed": len(documents),
        "chunks_created": len(chunks),
        "points_upserted": total,
        "elapsed_seconds": round(elapsed, 2),
    }


import asyncio

if __name__ == "__main__":
    force_full = "--full" in sys.argv
    data_directory = "data"
    for arg in sys.argv[1:]:
        if arg != "--full":
            data_directory = arg
    asyncio.run(run_ingestion(data_directory, full=force_full))
