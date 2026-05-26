from __future__ import annotations

from typing import Any

from python_src.hooks.useExitOnCtrlCD import useExitOnCtrlCD


async def useExitOnCtrlCDWithKeybindings(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    bindings = dict(kwargs.get("bindings", {}) or {})
    key = str(kwargs.get("key", ""))
    if bindings.get(key) == "exit":
        return {"provider": "deepseek", "shouldExit": True, "source": "keybinding"}
    result = await useExitOnCtrlCD(key=key, ctrl=kwargs.get("ctrl", False), count=kwargs.get("count", 1))
    result["source"] = "ctrl-c"
    return result


__all__ = ["useExitOnCtrlCDWithKeybindings"]
