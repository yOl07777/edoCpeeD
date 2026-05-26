from __future__ import annotations

from typing import Any


class TerminalQuerier:
    def __init__(self, stdout: Any = None, *args: Any, **kwargs: Any) -> None:
        self.stdout = stdout
        self.responses: list[Any] = []

    def onResponse(self, response: Any) -> None:
        self.responses.append(response)

    async def query(self, sequence: str, fallback: Any = None) -> Any:
        if self.stdout is not None and hasattr(self.stdout, "write"):
            self.stdout.write(sequence)
        return self.responses.pop(0) if self.responses else fallback


async def cursorPosition(*args: Any, **kwargs: Any) -> Any:
    response = args[0] if args else kwargs.get("response")
    if isinstance(response, str) and response.startswith("\x1b[") and response.endswith("R"):
        body = response[2:-1]
        row, _, col = body.partition(";")
        return {"row": int(row) - 1, "col": int(col) - 1}
    return {"row": int(kwargs.get("row", 0)), "col": int(kwargs.get("col", 0))}


async def da1(*args: Any, **kwargs: Any) -> Any:
    return {"provider": "deepseek", "sequence": "\x1b[c", "response": kwargs.get("response")}


async def da2(*args: Any, **kwargs: Any) -> Any:
    return {"provider": "deepseek", "sequence": "\x1b[>c", "response": kwargs.get("response")}


async def decrqm(*args: Any, **kwargs: Any) -> Any:
    mode = int(args[0] if args else kwargs.get("mode", 0))
    return {"provider": "deepseek", "sequence": f"\x1b[?{mode}$p", "mode": mode, "enabled": kwargs.get("enabled")}


async def kittyKeyboard(*args: Any, **kwargs: Any) -> Any:
    return {"provider": "deepseek", "supported": bool(kwargs.get("supported", False))}


async def oscColor(*args: Any, **kwargs: Any) -> Any:
    color = args[0] if args else kwargs.get("color", "10")
    return {"provider": "deepseek", "sequence": f"\x1b]{color};?\x1b\\", "color": color, "response": kwargs.get("response")}


async def xtversion(*args: Any, **kwargs: Any) -> Any:
    response = str(args[0] if args else kwargs.get("response", ""))
    return response.removeprefix("\x1bP>|").removesuffix("\x1b\\")
