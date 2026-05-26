from __future__ import annotations

from typing import Any

CursorDeclarationContext: dict[str, Any] = {"provider": "deepseek", "visible": True, "style": "block"}


def createCursorDeclaration(**kwargs: Any) -> dict[str, Any]:
    context = dict(CursorDeclarationContext)
    context.update(kwargs)
    return context


default = CursorDeclarationContext
_module_migration_placeholder = createCursorDeclaration
