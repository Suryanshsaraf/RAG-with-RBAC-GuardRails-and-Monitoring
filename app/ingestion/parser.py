"""
Document parser module.

Handles parsing of:
  - Markdown (.md) files  →  raw text extraction
  - CSV (.csv) files      →  row-level text records (one LangChain Document per row)

Every document is tagged with metadata including:
  - source: file path
  - role: derived from parent folder name (e.g., data/hr/ → "hr")
  - file_type: "md" or "csv"
"""

import os
import csv
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader


def _extract_role_from_path(file_path: str) -> str:
    """
    Derive the RBAC role tag from the parent directory name.

    Example:  data/hr/hr_data.csv  →  "hr"
              data/finance/report.md  →  "finance"
    """
    return Path(file_path).parent.name.lower()


def parse_markdown(file_path: str) -> List[Document]:
    """
    Parse a Markdown file into a single LangChain Document.

    Parameters
    ----------
    file_path : str
        Absolute or relative path to the .md file.

    Returns
    -------
    list[Document]
        A list containing one Document with full file text and metadata.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    role = _extract_role_from_path(file_path)
    metadata = {
        "source": os.path.basename(file_path),
        "source_path": file_path,
        "role": role,
        "file_type": "md",
    }

    return [Document(page_content=content, metadata=metadata)]


def parse_pdf(file_path: str) -> List[Document]:
    """
    Parse a PDF file using LangChain's PyPDFLoader.
    """
    loader = PyPDFLoader(file_path)
    pages = loader.load()

    role = _extract_role_from_path(file_path)
    for page in pages:
        page.metadata.update({
            "source": os.path.basename(file_path),
            "source_path": file_path,
            "role": role,
            "file_type": "pdf",
        })

    return pages


def parse_csv(file_path: str) -> List[Document]:
    """
    Parse a CSV file into one LangChain Document per row.

    Each row is converted into a human-readable text block so the
    embedding model can meaningfully encode the tabular data.

    Parameters
    ----------
    file_path : str
        Absolute or relative path to the .csv file.

    Returns
    -------
    list[Document]
        One Document per CSV row, each with role and PII-flagging metadata.
    """
    documents: List[Document] = []
    role = _extract_role_from_path(file_path)

    # Columns that contain personally identifiable information
    pii_columns = {
        "full_name", "email", "date_of_birth", "salary",
        "leave_balance", "leaves_taken", "performance_rating",
    }

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []

        for row_idx, row in enumerate(reader):
            # Build a natural-language description of the row
            text_parts = []
            has_pii = False

            for col in headers:
                value = row.get(col, "").strip()
                if value:
                    text_parts.append(f"{col}: {value}")
                    if col.lower() in pii_columns:
                        has_pii = True

            text = "\n".join(text_parts)

            metadata = {
                "source": os.path.basename(file_path),
                "source_path": file_path,
                "role": role,
                "file_type": "csv",
                "row_index": row_idx,
                "contains_pii": has_pii,
            }

            documents.append(Document(page_content=text, metadata=metadata))

    return documents


def parse_document(file_path: str) -> List[Document]:
    """
    Route a file to the correct parser based on its extension.

    Parameters
    ----------
    file_path : str
        Path to the document.

    Returns
    -------
    list[Document]
        Parsed LangChain Documents.

    Raises
    ------
    ValueError
        If the file type is not supported.
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".md":
        return parse_markdown(file_path)
    elif ext == ".csv":
        return parse_csv(file_path)
    elif ext == ".pdf":
        return parse_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}  (file: {file_path})")


def load_all_documents(data_dir: str = "data") -> List[Document]:
    """
    Walk the data directory and parse every supported file.

    The directory structure is expected to be:
        data/
          hr/        → role = "hr"
          finance/   → role = "finance"
          engineering/ → role = "engineering"
          marketing/ → role = "marketing"
          general/   → role = "general"

    Parameters
    ----------
    data_dir : str
        Path to the root data directory.

    Returns
    -------
    list[Document]
        All parsed documents across every subdirectory.
    """
    all_docs: List[Document] = []
    supported_extensions = {".md", ".csv", ".pdf"}

    for root, _dirs, files in os.walk(data_dir):
        for fname in sorted(files):
            ext = Path(fname).suffix.lower()
            if ext in supported_extensions:
                full_path = os.path.join(root, fname)
                docs = parse_document(full_path)
                print(f"  Parsed {full_path}: {len(docs)} document(s)")
                all_docs.extend(docs)

    print(f"\nTotal documents loaded: {len(all_docs)}")
    return all_docs
