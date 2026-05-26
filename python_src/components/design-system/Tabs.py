from __future__ import annotations

from typing import Any

from importlib import import_module


async def Tab(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    tab_id = kwargs.get("id") or kwargs.get("value") or (args[0] if args else "tab")
    return shared.ui_payload("tab", id=str(tab_id), label=str(kwargs.get("label") or tab_id), selected=bool(kwargs.get("selected", False)), content=kwargs.get("content"))

async def Tabs(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    tabs = kwargs.get("tabs") or (args[0] if args else []) or []
    selected = kwargs.get("selected")
    rows = []
    for index, item in enumerate(tabs):
        if isinstance(item, dict):
            tab_id = item.get("id", item.get("value", index))
            label = item.get("label", tab_id)
            content = item.get("content")
        else:
            tab_id = item
            label = item
            content = None
        rows.append({"id": str(tab_id), "label": str(label), "content": content, "selected": selected == tab_id or (selected is None and index == 0)})
    return shared.ui_payload("tabs", tabs=rows, selected=next((row["id"] for row in rows if row["selected"]), None))

async def useTabHeaderFocus(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    index = int(kwargs.get("index") or (args[0] if args else 0) or 0)
    count = int(kwargs.get("count") or (args[1] if len(args) > 1 else 0) or 0)
    delta = int(kwargs.get("delta") or 0)
    next_index = max(0, min(index + delta, max(0, count - 1)))
    return shared.ui_payload("tab_header_focus", index=index, nextIndex=next_index, count=count)

async def useTabsWidth(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    tabs = kwargs.get("tabs") or (args[0] if args else []) or []
    labels = [str(tab.get("label", tab.get("id", "")) if isinstance(tab, dict) else tab) for tab in tabs]
    return shared.ui_payload("tabs_width", width=sum(len(label) + 4 for label in labels), labels=labels)


__all__ = ["Tab", "Tabs", "useTabHeaderFocus", "useTabsWidth"]
