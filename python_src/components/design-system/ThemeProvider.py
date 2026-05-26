from __future__ import annotations

import os
from typing import Any

from importlib import import_module


async def ThemeProvider(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    name = kwargs.get("theme") or kwargs.get("name") or os.environ.get("DEEPSEEK_THEME", "dark")
    return shared.ui_payload("theme_provider", theme=name, tokens=shared.theme(name), children=kwargs.get("children") or (args[0] if args else None))

async def usePreviewTheme(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    name = kwargs.get("theme") or (args[0] if args else "dark")
    return shared.ui_payload("preview_theme", theme=name, tokens=shared.theme(name))

async def useTheme(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    name = kwargs.get("theme") or os.environ.get("DEEPSEEK_THEME", "dark")
    return shared.theme(name)

async def useThemeSetting(*args: Any, **kwargs: Any) -> Any:
    name = kwargs.get("theme") or os.environ.get("DEEPSEEK_THEME", "dark")
    return {"provider": "deepseek", "theme": name, "source": "env" if os.environ.get("DEEPSEEK_THEME") else "default"}


__all__ = ["ThemeProvider", "usePreviewTheme", "useTheme", "useThemeSetting"]
