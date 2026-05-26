from __future__ import annotations

from typing import Any


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def isValidImagePaste(content: Any) -> bool:
    return _get(content, "type") == "image" and bool(_get(content, "content", ""))


def getImagePasteIds(pastedContents: dict[int, Any] | None) -> list[int] | None:
    if not pastedContents:
        return None
    ids = [int(_get(content, "id")) for content in pastedContents.values() if isValidImagePaste(content)]
    return ids or None


__all__ = ["getImagePasteIds", "isValidImagePaste"]
