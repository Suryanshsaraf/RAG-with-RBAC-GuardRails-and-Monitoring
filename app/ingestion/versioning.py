"""
Document versioning module.

Tracks upload timestamps, file hashes, and version numbers so the system
can detect changes and avoid re-ingesting unchanged documents.

Stores version metadata in a local JSON file (``doc_versions.json``).
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


VERSION_FILE = "doc_versions.json"


def _file_hash(file_path: str) -> str:
    """Compute SHA-256 hash of a file's contents."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(8192), b""):
            h.update(block)
    return h.hexdigest()


def load_version_registry(version_file: str = VERSION_FILE) -> Dict:
    """Load the version registry from disk."""
    if os.path.exists(version_file):
        with open(version_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_version_registry(registry: Dict, version_file: str = VERSION_FILE) -> None:
    """Persist the version registry to disk."""
    with open(version_file, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, default=str)


def get_changed_files(data_dir: str = "data", version_file: str = VERSION_FILE) -> List[str]:
    """
    Scan the data directory and return only files that are new or modified
    since the last ingestion.

    Parameters
    ----------
    data_dir : str
        Root data directory to scan.
    version_file : str
        Path to the version registry JSON.

    Returns
    -------
    list[str]
        Paths to files that need (re-)ingestion.
    """
    registry = load_version_registry(version_file)
    supported = {".md", ".csv"}
    changed: List[str] = []

    for root, _dirs, files in os.walk(data_dir):
        for fname in sorted(files):
            ext = Path(fname).suffix.lower()
            if ext not in supported:
                continue

            full_path = os.path.join(root, fname)
            current_hash = _file_hash(full_path)

            prev = registry.get(full_path)
            if prev is None or prev.get("hash") != current_hash:
                changed.append(full_path)

    return changed


def register_ingestion(
    file_paths: List[str],
    version_file: str = VERSION_FILE,
) -> Dict:
    """
    Record that the given files have been ingested.

    Updates the version registry with current hash, timestamp, and
    incremented version number.

    Parameters
    ----------
    file_paths : list[str]
        Files that were just ingested.
    version_file : str
        Path to the version registry JSON.

    Returns
    -------
    dict
        The updated registry.
    """
    registry = load_version_registry(version_file)
    now = datetime.now(timezone.utc).isoformat()

    for fp in file_paths:
        current_hash = _file_hash(fp)
        prev = registry.get(fp, {})
        prev_version = prev.get("version", 0)

        registry[fp] = {
            "hash": current_hash,
            "version": prev_version + 1,
            "last_ingested": now,
            "file_size_bytes": os.path.getsize(fp),
        }

    save_version_registry(registry, version_file)
    print(f"📋  Version registry updated for {len(file_paths)} file(s)")
    return registry
