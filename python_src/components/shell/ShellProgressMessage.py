from __future__ import annotations

from typing import Any

from python_src.components.shell._shared import shell_payload


async def ShellProgressMessage(*args: Any, **kwargs: Any) -> Any:
    command = str(kwargs.get("command") or (args[0] if args else "shell"))
    status = str(kwargs.get("status") or "running")
    return shell_payload("shell_progress_message", command=command, status=status, text=f"{command}: {status}")


__all__ = ["ShellProgressMessage"]
