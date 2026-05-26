from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def LanguagePicker(*args: Any, **kwargs: Any) -> Any:
    selected = str(option(args, kwargs, "selected", option(args, kwargs, "language", scalar_arg(args, "python"))))
    languages = normalize_items(option(args, kwargs, "languages", ["python", "typescript", "markdown", "json"]), text_key="name")
    for language in languages:
        language["selected"] = language["name"] == selected
    return component_payload("language_picker", selected=selected, languages=languages)


__all__ = ["LanguagePicker"]
