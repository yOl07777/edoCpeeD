"""Prompt text for NotebookEditTool."""

from __future__ import annotations

from python_src.tools.NotebookEditTool.constants import NOTEBOOK_EDIT_TOOL_NAME

DESCRIPTION = "Create or replace a cell in a Jupyter .ipynb file."
PROMPT = (
    f"Use {NOTEBOOK_EDIT_TOOL_NAME} to update one notebook cell at a time. "
    "Provide the target path, zero-based cell_index, full source text, and optional cell_type."
)

__all__ = ["DESCRIPTION", "PROMPT"]
