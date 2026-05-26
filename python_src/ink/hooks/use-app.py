from __future__ import annotations

from typing import Any


def useApp(*args: Any, **kwargs: Any) -> dict[str, Any]:
    exit_code = kwargs.get("exitCode")
    exited: list[Any] = []

    def exit(error: Any = None) -> dict[str, Any]:
        exited.append(error)
        return {"provider": "deepseek", "exited": True, "error": error, "exitCode": exit_code}

    return {"provider": "deepseek", "exit": exit, "exited": exited, "exitCode": exit_code}


default = useApp
_module_migration_placeholder = useApp
