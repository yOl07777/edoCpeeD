"""Local `/vim` command."""

from __future__ import annotations

from typing import Any

from python_src.utils.config import getGlobalConfig, saveGlobalConfig


async def getEditorMode() -> str:
    config = await getGlobalConfig()
    mode = str(config.get("editorMode") or "normal")
    return "normal" if mode == "emacs" else mode


async def setEditorMode(mode: str) -> dict[str, str]:
    normalized = "vim" if mode == "vim" else "normal"
    await saveGlobalConfig({"editorMode": normalized})
    return {
        "type": "text",
        "value": (
            "Editor mode set to vim. Use Escape key to toggle between INSERT and NORMAL modes."
            if normalized == "vim"
            else "Editor mode set to normal. Using standard keyboard bindings."
        ),
    }


async def call(*_args: Any, **_kwargs: Any) -> dict[str, str]:
    current = await getEditorMode()
    return await setEditorMode("normal" if current == "vim" else "vim")
