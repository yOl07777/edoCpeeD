from __future__ import annotations

import importlib
from typing import Any

root_mod = importlib.import_module("python_src.ink.root")


async def render(*args: Any, **kwargs: Any) -> Any:
    root = await root_mod.createRoot(args[0] if args else kwargs.get("node"), **kwargs)
    await root["render"]()
    return root


default = render
_module_migration_placeholder = render
