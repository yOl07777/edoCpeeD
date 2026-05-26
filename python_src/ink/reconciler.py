from __future__ import annotations

import os
import time
from typing import Any

dispatcher = {"provider": "deepseek", "kind": "local_reconciler"}
_profile = {"lastCommitMs": 0.0, "lastYogaMs": 0.0, "commitStart": None}


async def markCommitStart(*args: Any, **kwargs: Any) -> Any:
    _profile["commitStart"] = time.perf_counter()
    return _profile["commitStart"]


async def getLastCommitMs(*args: Any, **kwargs: Any) -> Any:
    if _profile["commitStart"] is not None:
        _profile["lastCommitMs"] = (time.perf_counter() - float(_profile["commitStart"])) * 1000
        _profile["commitStart"] = None
    return _profile["lastCommitMs"]


async def recordYogaMs(*args: Any, **kwargs: Any) -> Any:
    value = float(args[0] if args else kwargs.get("ms", 0))
    _profile["lastYogaMs"] = value
    return value


async def getLastYogaMs(*args: Any, **kwargs: Any) -> Any:
    return _profile["lastYogaMs"]


async def resetProfileCounters(*args: Any, **kwargs: Any) -> Any:
    _profile.update({"lastCommitMs": 0.0, "lastYogaMs": 0.0, "commitStart": None})
    return dict(_profile)


async def isDebugRepaintsEnabled(*args: Any, **kwargs: Any) -> Any:
    return str(kwargs.get("value", os.environ.get("DEEPSEEK_DEBUG_REPAINTS", ""))).lower() in {"1", "true", "yes", "on"}


async def getOwnerChain(*args: Any, **kwargs: Any) -> Any:
    node = args[0] if args else kwargs.get("node")
    chain = []
    while isinstance(node, dict):
        chain.append(node)
        node = node.get("parent")
    return chain
