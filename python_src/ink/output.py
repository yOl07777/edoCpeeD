from __future__ import annotations

from typing import Any


def createOutput(*args: Any, **kwargs: Any) -> dict[str, Any]:
    writes: list[str] = []

    def write(value: Any) -> int:
        text = str(value)
        writes.append(text)
        return len(text)

    return {"provider": "deepseek", "writes": writes, "write": write, "stdout": kwargs.get("stdout")}


default = createOutput
_module_migration_placeholder = createOutput
