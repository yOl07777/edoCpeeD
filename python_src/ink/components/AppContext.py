from __future__ import annotations

from typing import Any

AppContext: dict[str, Any] = {
    "provider": "deepseek",
    "isActive": True,
    "exitCode": None,
}


def createAppContext(**kwargs: Any) -> dict[str, Any]:
    context = dict(AppContext)
    context.update(kwargs)
    return context


def AppContextProvider(*children: Any, **kwargs: Any) -> dict[str, Any]:
    return {"type": "app_context_provider", "context": createAppContext(**kwargs), "children": list(children)}


default = AppContext
_module_migration_placeholder = createAppContext
