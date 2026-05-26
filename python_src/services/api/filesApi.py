"""Local file API helpers for the DeepSeek migration."""

from __future__ import annotations

import hashlib
import shutil
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def _safe_name(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in name).strip("._") or "file"


async def parseFileSpecs(files: Any) -> list[dict[str, Any]]:
    """Normalize file specs from strings, paths, or dictionaries."""

    if files is None:
        return []
    if isinstance(files, (str, Path, dict)):
        items = [files]
    else:
        items = list(files)
    specs: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, dict):
            path = item.get("path") or item.get("file") or item.get("name")
            specs.append({**item, "path": str(path) if path is not None else ""})
        else:
            specs.append({"path": str(item)})
    return specs


async def buildDownloadPath(file_spec: dict[str, Any] | str, output_dir: str | Path = ".") -> Path:
    """Build a safe local download path for a file descriptor or URL."""

    if isinstance(file_spec, dict):
        name = file_spec.get("filename") or file_spec.get("name") or file_spec.get("path") or file_spec.get("url") or "file"
    else:
        name = file_spec
    parsed = urlparse(str(name))
    candidate = Path(parsed.path if parsed.scheme else str(name)).name
    return Path(output_dir).expanduser().resolve() / _safe_name(candidate)


async def uploadFile(path: str | Path, purpose: str = "assistants", **metadata: Any) -> dict[str, Any]:
    """Return a local file descriptor compatible with OpenAI-style file APIs."""

    file_path = Path(path).expanduser().resolve()
    data = file_path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    return {
        "id": f"file-{digest[:16]}",
        "filename": file_path.name,
        "path": str(file_path),
        "bytes": len(data),
        "sha256": digest,
        "purpose": purpose,
        "created_at": int(file_path.stat().st_mtime),
        "metadata": metadata,
    }


async def uploadSessionFiles(files: Any, purpose: str = "assistants") -> list[dict[str, Any]]:
    return [await uploadFile(spec["path"], purpose=purpose) for spec in await parseFileSpecs(files) if spec.get("path")]


async def downloadFile(file_spec: dict[str, Any] | str | bytes) -> bytes:
    """Read file content from a local descriptor/path/bytes value.

    Remote URLs are intentionally not fetched here; this migration keeps the
    helper deterministic and network-free.
    """

    if isinstance(file_spec, bytes):
        return file_spec
    if isinstance(file_spec, dict):
        if "content" in file_spec:
            content = file_spec["content"]
            return content if isinstance(content, bytes) else str(content).encode("utf-8")
        path = file_spec.get("path") or file_spec.get("filename")
    else:
        path = str(file_spec)
    parsed = urlparse(str(path))
    if parsed.scheme in {"http", "https"}:
        raise ValueError("Remote file downloads are disabled in the local DeepSeek migration")
    return Path(str(path)).expanduser().resolve().read_bytes()


async def downloadAndSaveFile(file_spec: dict[str, Any] | str | bytes, output_dir: str | Path = ".") -> dict[str, Any]:
    data = await downloadFile(file_spec)
    target = await buildDownloadPath(file_spec if not isinstance(file_spec, bytes) else "download.bin", output_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return {"path": str(target), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


async def downloadSessionFiles(files: Any, output_dir: str | Path = ".") -> list[dict[str, Any]]:
    return [await downloadAndSaveFile(spec, output_dir=output_dir) for spec in await parseFileSpecs(files)]


async def listFilesCreatedAfter(directory: str | Path, created_after: float | int) -> list[dict[str, Any]]:
    root = Path(directory).expanduser().resolve()
    result: list[dict[str, Any]] = []
    threshold = float(created_after)
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        stat = path.stat()
        created = getattr(stat, "st_birthtime", stat.st_ctime)
        if created >= threshold or stat.st_mtime >= threshold:
            result.append({"path": str(path), "bytes": stat.st_size, "created_at": created, "modified_at": stat.st_mtime})
    return sorted(result, key=lambda item: item["path"])

