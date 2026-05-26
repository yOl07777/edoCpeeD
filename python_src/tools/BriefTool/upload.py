"""Dry-run BriefTool upload shim."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


async def uploadBriefAttachment(*args: Any, **kwargs: Any) -> dict[str, Any]:
    path_value = kwargs.get("path") or (args[0] if args else "")
    path = Path(str(path_value)).expanduser()
    content = kwargs.get("content")
    if content is None and path.is_file():
        data = path.read_bytes()
        name = path.name
    else:
        data = str(content or "").encode("utf-8")
        name = path.name or str(kwargs.get("name") or "attachment.txt")
    digest = hashlib.sha256(data).hexdigest()
    return {
        "uploaded": False,
        "provider": "local-dry-run",
        "name": name,
        "bytes": len(data),
        "sha256": digest,
        "uri": f"brief://local/{digest[:16]}/{name}",
    }


__all__ = ["uploadBriefAttachment"]
