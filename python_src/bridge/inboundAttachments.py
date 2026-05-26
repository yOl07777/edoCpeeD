"""Resolve file attachments referenced by inbound bridge messages."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import httpx

from .bridgeConfig import getBridgeAccessToken, getBridgeBaseUrl

DOWNLOAD_TIMEOUT_MS = 30_000


def extractInboundAttachments(msg: Any) -> list[dict[str, str]]:
    if not isinstance(msg, dict):
        return []
    raw = msg.get("file_attachments")
    if not isinstance(raw, list):
        return []
    attachments: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        file_uuid = item.get("file_uuid")
        file_name = item.get("file_name")
        if isinstance(file_uuid, str) and isinstance(file_name, str):
            attachments.append({"file_uuid": file_uuid, "file_name": file_name})
    return attachments


def _sanitize_file_name(name: str) -> str:
    base = Path(name).name
    safe = re.sub(r"[^a-zA-Z0-9._-]", "_", base)
    return safe or "attachment"


def _uploads_dir(session_id: str | None = None) -> Path:
    root = os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("DEEPSEEK_CODE_HOME")
    base = Path(root).expanduser() if root else Path.home() / ".deepcode"
    return base / "uploads" / (session_id or os.getenv("DEEPCODE_SESSION_ID", "default"))


async def _resolve_one(
    att: dict[str, str],
    *,
    client: httpx.AsyncClient | None = None,
    session_id: str | None = None,
) -> str | None:
    token = getBridgeAccessToken()
    if not token:
        return None
    owns_client = client is None
    http = client or httpx.AsyncClient(timeout=DOWNLOAD_TIMEOUT_MS / 1000)
    try:
        url = f"{getBridgeBaseUrl().rstrip('/')}/api/oauth/files/{att['file_uuid']}/content"
        response = await http.get(url, headers={"Authorization": f"Bearer {token}"})
        if response.status_code != 200:
            return None
        safe_name = _sanitize_file_name(att["file_name"])
        prefix = re.sub(r"[^a-zA-Z0-9_-]", "_", att["file_uuid"][:8] or "file")
        out_dir = _uploads_dir(session_id)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{prefix}-{safe_name}"
        out_path.write_bytes(response.content)
        return str(out_path)
    except (OSError, httpx.HTTPError):
        return None
    finally:
        if owns_client:
            await http.aclose()


async def resolveInboundAttachments(
    attachments: list[dict[str, str]],
    *,
    client: httpx.AsyncClient | None = None,
    session_id: str | None = None,
) -> str:
    if not attachments:
        return ""
    paths = [
        path
        for path in [
            await _resolve_one(att, client=client, session_id=session_id)
            for att in attachments
        ]
        if path
    ]
    return (" ".join(f'@"{path}"' for path in paths) + " ") if paths else ""


def prependPathRefs(content: str | list[dict[str, Any]], prefix: str) -> str | list[dict[str, Any]]:
    if not prefix:
        return content
    if isinstance(content, str):
        return prefix + content
    last_text = -1
    for idx, block in enumerate(content):
        if isinstance(block, dict) and block.get("type") == "text":
            last_text = idx
    if last_text >= 0:
        result = [dict(block) for block in content]
        result[last_text]["text"] = prefix + str(result[last_text].get("text", ""))
        return result
    return [*content, {"type": "text", "text": prefix.rstrip()}]


async def resolveAndPrepend(
    msg: Any,
    content: str | list[dict[str, Any]],
    *,
    client: httpx.AsyncClient | None = None,
    session_id: str | None = None,
) -> str | list[dict[str, Any]]:
    attachments = extractInboundAttachments(msg)
    if not attachments:
        return content
    prefix = await resolveInboundAttachments(attachments, client=client, session_id=session_id)
    return prependPathRefs(content, prefix)
