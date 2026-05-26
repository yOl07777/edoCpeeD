"""LSPTool schema compatibility helpers."""

from __future__ import annotations

from typing import Any

LSP_OPERATIONS = {
    "document_symbol",
    "find_references",
    "go_to_definition",
    "hover",
    "incoming_calls",
    "outgoing_calls",
    "prepare_call_hierarchy",
    "workspace_symbol",
    "symbol_search",
}

lspToolInputSchema = {
    "type": "object",
    "properties": {
        "operation": {"type": "string", "enum": sorted(LSP_OPERATIONS)},
        "query": {"type": "string"},
        "path": {"type": "string"},
        "line": {"type": "integer"},
        "character": {"type": "integer"},
    },
}


async def isValidLSPOperation(*args: Any, **kwargs: Any) -> bool:
    value = str(args[0] if args else kwargs.get("operation", ""))
    normalized = value.replace("-", "_").lower()
    return normalized in LSP_OPERATIONS


__all__ = ["LSP_OPERATIONS", "isValidLSPOperation", "lspToolInputSchema"]
