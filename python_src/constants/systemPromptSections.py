from __future__ import annotations

from typing import Any


_SECTIONS: list[dict[str, Any]] = []


async def systemPromptSection(name: Any = "", text: Any = "", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    section = {
        "name": str(kwargs.get("name") or name or f"section-{len(_SECTIONS) + 1}"),
        "text": str(kwargs.get("text") or text or ""),
        "cached": bool(kwargs.get("cached", True)),
        "priority": int(kwargs.get("priority", len(_SECTIONS))),
    }
    _SECTIONS.append(section)
    return dict(section)


async def DANGEROUS_uncachedSystemPromptSection(name: Any = "", text: Any = "", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    kwargs["cached"] = False
    return await systemPromptSection(name, text, **kwargs)


async def resolveSystemPromptSections(*_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
    return sorted((dict(section) for section in _SECTIONS), key=lambda item: item.get("priority", 0))


async def clearSystemPromptSections(*_args: Any, **_kwargs: Any) -> None:
    _SECTIONS.clear()
    return None


__all__ = [
    "DANGEROUS_uncachedSystemPromptSection",
    "clearSystemPromptSections",
    "resolveSystemPromptSections",
    "systemPromptSection",
]
