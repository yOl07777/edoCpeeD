"""Runnable Python tool implementations for the migrated project."""

from __future__ import annotations

from typing import Any

__all__ = ["DEFAULT_TOOLS", "build_default_tool_registry", "get_deepseek_tools"]


def get_deepseek_tools() -> list[dict[str, Any]]:
    from python_src.tools.runtime import get_deepseek_tools as _get_deepseek_tools

    return _get_deepseek_tools()


def build_default_tool_registry() -> Any:
    from python_src.tools.runtime import build_default_tool_registry as _build_default_tool_registry

    return _build_default_tool_registry()


def __getattr__(name: str) -> Any:
    if name == "DEFAULT_TOOLS":
        from python_src.tools.runtime import DEFAULT_TOOLS

        return DEFAULT_TOOLS
    raise AttributeError(name)
