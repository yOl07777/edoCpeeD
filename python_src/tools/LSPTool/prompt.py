"""Prompt constants for LSPTool."""

from __future__ import annotations

LSP_TOOL_NAME = "lsp_symbol_search"
DESCRIPTION = (
    "Search Python, TypeScript, TSX, and JavaScript files for function and class symbols. "
    "This Python migration is a local symbol index shim, not a live language server."
)

__all__ = ["DESCRIPTION", "LSP_TOOL_NAME"]
