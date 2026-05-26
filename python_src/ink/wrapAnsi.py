from __future__ import annotations

import importlib
from typing import Any

wrapText = importlib.import_module("python_src.ink.wrap-text").wrapText


def wrapAnsi(*args: Any, **kwargs: Any) -> str:
    return wrapText(*args, **kwargs)


default = wrapAnsi
_module_migration_placeholder = wrapAnsi
