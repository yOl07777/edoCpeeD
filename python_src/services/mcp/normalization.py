"""Name normalization helpers for MCP server and tool identifiers."""

from __future__ import annotations

import re
import unicodedata


async def normalizeNameForMCP(name: str) -> str:
    """Return an MCP-safe identifier made from ASCII letters, digits, and ``_``."""

    normalized = unicodedata.normalize("NFKD", str(name or ""))
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_name = re.sub(r"[^A-Za-z0-9_]+", "_", ascii_name).strip("_")
    ascii_name = re.sub(r"_+", "_", ascii_name)
    return ascii_name or "mcp"
