from __future__ import annotations

from typing import Any


def diff_payload(component: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"type": component, "provider": "deepseek"}
    payload.update(kwargs)
    return payload


def summarize_diff(diff: str) -> dict[str, int]:
    lines = str(diff or "").splitlines()
    return {
        "lines": len(lines),
        "added": sum(1 for line in lines if line.startswith("+") and not line.startswith("+++")),
        "removed": sum(1 for line in lines if line.startswith("-") and not line.startswith("---")),
        "files": sum(1 for line in lines if line.startswith("diff --git ") or line.startswith("+++ ")),
    }


def normalize_file(file: Any, index: int = 0) -> dict[str, Any]:
    if isinstance(file, dict):
        path = file.get("path") or file.get("file") or file.get("name") or f"file-{index}"
        diff = str(file.get("diff") or "")
    else:
        path = str(file)
        diff = ""
    item = {"index": index, "path": str(path), "diff": diff}
    item.update(summarize_diff(diff))
    return item

