from __future__ import annotations

import importlib
from typing import Any

measureText = importlib.import_module("python_src.ink.measure-text").measureText


def wrapText(*args: Any, **kwargs: Any) -> str:
    text = str(args[0] if args else kwargs.get("text", ""))
    width = int(args[1] if len(args) > 1 else kwargs.get("width", 80))
    if width <= 0:
        return text
    output: list[str] = []
    for line in text.splitlines() or [""]:
        current = ""
        for word in line.split(" "):
            candidate = word if not current else current + " " + word
            if measureText(candidate) <= width:
                current = candidate
            else:
                if current:
                    output.append(current)
                while measureText(word) > width:
                    output.append(word[:width])
                    word = word[width:]
                current = word
        output.append(current)
    return "\n".join(output)


default = wrapText
_module_migration_placeholder = wrapText
