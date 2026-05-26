from __future__ import annotations

from pathlib import Path
from typing import Any


def memory_payload(component: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"type": component, "provider": "deepseek"}
    payload.update(kwargs)
    return payload


def normalize_memory_file(file: Any, index: int = 0, selected: str | None = None) -> dict[str, Any]:
    path = file.get("path") if isinstance(file, dict) else file
    path_text = str(path or ".deepseek/memory.md")
    label = file.get("label", Path(path_text).name) if isinstance(file, dict) else Path(path_text).name
    return {"index": index, "path": path_text, "label": str(label), "selected": path_text == selected}

