from __future__ import annotations

import importlib
from typing import Any

render_mod = importlib.import_module("python_src.ink.render-to-screen")


async def renderSync(node: Any, **kwargs: Any) -> dict[str, Any]:
    return await render_mod.renderToScreen(node, **kwargs)


async def createRoot(*args: Any, **kwargs: Any) -> Any:
    state = {"provider": "deepseek", "node": args[0] if args else kwargs.get("node"), "screen": None, "renders": 0}

    async def render(node: Any = None) -> dict[str, Any]:
        if node is not None:
            state["node"] = node
        state["screen"] = await renderSync(state["node"], **kwargs)
        state["renders"] += 1
        return state["screen"]

    def unmount() -> dict[str, Any]:
        state["node"] = None
        state["screen"] = None
        return state

    state.update({"render": render, "unmount": unmount})
    return state
