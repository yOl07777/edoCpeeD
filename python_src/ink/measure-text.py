from __future__ import annotations

import re
import unicodedata
from typing import Any

ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\].*?(?:\x07|\x1b\\)")


def measureText(*args: Any, **kwargs: Any) -> int:
    text = str(args[0] if args else kwargs.get("text", ""))
    text = ANSI_RE.sub("", text)
    width = 0
    for char in text:
        if char in "\r\n":
            continue
        if unicodedata.combining(char):
            continue
        width += 2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1
    return width


default = measureText
_module_migration_placeholder = measureText
