"""
Text chunking module.

Splits parsed documents into retrieval-ready chunks:
  - Markdown files  →  RecursiveCharacterTextSplitter (512 tokens, 50 overlap)
  - CSV rows        →  Already atomic per-row; passed through as-is

All metadata (role, source, PII flags) is preserved on every chunk.
"""

from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ── Splitter configuration ─────────────────────────────────────────────
# Using character count as a proxy for tokens (≈4 chars/token for English).
# 512 tokens ≈ 2048 chars, 50 tokens ≈ 200 chars.
CHUNK_SIZE = 2048
CHUNK_OVERLAP = 200

_md_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", ". ", " ", ""],
    keep_separator=True,
)


def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Split a list of parsed Documents into retrieval-ready chunks.

    - Markdown documents are split using a recursive text splitter
      with heading-aware separators.
    - CSV row documents are already atomic and are passed through
      without further splitting.

    Parameters
    ----------
    documents : list[Document]
        Output from the parser module.

    Returns
    -------
    list[Document]
        Chunked documents, each retaining all original metadata plus
        a ``chunk_index`` field.
    """
    md_docs = [d for d in documents if d.metadata.get("file_type") == "md"]
    csv_docs = [d for d in documents if d.metadata.get("file_type") == "csv"]

    # ── Split Markdown documents ────────────────────────────────────
    md_chunks: List[Document] = []
    for doc in md_docs:
        splits = _md_splitter.split_documents([doc])
        for idx, chunk in enumerate(splits):
            chunk.metadata["chunk_index"] = idx
            chunk.metadata["total_chunks"] = len(splits)
            md_chunks.append(chunk)

    # ── CSV rows are already atomic ─────────────────────────────────
    for idx, doc in enumerate(csv_docs):
        doc.metadata["chunk_index"] = 0
        doc.metadata["total_chunks"] = 1

    all_chunks = md_chunks + csv_docs

    print(f"Chunking complete: {len(md_docs)} MD docs → {len(md_chunks)} chunks, "
          f"{len(csv_docs)} CSV rows kept as-is.  Total: {len(all_chunks)}")

    return all_chunks
