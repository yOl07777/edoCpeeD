from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, path_label


async def ExportDialog(*args: Any, **kwargs: Any) -> Any:
    formats = normalize_items(option(args, kwargs, "formats", ["markdown", "json"]), text_key="name")
    path = path_label(option(args, kwargs, "path", option(args, kwargs, "output", "")))
    return component_payload("export_dialog", path=path, formats=formats, selected=str(option(args, kwargs, "format", formats[0]["name"] if formats else "markdown")))


__all__ = ["ExportDialog"]
