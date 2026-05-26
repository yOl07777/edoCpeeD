from __future__ import annotations

from typing import Any, Callable

from ._basic import first_mapping, pick

_permission_callbacks: dict[str, Callable[[Any], Any] | Any] = {}
_sandbox_callbacks: dict[str, Callable[[Any], Any] | Any] = {}

async def clearAllPendingCallbacks(*args: Any, **kwargs: Any) -> Any:
    permission_count = len(_permission_callbacks)
    sandbox_count = len(_sandbox_callbacks)
    _permission_callbacks.clear()
    _sandbox_callbacks.clear()
    return {"provider": "deepseek", "cleared": permission_count + sandbox_count}

async def hasPermissionCallback(*args: Any, **kwargs: Any) -> Any:
    callback_id = str(args[0] if args else kwargs.get("id", ""))
    return callback_id in _permission_callbacks

async def hasSandboxPermissionCallback(*args: Any, **kwargs: Any) -> Any:
    callback_id = str(args[0] if args else kwargs.get("id", ""))
    return callback_id in _sandbox_callbacks

async def processMailboxPermissionResponse(*args: Any, **kwargs: Any) -> Any:
    response = first_mapping(*args, kwargs)
    callback_id = str(pick(response, "id", "callbackId", default=""))
    callback = _permission_callbacks.pop(callback_id, None)
    if callable(callback):
        callback(response)
    return {"provider": "deepseek", "handled": callback is not None, "id": callback_id, "response": response}

async def processSandboxPermissionResponse(*args: Any, **kwargs: Any) -> Any:
    response = first_mapping(*args, kwargs)
    callback_id = str(pick(response, "id", "callbackId", default=""))
    callback = _sandbox_callbacks.pop(callback_id, None)
    if callable(callback):
        callback(response)
    return {"provider": "deepseek", "handled": callback is not None, "id": callback_id, "response": response}

async def registerPermissionCallback(*args: Any, **kwargs: Any) -> Any:
    callback_id = str(args[0] if args else kwargs.get("id", ""))
    callback = args[1] if len(args) > 1 else kwargs.get("callback", True)
    if callback_id:
        _permission_callbacks[callback_id] = callback
    return {"provider": "deepseek", "registered": bool(callback_id), "id": callback_id}

async def registerSandboxPermissionCallback(*args: Any, **kwargs: Any) -> Any:
    callback_id = str(args[0] if args else kwargs.get("id", ""))
    callback = args[1] if len(args) > 1 else kwargs.get("callback", True)
    if callback_id:
        _sandbox_callbacks[callback_id] = callback
    return {"provider": "deepseek", "registered": bool(callback_id), "id": callback_id}

async def unregisterPermissionCallback(*args: Any, **kwargs: Any) -> Any:
    callback_id = str(args[0] if args else kwargs.get("id", ""))
    removed = _permission_callbacks.pop(callback_id, None) is not None
    return {"provider": "deepseek", "removed": removed, "id": callback_id}

async def useSwarmPermissionPoller(*args: Any, **kwargs: Any) -> Any:
    return {
        "provider": "deepseek",
        "pendingPermissions": len(_permission_callbacks),
        "pendingSandboxPermissions": len(_sandbox_callbacks),
    }
